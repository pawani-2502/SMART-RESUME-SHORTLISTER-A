import asyncio
import uuid
from datetime import datetime
from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models import BatchJob, Candidate, Job
from backend.services.document_parser import save_upload, parse_document
from backend.services.llm_service import parse_resume
from backend.services.progress_service import update_progress
from backend.services.file_security import validate_upload, encrypt_file_content
from ai.engines.career_trajectory import analyze_career_trajectory
from ai.engines.skill_graph import build_skill_graph
from ai.engines.credibility import detect_credibility_issues, create_blind_profile
import tempfile
import os as _os


async def process_batch_resumes(
    batch_id: uuid.UUID,
    job_id: uuid.UUID,
    files: list,
    task_id: str | None = None,
):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(BatchJob).where(BatchJob.id == batch_id))
        batch = result.scalar_one_or_none()
        if not batch:
            return

        batch.status = "processing"
        batch.total_files = len(files)
        await db.commit()

        for i, item in enumerate(files):
            filename = item["filename"] if isinstance(item, dict) else item[1]
            content = item["content"] if isinstance(item, dict) else item[0]
            try:
                valid, _ = validate_upload(filename, content)
                if not valid:
                    batch.failed_files += 1
                    continue

                ext = filename.rsplit(".", 1)[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                try:
                    raw_text = await parse_document(tmp_path, ext)
                finally:
                    _os.unlink(tmp_path)

                encrypted = encrypt_file_content(content)
                file_path = await save_upload(encrypted, filename, f"resumes/{job_id}")
                parsed = await parse_resume(raw_text)
                career = analyze_career_trajectory(parsed, "mid")
                skills = [s.get("name", s) if isinstance(s, dict) else s for s in parsed.get("skills", [])]

                candidate = Candidate(
                    job_id=job_id,
                    name=parsed.get("name"),
                    email=parsed.get("email"),
                    file_path=file_path,
                    file_type=ext,
                    raw_text=raw_text,
                    parsed_data=parsed,
                    normalized_profile=parsed,
                    career_metrics=career,
                    skill_graph=build_skill_graph(skills),
                    credibility=detect_credibility_issues(parsed),
                    blind_profile=create_blind_profile(parsed),
                    status="parsed",
                )
                db.add(candidate)
                batch.processed_files += 1
            except Exception as e:
                batch.failed_files += 1
                errors = list(batch.errors or [])
                errors.append({"file": filename, "error": str(e)})
                batch.errors = errors

            batch.progress = round((i + 1) / len(files) * 100, 2)
            if task_id:
                update_progress(
                    task_id, "batch_parse", "processing", "parsing",
                    batch.progress, f"Processed {i + 1}/{len(files)}", job_id=str(job_id),
                )
            await db.commit()

        batch.status = "completed"
        batch.completed_at = datetime.utcnow()
        await db.commit()
