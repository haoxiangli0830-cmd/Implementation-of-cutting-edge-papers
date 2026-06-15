# spec — mx-00-tsmom

**Paper:** Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum," *Journal of Financial Economics* 104(2).

## Claim
An instrument's own past 12-month return positively predicts its next-month
return, across ~58 futures/forwards spanning equities, bonds, commodities and
FX. A diversified, volatility-scaled long/short portfolio of these signals earns
a high Sharpe (paper reports ~1.2+ gross) with low correlation to traditional
asset classes and *positive* performance in market crises ("crisis alpha").

## Strategy spec (what we implement)
| Element | Paper | This implementation |
|---|---|---|
| Universe | ~58 futures (eq/bond/commodity/FX) | 11 liquid ETF futures-proxies, 2007→present |
| Signal | sign(past 12m excess return) | sign(past 12m total return) |
| Sizing | scale each to ~40% ann. vol (ex-ante) | same; rolling-12m vol, leverage capped ×5 |
| Rebalance | monthly | monthly |
| Aggregation | diversified average | equal-weight average across basket |
| Costs | modeled | 10 bps round-trip on turnover |
| Lag | t-signal → t+1 hold | signal shifted 1 month (no look-ahead) |

## Benchmark to reproduce
Positive, ~0.8–1.2 gross Sharpe; strong 2008; diversifying vs equities.

## Known critiques (triage)
- Much of the premium has **decayed since publication** (esp. 2015–2019).
- ETF proxies ≠ the paper's futures (no roll yield, narrower universe) → expect a
  lower Sharpe than the paper.
- Results sensitive to the volatility-scaling choice.
