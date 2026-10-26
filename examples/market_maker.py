"""
A simple market maker on BRCK: quote inside the spread around a moving average,
and lean the quotes against your inventory. It looks safe. Run it and see.
"""
from tell import Order


class SimpleMarketMaker:
    def on_tick(self, state):
        if state.t < 20:
            return []
        fair = state.mid["BRCK"][-30:].mean()
        skew = 0.02 * state.position["BRCK"]
        return [
            Order("BRCK", 5, round(fair - 1.0 - skew, 2)),
            Order("BRCK", -5, round(fair + 1.0 - skew, 2)),
        ]
