"""Screening test service — wraps existing AI screening module."""

import uuid
from sqlalchemy import select
from backend.database import AsyncSessionLocal
from backend.models import Job, Candidate, ScreeningTest, Ranking
from ai.engines.screening import generate_screening_test, grade_test_responses


async def create_test_for_candidate(job_id: uuid.UUID, candidate_id: uuid.UUID) -> uuid.UUID:
    async with AsyncSessionLocal() as db:
        job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
        candidate = (await db.execute(select(Candidate).where(Candidate.id == candidate_id))).scalar_one_or_none()
        if not job or not candidate:
            raise ValueError("Job or candidate not found")

        questions = await generate_screening_test(
            job.parsed_data or {},
            candidate.parsed_data or {},
            (job.parsed_data or {}).get("seniority", "mid"),
        )
        test = ScreeningTest(
            job_id=job_id,
            candidate_id=candidate_id,
            questions=questions,
            status="pending",
            assigned_status="draft",
        )
        db.add(test)
        await db.commit()
        return test.id


async def assign_test(test_id: uuid.UUID) -> ScreeningTest:
    async with AsyncSessionLocal() as db:
        test = (await db.execute(select(ScreeningTest).where(ScreeningTest.id == test_id))).scalar_one_or_none()
        if not test:
            raise ValueError("Test not found")
        test.assigned_status = "assigned"
        await db.commit()
        return test


async def submit_test(test_id: uuid.UUID, responses: list[dict]) -> ScreeningTest:
    async with AsyncSessionLocal() as db:
        test = (await db.execute(select(ScreeningTest).where(ScreeningTest.id == test_id))).scalar_one_or_none()
        if not test:
            raise ValueError("Test not found")

        graded = await grade_test_responses(test.questions, responses)
        test.responses = responses
        test.test_score = graded["test_score"]
        test.verification_score = graded["verification_score"]
        test.status = "completed"
        test.assigned_status = "completed"
        from datetime import datetime
        test.completed_at = datetime.utcnow()
        threshold = float(test.pass_threshold or 0.6)
        test.analytics = {
            "passed": graded["test_score"] >= threshold,
            "pass_threshold": threshold,
            "question_breakdown": graded.get("graded", []),
            "total_questions": len(test.questions),
            "answered": len(responses),
        }
        await db.commit()
        return test


async def get_job_test_analytics(job_id: uuid.UUID) -> dict:
    async with AsyncSessionLocal() as db:
        tests = (await db.execute(select(ScreeningTest).where(ScreeningTest.job_id == job_id))).scalars().all()
        completed = [t for t in tests if t.status == "completed"]
        passed = sum(1 for t in completed if (t.analytics or {}).get("passed"))
        return {
            "total_tests": len(tests),
            "assigned": sum(1 for t in tests if t.assigned_status == "assigned"),
            "completed": len(completed),
            "passed": passed,
            "failed": len(completed) - passed,
            "avg_score": round(sum(float(t.test_score or 0) for t in completed) / max(len(completed), 1), 3),
        }
