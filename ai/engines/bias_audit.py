"""Bias Audit Engine."""

from ai.engines.scoring import compute_final_score
from ai.engines.reciprocal_fit import compute_reciprocal_fit
from ai.engines.credibility import create_blind_profile


def run_bias_audit(
    parsed_resume: dict,
    job_requirements: dict,
    career_metrics: dict,
    original_scores: dict,
    blind_profile: dict | None = None,
) -> dict:
    blind = blind_profile or create_blind_profile(parsed_resume)

    blind_fit = compute_reciprocal_fit(blind, job_requirements, career_metrics)
    blind_scores = {
        **original_scores,
        "skill_coverage": blind_fit["candidate_to_role_fit"],
        "must_have_coverage": blind_fit["must_have_coverage"],
        "reciprocal_fit": blind_fit["reciprocal_fit_score"],
        "leadership_score": blind_fit["leadership_score"],
        "domain_experience": blind_fit["domain_experience"],
    }
    blind_result = compute_final_score(blind_scores)

    original = original_scores.get("final_score", 0)
    blind_score = blind_result["final_score"]
    fairness_diff = round(original - blind_score, 4)

    return {
        "original_score": round(original, 4),
        "blind_score": round(blind_score, 4),
        "fairness_difference": fairness_diff,
        "bias_flag": abs(fairness_diff) > 0.1,
        "interpretation": (
            "Significant score difference detected between identified and blind scoring"
            if abs(fairness_diff) > 0.1
            else "Scores are consistent between identified and blind evaluation"
        ),
    }
