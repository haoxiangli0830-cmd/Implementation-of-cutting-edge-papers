"""vo-f1-deep-hedging — Deep Hedging (Buehler, Gonon, Teichmann & Wood 2019).

Train a neural network to hedge a short ATM call under PROPORTIONAL TRANSACTION
COSTS, and compare it to the classic Black-Scholes delta hedge on the same
simulated paths.

The paper's point: with frictions, BS delta-hedging is no longer optimal — it
trades too much. A network trained to minimise tail risk learns to trade less and
achieves a better risk profile. No external data: stock paths are simulated GBM.

Run:  python implementation.py   ->  results/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import torch                                                  # noqa: E402
import torch.nn as nn                                         # noqa: E402
from core.models import set_seed                              # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# --- market / contract -------------------------------------------------------
S0, K, SIGMA, T, N = 100.0, 100.0, 0.20, 30 / 252, 30        # ATM call, ~1 month, daily
KAPPA = 0.01            # proportional transaction cost (1% of traded notional)
M = 20000               # simulated paths
DT = T / N


def bs_call_price(S, K, sigma, tau):
    from math import log, sqrt
    from statistics import NormalDist
    nd = NormalDist()
    if tau <= 0:
        return max(S - K, 0.0)
    d1 = (log(S / K) + 0.5 * sigma ** 2 * tau) / (sigma * sqrt(tau))
    d2 = d1 - sigma * sqrt(tau)
    return S * nd.cdf(d1) - K * nd.cdf(d2)


def simulate_paths(seed=0):
    set_seed(seed)
    z = torch.randn(M, N)
    logret = (-0.5 * SIGMA ** 2) * DT + SIGMA * np.sqrt(DT) * z   # risk-neutral, r=0
    S = torch.empty(M, N + 1)
    S[:, 0] = S0
    S[:, 1:] = S0 * torch.cumprod(torch.exp(logret), dim=1)
    return S


def hedge_pnl(S, deltas, premium):
    """P&L of selling the call and following the holding path `deltas` (M x N)."""
    payoff = torch.clamp(S[:, -1] - K, min=0.0)
    gains = (deltas * (S[:, 1:] - S[:, :-1])).sum(dim=1)          # trading gains
    prev = torch.zeros(S.shape[0])
    cost = torch.zeros(S.shape[0])
    for t in range(N):
        cost = cost + KAPPA * S[:, t] * (deltas[:, t] - prev).abs()
        prev = deltas[:, t]
    cost = cost + KAPPA * S[:, -1] * prev.abs()                   # unwind at expiry
    return premium - payoff + gains - cost


def entropic_risk(pnl, alpha=1.0):
    """Convex risk measure (lower = better). Minimised during training."""
    return (1.0 / alpha) * torch.logsumexp(-alpha * pnl - np.log(len(pnl)), dim=0)


def bs_deltas(S):
    """Black-Scholes delta at each step (the classic benchmark)."""
    from torch.distributions import Normal
    nd = Normal(0.0, 1.0)
    deltas = torch.empty(S.shape[0], N)
    for t in range(N):
        tau = T - t * DT
        d1 = (torch.log(S[:, t] / K) + 0.5 * SIGMA ** 2 * tau) / (SIGMA * np.sqrt(tau))
        deltas[:, t] = nd.cdf(d1)
    return deltas


class HedgeNet(nn.Module):
    """Maps (moneyness, time-to-maturity, current holding) -> new holding [0,1]."""
    def __init__(self, h=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, h), nn.ReLU(), nn.Linear(h, h), nn.ReLU(), nn.Linear(h, 1),
        )

    def forward(self, S):
        prev = torch.zeros(S.shape[0])
        out = []
        for t in range(N):
            tau = T - t * DT
            feat = torch.stack([torch.log(S[:, t] / K),
                                torch.full_like(S[:, t], tau),
                                prev], dim=1)
            d = torch.sigmoid(self.net(feat)).squeeze(1)         # call delta in [0,1]
            out.append(d)
            prev = d
        return torch.stack(out, dim=1)


def stats(pnl):
    p = pnl.detach().numpy()
    var5 = np.percentile(p, 5)
    cvar5 = p[p <= var5].mean()
    return dict(mean=p.mean(), std=p.std(), cvar5=cvar5)


def main():
    premium = bs_call_price(S0, K, SIGMA, T)
    S = simulate_paths(seed=0)

    # --- benchmark: Black-Scholes delta hedge ---------------------------------
    bs_pnl = hedge_pnl(S, bs_deltas(S), premium)

    # --- train the deep hedger ------------------------------------------------
    set_seed(1)
    net = HedgeNet()
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    for it in range(400):
        opt.zero_grad()
        pnl = hedge_pnl(S, net(S), premium)
        loss = entropic_risk(pnl, alpha=1.0)
        loss.backward()
        opt.step()
        if (it + 1) % 100 == 0:
            print(f"  iter {it+1:>3}  entropic risk {loss.item():.4f}")

    with torch.no_grad():
        dh_pnl = hedge_pnl(S, net(S), premium)

    bs_s, dh_s = stats(bs_pnl), stats(dh_pnl)
    print("\n" + "=" * 60)
    print(f"vo-f1-deep-hedging — short ATM call, {KAPPA*100:.0f}% costs, {M} paths")
    print("=" * 60)
    print(f"  BS premium received: {premium:.3f}")
    print(f"\n  {'metric':<10}{'BS delta':>12}{'Deep hedge':>14}")
    for k in ("mean", "std", "cvar5"):
        print(f"  {k:<10}{bs_s[k]:>12.3f}{dh_s[k]:>14.3f}")
    print("\n  Deep hedging optimises TAIL risk + cost efficiency (not variance).")
    cost_saved = (dh_s["mean"] - bs_s["mean"])
    tail_better = dh_s["cvar5"] > bs_s["cvar5"]
    print(f"  mean P&L improved by {cost_saved:+.2f}  (hedging-cost saving)")
    print(f"  CVaR(5%) {'improved' if tail_better else 'worse'}: "
          f"{bs_s['cvar5']:.2f} -> {dh_s['cvar5']:.2f}")
    won = (dh_s["mean"] > bs_s["mean"]) and tail_better
    print("  ->", "Deep hedge wins under costs (better mean + tail)." if won
          else "Mixed result.")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(bs_pnl.numpy(), bins=80, alpha=0.55, label="BS delta hedge", density=True)
    ax.hist(dh_pnl.numpy(), bins=80, alpha=0.55, label="Deep hedge", density=True)
    ax.set_title("Hedged P&L distribution (tighter = better)")
    ax.set_xlabel("Terminal P&L"); ax.legend(); ax.grid(True, alpha=0.3)
    fig.tight_layout(); fig.savefig(RESULTS / "pnl_distribution.png", dpi=120)
    np.savez(RESULTS / "pnl.npz", bs=bs_pnl.numpy(), deep=dh_pnl.numpy())
    print(f"\nSaved -> {RESULTS}\n")


if __name__ == "__main__":
    main()
