"""Career Trajectory Analysis Engine."""

from datetime import date
from typing import Optional
import re


SENIORITY_LEVELS = {
    "intern": 0, "junior": 1, "associate": 2, "mid": 3, "senior": 4,
    "lead": 5, "staff": 6, "principal": 7, "director": 8, "vp": 9,
}


def infer_seniority(title: str) -> int:
    title_lower = title.lower()
    for level, score in SENIORITY_LEVELS.items():
        if level in title_lower:
            return score
    if "sr" in title_lower or "senior" in title_lower:
        return 4
    if "jr" in title_lower:
        return 1
    return 3


def parse_year(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    match = re.search(r"(20\d{2}|19\d{2})", str(date_str))
    return int(match.group(1)) if match else None


def analyze_career_trajectory(parsed_resume: dict, target_seniority: str = "mid") -> dict:
    experiences = parsed_resume.get("experience", [])
    if not experiences:
        return {
            "career_trajectory_score": 0.3,
            "leadership_growth_score": 0.2,
            "stability_score": 0.5,
            "growth_potential_score": 0.3,
            "total_years": 0,
            "promotion_velocity": 0,
            "seniority_progression": [],
        }

    seniority_progression = []
    for exp in experiences:
        title = exp.get("title", "")
        start_year = parse_year(exp.get("start_date"))
        end_year = parse_year(exp.get("end_date")) or date.today().year
        seniority_progression.append({
            "title": title,
            "seniority_level": infer_seniority(title),
            "start_year": start_year,
            "end_year": end_year,
            "duration_years": (end_year - start_year) if start_year else 0,
        })

    seniority_progression.sort(key=lambda x: x.get("start_year") or 0)

    total_years = sum(e.get("duration_years", 0) for e in seniority_progression)
    levels = [e["seniority_level"] for e in seniority_progression]

    promotion_velocity = 0.0
    if len(levels) >= 2:
        level_growth = levels[-1] - levels[0]
        promotion_velocity = level_growth / max(total_years, 1)

    target_level = SENIORITY_LEVELS.get(target_seniority.lower(), 3)
    current_level = levels[-1] if levels else 1
    trajectory_alignment = 1.0 - abs(current_level - target_level) / max(target_level, 1)
    trajectory_alignment = max(0, min(1, trajectory_alignment))

    leadership_keywords = ["lead", "manage", "mentor", "direct", "head", "chief", "supervise"]
    leadership_count = sum(
        1 for exp in experiences
        if any(kw in exp.get("title", "").lower() or kw in exp.get("description", "").lower()
               for kw in leadership_keywords)
    )
    leadership_score = min(1.0, leadership_count / max(len(experiences), 1) + 0.2)

    durations = [e.get("duration_years", 0) for e in seniority_progression if e.get("duration_years", 0) > 0]
    avg_tenure = sum(durations) / len(durations) if durations else 0
    stability_score = min(1.0, avg_tenure / 3.0) if avg_tenure < 6 else max(0.5, 1.0 - (avg_tenure - 6) / 10)

    scope_expansion = 0.0
    if len(levels) >= 2:
        scope_expansion = (levels[-1] - levels[0]) / max(len(levels) - 1, 1) / 3

    growth_potential = (trajectory_alignment * 0.4 + scope_expansion * 0.3 + promotion_velocity * 0.3)
    growth_potential = max(0, min(1, growth_potential))

    return {
        "career_trajectory_score": round(trajectory_alignment, 4),
        "leadership_growth_score": round(leadership_score, 4),
        "stability_score": round(stability_score, 4),
        "growth_potential_score": round(growth_potential, 4),
        "total_years": round(total_years, 1),
        "promotion_velocity": round(promotion_velocity, 3),
        "seniority_progression": seniority_progression,
    }


def compute_total_experience_years(parsed_resume: dict) -> float:
    metrics = analyze_career_trajectory(parsed_resume)
    return metrics.get("total_years", 0)
