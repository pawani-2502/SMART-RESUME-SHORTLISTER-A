import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.database import get_db
from backend.models import User, Job, Candidate, Ranking, InterviewSimulation, ScreeningTest, InterviewPack, AnalyticsEvent
from backend.schemas import (
    ShortlistResponse, RankingResponse, ComparisonRequest, ComparisonResponse,
    InterviewSimulationResponse, ScreeningTestResponse, InterviewPackResponse,
    TestSubmission, ExportRequest, EvidenceResponse, EvidenceItem,
)
from backend.services.auth_service import get_current_user
from backend.services.export_service import export_shortlist
from ai.pipeline.ranking_pipeline import rank_candidates
from ai.engines.comparison import compare_candidates
from ai.engines.shadow_interview import run_shadow_interview
from ai.engines.screening import generate_screening_test, grade_test_responses, generate_interview_pack

router = APIRouter(tags=["Rankings & Intelligence"])


@router.post("/jobs/{job_id}/rank")
async def run_ranking(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    async_mode: bool = True,
):
    from backend.models import RecruiterOverride, RankingRun
    from backend.services.audit_service import log_audit
    from backend.workers.tasks import run_ranking_task

    job_result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    candidates_result = await db.execute(select(Candidate).where(Candidate.job_id == job_id))
    if not candidates_result.scalars().first():
        raise HTTPException(status_code=400, detail="No candidates to rank")

    override_result = await db.execute(select(RecruiterOverride).where(RecruiterOverride.job_id == job_id))
    override = override_result.scalar_one_or_none()

    run = RankingRun(
        job_id=job_id,
        user_id=user.id,
        status="queued",
        override_snapshot={
            "weights": override.weights if override else {},
            "required_skills": override.required_skills if override else [],
        },
    )
    db.add(run)
    await db.flush()

    await log_audit(db, user.id, "ranking_run", str(run.id), "queued", after_data={"job_id": str(job_id)})

    if async_mode:
        task = run_ranking_task.delay(str(job_id), str(user.id), str(run.id))
        run.status = "queued"
        return {
            "run_id": str(run.id),
            "task_id": task.id,
            "status": "queued",
            "message": "Ranking started in background",
        }

    from backend.services.ranking_service import execute_ranking_run
    await execute_ranking_run(job_id, user.id, run.id)
    return await get_rankings(job_id, None, user, db)


@router.get("/jobs/{job_id}/rankings", response_model=ShortlistResponse)
async def get_rankings(
    job_id: uuid.UUID,
    run_id: uuid.UUID | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from backend.models import RankingRun

    if not run_id:
        current_run = (await db.execute(
            select(RankingRun).where(RankingRun.job_id == job_id, RankingRun.is_current == True)
            .order_by(RankingRun.created_at.desc())
        )).scalar_one_or_none()
        run_id = current_run.id if current_run else None

    q = select(Ranking).where(Ranking.job_id == job_id)
    if run_id:
        q = q.where(Ranking.ranking_run_id == run_id)
    rankings_result = await db.execute(q.order_by(Ranking.rank.asc().nullslast()))
    rankings = rankings_result.scalars().all()

    candidates_result = await db.execute(select(Candidate).where(Candidate.job_id == job_id))
    candidates = {c.id: c for c in candidates_result.scalars().all()}

    from backend.schemas import CandidateResponse
    responses = []
    for r in rankings:
        resp = RankingResponse.model_validate(r)
        if r.candidate_id in candidates:
            resp.candidate = CandidateResponse.model_validate(candidates[r.candidate_id])
        responses.append(resp)

    eligible = sum(1 for r in rankings if r.eligibility_status == "eligible")
    return ShortlistResponse(
        job_id=job_id,
        total_candidates=len(rankings),
        eligible_count=eligible,
        ineligible_count=len(rankings) - eligible,
        rankings=responses,
    )


@router.post("/jobs/{job_id}/compare", response_model=ComparisonResponse)
async def compare(
    job_id: uuid.UUID,
    data: ComparisonRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    candidates_result = await db.execute(
        select(Candidate).where(Candidate.id.in_(data.candidate_ids), Candidate.job_id == job_id)
    )
    candidates = candidates_result.scalars().all()

    rankings_result = await db.execute(
        select(Ranking).where(Ranking.candidate_id.in_(data.candidate_ids))
    )
    rankings = [
        {**r.__dict__, "candidate_id": str(r.candidate_id)}
        for r in rankings_result.scalars().all()
    ]

    candidate_dicts = [
        {"id": c.id, "name": c.name, "parsed_data": c.parsed_data, "career_metrics": c.career_metrics}
        for c in candidates
    ]

    result = compare_candidates(candidate_dicts, rankings)
    return ComparisonResponse(job_id=job_id, **result)


@router.post("/jobs/{job_id}/candidates/{candidate_id}/interview", response_model=InterviewSimulationResponse)
async def simulate_interview(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    cand_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if not job or not candidate:
        raise HTTPException(status_code=404, detail="Job or candidate not found")

    result = await run_shadow_interview(candidate.parsed_data, job.parsed_data or {})

    sim = InterviewSimulation(
        job_id=job_id,
        candidate_id=candidate_id,
        transcript=result["transcript"],
        readiness_score=result["readiness_score"],
        communication_score=result["communication_score"],
        confidence_score=result["confidence_score"],
        red_flags=result["red_flags"],
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
        follow_up_questions=result["follow_up_questions"],
    )
    db.add(sim)
    await db.flush()
    return InterviewSimulationResponse.model_validate(sim)


@router.post("/jobs/{job_id}/candidates/{candidate_id}/test", response_model=ScreeningTestResponse)
async def generate_test(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    cand_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = cand_result.scalar_one_or_none()
    if not job or not candidate:
        raise HTTPException(status_code=404, detail="Job or candidate not found")

    questions = await generate_screening_test(
        job.parsed_data or {},
        candidate.parsed_data or {},
        job.parsed_data.get("seniority", "mid") if job.parsed_data else "mid",
    )

    test = ScreeningTest(
        job_id=job_id,
        candidate_id=candidate_id,
        questions=questions,
        status="pending",
    )
    db.add(test)
    await db.flush()
    return ScreeningTestResponse.model_validate(test)


@router.post("/tests/{test_id}/submit", response_model=ScreeningTestResponse)
async def submit_test(
    test_id: uuid.UUID,
    data: TestSubmission,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ScreeningTest).where(ScreeningTest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    graded = await grade_test_responses(test.questions, data.responses)
    test.responses = data.responses
    test.test_score = graded["test_score"]
    test.verification_score = graded["verification_score"]
    test.status = "completed"
    from datetime import datetime
    test.completed_at = datetime.utcnow()
    return ScreeningTestResponse.model_validate(test)


@router.post("/jobs/{job_id}/candidates/{candidate_id}/interview-pack", response_model=InterviewPackResponse)
async def create_interview_pack(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    cand_result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = cand_result.scalar_one_or_none()
    rank_result = await db.execute(
        select(Ranking).where(Ranking.candidate_id == candidate_id, Ranking.job_id == job_id)
    )
    ranking = rank_result.scalar_one_or_none()
    if not job or not candidate:
        raise HTTPException(status_code=404, detail="Job or candidate not found")

    ranking_data = {
        "missing_skills": ranking.missing_requirements if ranking else [],
        "matched_skills": ranking.strengths if ranking else [],
    }
    pack_data = await generate_interview_pack(job.parsed_data or {}, candidate.parsed_data or {}, ranking_data)

    pack = InterviewPack(
        job_id=job_id,
        candidate_id=candidate_id,
        **pack_data,
    )
    db.add(pack)
    await db.flush()
    return InterviewPackResponse.model_validate(pack)


@router.get("/rankings/{ranking_id}/evidence", response_model=EvidenceResponse)
async def get_evidence(
    ranking_id: uuid.UUID,
    score_type: str = "all",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Ranking).where(Ranking.id == ranking_id))
    ranking = result.scalar_one_or_none()
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")

    evidence = ranking.evidence or []
    if score_type != "all":
        evidence = [e for e in evidence if e.get("section") == score_type]

    return EvidenceResponse(
        candidate_id=ranking.candidate_id,
        score_type=score_type,
        evidence=[EvidenceItem(**e) for e in evidence if "claim" in e],
    )


@router.post("/jobs/{job_id}/export")
async def export_rankings(
    job_id: uuid.UUID,
    data: ExportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rankings_result = await db.execute(
        select(Ranking, Candidate).join(Candidate, Ranking.candidate_id == Candidate.id)
        .where(Ranking.job_id == job_id).order_by(Ranking.rank.asc().nullslast())
    )
    rows = rankings_result.all()

    export_data = []
    for ranking, candidate in rows:
        item = {**ranking.__dict__, "candidate_name": candidate.name, "candidate_id": str(candidate.id)}
        if not data.include_evidence:
            item.pop("evidence", None)
        export_data.append(item)

    content, mime, filename = export_shortlist(export_data, {"id": job.id, "title": job.title}, data.format)
    return Response(content=content, media_type=mime, headers={"Content-Disposition": f"attachment; filename={filename}"})
