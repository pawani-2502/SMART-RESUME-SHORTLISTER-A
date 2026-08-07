import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db, AsyncSessionLocal
from backend.models import User, Job, Candidate, BatchJob, ResumeChecksum
from backend.services.dedup_service import compute_checksum, detect_duplicate
from backend.services.audit_service import log_audit
from ai.engines.knowledge_graph import build_knowledge_graph, flatten_for_storage
from backend.models import KnowledgeNode
from backend.schemas import CandidateResponse, BatchJobResponse
from backend.services.auth_service import get_current_user
from backend.services.document_parser import parse_document, save_upload
from backend.services.file_security import validate_upload
from backend.services.llm_service import parse_resume
from backend.services.batch_service import process_batch_resumes
from ai.engines.career_trajectory import analyze_career_trajectory
from ai.engines.skill_graph import build_skill_graph
from ai.engines.credibility import detect_credibility_issues, create_blind_profile

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("/job/{job_id}", response_model=list[CandidateResponse])
async def list_candidates(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Candidate).where(Candidate.job_id == job_id).order_by(Candidate.created_at.desc())
    )
    return [CandidateResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/job/{job_id}/upload", response_model=CandidateResponse)
async def upload_resume(
    job_id: uuid.UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    if not job_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    content = await file.read()
    from backend.services.file_security import validate_upload, scan_file_hook, encrypt_file_content
    valid, msg = validate_upload(file.filename or "resume.txt", content)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "txt"
    # Parse from original content; store encrypted copy
    import tempfile, os as _os
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        raw_text = await parse_document(tmp_path, ext)
    finally:
        _os.unlink(tmp_path)

    encrypted = encrypt_file_content(content)
    file_path = await save_upload(encrypted, file.filename or "resume.txt", f"resumes/{job_id}")
    scan_file_hook(file_path)

    existing_result = await db.execute(
        select(Candidate).where(Candidate.job_id == job_id)
    )
    existing = existing_result.scalars().all()
    existing_for_dedup = [
        {
            "candidate_id": str(c.id),
            "checksum": compute_checksum(c.raw_text or ""),
            "text": c.raw_text or "",
        }
        for c in existing
    ]
    dup = detect_duplicate(raw_text, existing_for_dedup)
    if dup:
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate resume detected ({dup['type']}, similarity={dup.get('similarity', 1.0)})",
        )

    parsed = await parse_resume(raw_text)

    seniority = "mid"
    career_metrics = analyze_career_trajectory(parsed, seniority)
    skill_graph = build_skill_graph([
        s.get("name", s) if isinstance(s, dict) else s for s in parsed.get("skills", [])
    ])
    credibility = detect_credibility_issues(parsed)

    candidate = Candidate(
        job_id=job_id,
        name=parsed.get("name"),
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        location=parsed.get("location"),
        file_path=file_path,
        file_type=ext,
        raw_text=raw_text,
        parsed_data=parsed,
        normalized_profile=parsed,
        career_metrics=career_metrics,
        skill_graph=skill_graph,
        credibility=credibility,
        blind_profile=create_blind_profile(parsed),
        status="parsed",
    )
    db.add(candidate)
    await db.flush()

    checksum = compute_checksum(raw_text)
    db.add(ResumeChecksum(
        job_id=job_id, candidate_id=candidate.id, checksum_sha256=checksum,
    ))

    kg = build_knowledge_graph(parsed)
    for node in flatten_for_storage(kg):
        db.add(KnowledgeNode(
            candidate_id=candidate.id,
            node_type=node["node_type"],
            label=node["label"],
            properties=node.get("properties", {}),
        ))

    await log_audit(db, user.id, "candidate", str(candidate.id), "uploaded", after_data={
        "name": candidate.name, "job_id": str(job_id),
    })

    return CandidateResponse.model_validate(candidate)


@router.post("/job/{job_id}/batch", response_model=BatchJobResponse)
async def batch_upload(
    job_id: uuid.UUID,
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user.id))
    if not job_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")

    batch = BatchJob(job_id=job_id, user_id=user.id, total_files=len(files))
    db.add(batch)
    await db.flush()

    file_data = []
    for f in files:
        content = await f.read()
        valid, msg = validate_upload(f.filename or "resume.txt", content)
        if not valid:
            continue
        file_data.append({"content": content, "filename": f.filename or "resume.txt"})

    from backend.workers.tasks import parse_resume_batch
    task = parse_resume_batch.delay(str(batch.id), str(job_id), file_data)
    await log_audit(db, user.id, "batch_job", str(batch.id), "queued", after_data={"task_id": task.id})

    response = BatchJobResponse.model_validate(batch)
    return {"batch": response, "task_id": task.id}


@router.get("/batch/{batch_id}", response_model=BatchJobResponse)
async def get_batch_status(
    batch_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BatchJob).where(BatchJob.id == batch_id, BatchJob.user_id == user.id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch job not found")
    return BatchJobResponse.model_validate(batch)


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateResponse.model_validate(candidate)


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    await db.delete(candidate)
    return {"message": "Candidate deleted"}
