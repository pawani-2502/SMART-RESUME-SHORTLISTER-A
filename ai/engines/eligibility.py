"""Eligibility Gate - Knockout filters."""

from ai.engines.career_trajectory import compute_total_experience_years
from ai.engines.skill_graph import normalize_skill, compute_skill_coverage


def check_eligibility(
    parsed_resume: dict,
    job_requirements: dict,
    override: dict | None = None,
) -> tuple[bool, list[str]]:
    reasons = []
    override = override or {}

    min_exp = override.get("min_years_experience") or job_requirements.get("experience_years_min", 0)
    total_years = compute_total_experience_years(parsed_resume)
    if min_exp and total_years < float(min_exp):
        reasons.append(f"Insufficient experience: {total_years} years (minimum {min_exp} required)")

    required_skills = override.get("required_skills") or [
        s.get("name", s) if isinstance(s, dict) else s
        for s in job_requirements.get("required_skills", [])
    ]
    if required_skills:
        candidate_skills = [
            s.get("name", s) if isinstance(s, dict) else s
            for s in parsed_resume.get("skills", [])
        ]
        for exp in parsed_resume.get("experience", []):
            candidate_skills.extend(exp.get("technologies", []))
        coverage, _, missing = compute_skill_coverage(candidate_skills, required_skills)
        knockout_skills = override.get("knockout_filters", {}).get("mandatory_skills", required_skills)
        for skill in knockout_skills:
            skill_norm = normalize_skill(skill)
            found = any(
                skill_norm in normalize_skill(cs) or normalize_skill(cs) in skill_norm
                for cs in candidate_skills
            )
            if not found:
                reasons.append(f"Missing mandatory skill: {skill}")

    education_reqs = override.get("education_requirements") or job_requirements.get("education_requirements", [])
    if education_reqs:
        candidate_education = [
            (e.get("degree", "") + " " + e.get("field", "")).lower()
            for e in parsed_resume.get("education", [])
        ]
        has_degree = any(
            any(req.lower() in edu for edu in candidate_education)
            for req in education_reqs
        )
        if not has_degree and education_reqs:
            reasons.append(f"Education requirement not met: requires {', '.join(education_reqs)}")

    cert_reqs = override.get("certifications") or job_requirements.get("certifications", [])
    if cert_reqs:
        candidate_certs = [
            c.get("name", c).lower() if isinstance(c, dict) else str(c).lower()
            for c in parsed_resume.get("certifications", [])
        ]
        for cert in cert_reqs:
            if not any(cert.lower() in cc for cc in candidate_certs):
                reasons.append(f"Missing required certification: {cert}")

    location_reqs = override.get("location_requirements", [])
    if location_reqs:
        candidate_location = (parsed_resume.get("location") or "").lower()
        if candidate_location and not any(loc.lower() in candidate_location for loc in location_reqs):
            reasons.append(f"Location mismatch: candidate in {parsed_resume.get('location')}, requires {location_reqs}")

    work_auth = override.get("knockout_filters", {}).get("work_authorization")
    if work_auth:
        resume_text = str(parsed_resume).lower()
        if work_auth.lower() not in resume_text and "authorization" not in resume_text:
            reasons.append(f"Work authorization requirement not evidenced: {work_auth}")

    return len(reasons) == 0, reasons
