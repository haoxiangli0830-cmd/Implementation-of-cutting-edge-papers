# AI_LOG — rk-03-credit-risk

## 2026-06-15 — Risk track (Claude)
- Merton DtD/PD for 20 firms (equity vol from prices; mcap + totalDebt from
  yfinance.info). Simple Merton V≈E+D, sigma_V≈sigma_E*E/V.
- Portfolio: Basel single-factor (ASRF) MC loss distribution + IRB analytic capital
  cross-check; Basel asset-correlation formula.
- Result: PDs rank firms sensibly (autos riskiest, staples safest); all IG so 1y PD
  tiny. MC economic capital 2.24% vs IRB 0.16% — NOT a bug: 20 names is not granular,
  so a single default (LGD/20=2.25%) sets the 99.9% tail. The gap = concentration
  risk (Pillar-2 granularity). Strong teaching point.
- Next: granularity adjustment + vary N to show MC->IRB convergence; IFRS9 ECL.
