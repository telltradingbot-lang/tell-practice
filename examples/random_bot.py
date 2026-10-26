"""Trades at random. A useful floor: your bot should beat this."""
import numpy as np
from tell import Order


class RandomBot:
    def reset(self):
        self.rng = np.random.default_rng(12345)

    def on_tick(self, state):
        orders = []
        for p in state.products:
            if self.rng.random() < 0.05:
                qty = int(self.rng.integers(1, 4)) * (1 if self.rng.random() < 0.5 else -1)
                orders.append(Order(p, qty))
        return orders
