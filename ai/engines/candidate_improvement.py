"""Candidate Improvement Engine - actionable feedback for candidates."""

from typing import Any


def generate_improvement_suggestions(
    parsed_resume: dict,
    missing_requirements: list,
    weaknesses: list,
    job_requirements: dict,
) -> list[dict]:
    suggestions = []

    for skill in missing_requirements[:5]:
        suggestions.append({
            "category": "skill_gap",
            "title": f"Develop {skill} experience",
            "detail": f"Add a project or role demonstrating hands-on {skill} experience with measurable outcomes.",
            "priority": "high",
        })

    experiences = parsed_resume.get("experience", [])
    for exp in experiences:
        if not exp.get("achievements"):
            suggestions.append({
                "category": "resume_quality",
                "title": f"Add quantified achievements at {exp.get('company', 'employer')}",
                "detail": "Include metrics (%, $, time saved) for each role to strengthen credibility.",
                "priority": "medium",
            })
            break

    if not parsed_resume.get("summary"):
        suggestions.append({
            "category": "resume_quality",
            "title": "Add a professional summary",
            "detail": "Write a 2-3 sentence summary aligned to the target role's key requirements.",
            "priority": "medium",
        })

    required_certs = job_requirements.get("certifications", [])
    candidate_certs = [
        c.get("name", c) if isinstance(c, dict) else c
        for c in parsed_resume.get("certifications", [])
    ]
    for cert in required_certs:
        if not any(cert.lower() in str(c).lower() for c in candidate_certs):
            suggestions.append({
                "category": "certification",
                "title": f"Obtain {cert} certification",
                "detail": "This certification is listed as a job requirement.",
                "priority": "high",
            })

    for weakness in weaknesses[:3]:
        if weakness not in [s["title"] for s in suggestions]:
            suggestions.append({
                "category": "address_weakness",
                "title": weakness,
                "detail": "Address this gap with evidence in experience or projects section.",
                "priority": "medium",
            })

    return suggestions[:10]
