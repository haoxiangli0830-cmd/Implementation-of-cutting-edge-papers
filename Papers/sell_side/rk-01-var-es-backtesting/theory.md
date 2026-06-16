# theory (light) — VaR, ES & Basel backtesting

Deep dives → 74-week QMRM curriculum (risk-core weeks: VaR/ES, backtesting, EVT).

## The two risk numbers
- **Value-at-Risk (VaR)** at 99%: "On 99 days out of 100, we won't lose more than
  this." It's a *threshold* — a quantile of the loss distribution.
- **Expected Shortfall (ES)** at 97.5%: "*If* we breach, how bad is the average loss
  beyond the threshold?" It's the *tail average*. FRTB replaced VaR with ES because
  VaR says nothing about how bad the bad days are.

## Three ways to estimate them
1. **Historical** — just look at the empirical distribution of past returns. Captures
   real fat tails, but assumes the past repeats.
2. **Parametric** — assume returns are normal; VaR = μ + z·σ. Fast, but the normal
   has thin tails → **understates risk** (we saw 1.42% vs 2.06%).
3. **Monte-Carlo** — simulate many returns from a model; flexible but model-dependent.

## Backtesting — proving the model to the regulator
Each day, compare the realised loss to yesterday's VaR. A breach = "exception."
- **Kupiec POF**: are there the *right number* of breaches? (≈1% of days for 99% VaR.)
- **Christoffersen**: are breaches *independent*, or do they **cluster**? Clustering
  means the model is slow to react to rising volatility.
- **Basel traffic light**: 0–4 breaches in 250 days = green; 5–9 = yellow (more
  capital); 10+ = red (model rejected).

## The lesson this project hammers home
A model can pass the count test and still be **bad**: our VaR had ~the right number
of breaches but they clustered in 2008 and 2020 (Christoffersen p≈0). Risk lives in
the *timing* of losses, not just their average frequency — which is why volatility
scaling, ES, and the ML methods later in this track exist.
