"""
Your bot. Edit this class, then run:

  python run.py my_bot.py

What `state` gives you at tick t (nothing from the future):
  state.t                     current tick (0 to n_ticks-1)
  state.products              ["BRCK", "GOLDN", "STEL", "TOWR"]
  state.mid[product]          mid-price history up to now (numpy array)
  state.bid[product]          current best bid
  state.ask[product]          current best ask
  state.flow_buy[product]     quantities NPCs bought with market orders, up to the previous tick
  state.flow_sell[product]    the same for sells
  state.position[product]     your current position (negative = short)
  state.limits[product]       your position limit
  state.cash                  your cash

Return a list of Order(product, qty, price):
  qty > 0 buys, qty < 0 sells
  price=None sends a market order; any other price is a limit order for this tick only
"""
from tell import Order


class MyBot:
    def reset(self):
        # Called at the start of every scenario
        pass

    def on_tick(self, state):
        orders = []
        # Example: buy 5 BRCK once at the start and hold
        if state.t == 0:
            orders.append(Order("BRCK", 5))
        return orders
