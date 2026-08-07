"""Audit trail service."""

import uuid
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import AuditLog


async def log_audit(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    entity_type: str,
    entity_id: Optional[str],
    action: str,
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before_data=before_data,
        after_data=after_data,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.flush()
    return entry
