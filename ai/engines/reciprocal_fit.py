"""Reciprocal Fit Engine - Bidirectional candidate-role fit."""

from ai.engines.career_trajectory import analyze_career_trajectory, infer_seniority
from ai.engines.skill_graph import compute_skill_coverage, normalize_skill


def compute_reciprocal_fit(
    parsed_resume: dict,
    job_requirements: dict,
    career_metrics: dict,
) -> dict:
    candidate_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in parsed_resume.get("skills", [])
    ]
    for exp in parsed_resume.get("experience", []):
        candidate_skills.extend(exp.get("technologies", []))

    required_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in job_requirements.get("required_skills", [])
    ]
    nice_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in job_requirements.get("nice_to_have_skills", [])
    ]

    candidate_to_role, matched, missing = compute_skill_coverage(candidate_skills, required_skills + nice_skills)
    must_have_coverage, _, must_missing = compute_skill_coverage(candidate_skills, required_skills)

    target_seniority = job_requirements.get("seniority", "mid")
    target_level = {"junior": 1, "mid": 3, "senior": 4, "lead": 5, "principal": 7}.get(target_seniority, 3)

    experiences = parsed_resume.get("experience", [])
    current_level = infer_seniority(experiences[0].get("title", "")) if experiences else 1

    role_to_candidate = 0.5
    if career_metrics:
        growth = career_metrics.get("growth_potential_score", 0.5)
        trajectory = career_metrics.get("career_trajectory_score", 0.5)
        role_to_candidate = (growth * 0.5 + trajectory * 0.5)

        if current_level > target_level + 2:
            role_to_candidate *= 0.7
        elif current_level < target_level - 2:
            role_to_candidate *= 0.6

    domain_reqs = job_requirements.get("domain_requirements", [])
    domain_score = 0.5
    if domain_reqs:
        resume_text = str(parsed_resume).lower()
        domain_matches = sum(1 for d in domain_reqs if d.lower() in resume_text)
        domain_score = domain_matches / len(domain_reqs)

    reciprocal_fit = (candidate_to_role * 0.6 + role_to_candidate * 0.4)
    leadership_score = career_metrics.get("leadership_growth_score", 0.3) if career_metrics else 0.3

    return {
        "candidate_to_role_fit": round(candidate_to_role, 4),
        "role_to_candidate_fit": round(role_to_candidate, 4),
        "reciprocal_fit_score": round(reciprocal_fit, 4),
        "must_have_coverage": round(must_have_coverage, 4),
        "domain_experience": round(domain_score, 4),
        "leadership_score": round(leadership_score, 4),
        "matched_skills": matched,
        "missing_skills": missing,
        "must_have_missing": must_missing,
    }
