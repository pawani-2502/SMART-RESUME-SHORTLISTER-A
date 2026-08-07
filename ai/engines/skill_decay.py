"""Temporal Skill Decay Engine - Recency-adjusted skill scoring."""

from datetime import datetime, date
from typing import Optional
import re


def parse_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    date_str = date_str.lower().strip()
    if date_str in ("present", "current", "now", "ongoing"):
        return date.today()

    formats = ["%Y-%m", "%Y/%m", "%m/%Y", "%Y", "%b %Y", "%B %Y"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str[:20], fmt)
            return parsed.date()
        except ValueError:
            continue

    year_match = re.search(r"(20\d{2}|19\d{2})", date_str)
    if year_match:
        return date(int(year_match.group(1)), 6, 1)
    return None


def months_since(d: Optional[date]) -> Optional[int]:
    if not d:
        return None
    today = date.today()
    return (today.year - d.year) * 12 + (today.month - d.month)


def decay_factor(months_ago: Optional[int], half_life_months: int = 24) -> float:
    if months_ago is None:
        return 0.3
    if months_ago <= 0:
        return 1.0
    return max(0.1, 0.5 ** (months_ago / half_life_months))


def compute_skill_freshness(parsed_resume: dict) -> dict:
    skill_timestamps: dict[str, list[int]] = {}

    for exp in parsed_resume.get("experience", []):
        end = parse_date(exp.get("end_date"))
        months = months_since(end)
        for tech in exp.get("technologies", []):
            key = tech.lower()
            if key not in skill_timestamps:
                skill_timestamps[key] = []
            if months is not None:
                skill_timestamps[key].append(months)

        desc = (exp.get("description", "") + " " + " ".join(exp.get("achievements", []))).lower()
        for skill in parsed_resume.get("skills", []):
            name = skill.get("name", "").lower() if isinstance(skill, dict) else str(skill).lower()
            if name and name in desc:
                if name not in skill_timestamps:
                    skill_timestamps[name] = []
                if months is not None:
                    skill_timestamps[name].append(months)

    for proj in parsed_resume.get("projects", []):
        end = parse_date(proj.get("end_date"))
        months = months_since(end)
        for tech in proj.get("technologies", []):
            key = tech.lower()
            if key not in skill_timestamps:
                skill_timestamps[key] = []
            if months is not None:
                skill_timestamps[key].append(months)

    skill_scores = {}
    for skill, timestamps in skill_timestamps.items():
        min_months = min(timestamps) if timestamps else None
        freshness = decay_factor(min_months)
        skill_scores[skill] = {
            "months_since_last_use": min_months,
            "freshness": round(freshness, 3),
            "relevance": round(freshness, 3),
        }

    for skill in parsed_resume.get("skills", []):
        name = skill.get("name", "").lower() if isinstance(skill, dict) else str(skill).lower()
        if name and name not in skill_scores:
            skill_scores[name] = {"months_since_last_use": None, "freshness": 0.5, "relevance": 0.5}

    if not skill_scores:
        return {"skills": {}, "avg_freshness": 0.5, "avg_relevance": 0.5}

    avg_freshness = sum(s["freshness"] for s in skill_scores.values()) / len(skill_scores)
    return {
        "skills": skill_scores,
        "avg_freshness": round(avg_freshness, 3),
        "avg_relevance": round(avg_freshness, 3),
    }


def recency_adjusted_skill_score(
    candidate_skills: list[str],
    required_skills: list[str],
    freshness_data: dict,
) -> float:
    if not required_skills:
        return 1.0

    total = 0.0
    for req in required_skills:
        req_lower = req.lower()
        matched = False
        freshness = 0.3
        for skill, data in freshness_data.get("skills", {}).items():
            if req_lower in skill or skill in req_lower:
                matched = True
                freshness = max(freshness, data["freshness"])
        if matched:
            total += freshness

    return round(total / len(required_skills), 4)
