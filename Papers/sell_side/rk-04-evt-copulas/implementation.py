"""rk-04-evt-copulas — Tail risk: Extreme Value Theory + copulas.

Two tools for the part of the loss distribution that matters most — the extreme
tail, where normal-based risk models fail:

  1. EVT (Peaks-Over-Threshold): fit a Generalised Pareto Distribution to the tail of
     losses and read VaR/ES at extreme quantiles (99.9%). Compare to normal & empirical.
  2. COPULAS: model the *dependence* between assets. A Gaussian copula has no tail
     dependence (assets crash together only by chance); a Student-t copula does.
     We show the t-copula implies materially higher portfolio tail risk.

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

BOOK = ["SPY", "EFA", "EEM", "TLT", "GLD"]
THRESHOLD_Q = 0.95          # POT threshold
T_DOF = 4                   # Student-t copula degrees of freedom


# --- EVT (Peaks-Over-Threshold) ----------------------------------------------
def pot_var_es(losses, alpha, threshold_q=THRESHOLD_Q):
    u = np.quantile(losses, threshold_q)
    exc = losses[losses > u] - u
    n, nu = len(losses), len(exc)
    xi, _, beta = stats.genpareto.fit(exc, floc=0)           # shape, loc=0, scale
    var = u + (beta / xi) * (((n / nu) * (1 - alpha)) ** (-xi) - 1)
    es = (var + beta - xi * u) / (1 - xi)
    return var, es, xi


# --- copulas ------------------------------------------------------------------
def normal_scores(R):
    ranks = pd.DataFrame(R).rank().values / (len(R) + 1)
    return stats.norm.ppf(ranks)


def simulate_copula(R, corr, kind, n, seed=0):
    """Simulate returns from a Gaussian or Student-t copula with empirical margins."""
    rng = np.random.default_rng(seed)
    d = R.shape[1]
    L = np.linalg.cholesky(corr)
    Z = rng.standard_normal((n, d)) @ L.T
    if kind == "t":
        w = rng.chisquare(T_DOF, n) / T_DOF
        Tv = Z / np.sqrt(w)[:, None]
        U = stats.t.cdf(Tv, T_DOF)
    else:
        U = stats.norm.cdf(Z)
    # map uniforms back through each asset's empirical quantile function
    out = np.empty_like(U)
    for j in range(d):
        out[:, j] = np.quantile(R[:, j], U[:, j])
    return out


def main():
    prices = get_prices(BOOK, start="2007-01-01")
    R = prices.pct_change().dropna().values
    port = R.mean(axis=1)                     # equal-weight book
    losses = -port                            # positive = loss

    # --- EVT vs normal vs empirical -------------------------------------------
    print("\n" + "=" * 60)
    print("rk-04 — Tail risk (EVT + copulas)")
    print("=" * 60)
    mu, sd = port.mean(), port.std()
    print("\n[EVT]  1-day VaR / ES of the equal-weight book:")
    print(f"  {'level':<8}{'Normal':>10}{'Empirical':>12}{'EVT (GPD)':>12}")
    for a in (0.99, 0.999):
        v_n = -(mu + stats.norm.ppf(1 - a) * sd)
        v_e = np.quantile(losses, a)
        v_evt, es_evt, xi = pot_var_es(losses, a)
        print(f"  {a:<8.3f}{v_n*100:>9.2f}%{v_e*100:>11.2f}%{v_evt*100:>11.2f}%")
    print(f"  GPD tail index xi = {xi:.2f}  "
          + ("(heavy tail — fatter than normal)" if xi > 0 else "(thin tail)"))

    # --- copula comparison -----------------------------------------------------
    Zs = normal_scores(R)
    corr = np.corrcoef(Zs.T)
    print("\n[Copulas]  99% VaR of the book under different dependence:")
    res = {}
    for kind in ("gaussian", "t"):
        sim = simulate_copula(R, corr, kind, n=200_000, seed=1)
        sim_port = sim.mean(axis=1)
        res[kind] = np.quantile(-sim_port, 0.99)
        print(f"  {kind:<10} copula: {res[kind]*100:.2f}%")
    bump = (res["t"] / res["gaussian"] - 1) * 100
    print(f"  -> Student-t copula VaR is {bump:+.0f}% vs Gaussian "
          "(tail dependence = assets crash together).")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    # left: tail fit
    u = np.quantile(losses, THRESHOLD_Q)
    exc = np.sort(losses[losses > u])
    xi, _, beta = stats.genpareto.fit(exc - u, floc=0)
    ax[0].plot(exc * 100, np.linspace(0, 1, len(exc)), ".", ms=3, label="empirical tail")
    ax[0].plot(exc * 100, stats.genpareto.cdf(exc - u, xi, 0, beta), lw=1.5, label="GPD fit")
    ax[0].set_title("EVT: GPD fit to loss tail"); ax[0].set_xlabel("loss %"); ax[0].legend()
    ax[0].grid(True, alpha=0.3)
    # right: copula scatter (SPY vs EEM simulated, t vs gaussian)
    g = simulate_copula(R, corr, "gaussian", 4000, 2)
    t = simulate_copula(R, corr, "t", 4000, 2)
    ax[1].scatter(g[:, 0] * 100, g[:, 2] * 100, s=3, alpha=0.3, label="Gaussian")
    ax[1].scatter(t[:, 0] * 100, t[:, 2] * 100, s=3, alpha=0.3, label="Student-t")
    ax[1].set_title("Copula dependence (SPY vs EEM)"); ax[1].set_xlabel("SPY %")
    ax[1].set_ylabel("EEM %"); ax[1].legend(); ax[1].grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "tail_risk.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
