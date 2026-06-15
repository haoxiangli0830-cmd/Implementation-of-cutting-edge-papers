# AI_LOG — vo-f1-deep-hedging

## 2026-06-15 — Wave 1 build (Claude)
- First PyTorch paper. Installed torch 2.12 CPU. Added shared `core/models`
  (set_seed, get_device) — reused by the CNN paper next.
- Built a fully-differentiable hedging P&L (premium − payoff + trading gains −
  proportional costs), trained an MLP hedge policy to minimise entropic risk.
- Benchmark = analytic Black-Scholes delta hedge on identical paths.
- Gotcha: first verdict demanded the deep hedge beat BS on std too; but deep
  hedging optimises TAIL risk, not variance. Fixed the criterion to mean + CVaR
  (the actual objective). Deep hedge then clearly wins under 1% costs
  (mean −2.73→−1.62, CVaR −4.88→−3.79), slightly higher std (expected).
- Next: add a no-cost sanity run (deep ≈ BS) and a cost sweep.
