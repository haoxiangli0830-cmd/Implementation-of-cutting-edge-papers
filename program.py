"""program.py — single source of truth for the paper-implementation program.

Lists every project (folder id, paper, track, tier, status). Run directly to
print a status board:

    python program.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAPERS = ROOT / "Papers"


@dataclass(frozen=True)
class Project:
    id: str
    track: str          # E, M, C, V, L, Q
    tier: str           # scaffolding | frontier
    paper: str
    status: str = "todo"  # todo | in_progress | done


PROJECTS: list[Project] = [
    # --- Layer 0: scaffolding -------------------------------------------------
    Project("eq-00-fama-french", "E", "scaffolding", "Fama-French 3/5-factor + Carhart", "done"),
    Project("mx-00-tsmom", "M", "scaffolding", "Moskowitz, Ooi & Pedersen (2012) Time-Series Momentum", "done"),
    Project("mx-00-carry", "M", "scaffolding", "Koijen et al. (2018) Carry"),
    Project("vo-00-har-optiver", "V", "scaffolding", "Corsi (2009) HAR-RV + Optiver", "done"),
    # --- Layer 1: frontier ----------------------------------------------------
    Project("eq-f1-eapml-gkx2020", "E", "frontier", "Gu, Kelly & Xiu (2020) Empirical Asset Pricing via ML", "done"),
    Project("eq-f2-virtue-complexity", "E", "frontier", "Kelly, Malamud & Zhou (2024) Virtue of Complexity", "done"),
    Project("eq-f3-deep-learning-apt", "E", "frontier", "Chen, Pelger & Zhu (2024) Deep Learning in Asset Pricing"),
    Project("eq-f4-deep-statarb", "E", "frontier", "Guijarro-Ordonez, Pelger & Zanotti (2024) Deep Learning Stat-Arb"),
    Project("eq-f5-alphaportfolio", "E", "frontier", "Cong et al. (2021) AlphaPortfolio"),
    Project("eq-f6-price-trends-cnn", "E", "frontier", "Jiang, Kelly & Xiu (2023) Re-Imag(in)ing Price Trends", "done"),
    Project("llm-f1-chatgpt-returns", "L", "frontier", "Lopez-Lira & Tang (2023) Can ChatGPT Forecast Returns", "done"),
    Project("llm-f2-fin-statements", "L", "frontier", "Kim, Muhn & Nikolaev (2024) Financial Statement Analysis w/ LLMs"),
    Project("llm-f3-llm-embeddings", "L", "frontier", "Chen, Kelly & Xiu (2023) Expected Returns and LLMs"),
    Project("llm-f4-chatgpt-corporate", "L", "frontier", "Jha et al. (2024) ChatGPT and Corporate Policies"),
    Project("vo-f1-deep-hedging", "V", "frontier", "Buehler et al. (2019) Deep Hedging", "done"),
    Project("vo-f2-rough-vol", "V", "frontier", "Gatheral, Jaisson & Rosenbaum (2018) Volatility is Rough"),
    Project("vo-f3-deep-vol-calib", "V", "frontier", "Horvath et al. (2021) Deep Learning Volatility"),
    Project("vo-f4-quant-gans", "V", "frontier", "Wiese et al. (2020) Quant GANs"),
    Project("ms-f1-deeplob", "Q", "frontier", "Zhang, Zohren & Roberts (2019) DeepLOB"),
    Project("ms-f2-price-formation", "Q", "frontier", "Sirignano & Cont (2019) Universal Price Formation"),
    Project("ms-f3-rl-execution", "Q", "frontier", "Ning, Lin & Jaimungal (2021) Deep RL Optimal Execution"),
    Project("cr-f1-crypto-factors", "C", "frontier", "Liu, Tsyvinski & Wu (2022) Crypto Risk Factors", "done"),
    Project("cr-f2-text-returns-sestm", "C", "frontier", "Ke, Kelly & Xiu (2019) Predicting Returns with Text"),
]

_ICON = {"todo": "[ ]", "in_progress": "[~]", "done": "[x]"}


def main() -> None:
    print("\nAI Quant Research — project board\n" + "=" * 60)
    for tier in ("scaffolding", "frontier"):
        print(f"\n{tier.upper()}")
        for p in PROJECTS:
            if p.tier != tier:
                continue
            has_pdf = (PAPERS / p.id / "paper.pdf").exists()
            pdf = "pdf" if has_pdf else "   "
            print(f"  {_ICON[p.status]} {pdf}  {p.id:<26} {p.paper}")
    print()


if __name__ == "__main__":
    main()
