"""Sentence-embedding helper (free, local) for the LLM-embeddings paper.

Model: sentence-transformers/all-MiniLM-L6-v2 (~80 MB, cached after first use).
"""
from __future__ import annotations

_model = None


def get_embedder():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed(texts):
    texts = [str(t) for t in texts]
    return get_embedder().encode(texts, show_progress_bar=False, normalize_embeddings=True)
