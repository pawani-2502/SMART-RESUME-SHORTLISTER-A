import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.database import get_db
from backend.models import User, Job, RankingRun, Ranking, Candidate
from backend.services.auth_service import get_current_user, require_permission
from backend.services.ranking_service import compare_ranking_runs
from backend.services.audit_service import log_audit

router = APIRouter(prefix="/ranking-history", tags=["Ranking History"])


class RankingRunResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    status: str
    candidate_count: int
    eligible_count: int
    ineligible_count: int
    summary_stats: dict
    override_snapshot: dict
    is_current: bool
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/jobs/{job_id}/runs", response_model=list[RankingRunResponse])
async def list_ranking_runs(
    job_id: uuid.UUID,
    user: User = Depends(require_permission("rankings:read")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RankingRun).where(RankingRun.job_id == job_id).order_by(RankingRun.created_at.desc())
    )
    return [RankingRunResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/runs/{run_id}")
async def get_ranking_run(
    run_id: uuid.UUID,
    user: User = Depends(require_permission("rankings:read")),
    db: AsyncSession = Depends(get_db),
):
    run = (await db.execute(select(RankingRun).where(RankingRun.id == run_id))).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    rankings = (await db.execute(
        select(Ranking, Candidate)
        .join(Candidate, Ranking.candidate_id == Candidate.id)
        .where(Ranking.ranking_run_id == run_id)
        .order_by(Ranking.rank.asc().nullslast())
    )).all()

    return {
        "run": RankingRunResponse.model_validate(run),
        "rankings": [
            {
                "candidate_id": str(r.candidate_id),
                "candidate_name": c.name,
                "rank": r.rank,
                "final_score": float(r.final_score) if r.final_score else None,
                "confidence_level": r.confidence_level,
                "eligibility_status": r.eligibility_status,
            }
            for r, c in rankings
        ],
        "snapshot": run.rankings_snapshot,
    }


@router.get("/runs/compare")
async def compare_runs(
    run_a: uuid.UUID = Query(...),
    run_b: uuid.UUID = Query(...),
    user: User = Depends(require_permission("rankings:read")),
):
    try:
        return await compare_ranking_runs(run_a, run_b)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
