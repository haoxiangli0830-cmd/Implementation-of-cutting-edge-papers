# Replication report — vo-00-har-optiver (HAR-RV)

**Verdict: Replicates cleanly.** The HAR model's three components are all
positive and ordered as the theory predicts, and it beats the naive random-walk
forecast out-of-sample by a clear margin — exactly Corsi's (2009) result.

## Setup
- S&P 500 (^GSPC), 1990 → present, 9,157 daily observations.
- Daily realised volatility proxied by the **Garman-Klass** OHLC estimator.
- Train on first 70%, forecast next-day vol on the last 30% (out-of-sample).

## HAR coefficients (all positive)
| Component | Coefficient |
|---|---|
| Daily RV | +0.135 |
| Weekly RV | +0.481 |
| Monthly RV | +0.306 |
| Intercept | +0.009 |

All three look-backs contribute → volatility has **long memory**: today's, this
week's and this month's vol all help predict tomorrow's. The weekly term
dominating is consistent with the literature.

## Out-of-sample accuracy
| Model | OOS R² | MSE |
|---|---|---|
| **HAR** | **0.505** | 0.00296 |
| Random walk (RV[t+1]=RV[t]) | 0.399 | 0.00358 |

**HAR reduces forecast MSE by 17.5%** versus the random walk. See
`results/har_forecast.png`.

## Why this matters
Volatility (unlike returns) is genuinely *forecastable*, and HAR shows you don't
need a complex long-memory model (fractional integration) to capture it — three
simple averages do most of the job. This is the volatility baseline that the
frontier vol papers in this program (rough vol, deep-learning vol) must beat.

## Limitations / next steps
- Garman-Klass from daily bars is a proxy; **true realised vol uses intraday
  data** — that's where the **Optiver Kaggle** order-book dataset (already on
  disk) comes in as the natural upgrade.
- Add HAR-RV-J (jump component) and a QLIKE loss in addition to MSE.
- Benchmark against GARCH(1,1) (the `arch` library) for a fuller comparison.
