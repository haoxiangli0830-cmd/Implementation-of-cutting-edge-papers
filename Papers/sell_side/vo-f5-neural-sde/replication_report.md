# Report — vo-f5: Robust Pricing & Hedging via Neural SDEs

**Status: faithful base built ✅ — creative extension next.** The core method
reproduces: a neural SDE is calibrated to a vanilla-option surface, and then used
to put **robust bounds on an exotic** — quantifying the model risk that any single
calibrated model conceals.

## Setup
- "Market" = a Heston model generating a 5-strike × 3-maturity **vanilla call surface**
  (the calibration target).
- **Neural SDE:** `dS = √V·S·dW₁`, `dV = [κ(θ−V) + b_net(V)]dt + s_net(V)·√V·dW₂`,
  correlation ρ. The drift/diffusion are a **neural correction to a base stochastic-vol
  model** — flexible yet stable (κ, θ, ξ, ρ, v₀ and two small nets are all learned).
- Calibration via **differentiable Monte-Carlo**: simulate the neural SDE, price the
  vanillas, backprop the surface error.

## Results
**Calibration:** implied-vol **RMSE 0.77 vol points** across the surface — the neural
SDE reproduces the Heston smile/term-structure well (see `results/calibration.png`).

**Robust bounds on an up-and-out barrier call (K=100, B=130, T=1):**
| | Barrier price | Vanilla fit (vol-RMSE) |
|---|---|---|
| Single calibrated model | 5.04 | 0.77 pts |
| **Lower bound** | **4.71** | 0.83 pts |
| **Upper bound** | **5.64** | 1.19 pts |
| **Robust interval** | **width 0.92 ≈ 18% of price** | — |

## What this means (the headline)
A vanilla surface does **not** uniquely determine a model. We trained the neural SDE
to *maximise* and to *minimise* the barrier price while still fitting the vanillas —
and got an **18%-wide price interval**. Every model in that interval is consistent
with the same market data, yet they disagree by 18% on the exotic. **That spread is
the model risk** — invisible if you quote a single number from one calibrated model.
This is exactly the paper's contribution: data-driven, model-agnostic uncertainty
quantification.

## Honest caveats
- The upper-bound model fits the vanillas a bit looser (1.19 vs 0.83 pts) — the
  vanilla-fit penalty λ should be raised so both bounds are equally iso-calibrated;
  the true robust interval is therefore slightly *narrower* than 18%.
- Synthetic "market" (Heston), small surface, small MC (8k paths) for CPU speed.

## Planned creative extension (the "thought hard" piece — to choose)
1. **Generator → Deep Hedging stress test** *(connects to `vo-f1`)*: use the
   calibrated neural SDE as the path generator to train a deep hedger, and test
   whether it out-hedges one trained on plain Black-Scholes paths.
2. **Model risk vs data**: shrink/grow the vanilla calibration set and show the
   robust interval *widen as data thins* — a clean "uncertainty ← information" curve.
3. **Rough-vol check** *(connects to `vo-f2`)*: test whether the learned variance
   dynamics exhibit rough (low-Hurst) behaviour.

## Why this is a strong UZH–ETH application piece
Neural SDEs sit on the Teichmann (ETH) deep-hedging / neural-SDE research line and
fuse machine learning with stochastic calculus — demonstrating both the computational
edge and the mathematical-finance depth the programme is built around.
