# spec — rk-04-evt-copulas

**Domain:** Market & tail risk (bank risk quant).
**References:** McNeil, Frey & Embrechts, *Quantitative Risk Management* (EVT &
copula chapters); Embrechts et al. on POT.

## What this addresses
Standard VaR assumes normal returns and simple dependence. Both fail in the tail —
the region regulators (FRTB ES, stress tests) care about most. This project models
the tail directly.

## What we implement
1. **EVT (Peaks-Over-Threshold)**: fit a Generalised Pareto Distribution to losses
   above the 95th percentile; compute VaR/ES at 99% and 99.9%; compare to normal and
   empirical; report the tail index ξ.
2. **Copulas**: estimate dependence, simulate from a Gaussian vs a Student-t copula
   (with empirical margins), and compare the book's 99% VaR — isolating the effect of
   tail dependence.

## Data
- yfinance prices for a 5-asset book, via `core.data.get_prices`.

## Benchmark to reproduce
- Normal VaR ≈ EVT at 99% but far below EVT/empirical at 99.9% (heavy tails, ξ>0).
- Student-t copula VaR > Gaussian copula VaR (tail dependence).

## Known limits
- t-copula ν fixed at 4 (not estimated); single-threshold POT.
