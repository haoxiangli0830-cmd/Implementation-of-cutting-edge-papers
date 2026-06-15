# Replication report — eq-f2-virtue-complexity

**Verdict: Mechanism replicates qualitatively; economic magnitude is modest.**
The tell-tale "double descent" appears — out-of-sample R² is *worst* when the
number of parameters ≈ the number of observations (c≈1) and then **recovers as
complexity grows past that point** (P ≫ T). That recovery is exactly Kelly,
Malamud & Zhou's (2024) point: adding parameters beyond T does not destroy
out-of-sample performance. The market-timing Sharpe gain, however, is small in our
simplified setup — fair, given this is a genuinely contested result.

## Setup
- Target: next-month market excess return (Ken French Mkt-RF), 1963–2025 (749 mo).
- Predictors: the 13 JKP theme factors (you downloaded), monthly, capped VW.
- Each month's 13 predictors expanded into **P random Fourier features**
  (P from 2 to 1280), ridge-regressed (dual form, so P ≫ T is cheap), 120-month
  rolling window. Timing weight = the conditional-mean forecast.

## Results — performance vs complexity c = P/T
| P | c | Timing Sharpe | OOS R² |
|---|---|---|---|
| 12 | 0.10 | −0.29 | −12.0% |
| 80 | 0.67 | 0.05 | −17.6% |
| 160 | **1.33** | −0.33 | **−18.8%** ← worst at c≈1 |
| 320 | 2.67 | 0.11 | −6.2% |
| 640 | 5.33 | 0.11 | −4.0% |
| 1280 | **10.67** | 0.09 | **−3.2%** ← recovered |

See `results/complexity_curve.png`.

## What replicates (the important part)
- **Double descent / no overfitting collapse.** Classical statistics predicts
  that once P ≥ T you overfit and out-of-sample performance falls apart. Instead,
  OOS R² is worst right around c=1 and then **improves steadily** as P climbs to
  10× T. The high-complexity model is the *best* out-of-sample, not the worst.
  This is the paper's central, counter-intuitive claim, and it shows.

## What's weak / not fully replicated
- **Economic magnitude.** The timing Sharpe only stabilises around +0.1 at high
  complexity — positive, but modest. KMZ report larger gains. Likely because we
  use 13 factor predictors → time the single market, vs their richer predictor set
  and construction; and our shrinkage/bandwidth are untuned.
- All OOS R² values are negative vs a *zero* benchmark — return prediction is hard;
  what matters here is the *shape* (recovery), not the level.

## Honest takeaway
This is the most *contested* paper in the program, and our result is appropriately
nuanced: the surprising statistical phenomenon (complexity helps OOS) is real and
visible; whether it delivers large tradable gains is where the academic debate
lives, and our modest Sharpe sits on the skeptical side of that debate.

## Next steps
- Use the 15 Goyal-Welch predictors (the paper's actual inputs) instead of JKP factors.
- Tune the random-feature bandwidth and ridge z; trace Sharpe for several z levels.
- Add the paper's "expected return × volatility" timing normalisation.
