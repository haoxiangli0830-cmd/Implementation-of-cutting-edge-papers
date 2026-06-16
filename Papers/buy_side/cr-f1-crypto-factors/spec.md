# spec — cr-f1-crypto-factors

**Paper:** Liu, Tsyvinski & Wu (2022), "Common Risk Factors in Cryptocurrency,"
*Journal of Finance* 77(2).

## Claim
Three factors — crypto **market**, **size**, and **momentum** — capture the
cross-section of cryptocurrency returns, analogous to equity factor models.
Crypto momentum at the 1–4 week horizon is notably strong.

## What we implement
- **Market**: equal-weight basket return of the universe.
- **Size**: small-minus-big long/short (dollar-volume as a market-cap proxy).
- **Momentum**: 3-week cross-sectional rank, long top third / short bottom third,
  weekly rebalance, run through `core.backtest`.
- Overfitting check: look-back sweep (1–4 wk) → Deflated Sharpe.

## Data
- yfinance weekly prices for 16 liquid coins, 2019→present (free).
- Dollar volume (Close×Volume) as the size proxy.

## Benchmark to reproduce
Positive market & size premia; momentum distinct from market; strong momentum
Sharpe (paper era).

## Known critiques / limits
- Our window (2019→) is mostly **out-of-sample** vs the paper's 2014–2018 core.
- 16 liquid coins miss the small-cap tail where crypto momentum was strongest.
- Volume ≠ market cap; use CoinGecko for true caps to improve the size factor.
