"""eq-f2-virtue-complexity — The Virtue of Complexity in Return Prediction
(Kelly, Malamud & Zhou, 2024, Journal of Finance).

Counter-intuitive claim: for market-return prediction, MORE model complexity keeps
helping out-of-sample — even when the number of parameters far exceeds the number
of observations (P >> T), where classical statistics says you must overfit. The
trick is many random nonlinear features + ridge shrinkage.

We predict the next-month market excess return (Ken French Mkt-RF) from the 13
JKP theme factors, expanded into P random Fourier features, and trace the
out-of-sample market-timing Sharpe as complexity c = P/T grows past 1.

Run:  python implementation.py   ->  results/
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.data.factors import get_french_factors                # noqa: E402
from core.evaluation import sharpe                               # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

T_TRAIN = 120                       # rolling window (months)
ALPHA = 1.0                         # ridge shrinkage (meaningful, KMZ-style)
P_GRID = [2, 3, 5, 8, 12, 20, 40, 80, 160, 320, 640, 1280]


def load_data():
    cands = [p for p in glob.glob(str(HERE / "**" / "*.csv"), recursive=True)
             if "results" not in p.replace("\\", "/").lower()]
    jkp = pd.read_csv(cands[0], parse_dates=["date"])
    X = jkp.pivot_table(index="date", columns="name", values="ret").dropna()
    mkt = get_french_factors("F-F_Research_Data_5_Factors_2x3")["Mkt-RF"]
    df = X.join(mkt.rename("mkt"), how="inner").dropna()
    feats = df.drop(columns="mkt")
    target = df["mkt"].shift(-1)                  # predict next month
    ok = target.notna()
    return feats[ok].values, target[ok].values, df.index[ok]


def rff_map(P, d, seed=0, scale=1.0):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((d, P)) * scale
    b = rng.uniform(0, 2 * np.pi, P)
    return W, b


def featurize(Xz, W, b):
    P = W.shape[1]
    return np.sqrt(2.0 / P) * np.cos(Xz @ W + b)     # 1/sqrt(P): keep shrinkage comparable across P


def dual_ridge_predict(Ztr, ytr, Zte, alpha):
    """Ridge via the T x T dual form — cheap even when P >> T."""
    K = Ztr @ Ztr.T
    A = K + alpha * np.eye(len(ytr))
    sol = np.linalg.solve(A, ytr)
    return Zte @ (Ztr.T @ sol)


def run_complexity(X, y):
    n = len(y)
    rows = []
    for P in P_GRID:
        W, b = rff_map(P, X.shape[1], seed=0)
        preds, rets = [], []
        for t in range(T_TRAIN, n):
            tr = slice(t - T_TRAIN, t)
            mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-8
            Ztr = featurize((X[tr] - mu) / sd, W, b)
            Zte = featurize((X[t:t + 1] - mu) / sd, W, b)
            pred = dual_ridge_predict(Ztr, y[tr], Zte, ALPHA)[0]
            preds.append(pred); rets.append(y[t])
        preds, rets = np.array(preds), np.array(rets)
        # KMZ market-timing weight = the conditional-mean forecast (magnitude, not just sign).
        # Standardise the weight so the comparison across P is about timing, not bet size.
        w = preds / (np.std(preds) + 1e-12)
        strat = w * rets
        sr = sharpe(pd.Series(strat), 12)
        r2 = 1 - np.sum((rets - preds) ** 2) / np.sum(rets ** 2)
        rows.append({"P": P, "complexity": P / T_TRAIN, "timing_sharpe": sr,
                     "oos_r2_%": r2 * 100, "timing_ann_%": strat.mean() * 12 * 100})
    return pd.DataFrame(rows)


def main():
    X, y, dates = load_data()
    print(f"  sample: {len(y)} months  ({dates[0].date()} -> {dates[-1].date()}), "
          f"{X.shape[1]} base factors, train window {T_TRAIN}")
    res = run_complexity(X, y)
    res.to_csv(RESULTS / "complexity_curve.csv", index=False)

    bh = sharpe(pd.Series(y[T_TRAIN:]), 12)         # buy-and-hold market

    print("\n" + "=" * 60)
    print("eq-f2 Virtue of Complexity — OOS market timing vs complexity")
    print("=" * 60)
    print(f"  {'P':>6}{'c=P/T':>8}{'timing Sharpe':>16}{'OOS R2 %':>10}")
    for _, r in res.iterrows():
        print(f"  {int(r.P):>6}{r.complexity:>8.2f}{r.timing_sharpe:>16.2f}{r['oos_r2_%']:>10.2f}")
    print(f"\n  buy-and-hold market Sharpe: {bh:.2f}")
    rising = res["timing_sharpe"].iloc[-1] > res["timing_sharpe"].iloc[0]
    print("  ->", "Sharpe RISES with complexity (VoC holds here)." if rising
          else "Sharpe does not rise with complexity in this sample.")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(res["complexity"], res["timing_sharpe"], "o-")
    ax.axvline(1.0, color="0.6", ls="--", lw=1, label="c = 1 (P = T)")
    ax.axhline(bh, color="C1", ls=":", lw=1, label="buy & hold")
    ax.set_xscale("log")
    ax.set_xlabel("model complexity  c = P / T  (log)")
    ax.set_ylabel("out-of-sample timing Sharpe")
    ax.set_title("Virtue of Complexity — timing Sharpe vs model size")
    ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "complexity_curve.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
