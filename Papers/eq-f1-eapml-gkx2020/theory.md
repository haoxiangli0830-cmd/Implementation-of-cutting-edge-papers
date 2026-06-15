# theory (light) — Empirical Asset Pricing via ML

Deep dives → 74-week curriculum (ML-for-risk weeks: trees, neural nets, regularisation).

## The question
Given a stock's **characteristics** today (its momentum, volatility, size,
liquidity…), what return do we expect next month? Classic finance answers with a
*linear* model (return = sum of characteristic × coefficient). GKX ask: what if
the truth is nonlinear — e.g. momentum only matters for liquid stocks, or two
characteristics interact?

## The setup (a "horse race")
1. Build a big table: one row per stock per month, columns = characteristics, plus
   next month's return as the target.
2. **Normalise characteristics each month** by rank — so "high momentum" means
   high *relative to other stocks that month*, comparable across time.
3. Train several models on the past, predict the future (out-of-sample):
   - **OLS** — the linear baseline.
   - **Random forest / gradient boosting** — trees that capture nonlinearity and
     interactions automatically.
   - **Neural net** — flexible nonlinear function approximator.
4. Score them two ways: statistical (out-of-sample R²) and economic (the Sharpe of
   a portfolio that buys the top predicted and shorts the bottom).

## Two subtleties worth internalising
- **R² here uses a *zero* benchmark, not the mean** (GKX convention): R²ₒₛ =
  1 − Σ(r−r̂)²/Σr². Predicting expected returns is so hard that beating "just say
  zero" by a fraction of a percent is meaningful.
- **Good ranking ≠ good level prediction.** Our neural net had negative R² (bad at
  the *number*) but the best long/short Sharpe (great at the *order*). For
  investing, getting the order right is what pays.
