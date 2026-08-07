import uuid
import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel
from backend.database import get_db
from backend.models import User, AuditLog, Feedback, Ranking
from backend.services.auth_service import require_permission

router = APIRouter(prefix="/audit", tags=["Audit"])


class FeedbackCreate(BaseModel):
    ranking_id: uuid.UUID
    decision: str
    reason_codes: list[str] = []
    notes: str | None = None


@router.get("/logs")
async def list_audit_logs(
    limit: int = 100,
    action: str | None = None,
    entity_type: str | None = None,
    search: str | None = None,
    user: User = Depends(require_permission("audit:read")),
    db: AsyncSession = Depends(get_db),
):
    q = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if action:
        q = q.where(AuditLog.action == action)
    if entity_type:
        q = q.where(AuditLog.entity_type == entity_type)
    result = await db.execute(q)
    logs = result.scalars().all()

    items = [
        {
            "id": str(l.id),
            "user_id": str(l.user_id) if l.user_id else None,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "action": l.action,
            "before_data": l.before_data,
            "after_data": l.after_data,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]
    if search:
        s = search.lower()
        items = [i for i in items if s in str(i).lower()]
    return items


@router.get("/logs/export")
async def export_audit_logs(
    user: User = Depends(require_permission("audit:read")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1000))
    logs = result.scalars().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "action", "entity_type", "entity_id", "user_id", "created_at"])
    for l in logs:
        writer.writerow([str(l.id), l.action, l.entity_type, l.entity_id, l.user_id, l.created_at.isoformat()])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-logs.csv"},
    )


@router.post("/feedback")
async def submit_feedback(
    data: FeedbackCreate,
    user: User = Depends(require_permission("rankings:read")),
    db: AsyncSession = Depends(get_db),
):
    from backend.services.audit_service import log_audit
    rank_result = await db.execute(select(Ranking).where(Ranking.id == data.ranking_id))
    if not rank_result.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Ranking not found")

    feedback = Feedback(
        user_id=user.id,
        ranking_id=data.ranking_id,
        decision=data.decision,
        reason_codes=data.reason_codes,
        notes=data.notes,
    )
    db.add(feedback)
    await db.flush()
    await log_audit(db, user.id, "feedback", str(feedback.id), "created", after_data={
        "ranking_id": str(data.ranking_id), "decision": data.decision,
    })
    return {"id": str(feedback.id), "message": "Feedback recorded"}
