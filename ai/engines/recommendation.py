"""Hiring Recommendation Engine."""

from typing import Any


def generate_recommendation(
    final_score: float,
    confidence_level: str,
    eligibility_status: str,
    human_review_required: bool,
    missing_requirements: list,
    interview_readiness: float,
    credibility_penalty: float,
) -> dict:
    if eligibility_status == "ineligible":
        return {
            "label": "Reject",
            "action": "Do not shortlist",
            "priority": "none",
            "rationale": "Candidate failed eligibility requirements",
        }

    if human_review_required and final_score >= 0.55:
        return {
            "label": "Human Review",
            "action": "Manual review before interview",
            "priority": "medium",
            "rationale": "Borderline or low-confidence assessment requires recruiter judgment",
        }

    if credibility_penalty > 0.15:
        return {
            "label": "Verify Claims",
            "action": "Run screening test or reference check",
            "priority": "high",
            "rationale": "Credibility concerns detected in resume",
        }

    if final_score >= 0.80 and confidence_level == "High":
        return {
            "label": "Strong Interview",
            "action": "Schedule interview immediately",
            "priority": "high",
            "rationale": "High fit with strong evidence backing",
        }

    if final_score >= 0.70:
        return {
            "label": "Interview",
            "action": "Include in interview shortlist",
            "priority": "medium",
            "rationale": "Good overall fit with acceptable gaps",
        }

    if final_score >= 0.55 and interview_readiness >= 0.6:
        return {
            "label": "Consider",
            "action": "Review with hiring manager",
            "priority": "low",
            "rationale": "Moderate fit; may excel in interview",
        }

    if len(missing_requirements) >= 4:
        return {
            "label": "Reject",
            "action": "Do not shortlist",
            "priority": "none",
            "rationale": f"Missing {len(missing_requirements)} key requirements",
        }

    return {
        "label": "Reject",
        "action": "Do not shortlist",
        "priority": "none",
        "rationale": "Score below shortlist threshold",
    }
