# AI_LOG — eq-f1-eapml-gkx2020

## 2026-06-15 — Wave 2 build (Claude)
- Added shared `core/data/panel.py`: builds a free firm-level characteristic panel
  (9 price/volume chars + next-month target) from yfinance OHLCV, with
  cross-sectional rank-normalisation. Reused by eq-f3/f4/f5 next.
- WRDS path declined by user -> price/volume-only panel; EDGAR fundamentals noted
  as upgrade.
- Horse race OLS / RF / GBM / NN, strict time split (train <2019). Result matches
  GKX: nonlinear > linear on OOS R² and L/S Sharpe.
- Honest flags: (1) our OOS R² (~2%) is HIGHER than the paper's ~0.4% because the
  universe is small/clean — not a better model; (2) NN has negative R² but best
  Sharpe (ranking vs level); (3) L/S is gross.
- A few tickers (K, WBA, MMC) failed yfinance lookups (renames) — handled, ~137
  stocks used.
- Next: reuse the panel for AlphaPortfolio (eq-f5) and Deep Stat-Arb (eq-f4).
