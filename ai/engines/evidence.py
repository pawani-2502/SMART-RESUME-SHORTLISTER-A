"""Evidence Grounding Engine."""

from typing import Any


def find_evidence_for_skill(skill: str, parsed_resume: dict) -> list[dict]:
    evidence = []
    skill_lower = skill.lower()

    for exp in parsed_resume.get("experience", []):
        title = exp.get("title", "")
        company = exp.get("company", "")
        desc = exp.get("description", "")
        achievements = exp.get("achievements", [])
        techs = exp.get("technologies", [])

        if skill_lower in desc.lower() or any(skill_lower in t.lower() for t in techs):
            snippet = desc[:300] if desc else f"Used at {company} as {title}"
            evidence.append({
                "claim": f"Has experience with {skill}",
                "section": "experience",
                "source": f"{title} at {company}",
                "snippet": snippet,
                "confidence": 0.85,
            })
        for ach in achievements:
            if skill_lower in ach.lower():
                evidence.append({
                    "claim": f"Demonstrated {skill} expertise",
                    "section": "achievements",
                    "source": f"{title} at {company}",
                    "snippet": ach[:300],
                    "confidence": 0.9,
                })

    for proj in parsed_resume.get("projects", []):
        if skill_lower in proj.get("description", "").lower() or any(
            skill_lower in t.lower() for t in proj.get("technologies", [])
        ):
            evidence.append({
                "claim": f"Project experience with {skill}",
                "section": "projects",
                "source": proj.get("name", "Project"),
                "snippet": proj.get("description", "")[:300],
                "confidence": 0.8,
            })

    for cert in parsed_resume.get("certifications", []):
        cert_name = cert.get("name", cert) if isinstance(cert, dict) else cert
        if skill_lower in str(cert_name).lower():
            evidence.append({
                "claim": f"Certified in {skill}",
                "section": "certifications",
                "source": str(cert_name),
                "snippet": f"Certification: {cert_name}",
                "confidence": 0.95,
            })

    return evidence


def build_evidence_package(parsed_resume: dict, scores: dict, matched_skills: list, issues: list) -> list[dict]:
    evidence = []

    for skill in matched_skills[:10]:
        evidence.extend(find_evidence_for_skill(skill, parsed_resume))

    for issue in issues[:5]:
        evidence.append({
            "claim": issue.get("detail", issue.get("type", "")),
            "section": "credibility",
            "source": "credibility_analysis",
            "snippet": issue.get("detail", ""),
            "confidence": 0.7 if issue.get("severity") == "medium" else 0.9,
        })

    if scores.get("career_trajectory", 0) > 0.6:
        for exp in parsed_resume.get("experience", [])[:2]:
            evidence.append({
                "claim": "Strong career progression",
                "section": "experience",
                "source": exp.get("title", ""),
                "snippet": f"{exp.get('title')} at {exp.get('company')}: {exp.get('description', '')[:200]}",
                "confidence": scores.get("career_trajectory", 0.5),
            })

    return evidence[:20]


def generate_explanation(
    name: str,
    final_score: float,
    strengths: list[str],
    weaknesses: list[str],
    missing: list[str],
    confidence_level: str,
) -> str:
    score_pct = int(final_score * 100)
    parts = [f"{name} scores {score_pct}% overall fit with {confidence_level.lower()} confidence."]

    if strengths:
        parts.append(f"Key strengths: {', '.join(strengths[:5])}.")
    if weaknesses:
        parts.append(f"Areas of concern: {', '.join(weaknesses[:3])}.")
    if missing:
        parts.append(f"Missing requirements: {', '.join(missing[:5])}.")

    if final_score >= 0.75:
        parts.append("Recommended for interview.")
    elif final_score >= 0.55:
        parts.append("Borderline candidate — recommend human review before proceeding.")
    else:
        parts.append("Not recommended for shortlist based on current criteria.")

    return " ".join(parts)


def compute_resume_completeness(parsed_resume: dict) -> float:
    fields = {
        "name": 0.1, "skills": 0.2, "experience": 0.3,
        "education": 0.15, "projects": 0.1, "certifications": 0.15,
    }
    score = 0.0
    for field, weight in fields.items():
        val = parsed_resume.get(field)
        if val and (isinstance(val, list) and len(val) > 0 or isinstance(val, str) and val.strip()):
            score += weight
    return round(score, 2)
