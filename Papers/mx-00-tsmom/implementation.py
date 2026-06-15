"""mx-00-tsmom — Time-Series Momentum (Moskowitz, Ooi & Pedersen 2012).

Strategy in one breath: for each instrument, go long if its trailing 12-month
return is positive, short if negative; size each position inversely to its own
volatility (target ~40% annualised per instrument); hold one month; average
across a diversified basket. All signals are lagged one month -> no look-ahead.

Run:  python implementation.py
Outputs land in ./results/ ; a summary prints to stdout.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# make the shared library importable (program root is two levels up)
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.data import get_prices, monthly_returns          # noqa: E402
from core.backtest import backtest                          # noqa: E402
from core.evaluation import performance_summary, sharpe, deflated_sharpe_ratio  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# Diversified cross-asset basket of liquid ETFs (futures proxies), all live by 2007
UNIVERSE = ["SPY", "QQQ", "EFA", "EEM", "IEF", "TLT", "LQD", "GLD", "DBC", "VNQ", "UUP"]
START = "2007-01-01"
TARGET_VOL = 0.40          # per-instrument annualised vol target (paper uses 40%)
VOL_WINDOW = 12            # months to estimate ex-ante vol
COST_BPS = 10.0            # round-trip transaction cost assumption


def tsmom_weights(prices_m: pd.DataFrame, rets_m: pd.DataFrame, lookback: int) -> pd.DataFrame:
    """Vol-scaled, one-month-lagged time-series-momentum weights."""
    signal = np.sign(prices_m.pct_change(lookback))                 # +/-1 trend
    ann_vol = rets_m.rolling(VOL_WINDOW).std() * np.sqrt(12)        # ex-ante vol
    scale = (TARGET_VOL / ann_vol).clip(upper=5.0)                  # cap leverage
    raw = signal * scale
    weights = raw.shift(1) / len(prices_m.columns)                 # lag + diversify
    return weights


def run(lookback: int = 12) -> pd.DataFrame:
    prices = get_prices(UNIVERSE, start=START)
    prices_m = prices.resample("ME").last()
    rets_m = monthly_returns(prices)
    weights = tsmom_weights(prices_m, rets_m, lookback)
    return backtest(weights, rets_m, cost_bps=COST_BPS)


def main() -> None:
    # --- headline run (12-month look-back) -------------------------------------
    bt = run(lookback=12)
    gross_summary = performance_summary(bt["gross"])
    net_summary = performance_summary(bt["net"])

    # --- parameter sweep -> multiple-testing penalty for the Deflated Sharpe ----
    lookbacks = [3, 6, 9, 12, 15]
    sweep_sharpes = [sharpe(run(lb)["net"]) for lb in lookbacks]
    sr_std = float(np.nanstd(sweep_sharpes, ddof=1))
    dsr = deflated_sharpe_ratio(bt["net"], n_trials=len(lookbacks), sr_trials_std=sr_std)

    # --- save artifacts --------------------------------------------------------
    bt.to_csv(RESULTS / "backtest.csv")
    summary = pd.DataFrame({"gross": gross_summary, "net": net_summary}).T
    summary.to_csv(RESULTS / "summary.csv")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    bt["equity_gross"].plot(ax=ax, label="Gross", lw=1.4)
    bt["equity_net"].plot(ax=ax, label=f"Net ({COST_BPS:.0f} bps)", lw=1.4)
    ax.set_yscale("log")
    ax.set_title("Time-Series Momentum (12m) — cumulative growth of $1")
    ax.set_ylabel("Equity (log scale)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS / "equity_curve.png", dpi=120)

    # --- report to stdout ------------------------------------------------------
    print("\n" + "=" * 60)
    print("mx-00-tsmom — Time-Series Momentum  (2007 -> present)")
    print("=" * 60)
    print(f"Universe ({len(UNIVERSE)}): {', '.join(UNIVERSE)}")
    print(f"\n{'metric':<16}{'GROSS':>12}{'NET':>12}")
    for k in ["cagr", "ann_vol", "sharpe", "sortino", "max_drawdown", "skew", "psr_vs_0"]:
        print(f"{k:<16}{gross_summary[k]:>12.3f}{net_summary[k]:>12.3f}")
    print("\nMultiple-testing / overfitting check")
    print(f"  look-back sweep (net Sharpe): "
          + ", ".join(f"{lb}m={s:.2f}" for lb, s in zip(lookbacks, sweep_sharpes)))
    print(f"  Deflated Sharpe Ratio (5 trials): {dsr:.3f}  "
          + ("PASS (>0.95)" if dsr > 0.95 else "weak / does not clearly survive"))
    print(f"\nSaved: {RESULTS/'equity_curve.png'}, summary.csv, backtest.csv\n")


if __name__ == "__main__":
    main()
