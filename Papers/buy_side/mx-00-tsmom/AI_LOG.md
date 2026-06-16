# AI_LOG — mx-00-tsmom

## 2026-06-14 — first build (Claude)
- **Goal**: first project; build the reusable `core/` spine while replicating TSMOM.
- Built `core/data` (yfinance + parquet cache), `core/backtest` (vectorized engine,
  no-shift convention), `core/evaluation` (Sharpe/Sortino/DD + PSR + Deflated Sharpe).
- Chose 11 liquid ETFs as futures proxies (full history from 2007) instead of real
  futures — keeps the first build free + offline-repeatable. Documented the tradeoff.
- Decisions:
  - vol target 40% per instrument, leverage cap ×5, 12-month vol window.
  - costs 10 bps round-trip on turnover.
  - look-back sweep {3,6,9,12,15} feeds the Deflated Sharpe (n_trials=5).
- **Result**: net Sharpe 0.55, DSR 0.98 (passes). Lower than paper's ~1.2 — expected,
  due to narrower universe + post-publication decay. Crisis-alpha (2008) replicates.
- **Gotcha avoided**: keeping the lag inside the strategy (not the engine) so the
  no-look-ahead rule is explicit and reusable for every future paper.
- **Next**: broaden universe; add explicit pre/post-2012 OOS split.
