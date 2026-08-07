"""Resume duplication detection."""

import hashlib
import re
from difflib import SequenceMatcher


def compute_checksum(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def fuzzy_similarity(text_a: str, text_b: str) -> float:
    a = re.sub(r"\s+", " ", text_a.lower().strip())
    b = re.sub(r"\s+", " ", text_b.lower().strip())
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def detect_duplicate(
    new_text: str,
    existing: list[dict],
    exact_threshold: float = 1.0,
    fuzzy_threshold: float = 0.92,
) -> dict | None:
    new_checksum = compute_checksum(new_text)
    for item in existing:
        if item.get("checksum") == new_checksum:
            return {"type": "exact", "candidate_id": item["candidate_id"], "similarity": 1.0}
        similarity = fuzzy_similarity(new_text, item.get("text", ""))
        if similarity >= fuzzy_threshold:
            return {
                "type": "fuzzy",
                "candidate_id": item["candidate_id"],
                "similarity": round(similarity, 4),
            }
    return None
