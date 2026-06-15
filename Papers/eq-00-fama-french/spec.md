# spec — eq-00-fama-french

**Papers:** Fama & French (1993) "Common Risk Factors…" *JFE* 33; Fama & French
(2015) "A Five-Factor Asset Pricing Model" *JFE* 116; Carhart (1997) momentum.
Companion (rigor): Choi & Zhao (2020), Carhart performance persistence OOS.

## Claim
The cross-section of stock returns is explained by exposure to a small set of
long/short factor portfolios: market (Mkt-RF), size (SMB), value (HML),
profitability (RMW), investment (CMA), and momentum (WML/Carhart). Each earns a
positive long-run premium.

## What we implement
1. **Replicate the premia** straight from the official Ken French monthly data
   (1963→present): annualised premium, t-stat, full-sample Sharpe, and Sharpe
   *since 2010* to expose factor decay.
2. **Construct momentum from scratch**: 12-1 cross-sectional rank long/short on a
   free 40-stock universe, then validate by correlating with French's WML.

## Data
- Ken French Data Library (free) via `core.data.factors.get_french_factors`.
- yfinance prices for the construction universe.

## Benchmark to reproduce
Positive premia with t-stats ≳ 2; momentum & market the strongest; visible
weakening of value/size in the last ~15 years.

## Known critiques
- Premia have decayed out-of-sample (Choi-Zhao; "factor zoo" / Harvey-Liu-Zhu).
- A 40-stock universe can validate *construction* (correlation) but not reproduce
  the full-universe premium *level*.
