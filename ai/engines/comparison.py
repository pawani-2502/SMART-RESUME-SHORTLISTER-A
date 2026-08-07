"""Candidate Comparison Engine."""

from ai.engines.skill_graph import normalize_skill


def compare_candidates(candidates: list[dict], rankings: list[dict]) -> dict:
    if len(candidates) < 2:
        return {"candidates": [], "skill_overlap": {}, "recommendations": []}

    all_skills: dict[str, set[str]] = {}
    for c in candidates:
        cid = str(c["id"])
        skills = set()
        for s in c.get("parsed_data", {}).get("skills", []):
            name = s.get("name", s) if isinstance(s, dict) else s
            skills.add(normalize_skill(str(name)))
        for exp in c.get("parsed_data", {}).get("experience", []):
            for t in exp.get("technologies", []):
                skills.add(normalize_skill(t))
        all_skills[cid] = skills

    common_skills = set.intersection(*all_skills.values()) if all_skills else set()

    ranking_map = {str(r["candidate_id"]): r for r in rankings}
    comparison_data = []

    for c in candidates:
        cid = str(c["id"])
        ranking = ranking_map.get(cid, {})
        comparison_data.append({
            "candidate_id": cid,
            "name": c.get("name", "Unknown"),
            "final_score": ranking.get("final_score", 0),
            "skills": list(all_skills.get(cid, set())),
            "skill_count": len(all_skills.get(cid, set())),
            "total_years": c.get("career_metrics", {}).get("total_years", 0),
            "strengths": ranking.get("strengths", []),
            "weaknesses": ranking.get("weaknesses", []),
            "missing_requirements": ranking.get("missing_requirements", []),
            "score_breakdown": ranking.get("score_breakdown", {}),
        })

    comparison_data.sort(key=lambda x: x.get("final_score", 0), reverse=True)

    recommendations = []
    if comparison_data:
        top = comparison_data[0]
        recommendations.append({
            "type": "top_pick",
            "candidate_id": top["candidate_id"],
            "name": top["name"],
            "reason": f"Highest overall score ({int(top['final_score'] * 100)}%) with {top['skill_count']} relevant skills",
        })

        if len(comparison_data) >= 2:
            score_diff = comparison_data[0]["final_score"] - comparison_data[1]["final_score"]
            if score_diff < 0.05:
                recommendations.append({
                    "type": "close_call",
                    "candidate_ids": [comparison_data[0]["candidate_id"], comparison_data[1]["candidate_id"]],
                    "reason": "Top two candidates are very close in score — recommend side-by-side interview",
                })

    unique_skills = {}
    for cid, skills in all_skills.items():
        unique = skills - common_skills
        name = next((c["name"] for c in candidates if str(c["id"]) == cid), cid)
        unique_skills[name] = list(unique)

    return {
        "candidates": comparison_data,
        "skill_overlap": {
            "common_skills": list(common_skills),
            "unique_per_candidate": unique_skills,
        },
        "recommendations": recommendations,
    }
