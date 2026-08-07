import os
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from backend.config import get_settings
from backend.services.auth_service import get_current_user
from backend.services.file_security import verify_signed_url, decrypt_file_content
from backend.models import User

router = APIRouter(prefix="/files", tags=["Files"])
settings = get_settings()


@router.get("/download")
async def download_file(
    path: str = Query(...),
    expires: int = Query(...),
    sig: str = Query(...),
    uid: str = Query(...),
):
    if not verify_signed_url(path, uid, expires, sig):
        raise HTTPException(status_code=403, detail="Invalid or expired download link")

    full_path = os.path.join(settings.upload_dir, path.lstrip("/"))
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(full_path, "rb") as f:
        content = decrypt_file_content(f.read())

    filename = os.path.basename(path)
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/signed-url")
async def get_signed_url(
    path: str = Query(...),
    user: User = Depends(get_current_user),
):
    from backend.services.file_security import generate_signed_download_url
    return {"url": generate_signed_download_url(path, str(user.id))}
