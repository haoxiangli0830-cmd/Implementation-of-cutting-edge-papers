# AI_LOG — rk-02-cva-exposure

## 2026-06-15 — Risk track (Claude)
- Added shared `core/risk/rates.py` (Vasicek paths + analytic ZCB). Reused by rk-f2.
- Built CVA/exposure on a 5y payer IR swap: 20k Vasicek paths, analytic swap
  re-valuation, EE/EPE/PFE profiles, CVA via discounted-EE × hazard default prob.
- BUG: first run gave 0 exposure — `vasicek_zcb` used `np.outer` which mangled
  array shapes in the per-date loop. Fixed to clean elementwise broadcasting.
- Result: EPE 0.96%, peak EE 1.31% @1.75y, PFE 6.2%, CVA 6.1 bps — textbook hump.
- Next: collateral/CSA, DVA/FVA, wrong-way risk; rk-f2 neural XVA matches this.
