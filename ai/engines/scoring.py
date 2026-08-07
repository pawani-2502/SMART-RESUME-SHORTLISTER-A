"""Scoring Engine - Final weighted score computation."""

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


def compute_final_score(scores: dict, weights: dict | None = None) -> dict:
    w = {**DEFAULT_WEIGHTS, **(weights or {})}

    components = {
        "semantic_fit": scores.get("semantic_fit", 0),
        "skill_coverage": scores.get("skill_coverage", 0),
        "career_trajectory": scores.get("career_trajectory", 0),
        "must_have_coverage": scores.get("must_have_coverage", 0),
        "reciprocal_fit": scores.get("reciprocal_fit", 0),
        "interview_readiness": scores.get("interview_readiness", 0.5),
        "verification_score": scores.get("verification_score", 0.5),
        "leadership": scores.get("leadership_score", 0),
        "domain_experience": scores.get("domain_experience", 0),
    }

    penalty = scores.get("credibility_penalty", 0)

    weighted_sum = sum(components[k] * w.get(k, 0) for k in components)
    final = max(0.0, min(1.0, weighted_sum - penalty * w.get("credibility_penalty", 0.05)))

    breakdown = {
        k: {"score": round(v, 4), "weight": w.get(k, 0), "weighted": round(v * w.get(k, 0), 4)}
        for k, v in components.items()
    }
    breakdown["credibility_penalty"] = {
        "score": round(penalty, 4),
        "weight": w.get("credibility_penalty", 0.05),
        "weighted": round(-penalty * w.get("credibility_penalty", 0.05), 4),
    }

    return {
        "final_score": round(final, 4),
        "score_breakdown": breakdown,
        **components,
        "credibility_penalty": round(penalty, 4),
    }


def compute_confidence(
    evidence_count: int,
    resume_completeness: float,
    verification_score: float,
    matching_confidence: float,
) -> dict:
    evidence_quality = min(1.0, evidence_count / 10)
    confidence = (
        evidence_quality * 0.3
        + resume_completeness * 0.25
        + verification_score * 0.25
        + matching_confidence * 0.2
    )
    confidence = round(max(0, min(1, confidence)), 4)

    if confidence >= 0.75:
        level = "High"
    elif confidence >= 0.5:
        level = "Medium"
    else:
        level = "Low"

    return {"confidence_score": confidence, "confidence_level": level}


def assess_human_review(
    confidence_score: float,
    credibility_issues: list,
    missing_requirements: list,
    final_score: float,
    borderline_threshold: float = 0.55,
) -> tuple[bool, list[str]]:
    reasons = []
    if confidence_score < 0.5:
        reasons.append("Low confidence in assessment due to limited evidence")
    if credibility_issues:
        reasons.append(f"Credibility concerns detected ({len(credibility_issues)} issues)")
    if missing_requirements and final_score > borderline_threshold:
        reasons.append("Borderline qualification with missing requirements")
    if 0.45 <= final_score <= 0.65:
        reasons.append("Borderline score requires human judgment")

    resume_fields = ["experience", "skills", "education"]
    return len(reasons) > 0, reasons
