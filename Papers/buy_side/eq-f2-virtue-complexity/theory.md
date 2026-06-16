# theory (light) — The Virtue of Complexity

Deep dives → 74-week curriculum (ML-for-risk: ridge regression, double descent).

## The orthodoxy it challenges
Every stats course says: if your model has more parameters (P) than data points
(T), it memorises noise and fails out-of-sample. So use *few*, carefully chosen
predictors. This paper says: for return prediction, do the opposite — use a
*huge* number of features.

## How it can possibly work
Two ingredients:
1. **Random features.** Take your handful of predictors and generate thousands of
   random nonlinear combinations of them (here, random cosine "Fourier features").
   This is a cheap way to let the model represent very flexible functions.
2. **Ridge shrinkage.** Don't fit those thousands of weights freely — *shrink* them
   toward zero. Shrinkage stops the explosion that classical overfitting fears.

## Double descent — the picture to remember
Plot out-of-sample error against model size:
- It first **worsens** as P approaches T (the classical overfitting zone, peak at
  c = P/T = 1),
- then **improves again** as P grows past T.

The high-complexity model lives on the *good* side of that second descent. Our run
shows exactly this: R² is worst at c≈1, then recovers as P reaches 10×T.

## Why read the result carefully
"Complexity helps" is statistically real here but **economically contested** — the
size of the trading profit it produces is debated. So the honest scientist reports
the *shape* (the recovery happened) separately from the *magnitude* (our timing
Sharpe was only modest). Distinguishing "the effect exists" from "the effect is
big enough to trade" is the whole skill.
