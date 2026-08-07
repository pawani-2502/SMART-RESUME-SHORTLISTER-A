"""Feedback Learning System - weight suggestions from recruiter outcomes."""

DEFAULT_WEIGHTS = {
    "semantic_fit": 0.15,
    "skill_coverage": 0.15,
    "career_trajectory": 0.10,
    "must_have_coverage": 0.15,
    "reciprocal_fit": 0.10,
    "interview_readiness": 0.10,
    "verification_score": 0.05,
    "leadership": 0.05,
    "domain_experience": 0.10,
    "credibility_penalty": 0.05,
}


def suggest_weight_adjustments(
    feedback_records: list[dict],
    current_weights: dict | None = None,
) -> dict:
    weights = {**DEFAULT_WEIGHTS, **(current_weights or {})}
    if len(feedback_records) < 5:
        return {
            "suggested_weights": weights,
            "confidence": "low",
            "reason": "Insufficient feedback data (minimum 5 records needed)",
            "adjustments": [],
        }

    hired = [f for f in feedback_records if f.get("decision") == "hired"]
    rejected = [f for f in feedback_records if f.get("decision") == "rejected"]

    adjustments = []
    if hired and rejected:
        hired_avg = _avg_scores(hired)
        rejected_avg = _avg_scores(rejected)

        for key in ["skill_coverage", "must_have_coverage", "semantic_fit", "career_trajectory"]:
            diff = hired_avg.get(key, 0) - rejected_avg.get(key, 0)
            if diff > 0.1:
                new_weight = min(0.25, weights.get(key, 0.1) + 0.02)
                adjustments.append({
                    "component": key,
                    "current": weights.get(key),
                    "suggested": round(new_weight, 3),
                    "reason": f"Hired candidates score {diff:.2f} higher on average",
                })
                weights[key] = new_weight

    total = sum(v for k, v in weights.items() if k != "credibility_penalty")
    for k in weights:
        if k != "credibility_penalty":
            weights[k] = round(weights[k] / total * 0.95, 3)

    return {
        "suggested_weights": weights,
        "confidence": "medium" if len(feedback_records) >= 10 else "low",
        "reason": f"Based on {len(feedback_records)} feedback records",
        "adjustments": adjustments,
    }


def _avg_scores(records: list[dict]) -> dict:
    keys = ["skill_coverage", "must_have_coverage", "semantic_fit", "career_trajectory", "final_score"]
    totals = {k: 0.0 for k in keys}
    count = len(records)
    for r in records:
        scores = r.get("score_snapshot", {})
        for k in keys:
            totals[k] += float(scores.get(k, 0))
    return {k: totals[k] / max(count, 1) for k in keys}
