"""vo-f5-neural-sde — Robust Pricing and Hedging via Neural SDEs
(Gierjatowicz, Sabate-Vidales, Siska, Szpruch & Zuric, 2020).

Idea: instead of hand-crafting a stochastic-vol model, put NEURAL NETWORKS inside
an SDE and *calibrate it to market option prices*. Because a vanilla surface does
not pin down a unique model, you can then find the RANGE of prices an exotic can
take across all neural SDEs that fit the vanillas — robust bounds = model risk.

Pipeline:
  1. "Market": a Heston model generates a vanilla-call surface (our calibration target).
  2. Neural SDE: dS = sqrt(V) S dW1 ; dV = [k(th - V) + b_net(V)]dt + s_net(V) sqrt(V) dW2.
     (A neural *correction* to a base stoch-vol model — stable + faithful.)
  3. Calibrate the neural SDE to the vanilla surface (differentiable Monte-Carlo).
  4. Robust bounds: re-train it to MAX and to MIN an up-and-out barrier price while
     still fitting the vanillas. The gap = robust price interval (model risk).

Run:  python implementation.py   ->  results/   (PyTorch, CPU, a few min)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import torch                                                  # noqa: E402
import torch.nn as nn                                         # noqa: E402
from scipy.stats import norm                                  # noqa: E402
from scipy.optimize import brentq                             # noqa: E402
from core.models import set_seed                              # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

S0, R, TMAX, N = 100.0, 0.0, 1.0, 50
DT = TMAX / N
M = 8000
STRIKES = [80, 90, 100, 110, 120]
MAT_T = [0.25, 0.5, 1.0]
MAT_IDX = [int(round(t / DT)) for t in MAT_T]
HESTON = dict(kappa=2.0, theta=0.04, xi=0.3, rho=-0.7, v0=0.04)


# ---------------------------------------------------------------- simulation
def simulate(b_fn, s_fn, rho, v0, seed=0):
    """Euler-simulate the SV model; return S at maturities + running max."""
    g = torch.Generator().manual_seed(seed)
    Z1 = torch.randn(M, N, generator=g)
    Z2 = torch.randn(M, N, generator=g)
    rho = torch.as_tensor(rho, dtype=torch.float32)
    v0 = torch.as_tensor(v0, dtype=torch.float32)
    W2 = rho * Z1 + torch.sqrt(torch.clamp(1 - rho ** 2, min=1e-6)) * Z2
    logS = torch.full((M,), float(np.log(S0)))
    V = v0 * torch.ones(M)                                 # keep grad through v0
    runmax = torch.full((M,), S0)
    S_mat = {}
    for t in range(N):
        sqrtV = torch.sqrt(torch.clamp(V, min=1e-8))
        logS = logS - 0.5 * V * DT + sqrtV * np.sqrt(DT) * Z1[:, t]
        S = torch.exp(logS)
        runmax = torch.maximum(runmax, S)
        V = V + b_fn(V) * DT + s_fn(V) * np.sqrt(DT) * W2[:, t]
        V = torch.clamp(V, min=1e-8)
        if (t + 1) in MAT_IDX:
            S_mat[t + 1] = S
    return S_mat, runmax


def vanilla_prices(S_mat):
    px = {}
    for ti, idx in enumerate(MAT_IDX):
        S = S_mat[idx]
        for K in STRIKES:
            px[(K, MAT_T[ti])] = torch.clamp(S - K, min=0).mean()
    return px


def heston_target():
    h = HESTON
    b = lambda V: h["kappa"] * (h["theta"] - V)
    s = lambda V: h["xi"] * torch.sqrt(torch.clamp(V, min=1e-8))
    with torch.no_grad():
        S_mat, _ = simulate(b, s, h["rho"], h["v0"], seed=123)
        return {k: v.item() for k, v in vanilla_prices(S_mat).items()}


# ---------------------------------------------------------------- neural SDE
class NeuralSV(nn.Module):
    """Neural correction to a base mean-reverting variance model."""
    def __init__(self):
        super().__init__()
        self.kappa = nn.Parameter(torch.tensor(1.5))
        self.theta = nn.Parameter(torch.tensor(0.04))
        self.xi = nn.Parameter(torch.tensor(0.3))
        self.rho_raw = nn.Parameter(torch.tensor(-0.8))
        self.v0_raw = nn.Parameter(torch.tensor(np.log(0.04)))
        self.b_net = nn.Sequential(nn.Linear(1, 16), nn.Tanh(), nn.Linear(16, 1))
        self.s_net = nn.Sequential(nn.Linear(1, 16), nn.Tanh(), nn.Linear(16, 1))

    @property
    def rho(self):
        return torch.tanh(self.rho_raw)

    @property
    def v0(self):
        return torch.exp(self.v0_raw)

    def b(self, V):
        corr = self.b_net(V.unsqueeze(1)).squeeze(1)
        return self.kappa * (self.theta - V) + 0.1 * corr

    def s(self, V):
        base = torch.abs(self.xi) * torch.sqrt(torch.clamp(V, min=1e-8))
        return base * torch.exp(0.2 * self.s_net(V.unsqueeze(1)).squeeze(1))

    def price_vanillas(self, seed=0):
        S_mat, _ = simulate(self.b, self.s, self.rho, self.v0, seed=seed)
        return vanilla_prices(S_mat)

    def barrier_price(self, K=100, B=130, seed=0):
        S_mat, runmax = simulate(self.b, self.s, self.rho, self.v0, seed=seed)
        S_T = S_mat[MAT_IDX[-1]]
        knock = torch.sigmoid(20 * (B - runmax))          # soft up-and-out
        return (torch.clamp(S_T - K, min=0) * knock).mean()


def vanilla_mse(model, target, seed):
    px = model.price_vanillas(seed=seed)
    return sum((px[k] - target[k]) ** 2 for k in target) / len(target)


def implied_vol(price, K, T):
    price = max(price, 1e-6)
    bs = lambda s: (S0 * norm.cdf((np.log(S0/K)+0.5*s*s*T)/(s*np.sqrt(T)))
                    - K * norm.cdf((np.log(S0/K)-0.5*s*s*T)/(s*np.sqrt(T))))
    try:
        return brentq(lambda s: bs(s) - price, 1e-3, 3.0)
    except Exception:
        return np.nan


def train(model, target, steps, objective=None, lam=50.0, tag=""):
    opt = torch.optim.Adam(model.parameters(), lr=5e-3)
    for it in range(steps):
        opt.zero_grad()
        loss = vanilla_mse(model, target, seed=it % 8)
        if objective is not None:
            loss = lam * loss + objective(model)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        opt.step()
        if (it + 1) % 50 == 0:
            print(f"    [{tag}] step {it+1}/{steps}  vanilla-mse {vanilla_mse(model,target,0).item():.5f}")


def surface_rmse(model, target):
    px = model.price_vanillas(seed=999)
    errs = []
    for (K, T), tgt in target.items():
        errs.append((implied_vol(px[(K,T)].item(), K, T) - implied_vol(tgt, K, T)) ** 2)
    return np.sqrt(np.nanmean(errs))


def main():
    set_seed(0)
    print("\n" + "=" * 62)
    print("vo-f5 Neural SDE — calibrate to a vanilla surface, bound an exotic")
    print("=" * 62)
    target = heston_target()
    print(f"  'market' = Heston; {len(target)} vanilla prices as calibration target")

    print("\n[1] Calibrating neural SDE to the vanilla surface...")
    base = NeuralSV()
    train(base, target, steps=300, tag="calib")
    rmse = surface_rmse(base, target)
    print(f"  -> implied-vol RMSE across surface: {rmse*100:.2f} vol points "
          + ("(good fit)" if rmse < 0.01 else "(approx fit)"))
    base_barrier = base.barrier_price(seed=999).item()
    print(f"  calibrated model's up-and-out barrier price: {base_barrier:.3f}")

    print("\n[2] Robust bounds: re-train to MAX / MIN the barrier s.t. vanilla fit...")
    hi = NeuralSV(); hi.load_state_dict(base.state_dict())
    lo = NeuralSV(); lo.load_state_dict(base.state_dict())
    train(hi, target, steps=150, objective=lambda m: -m.barrier_price(seed=7), tag="max")
    train(lo, target, steps=150, objective=lambda m: +m.barrier_price(seed=7), tag="min")
    p_hi = hi.barrier_price(seed=999).item()
    p_lo = lo.barrier_price(seed=999).item()
    rmse_hi, rmse_lo = surface_rmse(hi, target), surface_rmse(lo, target)

    print("\n" + "-" * 62)
    print("RESULT — robust price bounds for the up-and-out barrier call")
    print("-" * 62)
    print(f"  lower bound : {min(p_lo,p_hi):.3f}   (vol-RMSE {rmse_lo*100:.2f}pts)")
    print(f"  upper bound : {max(p_lo,p_hi):.3f}   (vol-RMSE {rmse_hi*100:.2f}pts)")
    width = abs(p_hi - p_lo)
    print(f"  robust interval width: {width:.3f}  = {width/base_barrier*100:.0f}% of price")
    print("  -> models that ALL fit the vanillas still disagree this much on the")
    print("     exotic. That spread IS the model risk a single calibration hides.")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for T in MAT_T:
        ks = STRIKES
        mkt = [implied_vol(target[(K,T)], K, T)*100 for K in ks]
        fit = [implied_vol(base.price_vanillas(999)[(K,T)].item(), K, T)*100 for K in ks]
        ax.plot(ks, mkt, "o-", label=f"market T={T}")
        ax.plot(ks, fit, "x--", label=f"neural SDE T={T}")
    ax.set_xlabel("strike"); ax.set_ylabel("implied vol %")
    ax.set_title("Neural SDE calibration to the vanilla surface")
    ax.legend(fontsize=7); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "calibration.png", dpi=120)
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
