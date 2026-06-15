# AI_LOG — eq-f2-virtue-complexity

## 2026-06-15 — Wave 2 build (Claude)
- User downloaded JKP Factor Returns (USA monthly capped-VW) = 13 theme factors,
  1926-2025. Used as predictors of the next-month market (Ken French Mkt-RF).
- Implemented random Fourier features + ridge in DUAL form (T x T) so P >> T is cheap.
- BUG (first run): forgot the 1/sqrt(P) feature normalisation -> effective shrinkage
  changed with P, confounding the complexity comparison; also used sign() timing.
  Fixed: sqrt(2/P) features + magnitude (conditional-mean) timing weight.
- After fix: OOS R² shows the double-descent recovery (worst at c~1, improves to
  c~10) = the VoC signature. Timing Sharpe only ~0.1 at high complexity (modest).
- Also fixed a glob bug (was re-reading results/complexity_curve.csv).
- Honest verdict: mechanism replicates, economic magnitude weak — fitting for the
  most contested paper in the set.
- Next: swap in Goyal-Welch predictors; tune bandwidth + ridge z.
