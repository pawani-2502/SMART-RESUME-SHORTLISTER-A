import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.database import get_db
from backend.models import User, Job, Candidate, Ranking, AnalyticsEvent
from backend.schemas import AnalyticsDashboard
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_dashboard(
    job_id: uuid.UUID | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    jobs_q = select(func.count(Job.id)).where(Job.user_id == user.id)
    if job_id:
        jobs_q = jobs_q.where(Job.id == job_id)
    total_jobs = (await db.execute(jobs_q)).scalar() or 0

    candidates_q = select(func.count(Candidate.id))
    if job_id:
        candidates_q = candidates_q.where(Candidate.job_id == job_id)
    else:
        job_ids = select(Job.id).where(Job.user_id == user.id)
        candidates_q = candidates_q.where(Candidate.job_id.in_(job_ids))
    total_candidates = (await db.execute(candidates_q)).scalar() or 0

    rankings_q = select(func.count(Ranking.id), func.avg(Ranking.final_score))
    if job_id:
        rankings_q = rankings_q.where(Ranking.job_id == job_id)
    rank_result = await db.execute(rankings_q)
    row = rank_result.one()
    total_rankings = row[0] or 0
    avg_score = float(row[1] or 0)

    eligible_q = select(func.count(Ranking.id)).where(Ranking.eligibility_status == "eligible")
    review_q = select(func.count(Ranking.id)).where(Ranking.human_review_required == True)
    if job_id:
        eligible_q = eligible_q.where(Ranking.job_id == job_id)
        review_q = review_q.where(Ranking.job_id == job_id)
    eligible_count = (await db.execute(eligible_q)).scalar() or 0
    review_count = (await db.execute(review_q)).scalar() or 0

    score_buckets = {"0-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0}
    rankings_all_q = select(Ranking.final_score, Ranking.eligibility_status)
    if job_id:
        rankings_all_q = rankings_all_q.where(Ranking.job_id == job_id)
    all_rankings = (await db.execute(rankings_all_q)).all()
    for score, status in all_rankings:
        if status != "eligible" or score is None:
            continue
        s = float(score)
        if s < 0.4:
            score_buckets["0-40%"] += 1
        elif s < 0.6:
            score_buckets["40-60%"] += 1
        elif s < 0.8:
            score_buckets["60-80%"] += 1
        else:
            score_buckets["80-100%"] += 1

    exp_buckets = {"0-2 yrs": 0, "2-5 yrs": 0, "5-10 yrs": 0, "10+ yrs": 0}
    candidates_all_q = select(Candidate.career_metrics)
    if job_id:
        candidates_all_q = candidates_all_q.where(Candidate.job_id == job_id)
    for (metrics,) in (await db.execute(candidates_all_q)).all():
        years = (metrics or {}).get("total_years", 0)
        if years < 2:
            exp_buckets["0-2 yrs"] += 1
        elif years < 5:
            exp_buckets["2-5 yrs"] += 1
        elif years < 10:
            exp_buckets["5-10 yrs"] += 1
        else:
            exp_buckets["10+ yrs"] += 1

    skill_dist: dict[str, int] = {}
    candidates_skills_q = select(Candidate.parsed_data)
    if job_id:
        candidates_skills_q = candidates_skills_q.where(Candidate.job_id == job_id)
    for (parsed,) in (await db.execute(candidates_skills_q)).all():
        for s in (parsed or {}).get("skills", [])[:20]:
            name = s.get("name", s) if isinstance(s, dict) else str(s)
            skill_dist[name] = skill_dist.get(name, 0) + 1
    top_skills = sorted(skill_dist.items(), key=lambda x: x[1], reverse=True)[:15]

    return AnalyticsDashboard(
        total_jobs=total_jobs,
        total_candidates=total_candidates,
        total_rankings=total_rankings,
        avg_score=round(avg_score, 3),
        hiring_funnel={
            "uploaded": total_candidates,
            "ranked": total_rankings,
            "eligible": eligible_count,
            "needs_review": review_count,
            "shortlisted": sum(1 for s, st in all_rankings if st == "eligible" and s and float(s) >= 0.7),
        },
        skill_distribution=[{"skill": k, "count": v} for k, v in top_skills],
        score_distribution=[{"range": k, "count": v} for k, v in score_buckets.items()],
        experience_distribution=[{"range": k, "count": v} for k, v in exp_buckets.items()],
        candidate_quality={
            "avg_score": round(avg_score, 3),
            "high_quality_pct": round(
                sum(1 for s, st in all_rankings if st == "eligible" and s and float(s) >= 0.7)
                / max(total_rankings, 1) * 100, 1
            ),
        },
    )
