# Report — rk-02: Counterparty exposure & CVA

**Core deliverable of an XVA desk.** Simulates the bank's counterparty exposure on
an interest-rate swap and prices the default risk as a CVA. The exposure shows the
textbook "hump" shape and produces a realistic CVA.

## Setup
- 5-year payer interest-rate swap, notional 1, quarterly, par fixed rate **2.98%**.
- Rates simulated with a **Vasicek** short-rate model (20,000 paths); the swap is
  re-valued analytically on every path and date.
- Counterparty: LGD 60%, CDS 150 bps → hazard 2.5%/yr.

## Results
| Metric | Value |
|---|---|
| Expected Positive Exposure (EPE) | **0.96%** of notional |
| Peak Expected Exposure | 1.31% at t≈1.75y |
| Peak PFE (97.5%) | 6.21% at t≈1.75y |
| **CVA** | **6.1 bps** of notional |

See `results/exposure_profile.png`.

## What the shape tells you (the lesson)
The exposure **rises then falls** — a hump peaking ~1/3 into the swap's life. Two
opposing forces:
- **Diffusion**: as time passes, rates can drift further from the fixed rate, so the
  swap can be more in-the-money → exposure grows.
- **Amortisation**: as payments are made, fewer cashflows remain → exposure shrinks.
They net to a peak in the middle. This hump is *the* canonical IR-swap exposure
profile and is why CVA depends on the whole profile, not just today's value.

## Methods & practices demonstrated
✔ Monte-Carlo exposure simulation · ✔ EE / EPE / PFE profiles · ✔ CVA via
discounted-EE × default-probability · ✔ Vasicek short-rate + analytic bond pricing
(reusable `core/risk/rates.py`).

## Next steps
- Add netting & collateral (CSA) → collateralised exposure and the resulting CVA drop.
- Add DVA/FVA for the full xVA stack.
- Wrong-way risk (correlate the counterparty's default with the exposure).
- This is the analytic baseline the frontier `rk-f2-deep-xva` (neural BSDE) must match.
