# Replication report — cr-f1-crypto-factors

**Verdict: Mixed — and that's the interesting part.** The crypto **market** and
**size** factors replicate clearly; the **momentum** factor the paper highlighted
**does not survive** our 2019→present out-of-sample window (Deflated Sharpe 0.46,
fails). Momentum *is* statistically distinct from the market (corr −0.07) — it's
just no longer profitable.

## Results (weekly, 2019 → present, 16 coins, 30 bps costs)
| Factor | Ann. return | Vol | Sharpe | Max DD |
|---|---|---|---|---|
| Market (EW basket) | +44% | 77% | **0.85** | −82% |
| Size (small−big, vol-proxy) | +18% | 69% | **0.53** | −72% |
| Momentum (3-wk L/S) | −5.5% | 60% | 0.25 | −84% |

See `results/crypto_factors.png`.

## What replicates
- **Market premium**: large and positive (Sharpe 0.85) — but with brutal ~80%
  drawdowns. The premium is real; the risk is extreme.
- **Size effect**: small coins beat large (Sharpe 0.53), matching the paper's SMB.
- **Momentum is a distinct dimension**: correlation with the market is ≈0, so it
  is *not* just disguised market beta — consistent with the paper's claim that
  it's a separate factor.

## What does NOT replicate
- **Momentum profitability.** Look-back sweep Sharpes (1–4 weeks): −0.34, −0.02,
  0.25, 0.23 — unstable and mostly weak. The **Deflated Sharpe is 0.46**: once we
  account for trying 4 look-backs, the best one is no better than luck.
- Most likely causes: (a) the paper's strong momentum was estimated on the
  2014–2018 boom; (b) crypto microstructure changed (more efficient, more
  institutional) post-2019; (c) our universe (16 liquid coins) misses the
  small-cap tail where crypto momentum was strongest.

## Honest takeaway
This is the program working as intended: a famous factor's headline result
**decayed out-of-sample**, and the rigor layer caught it instead of letting a
cherry-picked look-back masquerade as alpha.

## Next steps
- Broaden the universe via `ccxt` (hundreds of coins incl. small caps).
- Use true historical market cap (CoinGecko API) instead of a volume proxy.
- Split 2019–2021 vs 2022–present to date the momentum decay precisely.
