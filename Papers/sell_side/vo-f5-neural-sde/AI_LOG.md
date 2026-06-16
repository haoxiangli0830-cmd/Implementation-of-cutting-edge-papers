# AI_LOG — vo-f5-neural-sde

## 2026-06-16 — flagship application build (Claude)
- Chosen as the UZH-ETH MSc QF application piece: ML x stochastic calculus, on the
  Teichmann (ETH) neural-SDE / deep-hedging research line.
- Read the paper (arXiv:2007.04154). Core = calibrate a neural SDE to vanillas, then
  robust max/min bounds on exotics = model risk.
- Design choice for stability: neural SDE as a **correction to a base mean-reverting
  SV model** (κ,θ,ξ,ρ,v0 + two small nets), not a free-form net — converges reliably.
- Differentiable Monte-Carlo calibration (like deep hedging). Reused `core.models`.
- Bugs: (1) torch.clamp got a float when Heston passed rho -> cast to tensor;
  (2) v0 was detached via float() -> not learnable; fixed to keep the graph.
- Result: calibration vol-RMSE 0.77 pts; barrier robust interval 4.71-5.64 (~18% of
  price). Faithful reproduction of the model-risk headline.
- Caveat: upper-bound model fits vanillas looser (1.19 vs 0.83 pts) -> raise the
  vanilla-fit penalty lambda so bounds are equally iso-calibrated (true interval a bit
  narrower).
- NEXT = the creative extension (user picks): (1) generator->Deep Hedging stress test
  [ties vo-f1], (2) model-risk-vs-data curve, (3) rough-vol check [ties vo-f2].
