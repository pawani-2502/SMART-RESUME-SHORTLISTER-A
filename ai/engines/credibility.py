"""Credibility Detection Engine."""

import re
from datetime import date
from ai.engines.career_trajectory import parse_year, infer_seniority


def detect_credibility_issues(parsed_resume: dict) -> dict:
    issues = []
    penalty = 0.0

    experiences = parsed_resume.get("experience", [])
    skills = parsed_resume.get("skills", [])
    skill_names = [
        s.get("name", "").lower() if isinstance(s, dict) else str(s).lower()
        for s in skills
    ]

    for exp in experiences:
        start = parse_year(exp.get("start_date"))
        end = parse_year(exp.get("end_date")) or date.today().year
        if start and end and start > end:
            issues.append({
                "type": "contradictory_timeline",
                "detail": f"Start date after end date at {exp.get('company', 'unknown')}",
                "severity": "high",
            })
            penalty += 0.15

        title = exp.get("title", "")
        if infer_seniority(title) >= 5:
            achievements = exp.get("achievements", [])
            if not achievements and not exp.get("description"):
                issues.append({
                    "type": "senior_without_evidence",
                    "detail": f"Senior title '{title}' without supporting achievements",
                    "severity": "medium",
                })
                penalty += 0.08

    advanced_skills = ["kubernetes", "machine learning", "deep learning", "architecture", "distributed systems"]
    for skill in advanced_skills:
        if skill in skill_names:
            evidenced = False
            for exp in experiences:
                text = (exp.get("description", "") + " " + " ".join(exp.get("achievements", []))).lower()
                if skill in text or any(skill in t.lower() for t in exp.get("technologies", [])):
                    evidenced = True
                    break
            for proj in parsed_resume.get("projects", []):
                if skill in proj.get("description", "").lower() or any(
                    skill in t.lower() for t in proj.get("technologies", [])
                ):
                    evidenced = True
                    break
            if not evidenced:
                issues.append({
                    "type": "unsupported_skill_claim",
                    "detail": f"Skill '{skill}' listed but not evidenced in experience/projects",
                    "severity": "medium",
                })
                penalty += 0.05

    total_years = sum(
        (parse_year(e.get("end_date")) or date.today().year) - (parse_year(e.get("start_date")) or 0)
        for e in experiences
        if parse_year(e.get("start_date"))
    )
    skill_count = len(skill_names)
    if skill_count > 30 and total_years < 3:
        issues.append({
            "type": "unrealistic_expertise",
            "detail": f"{skill_count} skills claimed with only ~{total_years} years experience",
            "severity": "high",
        })
        penalty += 0.12

    credibility_score = max(0.0, min(1.0, 1.0 - penalty))
    return {
        "credibility_score": round(credibility_score, 4),
        "credibility_penalty": round(penalty, 4),
        "issues": issues,
        "issue_count": len(issues),
    }


def create_blind_profile(parsed_resume: dict) -> dict:
    blind = {
        "skills": parsed_resume.get("skills", []),
        "experience": [],
        "projects": parsed_resume.get("projects", []),
        "education": parsed_resume.get("education", []),
        "certifications": parsed_resume.get("certifications", []),
    }
    for exp in parsed_resume.get("experience", []):
        blind["experience"].append({
            "title": exp.get("title"),
            "company": "Company Redacted",
            "description": exp.get("description"),
            "achievements": exp.get("achievements", []),
            "technologies": exp.get("technologies", []),
            "start_date": exp.get("start_date"),
            "end_date": exp.get("end_date"),
        })
    return blind
