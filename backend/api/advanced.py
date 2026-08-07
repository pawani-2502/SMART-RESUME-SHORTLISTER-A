import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.database import get_db
from backend.models import User, Job, Candidate, Ranking, CopilotMessage, Feedback
from backend.services.auth_service import get_current_user
from ai.agents.copilot_agent import copilot_chat
from ai.engines.feedback_learning import suggest_weight_adjustments
from ai.engines.jd_quality import analyze_jd_quality
from ai.engines.multi_job_fit import analyze_multi_job_fit
from ai.engines.knowledge_graph import build_knowledge_graph, flatten_for_storage
from ai.engines.candidate_improvement import generate_improvement_suggestions
from ai.engines.recommendation import generate_recommendation
from backend.models import KnowledgeNode, RecruiterOverride

router = APIRouter(tags=["Advanced Intelligence"])


class CopilotChatRequest(BaseModel):
    message: str


class CopilotChatResponse(BaseModel):
    answer: str
    intent: str
    citations: list


@router.post("/jobs/{job_id}/copilot/chat", response_model=CopilotChatResponse)
async def copilot_chat_endpoint(
    job_id: uuid.UUID,
    data: CopilotChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates_result = await db.execute(select(Candidate).where(Candidate.job_id == job_id))
    candidates = candidates_result.scalars().all()

    rankings_result = await db.execute(
        select(Ranking, Candidate)
        .join(Candidate, Ranking.candidate_id == Candidate.id)
        .where(Ranking.job_id == job_id)
        .order_by(Ranking.rank.asc().nullslast())
    )
    rankings = []
    for r, c in rankings_result.all():
        rankings.append({
            **{k: v for k, v in r.__dict__.items() if not k.startswith("_")},
            "candidate_id": str(r.candidate_id),
            "candidate_name": c.name,
        })

    job_dict = {"id": str(job.id), "title": job.title, "status": job.status, "parsed_data": job.parsed_data}
    candidate_dicts = [{"id": str(c.id), "name": c.name, "parsed_data": c.parsed_data} for c in candidates]

    result = await copilot_chat(data.message, job_dict, rankings, candidate_dicts)

    db.add(CopilotMessage(
        job_id=job_id, user_id=user.id, role="user", content=data.message,
    ))
    db.add(CopilotMessage(
        job_id=job_id, user_id=user.id, role="assistant",
        content=result["answer"], citations=result["citations"],
    ))

    return CopilotChatResponse(**result)


@router.get("/jobs/{job_id}/copilot/history")
async def copilot_history(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CopilotMessage)
        .where(CopilotMessage.job_id == job_id, CopilotMessage.user_id == user.id)
        .order_by(CopilotMessage.created_at.asc())
        .limit(50)
    )
    return [
        {"role": m.role, "content": m.content, "citations": m.citations, "created_at": m.created_at.isoformat()}
        for m in result.scalars().all()
    ]


@router.post("/jobs/{job_id}/analyze-quality")
async def jd_quality(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return analyze_jd_quality(job.raw_text or job.description or "", job.parsed_data)


@router.get("/candidates/{candidate_id}/knowledge-graph")
async def get_knowledge_graph(
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return build_knowledge_graph(candidate.parsed_data or {})


@router.get("/candidates/{candidate_id}/improvements")
async def get_improvements(
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cand_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job_result = await db.execute(select(Job).where(Job.id == candidate.job_id))
    job = job_result.scalar_one_or_none()
    rank_result = await db.execute(select(Ranking).where(Ranking.candidate_id == candidate_id))
    ranking = rank_result.scalar_one_or_none()

    return generate_improvement_suggestions(
        candidate.parsed_data or {},
        ranking.missing_requirements if ranking else [],
        ranking.weaknesses if ranking else [],
        job.parsed_data if job else {},
    )


@router.get("/candidates/{candidate_id}/recommendation")
async def get_recommendation(
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rank_result = await db.execute(select(Ranking).where(Ranking.candidate_id == candidate_id))
    ranking = rank_result.scalar_one_or_none()
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")

    return generate_recommendation(
        float(ranking.final_score or 0),
        ranking.confidence_level or "Low",
        ranking.eligibility_status,
        ranking.human_review_required,
        ranking.missing_requirements or [],
        float(ranking.interview_readiness or 0),
        float(ranking.credibility_penalty or 0),
    )


@router.get("/candidates/{candidate_id}/multi-job-fit")
async def multi_job_fit(
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cand_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    jobs_result = await db.execute(select(Job).where(Job.user_id == user.id))
    jobs = [
        {"id": j.id, "title": j.title, "parsed_data": j.parsed_data}
        for j in jobs_result.scalars().all()
    ]

    profile = {
        **(candidate.parsed_data or {}),
        "career_metrics": candidate.career_metrics or {},
    }
    return analyze_multi_job_fit(profile, jobs)


@router.get("/jobs/{job_id}/feedback/weight-suggestions")
async def weight_suggestions(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rankings_result = await db.execute(select(Ranking).where(Ranking.job_id == job_id))
    ranking_ids = [r.id for r in rankings_result.scalars().all()]

    if not ranking_ids:
        return {"suggested_weights": {}, "confidence": "low", "reason": "No rankings", "adjustments": []}

    feedback_result = await db.execute(select(Feedback).where(Feedback.ranking_id.in_(ranking_ids)))
    feedbacks = feedback_result.scalars().all()

    records = []
    for f in feedbacks:
        rank_result = await db.execute(select(Ranking).where(Ranking.id == f.ranking_id))
        r = rank_result.scalar_one_or_none()
        if r:
            records.append({
                "decision": f.decision,
                "score_snapshot": {
                    "final_score": float(r.final_score or 0),
                    "skill_coverage": float(r.skill_coverage or 0),
                    "must_have_coverage": float(r.must_have_coverage or 0),
                    "semantic_fit": float(r.semantic_fit or 0),
                    "career_trajectory": float(r.career_trajectory or 0),
                },
            })

    override_result = await db.execute(select(RecruiterOverride).where(RecruiterOverride.job_id == job_id))
    override = override_result.scalar_one_or_none()
    current_weights = override.weights if override else {}

    return suggest_weight_adjustments(records, current_weights)
