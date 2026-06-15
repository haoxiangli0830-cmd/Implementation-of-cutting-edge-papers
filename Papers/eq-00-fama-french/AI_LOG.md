# AI_LOG — eq-00-fama-french

## 2026-06-15 — Wave 1 build (Claude)
- Added a NEW shared module `core/data/factors.py` (Ken French loader: download +
  parse monthly CSV zip, cache parquet). Reused by all later equity papers.
- pandas-datareader is broken on Python 3.13 (imports removed `distutils`), so I
  wrote a direct downloader instead — more robust anyway.
- Replicated FF5 + WML premia 1963→2026; added a "since 2010" Sharpe column to
  expose factor decay (HML/SMB go negative — value's lost decade).
- Built 12-1 momentum from scratch on 40 large-caps; validated by correlation
  (0.79) with French WML rather than by matching the premium level (impossible
  with a 40-stock universe).
- Reused unchanged: `core.data.get_prices`, `core.data.monthly_returns`,
  `core.evaluation`. Proof that paper #2 needed almost no new plumbing.
- Next: expand universe; Fama-MacBeth pricing test.
