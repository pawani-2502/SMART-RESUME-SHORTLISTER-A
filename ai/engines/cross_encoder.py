"""Cross-Encoder Reranking Engine."""

import numpy as np
from typing import Optional
from backend.config import get_settings

settings = get_settings()
_cross_encoder = None


def _get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        try:
            from sentence_transformers import CrossEncoder
            _cross_encoder = CrossEncoder(settings.cross_encoder_model)
        except Exception:
            _cross_encoder = "fallback"
    return _cross_encoder


def rerank_candidates(
    query: str,
    candidates: list[dict],
    top_k: int = 10,
) -> list[tuple[str, float, float]]:
    if not candidates:
        return []

    model = _get_cross_encoder()
    pairs = []
    ids = []
    for c in candidates:
        text = c.get("raw_text", "")[:2000] or str(c.get("parsed_data", {}))[:2000]
        pairs.append([query[:1000], text])
        ids.append(str(c["id"]))

    if model == "fallback":
        scores = []
        query_tokens = set(query.lower().split())
        for pair in pairs:
            doc_tokens = set(pair[1].lower().split())
            overlap = len(query_tokens & doc_tokens)
            score = overlap / max(len(query_tokens), 1)
            scores.append(min(1.0, score))
    else:
        scores = model.predict(pairs)
        scores = [float(s) for s in scores]

    min_s, max_s = min(scores), max(scores)
    norm_scores = [(s - min_s) / (max_s - min_s + 1e-8) for s in scores]

    ranked = sorted(zip(ids, scores, norm_scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def compute_semantic_fit(query: str, candidate_text: str) -> tuple[float, float]:
    results = rerank_candidates(query, [{"id": "temp", "raw_text": candidate_text}], top_k=1)
    if results:
        return round(results[0][2], 4), round(results[0][1], 4)
    return 0.5, 0.5
