"""rk-02-cva-exposure — Counterparty credit exposure & CVA (XVA desk).

When a bank trades a swap with a client, it is exposed to the client defaulting
while the swap is in the bank's favour. This script computes that exposure and
prices it as a Credit Valuation Adjustment (CVA) — core work of an XVA desk.

Steps:
  1. Simulate interest rates (Vasicek) -> value a 5y payer swap on every path/date
  2. Exposure = max(swap value, 0); compute EE, EPE, and PFE (97.5%) profiles
  3. CVA = LGD * integral of discounted EE against the counterparty default prob

No external data — fully simulated.

Run:  python implementation.py   ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from core.risk.rates import vasicek_paths, vasicek_zcb       # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# swap & model parameters
NOTIONAL = 1.0
MATURITY = 5.0
FREQ = 4                       # quarterly
TAU = 1 / FREQ
N_PAY = int(MATURITY * FREQ)
A, B, SIGMA, R0 = 0.10, 0.03, 0.01, 0.03      # Vasicek
N_PATHS = 20_000
# counterparty credit
LGD = 0.6
CDS_SPREAD = 0.015            # 150 bps
HAZARD = CDS_SPREAD / LGD


def main():
    grid = np.linspace(0, MATURITY, N_PAY + 1)          # 0, .25, ..., 5
    rates = vasicek_paths(R0, A, B, SIGMA, MATURITY, N_PAY, N_PATHS, seed=0)

    # par fixed rate so the swap is worth ~0 at inception
    zcb0 = np.array([vasicek_zcb(R0, A, B, SIGMA, t) for t in grid[1:]])
    K = (1 - zcb0[-1]) / (TAU * zcb0.sum())

    # value the (payer) swap at each exposure date on each path
    ee, pfe, times = [], [], []
    disc_ee = 0.0
    for i in range(1, N_PAY):                # exposure dates (skip 0 and final)
        t = grid[i]
        r_t = rates[:, i]
        remaining = grid[i + 1:]             # future payment times
        P = np.array([vasicek_zcb(r_t, A, B, SIGMA, T - t) for T in remaining]).T  # (paths, n_remaining)
        float_leg = 1 - P[:, -1]
        fixed_leg = K * TAU * P.sum(axis=1)
        value = NOTIONAL * (float_leg - fixed_leg)
        exp = np.maximum(value, 0.0)
        ee.append(exp.mean())
        pfe.append(np.percentile(exp, 97.5))
        times.append(t)
        # CVA increment: discounted EE * marginal default prob over (t_{i-1}, t_i]
        df = vasicek_zcb(R0, A, B, SIGMA, t)
        dPD = np.exp(-HAZARD * grid[i - 1]) - np.exp(-HAZARD * t)
        disc_ee += df * exp.mean() * dPD

    ee, pfe, times = np.array(ee), np.array(pfe), np.array(times)
    epe = ee.mean()
    cva = LGD * disc_ee

    print("\n" + "=" * 60)
    print("rk-02 — Counterparty exposure & CVA (5y payer IR swap)")
    print("=" * 60)
    print(f"  par fixed rate         : {K*100:.2f}%")
    print(f"  Expected Pos. Exposure : {epe*100:.3f}% of notional")
    print(f"  peak EE                : {ee.max()*100:.3f}%  at t={times[ee.argmax()]:.2f}y")
    print(f"  peak PFE (97.5%)       : {pfe.max()*100:.3f}%  at t={times[pfe.argmax()]:.2f}y")
    print(f"  CVA                    : {cva*1e4:.1f} bps of notional")
    print(f"  (LGD {LGD}, CDS {CDS_SPREAD*1e4:.0f}bps -> hazard {HAZARD*100:.2f}%/yr)")

    np.savez(RESULTS / "exposure.npz", times=times, ee=ee, pfe=pfe, cva=cva)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(times, ee * 100, "o-", label="Expected Exposure (EE)")
    ax.plot(times, pfe * 100, "s--", label="PFE (97.5%)")
    ax.fill_between(times, 0, ee * 100, alpha=0.15)
    ax.set_xlabel("years"); ax.set_ylabel("% of notional")
    ax.set_title(f"rk-02 — swap exposure profile (CVA = {cva*1e4:.1f} bps)")
    ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "exposure_profile.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
