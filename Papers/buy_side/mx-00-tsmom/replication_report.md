# Replication report — mx-00-tsmom (Time-Series Momentum)

**Verdict: Partially replicates. The effect is real and survives our
multiple-testing check, but it is materially weaker than the 2012 paper —
consistent with well-documented post-publication decay and our simplified
ETF universe.**

## Results (2007 → present, 11-ETF basket, monthly, 10 bps costs)
| Metric | Gross | Net |
|---|---|---|
| CAGR | 10.6% | 9.6% |
| Annualised vol | 20.4% | 20.3% |
| **Sharpe** | **0.60** | **0.55** |
| Sortino | 0.59 | 0.55 |
| Max drawdown | −45% | −46% |
| Skew | −0.30 | −0.30 |
| Prob. Sharpe > 0 | 0.99 | 0.99 |

Cumulative growth of $1 → ~$6 (net) over ~19 years. See `results/equity_curve.png`.

## Overfitting / honesty checks
- **Look-back sweep** (net Sharpe): 3m 0.49 · 6m 0.49 · 9m 0.49 · 12m 0.55 · 15m 0.40.
  Stable across look-backs → the signal is not a single lucky parameter.
- **Deflated Sharpe Ratio** (penalising the 5 variants tried): **0.98 → passes**
  the >0.95 bar. The Sharpe is statistically distinguishable from the best you'd
  expect by chance after that many trials.
- **Costs**: trivial at 10 bps (Sharpe 0.60 → 0.55) because turnover is low
  (monthly, vol-scaled). Robust to realistic costs.

## How it differs from the paper, and why our Sharpe is lower
1. **Universe**: 11 ETFs vs ~58 futures → far less diversification (the paper's
   Sharpe is largely a diversification effect across many low-correlated bets).
2. **Instruments**: ETFs miss futures roll yield and use a later start (2007),
   which is mostly *out-of-sample* relative to the 2012 publication.
3. **Decay**: the flat 2015–2019 stretch in the equity curve is the
   widely-reported weakening of trend-following post-2012.

## What held up
- The **direction and crisis behaviour** replicate cleanly: the strategy made
  money in 2008 (going short risk) — the paper's headline "crisis alpha".
- A positive, cost-robust, parameter-stable premium remains.

## Next steps to strengthen
- Broaden the universe (more ETFs / actual futures via a data vendor).
- Add an explicit out-of-sample split at the 2012 publication date and report
  pre/post Sharpe separately.
- Compare against a buy-and-hold 60/40 to quantify the diversification benefit.
