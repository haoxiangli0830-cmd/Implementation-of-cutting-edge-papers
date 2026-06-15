"""Free, local NLP engine (no API key) — shared by the LLM-track papers.

    score_sentiment(texts) -> list of FinBERT scores in [-1, 1]  (P(pos) - P(neg))
    embed(texts)           -> sentence-transformer embedding matrix
"""
from .sentiment import score_sentiment
from .embed import embed, get_embedder

__all__ = ["score_sentiment", "embed", "get_embedder"]
