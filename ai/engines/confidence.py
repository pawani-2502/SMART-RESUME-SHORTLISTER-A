"""Confidence and Human Review Engines."""

def compute_confidence(
    evidence_count: int,
    resume_completeness: float,
    verification_score: float,
    matching_confidence: float,
    credibility_score: float,
) -> tuple[float, str]:
    evidence_factor = min(1.0, evidence_count / 10)
    confidence = (
        evidence_factor * 0.25
        + resume_completeness * 0.20
        + verification_score * 0.20
        + matching_confidence * 0.20
        + credibility_score * 0.15
    )
    confidence = round(max(0, min(1, confidence)), 4)

    if confidence >= 0.75:
        level = "High"
    elif confidence >= 0.5:
        level = "Medium"
    else:
        level = "Low"

    return confidence, level


def assess_human_review(
    confidence_score: float,
    confidence_level: str,
    credibility_issues: list,
    missing_requirements: list,
    final_score: float,
    borderline_threshold: float = 0.55,
) -> tuple[bool, list[str]]:
    reasons = []

    if confidence_level == "Low":
        reasons.append("Low confidence in automated assessment")
    if credibility_issues:
        high_severity = [i for i in credibility_issues if i.get("severity") == "high"]
        if high_severity:
            reasons.append(f"Credibility concerns: {len(high_severity)} high-severity issues")
    if len(missing_requirements) >= 3:
        reasons.append(f"Multiple missing requirements ({len(missing_requirements)})")
    if borderline_threshold - 0.1 <= final_score <= borderline_threshold + 0.1:
        reasons.append("Borderline qualification - score near threshold")
    if confidence_score < 0.4:
        reasons.append("Insufficient evidence for reliable scoring")

    return len(reasons) > 0, reasons


def compute_resume_completeness(parsed_resume: dict) -> float:
    fields = ["name", "skills", "experience", "education"]
    filled = sum(1 for f in fields if parsed_resume.get(f))
    skills_score = min(1.0, len(parsed_resume.get("skills", [])) / 5)
    exp_score = min(1.0, len(parsed_resume.get("experience", [])) / 2)
    return round((filled / len(fields) * 0.5 + skills_score * 0.25 + exp_score * 0.25), 4)
