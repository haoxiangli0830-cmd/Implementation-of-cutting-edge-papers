# spec — vo-f1-deep-hedging

**Paper:** Buehler, Gonon, Teichmann & Wood (2019), "Deep Hedging,"
*Quantitative Finance* 19(8). arXiv:1802.03042.

## Claim
Hedging derivatives can be framed as training a neural network to choose the
trading strategy that minimises a chosen risk measure of terminal P&L, directly
incorporating market frictions (transaction costs, liquidity). Under costs this
beats classical Greek-based hedging, which assumes a frictionless market.

## What we implement
- Simulate GBM paths; sell one ATM European call.
- A network maps state → hedge ratio at each step, trained to minimise the
  **entropic risk** of P&L net of **proportional transaction costs**.
- Benchmark: Black-Scholes delta hedge on identical paths.
- Compare mean, std, and CVaR(5%) of terminal P&L.

## Data
- None external — risk-neutral GBM simulation (S₀=100, σ=20%, 1 month, 30 steps).

## Benchmark to reproduce
Deep hedge ≥ BS delta on the risk measure under costs; ≈ BS delta without costs.

## Known limits
- Stylised dynamics/contract; the paper covers stochastic-vol, baskets, richer
  frictions. Reuses `core.models` (seeding/device) — shared with the CNN paper.
