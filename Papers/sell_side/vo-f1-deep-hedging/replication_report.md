# Replication report — vo-f1-deep-hedging

**Verdict: Replicates the core thesis.** Under transaction costs, a neural
network trained to minimise tail risk hedges a short call **more cost-efficiently
and with a better tail** than the textbook Black-Scholes delta hedge — exactly
Buehler et al.'s (2019) result. It does *not* beat BS on raw variance, because it
isn't optimising variance.

## Setup
- Short one ATM European call (S₀=K=100, σ=20%, ~1 month, 30 daily steps).
- **1% proportional transaction cost** on every rebalance.
- 20,000 simulated GBM paths. Premium received = BS price = 2.75.
- Network: small MLP mapping (moneyness, time-to-maturity, current holding) →
  hedge ratio; trained to minimise the **entropic risk** of terminal P&L.

## Results
| Metric | BS delta hedge | Deep hedge |
|---|---|---|
| Mean P&L | −2.73 | **−1.62** |
| Std P&L | 0.95 | 1.03 |
| CVaR (5%) | −4.88 | **−3.79** |

- **Mean P&L improved by +1.12** — the deep hedger recovers ~40% of the hedging
  cost the BS hedge bleeds away.
- **Tail risk (CVaR) improved** from −4.88 to −3.79.
- Variance slightly higher — the deliberate trade-off (see below).

See `results/pnl_distribution.png`.

## Why this happens (the lesson)
Black-Scholes delta is optimal in a *frictionless* world. With a 1% cost,
rebalancing to the exact delta every day is ruinously expensive — note the BS
hedge loses almost the entire 2.75 premium to costs (mean −2.73). The network
learns to **trade less and tolerate small mis-hedges**, paying far less in costs.
Because it was trained on the entropic/tail objective, it improves mean and CVaR
while accepting marginally more variance. That trade-off is the whole point:
*the right hedge depends on your risk measure and your costs, not on a formula.*

## Caveats / next steps
- Stylised: GBM dynamics, one instrument, proportional costs only. The paper
  generalises to Heston/rough vol, baskets, and richer frictions.
- Add a no-cost run to confirm deep hedge ≈ BS delta when frictions vanish (a
  good sanity check the paper emphasises).
- Sweep cost levels to show the deep-hedge advantage grows with costs.
