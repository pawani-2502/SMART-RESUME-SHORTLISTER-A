import uuid
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models import User, InterviewPack, Candidate, Job, Ranking
from backend.schemas import InterviewPackResponse
from backend.services.auth_service import require_permission
from backend.services.interview_pack_service import create_pack_for_candidate
from backend.services.audit_service import log_audit
from backend.workers.tasks import generate_interview_pack_task

router = APIRouter(prefix="/interview-packs", tags=["Interview Packs"])


@router.get("/jobs/{job_id}")
async def list_packs(
    job_id: uuid.UUID,
    user: User = Depends(require_permission("interviews:read")),
    db: AsyncSession = Depends(get_db),
):
    rows = (await db.execute(
        select(InterviewPack, Candidate)
        .join(Candidate, InterviewPack.candidate_id == Candidate.id)
        .where(InterviewPack.job_id == job_id)
        .order_by(InterviewPack.created_at.desc())
    )).all()
    return [
        {**InterviewPackResponse.model_validate(p).model_dump(), "candidate_name": c.name}
        for p, c in rows
    ]


@router.get("/{pack_id}")
async def get_pack(
    pack_id: uuid.UUID,
    user: User = Depends(require_permission("interviews:read")),
    db: AsyncSession = Depends(get_db),
):
    pack = (await db.execute(select(InterviewPack).where(InterviewPack.id == pack_id))).scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")
    candidate = (await db.execute(select(Candidate).where(Candidate.id == pack.candidate_id))).scalar_one_or_none()
    job = (await db.execute(select(Job).where(Job.id == pack.job_id))).scalar_one_or_none()
    ranking = (await db.execute(
        select(Ranking).where(Ranking.candidate_id == pack.candidate_id, Ranking.job_id == pack.job_id)
        .order_by(Ranking.created_at.desc())
    )).scalar_one_or_none()
    return {
        **InterviewPackResponse.model_validate(pack).model_dump(),
        "candidate_name": candidate.name if candidate else None,
        "job_title": job.title if job else None,
        "red_flags": pack.red_flags or (ranking.weaknesses[:5] if ranking else []),
        "interview_objectives": pack.interview_objectives or [],
    }


@router.post("/jobs/{job_id}/candidates/{candidate_id}/generate")
async def generate_pack_async(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    user: User = Depends(require_permission("interviews:write")),
    db: AsyncSession = Depends(get_db),
):
    task = generate_interview_pack_task.delay(str(job_id), str(candidate_id))
    await log_audit(db, user.id, "interview_pack", str(candidate_id), "generate_queued", after_data={"task_id": task.id})
    return {"task_id": task.id}


@router.post("/jobs/{job_id}/candidates/{candidate_id}/generate-sync", response_model=InterviewPackResponse)
async def generate_pack_sync(
    job_id: uuid.UUID,
    candidate_id: uuid.UUID,
    user: User = Depends(require_permission("interviews:write")),
    db: AsyncSession = Depends(get_db),
):
    pack_id = await create_pack_for_candidate(job_id, candidate_id)
    pack = (await db.execute(select(InterviewPack).where(InterviewPack.id == pack_id))).scalar_one()
    await log_audit(db, user.id, "interview_pack", str(pack_id), "generated")
    return InterviewPackResponse.model_validate(pack)


@router.get("/{pack_id}/export-pdf")
async def export_pack_pdf(
    pack_id: uuid.UUID,
    user: User = Depends(require_permission("exports:read")),
    db: AsyncSession = Depends(get_db),
):
    pack = (await db.execute(select(InterviewPack).where(InterviewPack.id == pack_id))).scalar_one_or_none()
    candidate = (await db.execute(select(Candidate).where(Candidate.id == pack.candidate_id))).scalar_one_or_none() if pack else None
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"Interview Pack: {candidate.name if candidate else 'Candidate'}", styles["Title"]),
        Paragraph("Technical Questions", styles["Heading2"]),
    ]
    for q in pack.technical_questions or []:
        elements.append(Paragraph(f"• {q.get('question', q)}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Behavioral Questions", styles["Heading2"]))
    for q in pack.behavioral_questions or []:
        elements.append(Paragraph(f"• {q.get('question', q)}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Gap-Focused Questions", styles["Heading2"]))
    for q in pack.gap_questions or []:
        elements.append(Paragraph(f"• {q.get('question', q)}", styles["Normal"]))
    doc.build(elements)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=interview-pack-{pack_id}.pdf"},
    )
