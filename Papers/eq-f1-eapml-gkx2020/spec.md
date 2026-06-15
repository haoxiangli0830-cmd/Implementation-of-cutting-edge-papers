# spec — eq-f1-eapml-gkx2020

**Paper:** Gu, Kelly & Xiu (2020), "Empirical Asset Pricing via Machine Learning,"
*Review of Financial Studies* 33(5).

## Claim
Machine-learning models predict the cross-section of stock returns substantially
better than linear regression, because the mapping from firm characteristics to
expected returns is nonlinear with interactions. Trees and neural networks deliver
the highest out-of-sample R² and the most profitable long/short portfolios. The
most important predictors are price-trend (momentum/reversal) and liquidity
characteristics.

## What we implement
- A firm-level panel: stock × month × characteristics (price/volume features).
- Rank-normalise characteristics cross-sectionally each month.
- Train OLS / Random Forest / Gradient Boosting / Neural Net; predict next-month
  return; compare OOS R² (vs a zero benchmark, GKX style) and a quintile L/S Sharpe.

## Data
- yfinance OHLCV for ~140 US large-caps (free), via `core.data.panel.build_panel`.
- NO WRDS. Fundamentals (EDGAR) are a documented upgrade.

## Benchmark to reproduce
Nonlinear models beat OLS on OOS R² and L/S Sharpe; price-trend chars matter most.

## Known limits
- Small, survivorship-biased universe; price/volume features only; gross L/S.
- Magnitudes not comparable to the paper's full-CRSP, 94-characteristic study.
