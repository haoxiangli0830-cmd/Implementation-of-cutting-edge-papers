# theory (light) — Time-Series Momentum

Only the math needed to implement. Deep dives → 74-week curriculum
(`Career/Quantitative_Finance/Curriculum/`): time-series / stochastic-process weeks.

## The one equation
For instrument *i*, position next month is the **sign of the trailing return**,
scaled by inverse volatility to a target:

    w[i,t] = sign( r[i, t-12 : t] ) · ( σ_target / σ̂[i,t] )

- `sign(...)` makes it long winners / short losers on each instrument *on its own*
  (this is *time-series*, not cross-sectional, momentum — each asset vs its own past).
- `σ̂[i,t]` is the **ex-ante** volatility (rolling 12-month, annualised). Dividing
  by it equalises risk so a quiet bond and a wild commodity contribute equally.
- `σ_target` (40%) sets each instrument's risk before diversifying.

## Why it works (intuition, not proof)
Under-reaction to news and herding create multi-month trends; vol-scaling +
diversification across many low-correlated trends is what produces the high
Sharpe — not any single market.

## The two things that keep it honest
- **Lag**: the signal at month-end *t* is held over *t+1*. Forgetting this lag is
  the classic look-ahead bug; our `core.backtest` engine does **not** shift for
  you, so the strategy shifts the weights itself.
- **Ex-ante vol**: σ̂ must use only past data (rolling), never full-sample.
