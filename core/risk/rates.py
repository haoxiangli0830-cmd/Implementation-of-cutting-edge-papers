"""Vasicek short-rate model — simulation + analytic zero-coupon bond pricing.

Used by the counterparty-risk papers (rk-02 CVA, rk-f2 deep XVA) to value an
interest-rate swap along simulated rate paths.
"""
from __future__ import annotations

import numpy as np


def vasicek_paths(r0, a, b, sigma, T, steps, n_paths, seed=0):
    """Simulate short-rate paths: dr = a(b - r)dt + sigma dW.  Shape (n_paths, steps+1)."""
    dt = T / steps
    rng = np.random.default_rng(seed)
    r = np.empty((n_paths, steps + 1))
    r[:, 0] = r0
    for t in range(steps):
        r[:, t + 1] = (r[:, t] + a * (b - r[:, t]) * dt
                       + sigma * np.sqrt(dt) * rng.standard_normal(n_paths))
    return r


def vasicek_zcb(r, a, b, sigma, tau):
    """Price at short rate `r` of a zero-coupon bond maturing in `tau` years.

    Broadcasts elementwise: pass `r` as an array (one per path) with scalar `tau`,
    or scalar `r` with array `tau`. Returns the matching shape.
    """
    r = np.asarray(r, dtype=float)
    tau = np.asarray(tau, dtype=float)
    B = (1 - np.exp(-a * tau)) / a
    A = np.exp((B - tau) * (a ** 2 * b - sigma ** 2 / 2) / a ** 2
               - sigma ** 2 * B ** 2 / (4 * a))
    return A * np.exp(-B * r)
