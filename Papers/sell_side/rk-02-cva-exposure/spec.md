# spec — rk-02-cva-exposure

**Domain:** Counterparty credit risk / XVA desk (sell-side risk quant).
**References:** Gregory, *The xVA Challenge*; Basel CCR / SA-CVA framework.

## What an XVA desk does
When a bank trades a derivative with a client, it bears the risk that the client
defaults while the trade is in the bank's favour. The desk simulates that
**exposure**, summarises it (EE, EPE, PFE), and charges its expected cost as a
**CVA** (Credit Valuation Adjustment) — an adjustment to the trade's price.

## What we implement
- Vasicek short-rate simulation; analytic re-valuation of a 5y payer swap on every
  path & date.
- **EE** (expected exposure), **EPE** (its time-average), **PFE** (97.5% quantile).
- **CVA** = LGD × Σ discounted-EE × marginal default probability (from a CDS-implied
  hazard rate).

## Data
- None — fully simulated. Uses `core.risk.rates` (Vasicek paths + ZCB pricing).

## Benchmark to reproduce
- Hump-shaped exposure profile peaking ~1/3 into the swap's life.
- CVA on the order of a few bps for a 5y swap at 150 bps CDS.

## Next layers
Collateral/netting (CSA), DVA/FVA, wrong-way risk; neural-network XVA (`rk-f2`).
