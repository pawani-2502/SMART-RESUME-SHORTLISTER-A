import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from backend.config import get_settings
from backend.services.auth_service import get_current_user, ALGORITHM
from backend.services.progress_service import get_progress, get_redis
from backend.models import User

router = APIRouter(prefix="/progress", tags=["Progress"])
settings = get_settings()
security = HTTPBearer(auto_error=False)


async def _resolve_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    token: str | None = Query(None),
) -> User:
    from backend.database import AsyncSessionLocal
    from sqlalchemy import select
    from backend.models import User as UserModel

    raw = credentials.credentials if credentials else token
    if not raw:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(raw, settings.api_secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(UserModel).where(UserModel.id == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


@router.get("/{task_id}")
async def get_task_progress(task_id: str, user: User = Depends(_resolve_user)):
    progress = get_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return progress


@router.get("/{task_id}/stream")
async def stream_progress(
    task_id: str,
    token: str | None = Query(None),
    user: User = Depends(_resolve_user),
):
    from sse_starlette.sse import EventSourceResponse
    async def event_generator():
        r = get_redis()
        pubsub = r.pubsub()
        pubsub.subscribe(f"progress_channel:{task_id}")
        existing = get_progress(task_id)
        if existing:
            yield {"event": "progress", "data": json.dumps(existing)}
            if existing.get("status") in ("completed", "failed"):
                return

        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                data = message["data"]
                yield {"event": "progress", "data": data}
                parsed = json.loads(data)
                if parsed.get("status") in ("completed", "failed"):
                    break
            else:
                await asyncio.sleep(0.5)
                current = get_progress(task_id)
                if current and current.get("status") in ("completed", "failed"):
                    yield {"event": "progress", "data": json.dumps(current)}
                    break

    return EventSourceResponse(event_generator())
