# theory (light) — Counterparty exposure & CVA

Deep dives → 74-week QMRM curriculum (credit risk, stochastic rates weeks).

## The risk
You're owed money on a swap. The counterparty goes bust. You lose what they owed
you (times loss-given-default). CVA is the *price* of that risk, baked into the deal.

## Three numbers that describe exposure
At each future date, on each simulated scenario, work out what the swap is worth to
you. Keep only the positive part (if it's negative, *you* owe *them* — no
counterparty risk to you).
- **EE** (Expected Exposure): the average positive exposure on a date.
- **EPE**: EE averaged over the swap's life (a single summary number).
- **PFE** (Potential Future Exposure): a bad-case quantile (97.5%) — "how bad could
  it get?" Used for credit limits.

## Why the profile humps
Two forces fight:
- Time lets rates wander → exposure *grows*.
- Payments get made → remaining value *shrinks*.
Result: a hump peaking partway through. (For an FX forward, with one big payment at
the end, exposure instead grows monotonically — the shape encodes the product.)

## CVA in one line
    CVA ≈ LGD × Σ  (discount factor) × (expected exposure) × (chance they default in this period)

The default probabilities come from the counterparty's **CDS spread** (the market's
price of their default). Riskier counterparty → higher hazard → bigger CVA.

## Why simulation
A swap's value depends on the whole future rate path, and exposure is a *non-linear*
(max with 0) function of it — no neat formula, so we simulate thousands of rate
scenarios. This is exactly the problem the frontier neural-network XVA methods
(`rk-f2`) try to solve faster in high dimensions.
