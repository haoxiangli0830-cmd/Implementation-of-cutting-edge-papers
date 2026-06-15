# AI Quant Research — working protocol

This repo turns cutting-edge quant papers into tested, buy-side-credible code.
Every project lives in `Papers/<folder-id>/` and goes through the same 7 stages.

## The loop (every paper)
1. **Triage** — claim, data needs, feasibility, known critiques → `spec.md` header.
2. **Decompose** — universe, signal, rebalance, weighting, risk controls, reported
   metrics → full `spec.md`.
3. **Theory (light)** — only the math needed to implement; link deep dives to the
   74-week curriculum (`Career/Quantitative_Finance/Curriculum/`) → `theory.md`.
4. **Implement** — code on top of `core/` (never re-implement data/backtest/metrics)
   → `implementation.py` (or `.ipynb`).
5. **Replicate** — match the paper's reported numbers over its sample → `results/`.
6. **Stress & critique** — out-of-sample, transaction costs, capacity, decay since
   publication, and the rigor layer (Deflated Sharpe). Honest verdict →
   `replication_report.md`.
7. **Log** — prompts, decisions, dead-ends → `AI_LOG.md`.

## Shared library (`core/`) — reuse, do not duplicate
- `core.data.get_prices(tickers, start)` → wide adjusted-close frame (parquet-cached).
- `core.data.monthly_returns(prices)` → month-end returns.
- `core.backtest.backtest(weights, returns, cost_bps)` → gross/net/turnover/equity.
  Convention: `weights.loc[t]` is held over period `t`; **lag your signal yourself**.
- `core.evaluation.performance_summary(returns)` and `deflated_sharpe_ratio(...)`.

## House rules
- No look-ahead. Signals use only past data; the engine does not shift for you.
- Always report **net of costs** and always run the Deflated Sharpe against the
  number of variants you tried. A backtest without a cost + multiple-testing check
  is not finished.
- Keep `core/` paper-agnostic; anything paper-specific lives in its `Papers/<id>/`.
