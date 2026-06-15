# theory (light) — Deep Hedging

Deep dives → 74-week curriculum (stochastic-calculus weeks: Black-Scholes, Greeks).

## The classical idea it replaces
Black-Scholes says: to hedge an option, hold **delta** shares, where delta = the
option's sensitivity to the stock. Re-compute and rebalance continuously and your
risk vanishes. This assumes trading is **free**.

## What breaks with costs
If every trade costs money, rebalancing to the exact delta every day burns the
premium. The optimal strategy is no longer "match delta" — it's "stay *close
enough* to delta while trading as little as possible." There's no clean formula
for that.

## The deep-hedging move
Stop looking for a formula. Instead:
1. Let a neural network output the hedge position at each step.
2. Simulate thousands of price paths.
3. Score the strategy by a **risk measure** of the final profit/loss — here the
   *entropic risk*, which heavily penalises large losses.
4. Use gradient descent to adjust the network until that risk is minimised.

The network discovers the cost-aware hedge on its own. Change the cost, the risk
measure, or the dynamics, and you just retrain — no new math.

## The one subtlety in reading the results
The network minimises **tail risk**, not variance. So it can have slightly higher
standard deviation yet a much better worst-case (CVaR) and mean — that's a
feature, not a bug. Always judge a hedge by the risk measure you actually care
about.
