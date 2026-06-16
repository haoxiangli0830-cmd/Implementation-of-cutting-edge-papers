# AI Quant Research — Implementing Cutting-Edge Papers

> Turning landmark and frontier quantitative-finance papers into working,
> backtested, **honestly stress-tested** code — one reproducible research loop at a time.

---

## Why this project exists

Most people *read* quant papers and nod. The skill that buy-side research desks
actually pay for is different: take a cutting-edge paper, turn its claim into code,
backtest it, and — critically — **find out whether the claimed edge survives
contact with reality** (out-of-sample data, transaction costs, and the statistics
of having tried many things).

This repository is a **paper-implementation factory** built around that skill. Every
paper goes through the same rigorous pipeline and lands in a searchable gallery with
an honest verdict. The emphasis on *replication rigor* — not just "did I get a nice
backtest" but "is this real?" — is the whole point.

**Focus:** multi-asset, spanning both the **buy-side** (equities & factors,
cross-asset/macro, crypto, volatility, microstructure) and the **sell-side
bank risk-quant** function (market risk, counterparty/XVA, credit, model
validation — the UBS/Santander/JPM risk-desk world), with a deliberate bias toward
recent machine-learning / deep-learning / LLM research.

---

## How it's achieved — the 7-stage research loop

Every project in `Papers/<id>/` runs the identical loop:

| Stage | What happens | Artifact |
|------|--------------|----------|
| 1. **Triage** | Read the paper; assess the claim, data needs, feasibility, known critiques | `spec.md` |
| 2. **Decompose** | Extract the exact strategy: universe, signal, rebalance, weighting, risk controls | `spec.md` |
| 3. **Theory (light)** | Only the math needed to implement; deep dives link out to a separate theory curriculum | `theory.md` |
| 4. **Implement** | Code the idea on top of the shared `core/` library | `implementation.py` |
| 5. **Replicate** | Run the backtest; try to match the paper's reported numbers | `results/` |
| 6. **Stress & critique** | Out-of-sample, transaction costs, decay-since-publication, **multiple-testing checks** | `replication_report.md` |
| 7. **Log** | Decisions, dead-ends, what worked | `AI_LOG.md` |

### The rigor layer — what makes this buy-side-credible
A backtest that ignores overfitting is worthless. The shared evaluation module runs,
on every project:
- **Probabilistic & Deflated Sharpe Ratio** (Bailey & López de Prado) — penalises a
  Sharpe for the number of strategy variants tried and for non-normal returns.
- **Transaction-cost sensitivity** and **net-of-cost reporting**.
- **Out-of-sample / post-publication splits** to expose factor decay.

This layer is built **once** and reused everywhere. It has already caught a famous
factor that looks profitable but isn't (see crypto momentum below).

---

## Architecture

```
.
├── program.py            # registry + status board of every project  (run: python program.py)
├── CLAUDE.md             # the working protocol (the 7-stage loop, house rules)
├── core/                 # SHARED library — built once, reused by every paper
│   ├── data/             #   prices, OHLC, Ken-French factors, firm-char panel, news
│   ├── backtest/         #   vectorized portfolio engine + cost model (no look-ahead by design)
│   ├── evaluation/       #   metrics + the Deflated-Sharpe rigor layer
│   ├── models/           #   PyTorch helpers (seeding, device)
│   ├── nlp/              #   FinBERT sentiment + sentence-transformer embeddings
│   └── risk/             #   VaR / Expected Shortfall + Basel backtesting (bank risk-quant)
└── Papers/
    ├── buy_side/         # alpha / return prediction (equities, macro, crypto, LLM)
    │   └── <id>/         #   one folder per paper: paper.pdf + the 6 loop artifacts
    └── sell_side/        # pricing · execution · bank risk (vol, microstructure, rk-*)
        └── <id>/
```

**Design principle:** `core/` is a *paper-agnostic library*; each `Papers/<id>/` is a
*thin application* that defines a signal and calls `core/`. A second paper reuses the
data/backtest/rigor plumbing almost entirely — so the cost of each new paper falls as
the shared substrate grows. The backtest engine deliberately **does not** auto-lag
signals: each strategy must lag its own, making look-ahead bias explicit and
unavoidable.

---

## Project gallery

Split by desk (`Papers/buy_side/` vs `Papers/sell_side/`); within each, **scaffolding**
(canonical, to build `core/`) then **frontier** (recent ML/DL/LLM — the real target).
Status: ✅ done · ☐ planned.

### 🟦 Buy-side — alpha & return prediction
| ID | Paper | Status | Headline result |
|----|-------|--------|-----------------|
| `mx-00-tsmom` | Time-Series Momentum (Moskowitz-Ooi-Pedersen 2012) | ✅ | Net Sharpe 0.55, Deflated Sharpe 0.98 (passes) |
| `eq-00-fama-french` | Fama-French + Carhart | ✅ | Premia replicate; value/size Sharpe **negative since 2010** |
| `mx-00-carry` | Carry (Koijen et al. 2018) | ☐ | — |
| `eq-f1-eapml-gkx2020` | Empirical Asset Pricing via ML (Gu-Kelly-Xiu 2020) | ✅ | Nonlinear beats linear; GBM L/S Sharpe 0.65 |
| `eq-f2-virtue-complexity` | Virtue of Complexity (Kelly-Malamud-Zhou 2024) | ✅ | Double-descent recovery shows; timing gain modest |
| `eq-f6-price-trends-cnn` | (Re-)Imag(in)ing Price Trends (Jiang-Kelly-Xiu 2023) | ✅ | CNN on chart images > coin-flip OOS (weak, overfits) |
| `cr-f1-crypto-factors` | Crypto Risk Factors (Liu-Tsyvinski-Wu 2022) | ✅ | Market/size replicate; **momentum fails** (DSR 0.46) |
| `llm-f1-chatgpt-returns` | Can ChatGPT Forecast Returns (Lopez-Lira-Tang 2023) | ✅ | FinBERT 84% acc; sentiment L/S Sharpe 1.44 (thin sample) |
| `eq-f3-deep-learning-apt` | Deep Learning in Asset Pricing (Chen-Pelger-Zhu 2024) | ☐ | — |
| `eq-f4-deep-statarb` | Deep Learning Statistical Arbitrage (2024) | ☐ | — |
| `eq-f5-alphaportfolio` | AlphaPortfolio (Cong et al. 2021) | ☐ | — |
| `llm-f3-llm-embeddings` | Expected Returns & LLMs (Chen-Kelly-Xiu 2023) | ☐ | — |
| `cr-f2-text-returns-sestm` | Predicting Returns with Text (Ke-Kelly-Xiu 2019) | ☐ | — |
| `llm-f2`, `llm-f4` | LLM-reasoning papers (financial statements, corporate policies) | ☐ | deferred (need local LLM) |

### 🟥 Sell-side — pricing, execution & bank risk
| ID | Paper / Project | Status | Headline result |
|----|-----------------|--------|-----------------|
| `vo-00-har-optiver` | HAR realized-volatility (Corsi 2009) | ✅ | OOS R² 0.50 vs 0.40 random-walk (−17.5% error) |
| `rk-01-var-es-backtesting` | VaR/ES + Basel backtesting (Kupiec, Christoffersen, FRTB) | ✅ | Passes coverage but breaches **cluster** → motivates vol-scaled VaR/ES; Basel GREEN |
| `rk-02-cva-exposure` | Counterparty exposure & CVA (EPE/PFE, Monte-Carlo) | ☐ | — |
| `rk-03-credit-risk` | Merton distance-to-default + portfolio loss / economic capital | ☐ | — |
| `rk-04-evt-copulas` | Extreme Value Theory + copulas for tail risk | ☐ | — |
| `vo-f1-deep-hedging` | Deep Hedging (Buehler et al. 2019) | ✅ | Beats Black-Scholes delta on mean + tail under costs |
| `vo-f2-rough-vol` | Volatility Is Rough (Gatheral et al. 2018) | ☐ | — |
| `vo-f3-deep-vol-calib` | Deep Learning Volatility (Horvath et al. 2021) | ☐ | — |
| `vo-f4-quant-gans` | Quant GANs (Wiese et al. 2020) | ☐ | — |
| `ms-f1-deeplob` | DeepLOB (Zhang-Zohren-Roberts 2019) | ☐ | — |
| `ms-f2-price-formation` | Universal Price Formation (Sirignano-Cont 2019) | ☐ | — |
| `ms-f3-rl-execution` | Deep RL Optimal Execution (Ning et al. 2021) | ☐ | — |
| `rk-f1-differential-ml` | Differential Machine Learning (Huge & Savine 2020, Danske Bank) | ☐ | — |
| `rk-f2-deep-xva` | Deep learning for XVA / neural CVA | ☐ | — |
| `rk-f3-ml-var` | Quantile-regression neural nets for VaR/ES | ☐ | — |

> **10 of 30 implemented.** Run `python program.py` for the live board.

---

## What the honest results show

The point isn't that everything "works" — it's that we find out *which* claims hold:

- **Factor decay is real.** Value (HML) and size (SMB) have had **negative** Sharpes
  since 2010 — a decade-plus drought for premia that looked rock-solid for 50 years.
- **Multiple testing kills fake edges.** Crypto cross-sectional momentum had a
  tempting 0.25 Sharpe at one look-back — but a **Deflated Sharpe of 0.46** revealed
  it's no better than luck once you account for the look-backs tried.
- **Ranking ≠ prediction.** The GKX neural net had *negative* R² yet the *best*
  long/short Sharpe — getting the *order* of stocks right is what pays.
- **Frictions change the optimum.** Deep Hedging beats textbook Black-Scholes
  delta-hedging precisely *because* it accounts for transaction costs.

---

## Getting started

```bash
# 1. Create the environment
python -m venv .venv
.venv\Scripts\activate            # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
# PyTorch (CPU) for the deep-learning papers:
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 2. See the project board
python program.py

# 3. Run any paper end-to-end (downloads data, backtests, writes results/)
python "Papers/buy_side/mx-00-tsmom/implementation.py"
python "Papers/sell_side/rk-01-var-es-backtesting/implementation.py"
```

Each paper prints a summary and saves charts/tables to its own `results/` folder; read
`Papers/<side>/<id>/replication_report.md` for the verdict.

---

## Data sources (all free)

| Data | Source | Used by |
|------|--------|---------|
| Prices / OHLCV | Yahoo Finance (`yfinance`) | most papers |
| Factor returns | Ken French Data Library; JKP Global Factor Data | Fama-French, Virtue of Complexity |
| Firm characteristics | self-built from yfinance (WRDS-free panel) | the ML cluster |
| News | Finnhub (free tier) + yfinance | LLM track |
| Simulated paths | GBM / model simulation | Deep Hedging, GANs |

API keys (e.g. Finnhub) live in a git-ignored `.env` at the repo root.

---

## Roadmap

- Finish the firm-level ML cluster (`eq-f3/f4/f5`) on the free characteristic panel.
- Complete the LLM track (`llm-f3`, `cr-f2`) and add a local LLM (Ollama) for the
  reasoning papers.
- Volatility frontier (rough vol, deep vol calibration, Quant GANs).
- Deep microstructure (DeepLOB, price formation, RL execution) on free LOB benchmarks.
- A cross-track **capstone**: combine validated signals into a multi-strategy
  portfolio with a unified risk model + institutional-style research memo.

---

## Disclaimer

This is a **research and educational** project. Replications use simplified universes
and free data, so reported numbers are *not* the original papers' results and are
*not* investment advice. The goal is method, rigor, and honest evaluation — including
documenting what fails.
