import uuid
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.database import get_db
from backend.models import User, ScreeningTest, Candidate, Job
from backend.schemas import ScreeningTestResponse, TestSubmission
from backend.services.auth_service import require_permission
from backend.services.screening_service import (
    create_test_for_candidate, assign_test, submit_test, get_job_test_analytics,
)
from backend.services.audit_service import log_audit
from backend.workers.tasks import generate_screening_test_task

router = APIRouter(prefix="/screening", tags=["Screening Tests"])


class AssignTestRequest(BaseModel):
    test_id: uuid.UUID


@router.get("/jobs/{job_id}/tests")
async def list_job_tests(
    job_id: uuid.UUID,
    user: User = Depends(require_permission("screening:read")),
    db: AsyncSession = Depends(get_db),
):
    tests = (await db.execute(
        select(ScreeningTest, Candidate)
        .join(Candidate, ScreeningTest.candidate_id == Candidate.id)
        .where(ScreeningTest.job_id == job_id)
        .order_by(ScreeningTest.created_at.desc())
    )).all()
    return [
        {
            **ScreeningTestResponse.model_validate(t).model_dump(),
            "candidate_name": c.name,
            "analytics": t.analytics,
            "assigned_status": t.assigned_status,
            "passed": (t.analytics or {}).get("passed"),
        }
        for t, c in tests
    ]


@router.get("/jobs/{job_id}/analytics")
async def test_analytics(
    job_id: uuid.UUID,
    user: User = Depends(require_permission("screening:read")),
):
    return await get_job_test_analytics(job_id)


@router.post("/jobs/{job_id}/candidates/{candidate_id}/generate")
async def generate_test_async(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    user: User = Depends(require_permission("screening:write")),
    db: AsyncSession = Depends(get_db),
):
    task = generate_screening_test_task.delay(str(job_id), str(candidate_id))
    await log_audit(db, user.id, "screening_test", str(candidate_id), "generate_queued", after_data={"task_id": task.id})
    return {"task_id": task.id, "message": "Test generation queued"}


@router.post("/jobs/{job_id}/candidates/{candidate_id}/generate-sync", response_model=ScreeningTestResponse)
async def generate_test_sync(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    user: User = Depends(require_permission("screening:write")),
    db: AsyncSession = Depends(get_db),
):
    test_id = await create_test_for_candidate(job_id, candidate_id)
    test = (await db.execute(select(ScreeningTest).where(ScreeningTest.id == test_id))).scalar_one()
    await log_audit(db, user.id, "screening_test", str(test_id), "generated")
    return ScreeningTestResponse.model_validate(test)


@router.post("/tests/{test_id}/assign")
async def assign_test_endpoint(
    test_id: uuid.UUID,
    user: User = Depends(require_permission("screening:write")),
    db: AsyncSession = Depends(get_db),
):
    test = await assign_test(test_id)
    await log_audit(db, user.id, "screening_test", str(test_id), "assigned")
    return ScreeningTestResponse.model_validate(test)


@router.get("/tests/{test_id}")
async def get_test(
    test_id: uuid.UUID,
    user: User = Depends(require_permission("screening:read")),
    db: AsyncSession = Depends(get_db),
):
    test = (await db.execute(select(ScreeningTest).where(ScreeningTest.id == test_id))).scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    candidate = (await db.execute(select(Candidate).where(Candidate.id == test.candidate_id))).scalar_one_or_none()
    return {
        **ScreeningTestResponse.model_validate(test).model_dump(),
        "candidate_name": candidate.name if candidate else None,
        "analytics": test.analytics,
        "assigned_status": test.assigned_status,
    }


@router.post("/tests/{test_id}/submit", response_model=ScreeningTestResponse)
async def submit_test_endpoint(
    test_id: uuid.UUID,
    data: TestSubmission,
    user: User = Depends(require_permission("screening:write")),
    db: AsyncSession = Depends(get_db),
):
    test = await submit_test(test_id, data.responses)
    await log_audit(db, user.id, "screening_test", str(test_id), "submitted", after_data=test.analytics)
    return ScreeningTestResponse.model_validate(test)
