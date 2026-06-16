# theory (light) — Neural SDEs

Deep dives → 74-week QMRM curriculum (stochastic calculus, SDEs, derivatives weeks).

## The idea in one line
A classical model writes the asset's dynamics as an SDE with *hand-picked* functions
(e.g. Heston's variance mean-reverts at a fixed speed). A **neural SDE replaces those
functions with neural networks** and *learns* them from market prices.

    dSₜ = √Vₜ · Sₜ · dW¹           (price)
    dVₜ = [κ(θ − Vₜ) + b_net(Vₜ)]dt + s_net(Vₜ)·√Vₜ · dW²   (variance)

We keep a classical mean-reverting backbone and let the nets add corrections — so the
model is flexible but doesn't blow up.

## How you "train" an SDE
You can't fit prices in closed form here, so:
1. **Simulate** thousands of price paths with the current network weights (Euler steps).
2. **Price** the vanilla options from those paths (average of payoffs).
3. **Compare** to the market surface; backpropagate the error into the network weights
   (the whole simulation is differentiable, like Deep Hedging).
Repeat until the simulated surface matches the market.

## Why robust *bounds*, not one price
Here's the deep point. Many different models reproduce the *same* vanilla prices but
disagree on **exotics** (a barrier option depends on the whole path, which vanillas
don't constrain). So we deliberately train the neural SDE **twice more** — once to
make the barrier as *expensive* as possible, once as *cheap* as possible, both while
still fitting the vanillas. The gap between them is the **model risk**: the honest
range of prices the market data alone allows. A single calibrated model hides this;
the neural SDE exposes it.

## The connection to the rest of the program
This is the generative core behind **Deep Hedging** (`vo-f1`, same ETH research line):
once you can *generate* realistic market scenarios, you can train hedges and stress
risk on them. It's machine learning expressed in the language of stochastic calculus.
