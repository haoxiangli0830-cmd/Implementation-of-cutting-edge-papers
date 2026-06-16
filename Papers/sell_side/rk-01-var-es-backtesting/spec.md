# spec — rk-01-var-es-backtesting

**Domain:** Bank market-risk (sell-side risk quant). Practices follow the Basel
market-risk framework and FRTB (Fundamental Review of the Trading Book).

## What a market-risk desk does
Estimate how much the trading book could lose, report it daily to management and
regulators as **Value-at-Risk** and **Expected Shortfall**, and **prove the model
is adequate** by backtesting it against realised P&L. Regulators set a capital
multiplier based on how often the model is breached (the Basel traffic light).

## What we implement
- **VaR** at 99% (Basel) and **ES** at 97.5% (FRTB) via Historical, Parametric
  (normal), and Monte-Carlo methods.
- A rolling out-of-sample backtest counting VaR exceptions.
- **Kupiec** proportion-of-failures test (unconditional coverage),
  **Christoffersen** independence test (no clustering), and the **Basel
  traffic-light** zone.

## Data
- yfinance prices for an equal-weight multi-asset ETF book, via `core.data.get_prices`.

## Benchmark to reproduce
- Historical VaR > parametric VaR (fat tails).
- A simple VaR passes coverage but breaches cluster (fails independence) — the
  classic motivation for volatility-scaled VaR / ES.

## Reusable assets
- `core/risk/var.py` — VaR/ES estimators + Kupiec/Christoffersen/Basel zone.
  Shared by all rk-* papers.
