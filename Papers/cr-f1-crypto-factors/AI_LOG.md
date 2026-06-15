# AI_LOG — cr-f1-crypto-factors

## 2026-06-15 — Wave 1 build (Claude)
- Reused `core.data.get_prices` (works for yfinance crypto tickers unchanged) and
  `core.backtest` for the momentum & size long/shorts. No core changes needed.
- Universe: 16 liquid coins via yfinance, weekly, 2019→present. 30 bps costs.
- Size proxied by dollar volume (yfinance has no historical market cap); flagged
  as a limitation in the report.
- Result: market (Sharpe 0.85) and size (0.53) replicate; momentum FAILS the
  Deflated Sharpe (0.46) — honest OOS decay vs the paper's 2014–2018 era.
- Decision: report the failure prominently rather than cherry-pick the 3-week
  look-back. The DSR is the hero of this write-up.
- Next: ccxt for a wider universe; CoinGecko for true market caps.
