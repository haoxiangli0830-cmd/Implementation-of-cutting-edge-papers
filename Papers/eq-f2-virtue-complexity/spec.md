# spec — eq-f2-virtue-complexity

**Paper:** Kelly, Malamud & Zhou (2024), "The Virtue of Complexity in Return
Prediction," *Journal of Finance*. arXiv:2211.13534.

## Claim
For return prediction, model complexity is *virtuous*: out-of-sample performance
(timing R² and Sharpe) keeps improving as the number of parameters P grows, even
far beyond the number of training observations T (P ≫ T), where classical theory
says you must overfit. Mechanism: many random nonlinear features + ridge shrinkage
produce a benign "double descent."

## What we implement
- Predict next-month market excess return (Mkt-RF) from the 13 JKP theme factors.
- Expand predictors into P random Fourier features; ridge-regress in dual form
  (efficient for P ≫ T); 120-month rolling window.
- Trace out-of-sample timing Sharpe and R² as complexity c = P/T grows 0.02 → 10.7.

## Data
- JKP Factor Returns (USA, monthly, capped VW) — user-downloaded CSV in this folder.
- Ken French Mkt-RF via `core.data.factors.get_french_factors`.

## Benchmark to reproduce
OOS performance does not collapse for P > T; ideally improves with complexity
(double descent), with the worst point near c ≈ 1.

## Known limits
- 13 factor predictors vs the paper's Goyal-Welch set; untuned bandwidth/shrinkage.
- Most contested paper in the program — expect a nuanced, partial result.
