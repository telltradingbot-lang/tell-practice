"""
Score your bot on the practice scenarios.

  python run.py my_bot.py            # all 50 practice scenarios
  python run.py my_bot.py --n 10     # first 10 only (faster while iterating)
  python run.py examples/random_bot.py
"""
import argparse, importlib.util, inspect, sys, time
import numpy as np
from tell import load_practice, run, PRODUCTS


def load_bot_class(path):
    spec = importlib.util.spec_from_file_location("user_bot", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["user_bot"] = mod
    spec.loader.exec_module(mod)
    classes = [c for _, c in inspect.getmembers(mod, inspect.isclass)
               if c.__module__ == "user_bot" and hasattr(c, "on_tick")]
    if not classes:
        sys.exit(f"No class with an on_tick() method was found in {path}.")
    named = [c for c in classes if c.__name__ == "MyBot"]
    return (named or classes)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot")
    ap.add_argument("--n", type=int, default=None, help="number of practice scenarios to run")
    a = ap.parse_args()

    Bot = load_bot_class(a.bot)
    scenarios = load_practice()[: a.n]
    t0 = time.time()
    pnls, by_prod = [], {p: [] for p in PRODUCTS}
    for sc in scenarios:
        r = run(Bot(), sc)
        pnls.append(r["pnl"])
        for p in PRODUCTS:
            by_prod[p].append(r["pnl_by_product"][p])
        print(f"{sc.name}  {r['pnl']:>10.0f}")
    x = np.array(pnls)
    se = x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else float("nan")
    print("\n" + "=" * 44)
    print(f"Bot            {Bot.__name__}")
    print(f"Scenarios      {len(x)}")
    print(f"Average P&L    {x.mean():.0f}  (±{2*se:.0f})")
    print(f"Median P&L     {np.median(x):.0f}")
    print(f"Win rate       {(x > 0).mean():.0%}")
    print("By product     " + "  ".join(f"{p} {np.mean(by_prod[p]):.0f}" for p in PRODUCTS))
    print(f"Time           {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
