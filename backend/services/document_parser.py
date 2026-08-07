import re
import os
from pathlib import Path
from typing import Optional
import aiofiles
from pypdf import PdfReader
from docx import Document
from backend.config import get_settings

settings = get_settings()


async def save_upload(file_content: bytes, filename: str, subdir: str) -> str:
    upload_path = Path(settings.upload_dir) / subdir
    upload_path.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w\-.]", "_", filename)
    file_path = upload_path / safe_name
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)
    return str(file_path)


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


async def parse_document(file_path: str, file_type: str) -> str:
    ext = file_type.lower().lstrip(".")
    if ext == "pdf":
        return extract_text_from_pdf(file_path)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(file_path)
    elif ext == "txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
