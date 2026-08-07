"""Ranking orchestration service — persists runs without modifying AI pipeline."""

import uuid
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import AsyncSessionLocal
from backend.models import Job, Candidate, Ranking, RankingRun, RecruiterOverride
from backend.services.progress_service import update_progress
from backend.services.audit_service import log_audit
from ai.pipeline.ranking_pipeline import rank_candidates


async def execute_ranking_run(
    job_id: uuid.UUID,
    user_id: uuid.UUID,
    run_id: uuid.UUID,
    task_id: str | None = None,
) -> RankingRun:
    async with AsyncSessionLocal() as db:
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise ValueError("Job not found")

        run_result = await db.execute(select(RankingRun).where(RankingRun.id == run_id))
        run = run_result.scalar_one_or_none()
        if not run:
            raise ValueError("Ranking run not found")

        run.status = "processing"
        run.started_at = datetime.utcnow()
        await db.commit()

        if task_id:
            update_progress(task_id, "ranking", "processing", "loading_candidates", 15, "Loading candidates", str(job_id))

        candidates_result = await db.execute(select(Candidate).where(Candidate.job_id == job_id))
        candidates = candidates_result.scalars().all()

        override_result = await db.execute(select(RecruiterOverride).where(RecruiterOverride.job_id == job_id))
        override = override_result.scalar_one_or_none()
        override_dict = _override_to_dict(override)
        run.override_snapshot = override_dict

        await db.execute(
            update(RankingRun).where(RankingRun.job_id == job_id).values(is_current=False)
        )

        if task_id:
            update_progress(task_id, "ranking", "processing", "evaluating", 40, "Running AI evaluation", str(job_id))

        candidate_dicts = [
            {"id": c.id, "parsed_data": c.parsed_data, "raw_text": c.raw_text or "", "name": c.name}
            for c in candidates
        ]

        # Call existing pipeline unchanged
        results = await rank_candidates(
            candidate_dicts,
            job.parsed_data or {},
            override_dict,
            str(job_id),
            job.raw_text or job.description or "",
        )

        if task_id:
            update_progress(task_id, "ranking", "processing", "saving", 80, "Saving results", str(job_id))

        eligible_count = 0
        ineligible_count = 0
        snapshot = []

        for result in results:
            cid = uuid.UUID(result["candidate_id"])
            candidate = next((c for c in candidates if c.id == cid), None)
            if not candidate:
                continue

            if result.get("interview_simulation"):
                result.pop("interview_simulation", None)

            if result["eligibility_status"] == "eligible":
                eligible_count += 1
            else:
                ineligible_count += 1

            ranking = Ranking(
                job_id=job_id,
                ranking_run_id=run_id,
                candidate_id=cid,
                rank=result.get("rank"),
                final_score=result.get("final_score"),
                score_breakdown=result.get("score_breakdown", {}),
                semantic_fit=result.get("semantic_fit"),
                skill_coverage=result.get("skill_coverage"),
                career_trajectory=result.get("career_trajectory"),
                must_have_coverage=result.get("must_have_coverage"),
                reciprocal_fit=result.get("reciprocal_fit"),
                interview_readiness=result.get("interview_readiness"),
                verification_score=result.get("verification_score"),
                leadership_score=result.get("leadership_score"),
                domain_experience=result.get("domain_experience"),
                credibility_penalty=result.get("credibility_penalty"),
                confidence_score=result.get("confidence_score"),
                confidence_level=result.get("confidence_level"),
                eligibility_status=result.get("eligibility_status", "eligible"),
                ineligibility_reasons=result.get("ineligibility_reasons", []),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                missing_requirements=result.get("missing_requirements", []),
                evidence=result.get("evidence", []),
                human_review_required=result.get("human_review_required", False),
                human_review_reasons=result.get("human_review_reasons", []),
                bias_audit=result.get("bias_audit", {}),
                explanation=result.get("explanation"),
            )
            db.add(ranking)

            snapshot.append({
                "candidate_id": str(cid),
                "candidate_name": candidate.name,
                "rank": result.get("rank"),
                "final_score": result.get("final_score"),
                "eligibility_status": result.get("eligibility_status"),
            })

            if result.get("career_metrics"):
                candidate.career_metrics = result["career_metrics"]
            if result.get("skill_graph"):
                candidate.skill_graph = result["skill_graph"]
            if result.get("credibility"):
                candidate.credibility = result["credibility"]

        scores = [s["final_score"] for s in snapshot if s.get("final_score") is not None]
        run.rankings_snapshot = snapshot
        run.summary_stats = {
            "avg_score": round(sum(scores) / len(scores), 4) if scores else 0,
            "top_score": max(scores) if scores else 0,
            "eligible_count": eligible_count,
            "ineligible_count": ineligible_count,
        }
        run.candidate_count = len(candidates)
        run.eligible_count = eligible_count
        run.ineligible_count = ineligible_count
        run.status = "completed"
        run.is_current = True
        run.completed_at = datetime.utcnow()
        job.status = "ranked"

        await log_audit(db, user_id, "ranking_run", str(run_id), "completed", after_data=run.summary_stats)
        await db.commit()
        return run


def _override_to_dict(override: RecruiterOverride | None) -> dict:
    if not override:
        return {}
    return {
        "required_skills": override.required_skills,
        "nice_to_have_skills": override.nice_to_have_skills,
        "certifications": override.certifications,
        "education_requirements": override.education_requirements,
        "min_years_experience": float(override.min_years_experience or 0),
        "location_requirements": override.location_requirements,
        "weights": override.weights,
        "knockout_filters": override.knockout_filters,
        "priority_skills": override.priority_skills,
    }


async def compare_ranking_runs(run_id_a: uuid.UUID, run_id_b: uuid.UUID) -> dict:
    async with AsyncSessionLocal() as db:
        a = (await db.execute(select(RankingRun).where(RankingRun.id == run_id_a))).scalar_one_or_none()
        b = (await db.execute(select(RankingRun).where(RankingRun.id == run_id_b))).scalar_one_or_none()
        if not a or not b:
            raise ValueError("Run not found")

        map_a = {r["candidate_id"]: r for r in (a.rankings_snapshot or [])}
        map_b = {r["candidate_id"]: r for r in (b.rankings_snapshot or [])}
        diffs = []
        for cid, ra in map_a.items():
            rb = map_b.get(cid)
            if rb:
                score_delta = (ra.get("final_score") or 0) - (rb.get("final_score") or 0)
                rank_delta = (ra.get("rank") or 0) - (rb.get("rank") or 0)
                if abs(score_delta) > 0.01 or rank_delta != 0:
                    diffs.append({
                        "candidate_id": cid,
                        "candidate_name": ra.get("candidate_name"),
                        "score_a": ra.get("final_score"),
                        "score_b": rb.get("final_score"),
                        "score_delta": round(score_delta, 4),
                        "rank_a": ra.get("rank"),
                        "rank_b": rb.get("rank"),
                        "rank_delta": rank_delta,
                    })
        moved_up = sum(1 for d in diffs if d["rank_delta"] < 0)
        moved_down = sum(1 for d in diffs if d["rank_delta"] > 0)
        avg_delta = round(sum(d["score_delta"] for d in diffs) / max(len(diffs), 1), 4)
        all_ids = set(map_a.keys()) | set(map_b.keys())
        rank_changes = []
        for cid in all_ids:
            ra = map_a.get(cid, {})
            rb = map_b.get(cid, {})
            rank_changes.append({
                "candidate_id": cid,
                "candidate_name": ra.get("candidate_name") or rb.get("candidate_name"),
                "rank_a": ra.get("rank"),
                "rank_b": rb.get("rank"),
                "rank_delta": (ra.get("rank") or 0) - (rb.get("rank") or 0),
                "score_a": ra.get("final_score"),
                "score_b": rb.get("final_score"),
                "score_delta": round((ra.get("final_score") or 0) - (rb.get("final_score") or 0), 4),
            })
        rank_changes.sort(key=lambda x: abs(x.get("rank_delta") or 0), reverse=True)

        return {
            "run_a": {
                "id": str(a.id),
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "summary_stats": a.summary_stats,
            },
            "run_b": {
                "id": str(b.id),
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "summary_stats": b.summary_stats,
            },
            "rank_changes": rank_changes,
            "diffs": sorted(diffs, key=lambda x: abs(x["score_delta"]), reverse=True),
            "summary": {
                "candidates_moved_up": moved_up,
                "candidates_moved_down": moved_down,
                "avg_score_delta": avg_delta,
            },
        }
