"""rk-01-var-es-backtesting — Market-risk VaR / Expected Shortfall + Basel backtesting.

The day-to-day work of a bank market-risk desk: estimate Value-at-Risk and Expected
Shortfall on a trading book, then prove to the regulator that the model is adequate
by backtesting it (Basel traffic-light, Kupiec, Christoffersen).

We use an equal-weight multi-asset ETF book as the "trading portfolio".

Methods & practices covered:
  - VaR (99%, Basel) and ES (97.5%, FRTB) via Historical / Parametric / Monte-Carlo
  - Rolling out-of-sample backtest: count VaR exceptions
  - Kupiec POF (unconditional coverage) + Christoffersen (independence) tests
  - Basel traffic-light zone on the last 250 days

Run:  python implementation.py   ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.data import get_prices                                # noqa: E402
from core.risk import (historical_var, historical_es, parametric_var, parametric_es,
                       monte_carlo_var, kupiec_pof, christoffersen_independence,
                       basel_traffic_light)                     # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

BOOK = ["SPY", "EFA", "EEM", "TLT", "IEF", "GLD", "DBC", "VNQ"]
WINDOW = 500            # estimation window (days)
ALPHA_BASEL = 0.99     # Basel market-risk VaR confidence
ALPHA_FRTB = 0.975     # FRTB Expected Shortfall confidence


def main():
    prices = get_prices(BOOK, start="2007-01-01")
    pnl = prices.pct_change().mean(axis=1).dropna()     # equal-weight book P&L

    # --- rolling 99% historical-VaR backtest ----------------------------------
    var_series, breaches, dates = [], [], []
    for t in range(WINDOW, len(pnl)):
        est = pnl.iloc[t - WINDOW:t]
        v = historical_var(est, ALPHA_BASEL)
        var_series.append(v)
        breaches.append(int(pnl.iloc[t] < -v))
        dates.append(pnl.index[t])
    var_series = pd.Series(var_series, index=dates)
    breaches = pd.Series(breaches, index=dates)
    realised = pnl.reindex(dates)

    n = len(breaches)
    exc = int(breaches.sum())
    expected = (1 - ALPHA_BASEL) * n
    lr_k, p_k = kupiec_pof(exc, n, ALPHA_BASEL)
    lr_c, p_c = christoffersen_independence(breaches.values)
    zone = basel_traffic_light(int(breaches.iloc[-250:].sum()), 250)

    # --- current risk numbers (latest window), three methods ------------------
    last = pnl.iloc[-WINDOW:]
    table = pd.DataFrame({
        "VaR 99% (Basel)": [historical_var(last, ALPHA_BASEL),
                            parametric_var(last, ALPHA_BASEL),
                            monte_carlo_var(last, ALPHA_BASEL)],
        "ES 97.5% (FRTB)": [historical_es(last, ALPHA_FRTB),
                            parametric_es(last, ALPHA_FRTB),
                            historical_es(last, ALPHA_FRTB)],
    }, index=["Historical", "Parametric", "Monte-Carlo"]) * 100
    table.to_csv(RESULTS / "risk_numbers.csv")

    print("\n" + "=" * 62)
    print("rk-01 — Market-risk VaR/ES + Basel backtesting")
    print(f"Book: equal-weight {', '.join(BOOK)}")
    print("=" * 62)
    print("\nCurrent 1-day risk (% of book value):")
    print(table.round(2).to_string())
    print(f"\nBacktest of 99% historical VaR over {n} days:")
    print(f"  exceptions observed : {exc}   (expected ~{expected:.0f})")
    print(f"  Kupiec POF test     : LR={lr_k:.2f}, p={p_k:.3f}  "
          + ("OK" if p_k > 0.05 else "REJECT coverage"))
    print(f"  Christoffersen ind. : LR={lr_c:.2f}, p={p_c:.3f}  "
          + ("OK (no clustering)" if p_c > 0.05 else "clustered breaches"))
    print(f"  Basel zone (last 250d, {int(breaches.iloc[-250:].sum())} exc): {zone}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(realised.index, realised.values * 100, lw=0.5, color="0.6", label="daily P&L")
    ax.plot(var_series.index, -var_series.values * 100, lw=0.8, color="C0", label="-99% VaR")
    br = realised[breaches == 1]
    ax.scatter(br.index, br.values * 100, s=12, color="red", zorder=5, label="exceptions")
    ax.set_title("rk-01 — VaR backtest: daily P&L vs 99% VaR (red = breach)")
    ax.set_ylabel("% of book"); ax.legend(loc="lower left"); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "var_backtest.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
