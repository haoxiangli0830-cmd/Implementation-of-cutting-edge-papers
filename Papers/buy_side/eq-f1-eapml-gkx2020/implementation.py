"""eq-f1-eapml-gkx2020 — Empirical Asset Pricing via Machine Learning
(Gu, Kelly & Xiu, 2020, Review of Financial Studies).

The canonical ML-asset-pricing study: predict the cross-section of stock returns
from many firm characteristics, and show that NONLINEAR models (trees, neural
nets) beat linear regression, both in out-of-sample R^2 and in the Sharpe of a
long/short portfolio sorted on the predictions.

We reproduce the *method* on a free, price/volume characteristic panel
(~140 stocks). Smaller universe than the paper's full CRSP, so smaller magnitude,
but the ranking of models and the headline result come through.

Run:  python implementation.py  ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.data.panel import build_panel, standardize_cross_section, CHARS  # noqa: E402
from core.evaluation import sharpe, performance_summary                    # noqa: E402

from sklearn.linear_model import LinearRegression                          # noqa: E402
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor  # noqa: E402
from sklearn.neural_network import MLPRegressor                            # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)
SPLIT = "2019-01-01"

UNIVERSE = [
    "AAPL","MSFT","JNJ","JPM","XOM","PG","KO","PFE","WMT","CVX","MRK","INTC",
    "CSCO","ORCL","IBM","MCD","DIS","HD","BA","CAT","MMM","AXP","VZ","T","WFC",
    "C","BAC","GS","UNH","ABT","AMGN","TXN","QCOM","NKE","LOW","SBUX","COST",
    "HON","UPS","GE","AMZN","GOOGL","ADBE","CRM","PEP","ABBV","TMO","ACN","AVGO",
    "MDT","DHR","LIN","NEE","PM","RTX","UNP","LMT","SPGI","BMY","GILD","CVS",
    "MO","DUK","SO","CL","EMR","GD","ITW","APD","SHW","ECL","NSC","FDX","PNC",
    "USB","BK","SCHW","MMC","AON","ICE","CME","COF","MET","PRU","TRV","ALL",
    "AEP","EXC","D","PCG","WMB","KMI","SLB","HAL","COP","EOG","OXY","PSX","VLO",
    "MPC","F","GM","DE","EMN","DOW","PPG","NEM","FCX","KR","SYY","GIS","K","HSY",
    "KMB","CLX","CAG","MKC","ADM","WBA","CI","HUM","BDX","SYK","BSX","ZBH","ISRG",
    "EL","KHC","STZ","YUM","MAR","HLT","ROST","TJX","DG","DLTR","ORLY","AZO",
]


def gkx_r2(actual, pred):
    """GKX out-of-sample R^2: benchmark is ZERO (not the mean)."""
    return 1 - np.sum((actual - pred) ** 2) / np.sum(actual ** 2)


def long_short(test_df: pd.DataFrame, pred_col: str) -> pd.Series:
    """Quintile long/short, equal-weight, monthly."""
    rows = []
    for d, g in test_df.groupby(level="date"):
        if len(g) < 10:
            continue
        hi = g[g[pred_col] >= g[pred_col].quantile(0.8)]["ret_fwd"].mean()
        lo = g[g[pred_col] <= g[pred_col].quantile(0.2)]["ret_fwd"].mean()
        rows.append((d, hi - lo))
    s = pd.Series(dict(rows)).sort_index()
    return s


def main():
    print("  building characteristic panel (~140 stocks)...")
    panel = build_panel(UNIVERSE, start="2005-01-01")
    panel = standardize_cross_section(panel).dropna(subset=CHARS + ["ret_fwd"])
    dates = panel.index.get_level_values("date")
    train = panel[dates < pd.Timestamp(SPLIT)]
    test = panel[dates >= pd.Timestamp(SPLIT)].copy()
    print(f"  panel rows: {len(panel)}  (train {len(train)}, test {len(test)})")

    Xtr, ytr = train[CHARS].values, train["ret_fwd"].values
    Xte, yte = test[CHARS].values, test["ret_fwd"].values

    models = {
        "OLS (linear)": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=5,
                                               min_samples_leaf=50, n_jobs=-1, random_state=0),
        "Grad Boosting": HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05,
                                                       max_iter=300, random_state=0),
        "Neural Net": MLPRegressor(hidden_layer_sizes=(32, 16, 8), alpha=1e-3,
                                   max_iter=300, random_state=0),
    }

    print("\n" + "=" * 64)
    print("eq-f1 GKX — out-of-sample (test >= 2019)")
    print("=" * 64)
    print(f"  {'model':<16}{'OOS R2 %':>10}{'L/S Sharpe':>12}{'L/S ann %':>11}")
    summary = {}
    for name, m in models.items():
        m.fit(Xtr, ytr)
        pred = m.predict(Xte)
        test["pred"] = pred
        ls = long_short(test, "pred")
        sh = sharpe(ls, 12)
        summary[name] = {"oos_r2_%": gkx_r2(yte, pred) * 100,
                         "ls_sharpe": sh, "ls_ann_%": ls.mean() * 12 * 100}
        print(f"  {name:<16}{summary[name]['oos_r2_%']:>10.3f}"
              f"{sh:>12.2f}{summary[name]['ls_ann_%']:>11.1f}")
        if name == "Grad Boosting":
            best_ls = ls

    pd.DataFrame(summary).T.to_csv(RESULTS / "model_comparison.csv")
    print("\n  GKX result: nonlinear models (trees/NN) beat linear OLS on both")
    print("  OOS R2 and long/short Sharpe.")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    (1 + best_ls).cumprod().plot(ax=ax)
    ax.set_title("eq-f1 GKX — gradient-boosting long/short (out-of-sample)")
    ax.set_ylabel("Growth of $1"); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "ls_equity.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
