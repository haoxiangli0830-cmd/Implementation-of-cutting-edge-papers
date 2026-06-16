"""eq-00-fama-french — Fama-French factors + Carhart momentum.

Two jobs:
  (1) REPLICATE the documented factor premia from the official Ken French data,
      and show the well-known post-2010 decay (especially value, HML).
  (2) CONSTRUCT a momentum factor from scratch on a free stock universe and
      validate it against French's official MOM (correlation check).

Run:  python implementation.py   ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.data import get_prices, monthly_returns           # noqa: E402
from core.data.factors import get_french_factors            # noqa: E402
from core.evaluation import performance_summary, sharpe      # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# ~40 large-cap US names with history back to ~2005, for from-scratch construction
UNIVERSE = [
    "AAPL", "MSFT", "JNJ", "JPM", "XOM", "PG", "KO", "PFE", "WMT", "CVX",
    "MRK", "INTC", "CSCO", "ORCL", "IBM", "MCD", "DIS", "HD", "BA", "CAT",
    "MMM", "AXP", "VZ", "T", "WFC", "C", "BAC", "GS", "UNH", "ABT",
    "AMGN", "TXN", "QCOM", "NKE", "LOW", "SBUX", "COST", "HON", "UPS", "GE",
]


def replicate_premia() -> pd.DataFrame:
    ff = get_french_factors("F-F_Research_Data_5_Factors_2x3")
    mom = get_french_factors("F-F_Momentum_Factor").rename(columns={"Mom": "WML"})
    factors = ff.join(mom, how="inner")
    cols = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "WML"]

    rows = {}
    for c in cols:
        s = factors[c]
        post = s.loc["2010":]
        rows[c] = {
            "ann_premium_%": s.mean() * 12 * 100,
            "sharpe_full": sharpe(s, 12),
            "sharpe_since2010": sharpe(post, 12),
            "tstat_full": s.mean() / s.std(ddof=1) * np.sqrt(len(s)),
        }
    table = pd.DataFrame(rows).T
    table.to_csv(RESULTS / "factor_premia.csv")

    # cumulative growth chart
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    (1 + factors[cols]).cumprod().plot(ax=ax, lw=1.1)
    ax.set_yscale("log")
    ax.set_title("Ken French factors — cumulative growth of $1 (long/short)")
    ax.set_ylabel("Equity (log)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS / "factor_cumulative.png", dpi=120)
    return table, factors


def construct_momentum(factors: pd.DataFrame) -> float:
    """Build a 12-1 momentum long/short from scratch; correlate with French WML."""
    prices = get_prices(UNIVERSE, start="2005-01-01")
    pm = prices.resample("ME").last()
    rets = monthly_returns(prices)

    # signal available at start of month t: return over t-12 .. t-1 (skip latest month)
    signal = pm.pct_change(11).shift(1)
    ranks = signal.rank(axis=1, pct=True)
    long = ranks >= 2 / 3
    short = ranks <= 1 / 3
    wml = (rets.where(long).mean(axis=1) - rets.where(short).mean(axis=1)).dropna()

    french = factors["WML"].reindex(wml.index)
    both = pd.concat([wml.rename("ours"), french.rename("french")], axis=1).dropna()
    corr = both["ours"].corr(both["french"])
    both.to_csv(RESULTS / "momentum_construction.csv")
    return corr, wml


def main() -> None:
    table, factors = replicate_premia()
    corr, wml = construct_momentum(factors)

    print("\n" + "=" * 64)
    print("eq-00-fama-french — factor premia (1963 -> 2026)")
    print("=" * 64)
    print(table.round(2).to_string())
    print("\nKey result: most premia positive long-run, but Sharpe SINCE 2010 is")
    print("much weaker — classic factor decay (look at HML / value).")

    print("\n" + "-" * 64)
    print("From-scratch 12-1 momentum vs official French WML")
    print("-" * 64)
    print(f"  our WML  : ann {wml.mean()*12*100:5.1f}%  Sharpe {sharpe(wml,12):.2f}  n={len(wml)}")
    print(f"  correlation with French WML: {corr:.2f}  "
          + ("GOOD construction" if corr > 0.5 else "weak"))
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
