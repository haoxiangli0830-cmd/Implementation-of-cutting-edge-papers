# spec — vo-f5-neural-sde

**Paper:** Gierjatowicz, Sabate-Vidales, Šiška, Szpruch & Žurič (2020), "Robust
Pricing and Hedging via Neural SDEs," arXiv:2007.04154.
**Research line:** ETH / Teichmann — neural SDEs, deep hedging, generative market models.

## Claim
Put neural networks inside a classical SDE and calibrate it to market data. Because
a vanilla surface does not pin down a unique model, one can compute **robust bounds**
on exotic prices and hedges across all neural SDEs consistent with the vanillas —
data-driven model-risk quantification. Neural SDEs are generative models (linked to
causal optimal transport) and calibrate under both real-world and risk-neutral measures.

## What we implement
- A stochastic-vol neural SDE (neural correction to a base mean-reverting variance).
- Differentiable Monte-Carlo calibration to a (Heston-generated) vanilla surface.
- Robust upper/lower bounds on an up-and-out barrier price via max/min training under
  a vanilla-fit constraint.

## Data
- None external — synthetic Heston "market". Uses `core.models` (seed/device), torch.

## Benchmark to reproduce
- Good calibration to the vanilla surface (low implied-vol RMSE).
- A non-trivial robust price interval for the exotic (model risk > 0).

## Extension (creative, to choose)
Generator→Deep-Hedging stress test · model-risk-vs-data curve · rough-vol check.
