"""cr-f1-crypto-factors — Common Risk Factors in Cryptocurrency
(Liu, Tsyvinski & Wu, 2022, Journal of Finance).

Claim: three factors — crypto MARKET, SIZE, and MOMENTUM — capture the
cross-section of crypto returns, and crypto momentum (1-4 week) is strong.

We build all three on a free yfinance universe (weekly), and backtest the
cross-sectional momentum long/short through the shared engine.

Run:  python implementation.py  ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.data import get_prices                              # noqa: E402
from core.backtest import backtest                            # noqa: E402
from core.evaluation import performance_summary, sharpe, deflated_sharpe_ratio  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)
PPY = 52  # weekly

UNIVERSE = [
    "BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "BCH-USD", "ADA-USD",
    "XLM-USD", "TRX-USD", "XMR-USD", "ETC-USD", "DOGE-USD", "LINK-USD",
    "DASH-USD", "ZEC-USD", "NEO-USD", "XTZ-USD",
]
START = "2019-01-01"
COST_BPS = 30.0  # crypto trading is pricier than equities


def _dollar_volume() -> pd.DataFrame | None:
    """Weekly dollar volume (size proxy). Best-effort via yfinance."""
    try:
        import yfinance as yf
        df = yf.download(UNIVERSE, start=START, auto_adjust=True,
                         progress=False, threads=False)
        dv = (df["Close"] * df["Volume"]).resample("W-FRI").mean()
        return dv
    except Exception as e:                       # pragma: no cover
        print(f"  (size factor skipped: {e})")
        return None


def momentum_long_short(weekly_ret: pd.DataFrame, lookback: int) -> pd.DataFrame:
    """Cross-sectional weekly momentum: long top third / short bottom third."""
    signal = (1 + weekly_ret).rolling(lookback).apply(np.prod, raw=True) - 1
    signal = signal.shift(1)                      # lag: decide on past, hold next
    ranks = signal.rank(axis=1, pct=True)
    n = ranks.notna().sum(axis=1).clip(lower=1)
    long = (ranks >= 2 / 3).astype(float)
    short = (ranks <= 1 / 3).astype(float)
    weights = long.div(long.sum(axis=1).clip(lower=1), axis=0) \
        - short.div(short.sum(axis=1).clip(lower=1), axis=0)
    return backtest(weights, weekly_ret, cost_bps=COST_BPS)


def main() -> None:
    prices = get_prices(UNIVERSE, start=START)
    weekly = prices.resample("W-FRI").last()
    wret = weekly.pct_change()

    # --- MARKET factor: equal-weight basket ------------------------------------
    market = wret.mean(axis=1).dropna()

    # --- MOMENTUM factor: 3-week cross-sectional long/short --------------------
    bt = momentum_long_short(wret, lookback=3)
    mom = bt["net"].dropna()

    # --- SIZE factor: small-minus-big by dollar-volume proxy -------------------
    size = None
    dv = _dollar_volume()
    if dv is not None:
        sz_rank = dv.shift(1).rank(axis=1, pct=True)
        small = (sz_rank <= 1 / 3).astype(float)
        big = (sz_rank >= 2 / 3).astype(float)
        w = small.div(small.sum(axis=1).clip(lower=1), axis=0) \
            - big.div(big.sum(axis=1).clip(lower=1), axis=0)
        size = backtest(w, wret, cost_bps=COST_BPS)["net"].dropna()

    # --- overfitting check on momentum -----------------------------------------
    sweep = [sharpe(momentum_long_short(wret, lb)["net"], PPY) for lb in (1, 2, 3, 4)]
    dsr = deflated_sharpe_ratio(mom, n_trials=4,
                                sr_trials_std=float(np.nanstd(sweep, ddof=1)),
                                periods_per_year=PPY)

    # --- report ----------------------------------------------------------------
    def line(name, s):
        d = performance_summary(s, PPY)
        print(f"  {name:<10} ann {d['cagr']*100:6.1f}%  vol {d['ann_vol']*100:5.1f}%"
              f"  Sharpe {d['sharpe']:5.2f}  maxDD {d['max_drawdown']*100:6.1f}%")

    print("\n" + "=" * 64)
    print("cr-f1-crypto-factors  (weekly, 2019 -> present, 16 coins)")
    print("=" * 64)
    line("MARKET", market)
    line("MOMENTUM", mom)
    if size is not None:
        line("SIZE", size)
    print(f"\n  momentum vs market corr: {mom.corr(market.reindex(mom.index)):.2f} "
          "(low = distinct factor)")
    print(f"  momentum look-back sweep Sharpe (1-4wk): "
          + ", ".join(f"{s:.2f}" for s in sweep))
    print(f"  Deflated Sharpe (4 trials): {dsr:.3f} "
          + ("PASS" if dsr > 0.95 else "weak"))

    pd.DataFrame({"market": market, "momentum": mom}).to_csv(RESULTS / "factors.csv")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    (1 + market).cumprod().plot(ax=ax, label="Market (EW basket)")
    (1 + mom).cumprod().plot(ax=ax, label="Momentum L/S")
    if size is not None:
        (1 + size).cumprod().plot(ax=ax, label="Size (SMB proxy)")
    ax.set_yscale("log"); ax.set_title("Crypto factors — growth of $1")
    ax.legend(); ax.grid(True, alpha=0.3); fig.tight_layout()
    fig.savefig(RESULTS / "crypto_factors.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
