# Report — rk-03: Credit risk (Merton + portfolio economic capital)

**Two bank credit-risk tools, and a real lesson about the Basel formula's limits.**
The Merton model ranks firms by default risk sensibly; the portfolio model exposes
**concentration risk** that the granular Basel IRB formula misses.

## 1. Merton structural PDs (20 large-caps, 1-year)
Distance-to-default (DtD) and PD backed out from equity value, equity vol and debt.

| Risk ranking | DtD | 1y PD |
|---|---|---|
| Safest: JNJ, KO, AAPL, PG | ~14–15 | ~0% |
| Mid: banks (JPM/BAC), BA, INTC | ~4.5–5 | ~0% |
| Riskiest: **GM** (DtD 3.3), **Ford** (DtD 2.9) | 2.9–3.3 | 0.04% / 0.19% |

The ordering is economically right: low-leverage, low-vol staples are far from
default; high-leverage, high-vol automakers are closest. All are investment-grade,
so 1-year PDs are tiny — as they should be.

## 2. Portfolio loss & economic capital (20 equal exposures, LGD 45%)
| Metric | Value |
|---|---|
| Expected Loss (EL) | 0.01% |
| 99.9% Credit VaR | **2.25%** |
| Economic Capital (Credit VaR − EL) | **2.24%** |
| Basel IRB analytic capital | **0.16%** |

See `results/loss_distribution.png` — note the heavily skewed tail.

## The lesson — concentration vs the Basel granularity assumption
The Monte-Carlo economic capital (2.24%) is **14× the Basel IRB analytic figure
(0.16%)**. That is *not* an error:
- The **Basel IRB (ASRF) formula assumes an infinitely granular portfolio** — many
  tiny exposures, so idiosyncratic risk diversifies away and only systematic risk
  remains.
- Our portfolio has **only 20 names**, so it is *lumpy*. At the 99.9% level the
  loss is "exactly one name defaults" = LGD × 1/20 = **2.25%**. That single-name
  jump dwarfs the smooth analytic capital.
- The difference **is concentration risk** — precisely what regulators address with
  Pillar-2 granularity/name-concentration add-ons. As the number of names grows,
  the MC capital converges down toward the IRB figure.

This is a standout teaching point: the headline regulatory formula is an asymptotic
approximation, and small/concentrated books need more capital than it implies.

## Methods & practices demonstrated
✔ Merton distance-to-default & PD · ✔ Basel IRB asset-correlation & ASRF capital ·
✔ single-factor Monte-Carlo loss distribution · ✔ Credit VaR & economic capital ·
✔ concentration vs granularity insight.

## Next steps / caveats
- Merton uses the simple V≈E+D approximation; a full KMV iteration solves for asset
  value/vol jointly.
- Add a granularity adjustment and vary N to show MC → IRB convergence.
- IFRS 9 expected-credit-loss (PD×LGD×EAD term structure) as a follow-on.
