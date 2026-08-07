import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from backend.database import get_db
from backend.models import User, Job, RecruiterOverride, AnalyticsEvent
from backend.schemas import (
    JobCreate, JobUpdate, JobResponse,
    RecruiterOverrideCreate, RecruiterOverrideResponse,
)
from backend.services.auth_service import get_current_user
from backend.services.document_parser import parse_document, save_upload
from backend.services.llm_service import parse_job_description

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Job).where(Job.user_id == user.id).order_by(Job.created_at.desc())
    )
    return [JobResponse.model_validate(j) for j in result.scalars().all()]


@router.post("", response_model=JobResponse)
async def create_job(
    data: JobCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = Job(user_id=user.id, title=data.title, description=data.description, status="draft")
    if data.text:
        job.raw_text = data.text
        parsed = await parse_job_description(data.text)
        job.parsed_data = parsed
        job.ideal_profile = parsed.get("ideal_candidate_profile", {})
        job.borderline_profile = parsed.get("borderline_candidate_profile", {})
        job.high_risk_profile = parsed.get("high_risk_candidate_profile", {})
        job.hidden_requirements = parsed.get("hidden_requirements", [])
        job.status = "parsed"
    db.add(job)
    await db.flush()

    override = RecruiterOverride(job_id=job.id)
    db.add(override)
    await db.flush()

    db.add(AnalyticsEvent(user_id=user.id, job_id=job.id, event_type="job_created"))
    return JobResponse.model_validate(job)


@router.post("/upload", response_model=JobResponse)
async def upload_job(
    title: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "txt"
    file_path = await save_upload(content, file.filename or "job.txt", "jobs")
    raw_text = await parse_document(file_path, ext)
    parsed = await parse_job_description(raw_text)

    job = Job(
        user_id=user.id,
        title=title,
        description=raw_text[:2000],
        raw_text=raw_text,
        file_path=file_path,
        file_type=ext,
        parsed_data=parsed,
        ideal_profile=parsed.get("ideal_candidate_profile", {}),
        borderline_profile=parsed.get("borderline_candidate_profile", {}),
        high_risk_profile=parsed.get("high_risk_candidate_profile", {}),
        hidden_requirements=parsed.get("hidden_requirements", []),
        status="parsed",
    )
    db.add(job)
    await db.flush()
    override = RecruiterOverride(
        job_id=job.id,
        required_skills=[s.get("name", s) if isinstance(s, dict) else s for s in parsed.get("required_skills", [])],
        nice_to_have_skills=[s.get("name", s) if isinstance(s, dict) else s for s in parsed.get("nice_to_have_skills", [])],
        min_years_experience=parsed.get("experience_years_min", 0),
        education_requirements=parsed.get("education_requirements", []),
        certifications=parsed.get("certifications", []),
    )
    db.add(override)
    await db.flush()
    return JobResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    data: JobUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    return JobResponse.model_validate(job)


@router.delete("/{job_id}")
async def delete_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
    return {"message": "Job deleted"}


@router.get("/{job_id}/override", response_model=RecruiterOverrideResponse)
async def get_override(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RecruiterOverride).where(RecruiterOverride.job_id == job_id))
    override = result.scalar_one_or_none()
    if not override:
        raise HTTPException(status_code=404, detail="Override not found")
    return RecruiterOverrideResponse.model_validate(override)


@router.put("/{job_id}/override", response_model=RecruiterOverrideResponse)
async def update_override(
    job_id: uuid.UUID,
    data: RecruiterOverrideCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RecruiterOverride).where(RecruiterOverride.job_id == job_id))
    override = result.scalar_one_or_none()
    if not override:
        override = RecruiterOverride(job_id=job_id)
        db.add(override)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(override, field, value)
    await db.flush()
    return RecruiterOverrideResponse.model_validate(override)
