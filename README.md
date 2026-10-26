# TELL practice kit

**Find the tell.** Write a Python trading bot, run it in markets we generate, and compete on profit. No real money, ever.

[日本語は下にあります](#日本語)

## Quick start

```bash
git clone https://github.com/telltradingbot-lang/tell-practice.git
cd tell-practice
pip install -r requirements.txt
python run.py examples/random_bot.py
python run.py my_bot.py
```

Requires Python 3.10 or later and numpy. No install? Open `TELL_quickstart.ipynb` in Google Colab.

## The game

Four fictional products trade in a fictional city. Each one hides something in how it moves. Find it, and your bot wins.

| Product | What it is | Position limit |
|---|---|---|
| BRCK | Brick. The city's foundation. Calm prices, wide spreads. | ±50 |
| GOLDN | Gold bar. Moody. The market's mood shifts from time to time. | ±20 |
| STEL | Steel. Every tower starts with steel. | ±30 |
| TOWR | Tower Co. The builder behind the city's skyline. | ±30 |

Each scenario is 2,000 ticks. Your score is profit and loss at the end, with open positions marked at the final mid price.

## Writing a bot

Edit `my_bot.py`. Your class needs one method, `on_tick(state)`, which returns a list of orders.

```python
from tell import Order

class MyBot:
    def on_tick(self, state):
        if state.mid["BRCK"][-1] < 99:
            return [Order("BRCK", 5)]      # market buy 5
        return []
```

What `state` gives you (nothing from the future):

| Field | Meaning |
|---|---|
| `state.t` | Current tick |
| `state.mid[p]` | Mid-price history up to now |
| `state.bid[p]`, `state.ask[p]` | Current best bid and ask |
| `state.flow_buy[p]`, `state.flow_sell[p]` | Quantities NPC traders bought / sold with market orders, up to the previous tick |
| `state.position[p]` | Your position (negative means short) |
| `state.limits[p]` | Your position limit |
| `state.cash` | Your cash |

## Execution rules

- `Order(p, qty)` with no price is a market order. It fills at the ask (buy) or bid (sell) and pays a 1 bps fee.
- `Order(p, qty, price)` is a limit order that lasts for this tick only. It fills only if priced strictly inside the bid/ask and an NPC trader arrives on the other side. No fee.
- Orders beyond your position limit are cut automatically.

## Practice vs the real thing

`data/practice.npz` holds 50 practice scenarios. Final rankings use **500 hidden scenarios** generated the same way, so a bot tuned to these 50 will not automatically win. Look for structure, not for the answers to these 50.

## Rules

- Bots run without internet access and with a time limit per tick.
- One account per person. Free to enter, play money only.
- Season details and prizes: see the TELL page.

Contact: tell.tradingbot@gmail.com

---

## 日本語

**Find the tell.** Pythonでトレーディングボットを書き、運営が生成した市場で収益性を競う大会の練習キットです。本物のお金は一切使いません。

### はじめかた

```bash
git clone https://github.com/telltradingbot-lang/tell-practice.git
cd tell-practice
pip install -r requirements.txt
python run.py examples/random_bot.py
python run.py my_bot.py
```

Python 3.10以上とnumpyが必要です。インストールなしで試すなら、`TELL_quickstart.ipynb` を Google Colab で開いてください。

### ゲームの中身

架空の街で、4つの架空の商品が取引されています。それぞれの値動きには何かが隠れています。それを見抜いたボットが勝ちます。

| 銘柄 | 説明 | ポジション上限 |
|---|---|---|
| BRCK | レンガ。都市の土台。値動きは穏やかだが、板のスプレッドは広い。 | ±50 |
| GOLDN | 金の延べ棒。気分屋。相場の空気が、ときどき入れ替わる。 | ±20 |
| STEL | 鉄鋼。ビルを建てるには、まず鉄がいる。 | ±30 |
| TOWR | 建設会社。街の高層ビルを手がける。 | ±30 |

1シナリオは2,000tick。最終tickの中値で保有分を時価評価した損益がスコアです。

### ボットの書き方

`my_bot.py` を編集します。必要なのは、注文のリストを返す `on_tick(state)` だけです。`state` で見られる情報は英語版の表のとおりです（未来のデータは含まれません）。`flow_buy` / `flow_sell` は、NPCが成行で売買した数量の履歴（歩み値）です。

### 約定ルール

- 価格なしの `Order(p, qty)` は成行。買いはask、売りはbidで約定し、1bpsの手数料がかかります
- 価格つきの `Order(p, qty, price)` は、そのtickだけ有効な指値。bid/askより内側の価格で、反対側にNPCが来たときだけ約定します。手数料なし
- ポジション上限を超える分は自動で切り捨てられます

### 練習と本番

`data/practice.npz` には練習用シナリオが50本入っています。最終順位は同じ仕組みで作った**非公開の500シナリオ**で決まるので、この50本に合わせ込んでも勝てるとは限りません。50本の答えではなく、市場の構造を探してください。

お問い合わせ：tell.tradingbot@gmail.com
