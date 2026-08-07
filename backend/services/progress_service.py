import json
import redis
from datetime import datetime
from typing import Optional
from backend.config import get_settings

settings = get_settings()
_redis: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def progress_key(task_id: str) -> str:
    return f"progress:{task_id}"


def update_progress(
    task_id: str,
    task_type: str,
    status: str,
    current_step: str,
    progress_pct: float,
    message: str = "",
    eta_seconds: Optional[int] = None,
    job_id: Optional[str] = None,
    user_id: Optional[str] = None,
    error: Optional[str] = None,
    meta: Optional[dict] = None,
) -> dict:
    payload = {
        "task_id": task_id,
        "task_type": task_type,
        "status": status,
        "current_step": current_step,
        "progress_pct": round(progress_pct, 2),
        "message": message,
        "eta_seconds": eta_seconds,
        "job_id": job_id,
        "user_id": user_id,
        "error": error,
        "meta": meta or {},
        "updated_at": datetime.utcnow().isoformat(),
    }
    r = get_redis()
    r.setex(progress_key(task_id), 86400, json.dumps(payload))
    r.publish(f"progress_channel:{task_id}", json.dumps(payload))
    return payload


def get_progress(task_id: str) -> Optional[dict]:
    raw = get_redis().get(progress_key(task_id))
    return json.loads(raw) if raw else None
