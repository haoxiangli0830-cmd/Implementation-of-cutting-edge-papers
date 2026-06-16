# theory (light) — Fama-French factors

Deep dives → 74-week curriculum (cross-sectional regression / linear algebra weeks).

## The idea in one line
A stock's average return is explained by its **exposure (beta) to a few
long/short factor portfolios**, not by the stock itself:

    E[R_i] − R_f = β_mkt·(Mkt−R_f) + β_smb·SMB + β_hml·HML + β_rmw·RMW + β_cma·CMA

Each factor is itself a **portfolio**: long the "good" stocks, short the "bad."
- **SMB** = small minus big (size)
- **HML** = high minus low book-to-market (value)
- **RMW** = robust minus weak profitability
- **CMA** = conservative minus aggressive investment
- **WML** = winners minus losers (Carhart momentum)

## How a factor is built (we did this for momentum)
1. Each month, rank every stock by a characteristic (here: past 12-1 month return).
2. Go long the top third, short the bottom third (dollar-neutral).
3. Hold one month, rebalance. The return series IS the factor.

The skip-month ("12-1", not "12-0") avoids short-term reversal contaminating the
momentum signal.

## Why "since 2010" matters
A factor premium is an *average* — averages can have long droughts. Testing the
premium on data the original authors never saw (post-publication) is the honest
test, and it's why value's recent collapse is such an important cautionary tale.
