"""Seed premium demo data for Resume-Centric Smart Shortlister.

Creates 4 demo jobs with 3 candidates each (strong/medium/weak tiers).
Uses static parsed data for reliability — no LLM API required.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from backend.database import AsyncSessionLocal, engine, Base
from backend.models import User, Job, RecruiterOverride, Candidate, Ranking, InterviewSimulation, ScreeningTest, InterviewPack
from backend.services.auth_service import get_password_hash
from ai.engines.career_trajectory import analyze_career_trajectory
from ai.engines.skill_graph import build_skill_graph
from ai.engines.credibility import detect_credibility_issues, create_blind_profile

DEMO_JOBS = [
    {
        "title": "Senior Full Stack Developer (Demo)",
        "description": "Build scalable web applications with Python, React, TypeScript, and AWS. Mentor engineers and own features end-to-end.",
        "parsed_data": {
            "seniority": "senior",
            "experience_years_min": 5,
            "required_skills": [{"name": "Python"}, {"name": "React"}, {"name": "TypeScript"}, {"name": "PostgreSQL"}, {"name": "AWS"}],
            "nice_to_have_skills": [{"name": "Docker"}, {"name": "Kubernetes"}],
        },
    },
    {
        "title": "AI Engineer (Demo)",
        "description": "Design ML pipelines, LLM integrations, and production AI systems. PyTorch, MLOps, and vector databases required.",
        "parsed_data": {
            "seniority": "senior",
            "experience_years_min": 4,
            "required_skills": [{"name": "Python"}, {"name": "PyTorch"}, {"name": "LLMs"}, {"name": "MLOps"}],
            "nice_to_have_skills": [{"name": "Vector Databases"}, {"name": "LangChain"}],
        },
    },
    {
        "title": "Data Scientist (Demo)",
        "description": "Drive data-driven decisions with statistical modeling, experimentation, and ML deployment.",
        "parsed_data": {
            "seniority": "mid",
            "experience_years_min": 3,
            "required_skills": [{"name": "Python"}, {"name": "SQL"}, {"name": "Statistics"}, {"name": "Scikit-learn"}],
            "nice_to_have_skills": [{"name": "Tableau"}, {"name": "TensorFlow"}],
        },
    },
    {
        "title": "Backend Engineer (Demo)",
        "description": "Architect high-throughput APIs, distributed systems, and data pipelines for enterprise clients.",
        "parsed_data": {
            "seniority": "senior",
            "experience_years_min": 5,
            "required_skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "PostgreSQL"}, {"name": "Redis"}, {"name": "Kafka"}],
            "nice_to_have_skills": [{"name": "Docker"}, {"name": "AWS"}],
        },
    },
]

CANDIDATE_TEMPLATES = {
    "strong": {
        "name": "Alex Johnson",
        "email": "alex.johnson@demo.com",
        "parsed_data": {
            "name": "Alex Johnson",
            "email": "alex.johnson@demo.com",
            "summary": "Senior engineer with 7 years full-stack experience. Expert in Python, React, AWS.",
            "skills": [{"name": s} for s in ["Python", "React", "TypeScript", "FastAPI", "PostgreSQL", "AWS", "Docker", "Kubernetes"]],
            "experience": [
                {"title": "Senior Software Engineer", "company": "TechCorp", "description": "Led API serving 2M+ daily requests", "achievements": ["Mentored 4 engineers", "Microservices migration -60% deploy time"]},
                {"title": "Software Engineer", "company": "StartupXYZ", "description": "Built full-stack features with Python and React"},
            ],
        },
        "scores": {"final": 0.91, "semantic": 0.94, "skill": 0.92, "trajectory": 0.88, "must_have": 0.95, "readiness": 0.89},
        "strengths": ["Full-stack Python + React", "AWS production scale", "Team leadership"],
        "weaknesses": ["Limited GraphQL experience"],
    },
    "medium": {
        "name": "Priya Sharma",
        "email": "priya.sharma@demo.com",
        "parsed_data": {
            "name": "Priya Sharma",
            "email": "priya.sharma@demo.com",
            "summary": "Full stack developer with 5 years React/Node.js focus. Growing backend skills.",
            "skills": [{"name": s} for s in ["JavaScript", "React", "Node.js", "PostgreSQL", "TypeScript", "GraphQL"]],
            "experience": [
                {"title": "Full Stack Developer", "company": "FinFlow", "description": "Built real-time trading dashboard", "achievements": ["Reduced page load 40%"]},
                {"title": "Frontend Developer", "company": "DesignHub", "description": "Component library adopted by 3 teams"},
            ],
        },
        "scores": {"final": 0.71, "semantic": 0.74, "skill": 0.68, "trajectory": 0.72, "must_have": 0.65, "readiness": 0.70},
        "strengths": ["Strong React frontend", "Startup experience", "Performance optimization"],
        "weaknesses": ["Limited Python/backend depth", "No Docker/Kubernetes"],
    },
    "weak": {
        "name": "Jordan Lee",
        "email": "jordan.lee@demo.com",
        "parsed_data": {
            "name": "Jordan Lee",
            "email": "jordan.lee@demo.com",
            "summary": "Junior developer with 2 years experience. Eager learner with limited production exposure.",
            "skills": [{"name": s} for s in ["JavaScript", "HTML", "CSS", "Basic Python", "Git"]],
            "experience": [
                {"title": "Junior Web Developer", "company": "LocalWeb Co.", "description": "Built portfolio and todo apps"},
            ],
        },
        "scores": {"final": 0.42, "semantic": 0.45, "skill": 0.38, "trajectory": 0.40, "must_have": 0.35, "readiness": 0.44},
        "strengths": ["Eager to learn", "Basic web fundamentals"],
        "weaknesses": ["Below experience threshold", "Missing must-have skills", "No production scale evidence"],
    },
}


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@shortlister.ai"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email="admin@shortlister.ai",
                password_hash=get_password_hash("admin123"),
                full_name="Admin User",
                role="admin",
                organization="Resume Shortlister",
            )
            db.add(user)
            await db.flush()
            print("Created admin user: admin@shortlister.ai / admin123")
        else:
            user.password_hash = get_password_hash("admin123")
            print("Updated admin password")

        for job_def in DEMO_JOBS:
            job_result = await db.execute(select(Job).where(Job.title == job_def["title"]))
            job = job_result.scalar_one_or_none()
            parsed = job_def["parsed_data"]

            if job:
                print(f"Job exists: {job.title}")
            else:
                job = Job(
                    user_id=user.id,
                    title=job_def["title"],
                    description=job_def["description"],
                    raw_text=job_def["description"],
                    parsed_data=parsed,
                    ideal_profile={"summary": "Strong match with production experience"},
                    borderline_profile={"summary": "Partial match, gaps in key areas"},
                    high_risk_profile={"summary": "Significant gaps vs requirements"},
                    hidden_requirements=[],
                    status="parsed",
                )
                db.add(job)
                await db.flush()

                override = RecruiterOverride(
                    job_id=job.id,
                    required_skills=[s["name"] for s in parsed.get("required_skills", [])],
                    nice_to_have_skills=[s["name"] for s in parsed.get("nice_to_have_skills", [])],
                    min_years_experience=parsed.get("experience_years_min", 3),
                )
                db.add(override)
                print(f"Created job: {job.title}")

            existing = await db.execute(select(Candidate).where(Candidate.job_id == job.id))
            if existing.scalars().first():
                print(f"  Candidates already exist for {job.title}, skipping")
                continue

            rank = 1
            for tier, template in CANDIDATE_TEMPLATES.items():
                parsed_resume = template["parsed_data"]
                career = analyze_career_trajectory(parsed_resume, parsed.get("seniority", "mid"))
                skills = [s["name"] for s in parsed_resume.get("skills", [])]

                candidate = Candidate(
                    job_id=job.id,
                    name=template["name"],
                    email=template["email"],
                    raw_text=str(parsed_resume),
                    file_type="txt",
                    parsed_data=parsed_resume,
                    normalized_profile=parsed_resume,
                    career_metrics=career,
                    skill_graph=build_skill_graph(skills),
                    credibility=detect_credibility_issues(parsed_resume),
                    blind_profile=create_blind_profile(parsed_resume),
                    status="parsed",
                )
                db.add(candidate)
                await db.flush()

                scores = template["scores"]
                ranking = Ranking(
                    job_id=job.id,
                    candidate_id=candidate.id,
                    rank=rank,
                    final_score=scores["final"],
                    semantic_fit=scores["semantic"],
                    skill_coverage=scores["skill"],
                    career_trajectory=scores["trajectory"],
                    must_have_coverage=scores["must_have"],
                    interview_readiness=scores["readiness"],
                    confidence_level="High" if tier == "strong" else "Medium" if tier == "medium" else "Low",
                    eligibility_status="eligible" if tier != "weak" else "ineligible",
                    strengths=template["strengths"],
                    weaknesses=template["weaknesses"],
                    explanation=f"{template['name']} — {tier} tier candidate with {int(scores['final']*100)}% fit score.",
                    evidence=[
                        {"claim": s, "section": "skills", "snippet": s, "confidence": 0.9}
                        for s in template["strengths"][:2]
                    ],
                )
                db.add(ranking)
                await db.flush()

                if tier == "strong":
                    db.add(InterviewSimulation(
                        job_id=job.id,
                        candidate_id=candidate.id,
                        transcript=[
                            {"role": "interviewer", "content": "Tell me about your experience building APIs at scale."},
                            {"role": "candidate", "content": "At TechCorp I led a FastAPI service handling 2M+ daily requests.", "evidence": [{"snippet": "Led API serving 2M+ daily requests"}]},
                        ],
                        readiness_score=0.89,
                        communication_score=0.85,
                        confidence_score=0.87,
                        red_flags=[],
                        strengths=template["strengths"],
                        weaknesses=template["weaknesses"],
                        follow_up_questions=[{"question": "Walk through your Kubernetes deployment strategy."}],
                    ))
                    db.add(InterviewPack(
                        job_id=job.id,
                        candidate_id=candidate.id,
                        technical_questions=[{"question": "Walk through the 2M+ RPS API architecture."}],
                        behavioral_questions=[{"question": "Tell me about mentoring junior engineers."}],
                        gap_questions=[{"question": "Limited GraphQL — how would you ramp up?"}],
                        follow_up_questions=[{"question": "Design a real-time notification system."}],
                        red_flags=[],
                        interview_objectives=["Validate system design", "Assess leadership"],
                    ))
                    db.add(ScreeningTest(
                        job_id=job.id,
                        candidate_id=candidate.id,
                        questions=[
                            {"question": "Design a REST API rate limiter using Redis.", "type": "system_design"},
                            {"question": "Explain React Server Components.", "type": "technical"},
                        ],
                        status="completed",
                        assigned_status="assigned",
                        test_score=0.92,
                        analytics={"passed": True, "time_minutes": 28},
                    ))

                print(f"  Added {tier} candidate: {template['name']} (rank #{rank})")
                rank += 1

        await db.commit()
        print("\nPremium demo seed complete!")
        print("Login: admin@shortlister.ai / admin123")
        print("4 jobs × 3 candidates with rankings, interviews, packs, and tests")


if __name__ == "__main__":
    asyncio.run(seed())
