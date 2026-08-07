"""JD Quality Analyzer."""

import re
from typing import Any


def analyze_jd_quality(jd_text: str, parsed_data: dict | None = None) -> dict:
    text = jd_text or ""
    parsed = parsed_data or {}
    issues = []
    suggestions = []
    score = 1.0

    if len(text) < 200:
        issues.append("Job description is too short (< 200 characters)")
        suggestions.append("Expand with responsibilities, requirements, and team context")
        score -= 0.2

    if not parsed.get("required_skills") and not re.search(
        r"(required|must have|qualifications)", text, re.I
    ):
        issues.append("No clear required skills section detected")
        suggestions.append("Add a 'Required Skills' or 'Qualifications' section")
        score -= 0.15

    if not parsed.get("responsibilities") and not re.search(
        r"(responsibilit|you will|duties)", text, re.I
    ):
        issues.append("Responsibilities section missing or unclear")
        suggestions.append("List 5-8 key responsibilities")
        score -= 0.15

    seniority = parsed.get("seniority")
    years_min = parsed.get("experience_years_min")
    if seniority in ("senior", "lead", "principal") and (not years_min or years_min < 5):
        issues.append("Seniority level may not match experience requirements")
        suggestions.append("Align seniority title with years of experience required")
        score -= 0.1

    if not re.search(r"(education|degree|bachelor|master)", text, re.I):
        suggestions.append("Consider specifying education requirements if applicable")

    vague_terms = ["rockstar", "ninja", "guru", "synergy", "wear many hats"]
    found_vague = [t for t in vague_terms if t in text.lower()]
    if found_vague:
        issues.append(f"Vague or exclusionary terms found: {', '.join(found_vague)}")
        suggestions.append("Use specific skill and experience requirements instead of buzzwords")
        score -= 0.1

    inclusivity_score = 1.0 - (len(found_vague) * 0.1)
    clarity_score = max(0, min(1, score))
    completeness = sum([
        bool(parsed.get("required_skills")),
        bool(parsed.get("responsibilities")),
        bool(parsed.get("technologies")),
        bool(seniority),
        len(text) > 500,
    ]) / 5

    overall = round((clarity_score * 0.4 + completeness * 0.4 + inclusivity_score * 0.2), 3)

    return {
        "overall_score": overall,
        "clarity_score": round(clarity_score, 3),
        "completeness_score": round(completeness, 3),
        "inclusivity_score": round(inclusivity_score, 3),
        "issues": issues,
        "suggestions": suggestions,
        "grade": "A" if overall >= 0.85 else "B" if overall >= 0.7 else "C" if overall >= 0.55 else "D",
    }
