"""
TELL match engine (public)

Every tick, your bot's on_tick(state) is called and returns a list of orders.

  Order(product, qty, price=None)
    qty   : positive = buy, negative = sell
    price : None = market order. A buy at price >= ask (or a sell at price <= bid)
            also executes immediately as a market order.
            Any other price is a limit order that rests for that tick only and
            fills if an NPC trader arrives.

Execution rules
  - Market orders fill at the ask (buy) / bid (sell) and pay a 1 bps taker fee
  - Limit orders only fill when priced strictly inside the market bid/ask.
    Each tick, NPC buyers/sellers arrive with some quantity and fill the best-priced
    limit orders first. No fee on limit fills.
  - Anything beyond your position limit is cut automatically
Scoring: profit and loss, with open positions marked at the final mid price
"""
from dataclasses import dataclass, field
import os
import numpy as np

PRODUCTS = ["BRCK", "GOLDN", "STEL", "TOWR"]
POSITION_LIMITS = {"BRCK": 50, "GOLDN": 20, "STEL": 30, "TOWR": 30}
TAKER_FEE_BPS = 1.0
BRCK_HALF_SPREAD = 2.0
OTHER_HALF_SPREAD_BPS = 5.0


@dataclass
class Order:
    product: str
    qty: int
    price: float | None = None


@dataclass
class Scenario:
    name: str
    mid: dict
    npc_buy_qty: dict
    npc_sell_qty: dict
    bid: dict = field(default_factory=dict)
    ask: dict = field(default_factory=dict)

    def __post_init__(self):
        for p in PRODUCTS:
            m = self.mid[p]
            if p == "BRCK":
                self.bid[p], self.ask[p] = m - BRCK_HALF_SPREAD, m + BRCK_HALF_SPREAD
            else:
                hs = OTHER_HALF_SPREAD_BPS / 1e4
                self.bid[p], self.ask[p] = m * (1 - hs), m * (1 + hs)

    @property
    def n_ticks(self):
        return len(self.mid[PRODUCTS[0]])


class State:
    """What your bot can see at tick t. It never contains future data."""
    def __init__(self, sc: Scenario, t: int, position: dict, cash: float):
        self.t = t
        self.n_ticks = sc.n_ticks
        self.products = PRODUCTS
        self.limits = dict(POSITION_LIMITS)
        self.position = dict(position)
        self.cash = cash
        self.mid = {p: sc.mid[p][:t + 1] for p in PRODUCTS}
        # Trade tape: market-order quantities NPCs bought/sold up to the previous tick
        self.flow_buy = {p: sc.npc_buy_qty[p][:t] for p in PRODUCTS}
        self.flow_sell = {p: sc.npc_sell_qty[p][:t] for p in PRODUCTS}
        self.bid = {p: float(sc.bid[p][t]) for p in PRODUCTS}
        self.ask = {p: float(sc.ask[p][t]) for p in PRODUCTS}


def _clamp(pos, qty, limit):
    if qty > 0:
        return max(0, min(qty, limit - pos))
    return min(0, max(qty, -limit - pos))


def run(bot, sc: Scenario):
    fee = TAKER_FEE_BPS / 1e4
    n = sc.n_ticks
    pos = {p: 0 for p in PRODUCTS}
    cash = 0.0
    equity = np.empty(n)
    cash_by_product = {p: 0.0 for p in PRODUCTS}
    n_trades = 0

    if hasattr(bot, "reset"):
        bot.reset()

    for t in range(n):
        orders = bot.on_tick(State(sc, t, pos, cash)) or []
        resting = {p: {"buy": [], "sell": []} for p in PRODUCTS}

        for o in orders:
            p = o.product
            if p not in pos or o.qty == 0:
                continue
            b, a = sc.bid[p][t], sc.ask[p][t]
            lim = POSITION_LIMITS[p]
            if o.qty > 0 and (o.price is None or o.price >= a):
                q = _clamp(pos[p], o.qty, lim)
                if q:
                    c = q * a * (1 + fee)
                    cash -= c; cash_by_product[p] -= c; pos[p] += q; n_trades += 1
            elif o.qty < 0 and (o.price is None or o.price <= b):
                q = _clamp(pos[p], o.qty, lim)
                if q:
                    c = -q * b * (1 - fee)
                    cash += c; cash_by_product[p] += c; pos[p] += q; n_trades += 1
            elif o.qty > 0:
                resting[p]["buy"].append([o.price, o.qty])
            else:
                resting[p]["sell"].append([o.price, -o.qty])

        for p in PRODUCTS:
            lim = POSITION_LIMITS[p]
            demand = int(sc.npc_buy_qty[p][t])
            a, b = sc.ask[p][t], sc.bid[p][t]
            sells = [x for x in resting[p]["sell"] if x[0] < a]
            buys = [x for x in resting[p]["buy"] if x[0] > b]
            for price, q in sorted(sells, key=lambda x: x[0]):
                if demand <= 0:
                    break
                fill = -_clamp(pos[p], -min(q, demand), lim)
                if fill:
                    cash += fill * price; cash_by_product[p] += fill * price
                    pos[p] -= fill; demand -= fill; n_trades += 1
            supply = int(sc.npc_sell_qty[p][t])
            for price, q in sorted(buys, key=lambda x: -x[0]):
                if supply <= 0:
                    break
                fill = _clamp(pos[p], min(q, supply), lim)
                if fill:
                    cash -= fill * price; cash_by_product[p] -= fill * price
                    pos[p] += fill; supply -= fill; n_trades += 1

        equity[t] = cash + sum(pos[p] * sc.mid[p][t] for p in PRODUCTS)

    pnl_by_product = {p: cash_by_product[p] + pos[p] * sc.mid[p][-1] for p in PRODUCTS}
    return {"pnl": float(equity[-1]), "equity": equity,
            "pnl_by_product": pnl_by_product, "n_trades": n_trades}


def load_practice(path=None):
    """Load the public practice scenarios as a list of Scenario objects."""
    path = path or os.path.join(os.path.dirname(__file__), "..", "data", "practice.npz")
    d = np.load(path)
    names = list(d["names"])
    out = []
    for i, name in enumerate(names):
        out.append(Scenario(
            name=str(name),
            mid={p: d[f"mid_{p}"][i].astype(np.float64) for p in PRODUCTS},
            npc_buy_qty={p: d[f"buy_{p}"][i].astype(np.int64) for p in PRODUCTS},
            npc_sell_qty={p: d[f"sell_{p}"][i].astype(np.int64) for p in PRODUCTS},
        ))
    return out
