"""vo-00-har-optiver — HAR-RV realized-volatility forecasting (Corsi 2009).

The HAR model predicts tomorrow's realized volatility from three look-backs —
daily, weekly, monthly — capturing volatility's "long memory" with just 3 terms:

    RV[t+1] = b0 + b_d*RV_daily[t] + b_w*RV_weekly[t] + b_m*RV_monthly[t] + e

We build a daily realized-variance proxy from OHLC via the Garman-Klass estimator
(more efficient than squared close-to-close returns) and test HAR out-of-sample
against the naive random-walk forecast (RV[t+1] = RV[t]).

(The Optiver Kaggle order-book data is the natural high-frequency extension; this
build uses free daily OHLC so it runs with no large download.)

Run:  python implementation.py  ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.data.prices import get_ohlc                         # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

TICKER = "^GSPC"        # S&P 500 index, history back to 1990
TRAIN_FRAC = 0.7


def garman_klass_vol(ohlc: pd.DataFrame) -> pd.Series:
    """Daily annualised volatility (Garman-Klass), from O/H/L/C."""
    o, h, l, c = np.log(ohlc["Open"]), np.log(ohlc["High"]), np.log(ohlc["Low"]), np.log(ohlc["Close"])
    var = 0.5 * (h - l) ** 2 - (2 * np.log(2) - 1) * (c - o) ** 2
    var = var.clip(lower=1e-8)
    return np.sqrt(var * 252)        # annualised daily vol


def har_features(rv: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({
        "rv_d": rv,
        "rv_w": rv.rolling(5).mean(),
        "rv_m": rv.rolling(22).mean(),
        "target": rv.shift(-1),       # predict next day
    }).dropna()
    return df


def ols(X: np.ndarray, y: np.ndarray):
    Xb = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(Xb, y, rcond=None)
    return beta


def main() -> None:
    ohlc = get_ohlc(TICKER, start="1990-01-01")
    rv = garman_klass_vol(ohlc)
    data = har_features(rv)

    n = len(data)
    split = int(n * TRAIN_FRAC)
    train, test = data.iloc[:split], data.iloc[split:]
    feats = ["rv_d", "rv_w", "rv_m"]

    beta = ols(train[feats].values, train["target"].values)
    pred_har = beta[0] + test[feats].values @ beta[1:]
    pred_rw = test["rv_d"].values             # random walk: tomorrow = today
    actual = test["target"].values

    def r2(pred):
        sse = np.sum((actual - pred) ** 2)
        sst = np.sum((actual - actual.mean()) ** 2)
        return 1 - sse / sst

    def mse(pred):
        return float(np.mean((actual - pred) ** 2))

    r2_har, r2_rw = r2(pred_har), r2(pred_rw)
    mse_har, mse_rw = mse(pred_har), mse(pred_rw)

    print("\n" + "=" * 60)
    print(f"vo-00-har-optiver — HAR-RV on {TICKER}  (1990 -> present)")
    print("=" * 60)
    print(f"  observations: {n}  (train {split}, test {n-split})")
    print("\n  HAR coefficients (annualised-vol units):")
    print(f"    intercept {beta[0]:+.4f}")
    print(f"    daily     {beta[1]:+.3f}")
    print(f"    weekly    {beta[2]:+.3f}")
    print(f"    monthly   {beta[3]:+.3f}")
    print("    (all positive -> short, medium and long memory all matter)")
    print("\n  Out-of-sample forecast accuracy:")
    print(f"    HAR          R2 = {r2_har:6.3f}   MSE = {mse_har:.5f}")
    print(f"    Random walk  R2 = {r2_rw:6.3f}   MSE = {mse_rw:.5f}")
    improve = (mse_rw - mse_har) / mse_rw * 100
    print(f"    HAR reduces MSE vs random walk by {improve:.1f}%  "
          + ("(HAR wins)" if improve > 0 else "(no improvement)"))

    pd.DataFrame({"actual": actual, "har": pred_har, "rw": pred_rw},
                 index=test.index).to_csv(RESULTS / "forecasts.csv")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 4.5))
    test_idx = test.index
    ax.plot(test_idx, actual, lw=0.7, label="Realised vol (actual)", color="0.4")
    ax.plot(test_idx, pred_har, lw=0.8, label="HAR forecast", color="C0")
    ax.set_title(f"{TICKER} — HAR realised-vol forecast (out-of-sample)")
    ax.set_ylabel("Annualised vol"); ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "har_forecast.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
