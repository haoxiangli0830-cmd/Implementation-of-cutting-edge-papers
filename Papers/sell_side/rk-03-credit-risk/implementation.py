"""rk-03-credit-risk — Structural credit risk + portfolio loss / economic capital.

Two halves of a bank credit-risk desk:
  1. MERTON structural model — treat a firm's equity as a call option on its assets;
     back out the distance-to-default and probability of default (PD) from the
     equity price, equity volatility and debt.
  2. PORTFOLIO model — a Vasicek/Basel single-factor (ASRF) model: many obligors
     share one systematic factor; simulate the loss distribution to get Expected
     Loss, 99.9% Credit VaR, and Economic Capital. Cross-check vs the Basel IRB
     analytic capital formula.

Run:  python implementation.py   ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.data import get_prices                                # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

FIRMS = ["AAPL", "MSFT", "JNJ", "PG", "KO", "JPM", "BAC", "XOM", "CVX", "WMT",
         "DIS", "BA", "F", "GM", "T", "VZ", "CAT", "GE", "INTC", "PFE"]
LGD = 0.45            # Basel foundation-IRB default
N_SCEN = 200_000


def merton_pd(equity, sigma_e, debt, T=1.0, rf=0.0):
    """Simple Merton: V ~ E+D, sigma_V ~ sigma_E*E/(E+D); PD = N(-DtD)."""
    V = equity + debt
    sigma_v = sigma_e * equity / V
    if debt <= 0 or sigma_v <= 0:
        return np.nan, np.nan
    dtd = (np.log(V / debt) + (rf - 0.5 * sigma_v ** 2) * T) / (sigma_v * np.sqrt(T))
    return float(dtd), float(stats.norm.cdf(-dtd))


def basel_corr(pd_):
    """Basel IRB asset correlation for corporate exposures."""
    w = (1 - np.exp(-50 * pd_)) / (1 - np.exp(-50))
    return 0.12 * w + 0.24 * (1 - w)


def irb_capital(pd_, lgd, rho):
    """Basel ASRF analytic capital requirement K (per unit EAD)."""
    cond = (stats.norm.ppf(pd_) + np.sqrt(rho) * stats.norm.ppf(0.999)) / np.sqrt(1 - rho)
    return lgd * (stats.norm.cdf(cond) - pd_)


def main():
    import yfinance as yf
    prices = get_prices(FIRMS, start="2022-01-01")
    rets = prices.pct_change()

    rows = []
    for tk in FIRMS:
        if tk not in prices.columns:
            continue
        sigma_e = rets[tk].dropna().std() * np.sqrt(252)
        try:
            info = yf.Ticker(tk).info
            mcap = info.get("marketCap")
            debt = info.get("totalDebt")
        except Exception:
            mcap = debt = None
        if not mcap or not debt:
            continue
        dtd, pd_ = merton_pd(mcap, sigma_e, debt)
        if np.isnan(pd_):
            continue
        rows.append({"firm": tk, "equity_vol": sigma_e, "leverage": debt / (mcap + debt),
                     "DtD": dtd, "PD_%": pd_ * 100})
    df = pd.DataFrame(rows).set_index("firm")
    df = df[df["PD_%"] < 50].sort_values("PD_%")          # drop nonsense
    df.to_csv(RESULTS / "merton_pd.csv")

    # --- portfolio loss (equal EAD = 1 per name) ------------------------------
    pds = df["PD_%"].values / 100
    rho = np.array([basel_corr(p) for p in pds])
    thresh = stats.norm.ppf(pds)
    rng = np.random.default_rng(0)
    Z = rng.standard_normal(N_SCEN)                       # one systematic factor
    losses = np.zeros(N_SCEN)
    for i, (p, r, c) in enumerate(zip(pds, rho, thresh)):
        a = np.sqrt(r) * Z + np.sqrt(1 - r) * rng.standard_normal(N_SCEN)
        losses += (a < c) * LGD                           # EAD=1, LGD loss on default
    n = len(pds)
    el = losses.mean()
    cvar = np.percentile(losses, 99.9)
    ec = cvar - el
    irb = sum(irb_capital(p, LGD, r) for p, r in zip(pds, rho))

    print("\n" + "=" * 62)
    print("rk-03 — Credit risk: Merton PDs + portfolio economic capital")
    print("=" * 62)
    print(f"\nMerton structural PDs ({n} firms):")
    print(df.round(2).to_string())
    print(f"\nPortfolio ({n} equal exposures, LGD {LGD}):")
    print(f"  Expected Loss (EL)      : {el/n*100:.2f}% of portfolio")
    print(f"  99.9% Credit VaR        : {cvar/n*100:.2f}%")
    print(f"  Economic Capital (UL)   : {ec/n*100:.2f}%")
    print(f"  Basel IRB analytic cap  : {irb/n*100:.2f}%  (cross-check vs EC)")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(losses / n * 100, bins=80, color="C3", alpha=0.7, density=True)
    ax.axvline(el / n * 100, color="k", ls="-", lw=1.5, label=f"EL {el/n*100:.2f}%")
    ax.axvline(cvar / n * 100, color="C0", ls="--", lw=1.5, label=f"99.9% VaR {cvar/n*100:.2f}%")
    ax.set_xlabel("portfolio loss (% of exposure)"); ax.set_ylabel("density")
    ax.set_title("rk-03 — credit portfolio loss distribution (skewed tail)")
    ax.legend(); ax.set_xlim(0, np.percentile(losses / n * 100, 99.99))
    fig.tight_layout(); fig.savefig(RESULTS / "loss_distribution.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
