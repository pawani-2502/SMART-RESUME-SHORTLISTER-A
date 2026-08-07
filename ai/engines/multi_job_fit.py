"""Multi-Job Fit Analysis."""

from ai.engines.skill_graph import compute_skill_coverage, normalize_skill


def analyze_multi_job_fit(
    candidate_profile: dict,
    jobs: list[dict],
) -> list[dict]:
    candidate_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in candidate_profile.get("skills", [])
    ]
    for exp in candidate_profile.get("experience", []):
        candidate_skills.extend(exp.get("technologies", []))

    results = []
    for job in jobs:
        parsed = job.get("parsed_data", {})
        required = [
            s.get("name", s) if isinstance(s, dict) else s
            for s in parsed.get("required_skills", [])
        ]
        coverage, matched, missing = compute_skill_coverage(candidate_skills, required)
        seniority = parsed.get("seniority", "mid")
        total_years = candidate_profile.get("career_metrics", {}).get("total_years", 0)
        exp_min = parsed.get("experience_years_min", 0)

        exp_fit = 1.0 if total_years >= exp_min else total_years / max(exp_min, 1)
        fit_score = round(coverage * 0.7 + exp_fit * 0.3, 4)

        results.append({
            "job_id": str(job.get("id")),
            "job_title": job.get("title"),
            "fit_score": fit_score,
            "skill_coverage": round(coverage, 4),
            "experience_fit": round(exp_fit, 4),
            "matched_skills": matched,
            "missing_skills": missing,
            "seniority_target": seniority,
            "recommendation": "Strong fit" if fit_score >= 0.75 else "Moderate fit" if fit_score >= 0.55 else "Weak fit",
        })

    results.sort(key=lambda x: x["fit_score"], reverse=True)
    return results
