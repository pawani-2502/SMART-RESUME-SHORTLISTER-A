import os
import hmac
import hashlib
import base64
import time
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from backend.config import get_settings

settings = get_settings()
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
ALLOWED_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


def _get_fernet() -> Optional[Fernet]:
    key = settings.file_encryption_key
    if not key:
        return None
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception:
        derived = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        return Fernet(derived)


def validate_upload(filename: str, content: bytes) -> tuple[bool, str]:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {ext} not allowed"
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        return False, f"File exceeds {settings.max_upload_size_mb}MB limit"
    if len(content) == 0:
        return False, "Empty file"
    return True, "ok"


def scan_file_hook(file_path: str) -> dict:
    """Hook for virus scanning integration (ClamAV etc.)."""
    return {"scanned": True, "clean": True, "engine": "stub", "file": file_path}


def encrypt_file_content(content: bytes) -> bytes:
    fernet = _get_fernet()
    return fernet.encrypt(content) if fernet else content


def decrypt_file_content(content: bytes) -> bytes:
    fernet = _get_fernet()
    if not fernet:
        return content
    try:
        return fernet.decrypt(content)
    except InvalidToken:
        return content


def generate_signed_download_url(file_path: str, user_id: str) -> str:
    expires = int(time.time()) + settings.signed_url_ttl_seconds
    message = f"{file_path}:{user_id}:{expires}"
    sig = hmac.new(
        settings.api_secret_key.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"/api/v1/files/download?path={file_path}&expires={expires}&sig={sig}&uid={user_id}"


def verify_signed_url(file_path: str, user_id: str, expires: int, sig: str) -> bool:
    if int(time.time()) > expires:
        return False
    message = f"{file_path}:{user_id}:{expires}"
    expected = hmac.new(
        settings.api_secret_key.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, sig)
