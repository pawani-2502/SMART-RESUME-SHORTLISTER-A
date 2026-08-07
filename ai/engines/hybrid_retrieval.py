"""Hybrid Retrieval Engine - BM25 + Dense Embeddings + FAISS."""

import os
import pickle
import numpy as np
from typing import Optional
from rank_bm25 import BM25Okapi
from backend.config import get_settings

settings = get_settings()

_embedding_model = None
_faiss_indices: dict[str, object] = {}


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(settings.embedding_model)
        except Exception:
            _embedding_model = "fallback"
    return _embedding_model


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


def _embed_texts(texts: list[str]) -> np.ndarray:
    model = _get_embedding_model()
    if model == "fallback":
        vectors = []
        for text in texts:
            tokens = _tokenize(text)
            vec = np.zeros(384)
            for i, t in enumerate(tokens[:384]):
                vec[i % 384] += hash(t) % 100 / 100.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)
        return np.array(vectors)
    return model.encode(texts, show_progress_bar=False)


class HybridRetriever:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.candidate_ids: list[str] = []
        self.corpus: list[str] = []
        self.bm25: Optional[BM25Okapi] = None
        self.embeddings: Optional[np.ndarray] = None
        self.index_path = os.path.join(settings.vector_store_path, f"{job_id}.pkl")

    def index_candidates(self, candidates: list[dict]):
        self.candidate_ids = []
        self.corpus = []
        for c in candidates:
            self.candidate_ids.append(str(c["id"]))
            text = c.get("raw_text", "") or str(c.get("parsed_data", {}))
            self.corpus.append(text)

        if not self.corpus:
            return

        tokenized = [_tokenize(doc) for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized)
        self.embeddings = _embed_texts(self.corpus)

        os.makedirs(settings.vector_store_path, exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump({
                "candidate_ids": self.candidate_ids,
                "corpus": self.corpus,
                "embeddings": self.embeddings,
            }, f)

    def load_index(self) -> bool:
        if not os.path.exists(self.index_path):
            return False
        with open(self.index_path, "rb") as f:
            data = pickle.load(f)
        self.candidate_ids = data["candidate_ids"]
        self.corpus = data["corpus"]
        self.embeddings = data["embeddings"]
        tokenized = [_tokenize(doc) for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized)
        return True

    def retrieve(self, query: str, top_k: int = 20, alpha: float = 0.5) -> list[tuple[str, float]]:
        if not self.corpus or self.bm25 is None or self.embeddings is None:
            return []

        bm25_scores = self.bm25.get_scores(_tokenize(query))
        bm25_max = max(bm25_scores) if max(bm25_scores) > 0 else 1
        bm25_norm = bm25_scores / bm25_max

        query_emb = _embed_texts([query])[0]
        dense_scores = np.dot(self.embeddings, query_emb)
        dense_max = max(dense_scores) if max(dense_scores) > 0 else 1
        dense_norm = dense_scores / dense_max

        hybrid_scores = alpha * bm25_norm + (1 - alpha) * dense_norm

        ranked_indices = np.argsort(hybrid_scores)[::-1][:top_k]
        return [
            (self.candidate_ids[i], float(hybrid_scores[i]))
            for i in ranked_indices
        ]
