"""FinBERT financial-sentiment scorer (free, local, no API key).

Model: ProsusAI/finbert (downloaded once, ~440 MB, then cached locally).
Returns a signed score in [-1, 1] = P(positive) - P(negative).
"""
from __future__ import annotations

_pipe = None


def _get_pipe():
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline("text-classification", model="ProsusAI/finbert", top_k=None)
    return _pipe


def score_sentiment(texts, batch_size: int = 16) -> list[float]:
    texts = [str(t) for t in texts]
    if not texts:
        return []
    out = _get_pipe()(texts, truncation=True, batch_size=batch_size)
    scores = []
    for res in out:
        d = {r["label"].lower(): r["score"] for r in res}
        scores.append(d.get("positive", 0.0) - d.get("negative", 0.0))
    return scores
