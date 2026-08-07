"""Main Ranking Pipeline - Orchestrates all AI engines."""

from ai.engines.career_trajectory import analyze_career_trajectory
from ai.engines.skill_decay import compute_skill_freshness, recency_adjusted_skill_score
from ai.engines.skill_graph import build_skill_graph, compute_skill_coverage
from ai.engines.credibility import detect_credibility_issues, create_blind_profile
from ai.engines.eligibility import check_eligibility
from ai.engines.retrieval import get_retriever
from ai.engines.reciprocal_fit import compute_reciprocal_fit
from ai.engines.scoring import compute_final_score
from ai.engines.confidence import compute_confidence, assess_human_review
from ai.engines.evidence import build_evidence_package, generate_explanation, compute_resume_completeness
from ai.engines.bias_audit import run_bias_audit
from ai.engines.shadow_interview import run_shadow_interview


async def process_candidate(
    candidate_id: str,
    parsed_resume: dict,
    raw_text: str,
    job_requirements: dict,
    override: dict | None = None,
    job_id: str = "",
    job_text: str = "",
) -> dict:
    override = override or {}
    weights = override.get("weights", {})

    eligible, ineligibility_reasons = check_eligibility(parsed_resume, job_requirements, override)

    target_seniority = job_requirements.get("seniority", "mid")
    career_metrics = analyze_career_trajectory(parsed_resume, target_seniority)
    freshness = compute_skill_freshness(parsed_resume)
    skill_graph = build_skill_graph([
        s.get("name", s) if isinstance(s, dict) else s
        for s in parsed_resume.get("skills", [])
    ])
    credibility = detect_credibility_issues(parsed_resume)
    blind_profile = create_blind_profile(parsed_resume)

    if not eligible:
        return {
            "candidate_id": candidate_id,
            "eligibility_status": "ineligible",
            "ineligibility_reasons": ineligibility_reasons,
            "final_score": 0,
            "rank": None,
            "career_metrics": career_metrics,
            "skill_graph": skill_graph,
            "credibility": credibility,
            "blind_profile": blind_profile,
        }

    reciprocal = compute_reciprocal_fit(parsed_resume, job_requirements, career_metrics)

    candidate_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in parsed_resume.get("skills", [])
    ]
    for exp in parsed_resume.get("experience", []):
        candidate_skills.extend(exp.get("technologies", []))

    required = override.get("required_skills") or [
        s.get("name", s) if isinstance(s, dict) else s
        for s in job_requirements.get("required_skills", [])
    ]
    skill_coverage, matched, missing = compute_skill_coverage(candidate_skills, required)
    recency_score = recency_adjusted_skill_score(candidate_skills, required, freshness)

    semantic_fit = 0.5
    if job_id and raw_text:
        retriever = get_retriever(job_id)
        retriever.add_candidate(candidate_id, raw_text)
        if job_text:
            results = retriever.rerank(job_text, [candidate_id], [raw_text])
            if results:
                semantic_fit = results[0][1]

    interview_result = await run_shadow_interview(parsed_resume, job_requirements, num_questions=3)

    scores = {
        "semantic_fit": semantic_fit,
        "skill_coverage": (skill_coverage + recency_score) / 2,
        "career_trajectory": career_metrics.get("career_trajectory_score", 0.3),
        "must_have_coverage": reciprocal.get("must_have_coverage", 0),
        "reciprocal_fit": reciprocal.get("reciprocal_fit_score", 0),
        "interview_readiness": interview_result.get("readiness_score", 0.5),
        "verification_score": 0.5,
        "leadership_score": reciprocal.get("leadership_score", 0),
        "domain_experience": reciprocal.get("domain_experience", 0),
        "credibility_penalty": credibility.get("credibility_penalty", 0),
    }

    final = compute_final_score(scores, weights)
    completeness = compute_resume_completeness(parsed_resume)
    evidence = build_evidence_package(parsed_resume, scores, matched, credibility.get("issues", []))
    confidence_score, confidence_level = compute_confidence(
        len(evidence), completeness, scores["verification_score"], semantic_fit,
        credibility.get("credibility_score", 0.5),
    )

    strengths = [f"Strong {s} experience" for s in matched[:5]]
    if career_metrics.get("career_trajectory_score", 0) > 0.7:
        strengths.append("Positive career trajectory")
    weaknesses = [f"Missing {s}" for s in missing[:5]]
    weaknesses.extend([i.get("detail", "") for i in credibility.get("issues", [])[:3]])

    human_review, review_reasons = assess_human_review(
        confidence_score,
        confidence_level,
        credibility.get("issues", []),
        missing,
        final["final_score"],
    )

    bias = run_bias_audit(parsed_resume, job_requirements, career_metrics, final, blind_profile)

    explanation = generate_explanation(
        parsed_resume.get("name", "Candidate"),
        final["final_score"],
        strengths,
        weaknesses,
        missing,
        confidence_level,
    )

    return {
        "candidate_id": candidate_id,
        "eligibility_status": "eligible",
        "ineligibility_reasons": [],
        "final_score": final["final_score"],
        "score_breakdown": final["score_breakdown"],
        "semantic_fit": final["semantic_fit"],
        "skill_coverage": final["skill_coverage"],
        "career_trajectory": final["career_trajectory"],
        "must_have_coverage": final["must_have_coverage"],
        "reciprocal_fit": final["reciprocal_fit"],
        "interview_readiness": final["interview_readiness"],
        "verification_score": final["verification_score"],
        "leadership_score": final["leadership"],
        "domain_experience": final["domain_experience"],
        "credibility_penalty": final["credibility_penalty"],
        "confidence_score": confidence_score,
        "confidence_level": confidence_level,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_requirements": missing,
        "evidence": evidence,
        "human_review_required": human_review,
        "human_review_reasons": review_reasons,
        "bias_audit": bias,
        "explanation": explanation,
        "career_metrics": career_metrics,
        "skill_graph": skill_graph,
        "credibility": credibility,
        "blind_profile": blind_profile,
        "interview_simulation": interview_result,
        "matched_skills": matched,
        "missing_skills": missing,
    }


async def rank_candidates(
    candidates: list[dict],
    job_requirements: dict,
    override: dict | None = None,
    job_id: str = "",
    job_text: str = "",
) -> list[dict]:
    results = []
    for c in candidates:
        result = await process_candidate(
            str(c["id"]),
            c.get("parsed_data", {}),
            c.get("raw_text", ""),
            job_requirements,
            override,
            job_id,
            job_text,
        )
        results.append(result)

    eligible = [r for r in results if r["eligibility_status"] == "eligible"]
    ineligible = [r for r in results if r["eligibility_status"] == "ineligible"]

    eligible.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    for i, r in enumerate(eligible):
        r["rank"] = i + 1

    for r in ineligible:
        r["rank"] = None

    return eligible + ineligible
