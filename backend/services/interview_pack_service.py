"""Interview pack service — wraps existing AI screening module."""

import uuid
from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models import Job, Candidate, Ranking, InterviewPack
from ai.engines.screening import generate_interview_pack


async def create_pack_for_candidate(job_id: uuid.UUID, candidate_id: uuid.UUID) -> uuid.UUID:
    async with AsyncSessionLocal() as db:
        job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
        candidate = (await db.execute(select(Candidate).where(Candidate.id == candidate_id))).scalar_one_or_none()
        ranking = (await db.execute(
            select(Ranking).where(Ranking.candidate_id == candidate_id, Ranking.job_id == job_id)
            .order_by(Ranking.created_at.desc())
        )).scalar_one_or_none()
        if not job or not candidate:
            raise ValueError("Job or candidate not found")

        ranking_data = {
            "missing_skills": ranking.missing_requirements if ranking else [],
            "matched_skills": ranking.strengths if ranking else [],
        }
        pack_data = await generate_interview_pack(
            job.parsed_data or {},
            candidate.parsed_data or {},
            ranking_data,
        )

        red_flags = (ranking.weaknesses or [])[:5] if ranking else []
        objectives = [
            "Validate technical depth for top matched skills",
            "Probe gaps in missing requirements",
            "Assess culture and communication fit",
        ]

        pack = InterviewPack(
            job_id=job_id,
            candidate_id=candidate_id,
            technical_questions=pack_data.get("technical_questions", []),
            behavioral_questions=pack_data.get("behavioral_questions", []),
            follow_up_questions=pack_data.get("follow_up_questions", []),
            gap_questions=pack_data.get("gap_questions", []),
            red_flags=red_flags,
            interview_objectives=objectives,
        )
        db.add(pack)
        await db.commit()
        return pack.id
