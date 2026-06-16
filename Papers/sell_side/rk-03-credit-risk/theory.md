# theory (light) — Credit risk: Merton & portfolio capital

Deep dives → 74-week QMRM curriculum (credit-risk weeks).

## Part 1 — Merton: when does a firm default?
A firm defaults when its assets fall below its debt. We can't see asset value
directly, but we *can* see the stock. Merton's insight: **equity is a call option on
the firm's assets** with strike = debt. If assets > debt at maturity, shareholders
keep the difference; if not, they walk away (limited liability).

From the share price (equity value) and how bumpy it is (equity vol), plus the debt,
we back out:
- **Distance-to-Default (DtD)**: how many standard deviations of asset value sit
  between the firm and its debt wall. Big DtD = safe.
- **PD** = the probability assets end up below debt = N(−DtD).

That's why our automakers (lots of debt, volatile equity) have small DtD and
staples have huge DtD.

## Part 2 — portfolio: one factor ties defaults together
Defaults aren't independent — in a recession *everyone's* assets fall together. The
**single-factor (Vasicek/Basel) model** captures this: each firm's asset value =
√ρ × (one common economic factor) + √(1−ρ) × (its own luck). ρ is the asset
correlation. We simulate the common factor, see who defaults, and add up losses over
many scenarios → a **loss distribution**.

- **Expected Loss** = the average (priced into spreads, covered by provisions).
- **Economic Capital** = the *unexpected* loss out to 99.9% (held as capital).

## The subtlety that bites
The famous **Basel IRB capital formula** assumes the book is *infinitely granular*
(countless tiny loans). Real books aren't. With 20 names, one default is a big chunk
(2.25%), so the simulated capital is far above the analytic formula — that gap **is
concentration risk**, and it's why the formula alone isn't enough.
