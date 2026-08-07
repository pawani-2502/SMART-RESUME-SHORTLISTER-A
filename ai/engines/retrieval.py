"""Hybrid Retrieval Engine - BM25 + Dense Embeddings + FAISS."""

import os
import pickle
import numpy as np
from typing import Optional
from rank_bm25 import BM25Okapi
from backend.config import get_settings

settings = get_settings()

_embedding_model = None
_cross_encoder = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(settings.embedding_model)
        except Exception:
            _embedding_model = False
    return _embedding_model if _embedding_model else None


def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        try:
            from sentence_transformers import CrossEncoder
            _cross_encoder = CrossEncoder(settings.cross_encoder_model)
        except Exception:
            _cross_encoder = False
    return _cross_encoder if _cross_encoder else None


def tokenize(text: str) -> list[str]:
    return text.lower().split()


def simple_embedding(text: str, dim: int = 384) -> np.ndarray:
    tokens = tokenize(text)
    vec = np.zeros(dim)
    for i, token in enumerate(tokens):
        vec[hash(token) % dim] += 1.0 / (i + 1)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


class HybridRetriever:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.store_path = os.path.join(settings.vector_store_path, job_id)
        os.makedirs(self.store_path, exist_ok=True)
        self.candidate_ids: list[str] = []
        self.candidate_texts: list[str] = []
        self.embeddings: Optional[np.ndarray] = None
        self.bm25: Optional[BM25Okapi] = None
        self._load()

    def _load(self):
        index_path = os.path.join(self.store_path, "index.pkl")
        if os.path.exists(index_path):
            with open(index_path, "rb") as f:
                data = pickle.load(f)
                self.candidate_ids = data["candidate_ids"]
                self.candidate_texts = data["candidate_texts"]
                self.embeddings = data.get("embeddings")
                if self.candidate_texts:
                    self.bm25 = BM25Okapi([tokenize(t) for t in self.candidate_texts])

    def _save(self):
        index_path = os.path.join(self.store_path, "index.pkl")
        with open(index_path, "wb") as f:
            pickle.dump({
                "candidate_ids": self.candidate_ids,
                "candidate_texts": self.candidate_texts,
                "embeddings": self.embeddings,
            }, f)

    def add_candidate(self, candidate_id: str, text: str):
        if candidate_id in self.candidate_ids:
            idx = self.candidate_ids.index(candidate_id)
            self.candidate_texts[idx] = text
        else:
            self.candidate_ids.append(candidate_id)
            self.candidate_texts.append(text)
        self._rebuild_index()

    def _rebuild_index(self):
        self.bm25 = BM25Okapi([tokenize(t) for t in self.candidate_texts])
        model = get_embedding_model()
        if model and self.candidate_texts:
            self.embeddings = model.encode(self.candidate_texts, show_progress_bar=False)
        elif self.candidate_texts:
            self.embeddings = np.array([simple_embedding(t) for t in self.candidate_texts])
        self._save()

    def retrieve(self, query: str, top_k: int = 20, alpha: float = 0.5) -> list[tuple[str, float]]:
        if not self.candidate_ids:
            return []

        query_tokens = tokenize(query)
        bm25_scores = self.bm25.get_scores(query_tokens) if self.bm25 else np.zeros(len(self.candidate_ids))

        if bm25_scores.max() > 0:
            bm25_scores = bm25_scores / bm25_scores.max()

        dense_scores = np.zeros(len(self.candidate_ids))
        if self.embeddings is not None:
            model = get_embedding_model()
            if model:
                query_emb = model.encode([query], show_progress_bar=False)[0]
            else:
                query_emb = simple_embedding(query, self.embeddings.shape[1])
            norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb)
            norms = np.where(norms == 0, 1, norms)
            dense_scores = np.dot(self.embeddings, query_emb) / norms
            if dense_scores.max() > dense_scores.min():
                dense_scores = (dense_scores - dense_scores.min()) / (dense_scores.max() - dense_scores.min())

        hybrid_scores = alpha * bm25_scores + (1 - alpha) * dense_scores
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
        return [(self.candidate_ids[i], float(hybrid_scores[i])) for i in top_indices]

    def rerank(self, query: str, candidate_ids: list[str], candidate_texts: list[str]) -> list[tuple[str, float]]:
        encoder = get_cross_encoder()
        if encoder:
            pairs = [[query, text] for text in candidate_texts]
            scores = encoder.predict(pairs)
            scores = (scores - scores.min()) / max(scores.max() - scores.min(), 1e-6)
            ranked = sorted(zip(candidate_ids, scores), key=lambda x: x[1], reverse=True)
            return [(cid, float(score)) for cid, score in ranked]

        return self.retrieve(query, top_k=len(candidate_ids))


_retrievers: dict[str, HybridRetriever] = {}


def get_retriever(job_id: str) -> HybridRetriever:
    if job_id not in _retrievers:
        _retrievers[job_id] = HybridRetriever(job_id)
    return _retrievers[job_id]
