import uuid
from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models import Job, Ranking, Candidate
from backend.services.export_service import export_shortlist


async def run_export(job_id: uuid.UUID, export_format: str) -> dict:
    async with AsyncSessionLocal() as db:
        job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
        if not job:
            raise ValueError("Job not found")

        from backend.models import RankingRun
        run = (await db.execute(
            select(RankingRun).where(RankingRun.job_id == job_id, RankingRun.is_current == True)
        )).scalar_one_or_none()

        q = select(Ranking, Candidate).join(Candidate, Ranking.candidate_id == Candidate.id).where(Ranking.job_id == job_id)
        if run:
            q = q.where(Ranking.ranking_run_id == run.id)
        rows = (await db.execute(q.order_by(Ranking.rank.asc().nullslast()))).all()

        export_data = []
        for ranking, candidate in rows:
            export_data.append({**{k: getattr(ranking, k) for k in ranking.__table__.columns.keys()}, "candidate_name": candidate.name})

        content, mime, filename = export_shortlist(export_data, {"id": job.id, "title": job.title}, export_format)
        import base64
        return {"filename": filename, "mime": mime, "content_base64": base64.b64encode(content).decode()}
