"""AI Screening Test Generator & Skill Claim Verification."""

import json
from backend.services.llm_service import llm_provider, extract_json_from_response

SKILL_VERIFICATION_QUESTIONS = {
    "react": [
        {"question": "Explain how the React virtual DOM works and why it improves performance.", "type": "technical", "difficulty": "mid"},
        {"question": "What is the difference between useState and useReducer?", "type": "technical", "difficulty": "mid"},
    ],
    "python": [
        {"question": "Explain the difference between a list and a tuple in Python.", "type": "technical", "difficulty": "junior"},
        {"question": "How does Python's GIL affect multithreading?", "type": "technical", "difficulty": "senior"},
    ],
    "docker": [
        {"question": "Explain the Docker container lifecycle from create to remove.", "type": "technical", "difficulty": "mid"},
        {"question": "What is the difference between a Docker image and a container?", "type": "technical", "difficulty": "junior"},
    ],
    "kubernetes": [
        {"question": "Explain how a Kubernetes Deployment ensures high availability.", "type": "architecture", "difficulty": "senior"},
    ],
    "aws": [
        {"question": "Describe when you would use S3 vs EBS vs EFS.", "type": "scenario", "difficulty": "mid"},
    ],
    "machine learning": [
        {"question": "Explain the bias-variance tradeoff with a practical example.", "type": "technical", "difficulty": "senior"},
    ],
    "fastapi": [
        {"question": "How does FastAPI leverage Python type hints for validation?", "type": "technical", "difficulty": "mid"},
    ],
}

BEHAVIORAL_TEMPLATES = [
    {"question": "Tell me about a time you had to learn a new technology quickly for a project.", "type": "behavioral"},
    {"question": "Describe a situation where you disagreed with a technical decision. How did you handle it?", "type": "behavioral"},
    {"question": "Give an example of when you mentored a junior team member.", "type": "behavioral"},
    {"question": "Describe a project where you had to balance speed with quality.", "type": "behavioral"},
]


async def generate_screening_test(job_requirements: dict, parsed_resume: dict, seniority: str = "mid") -> list[dict]:
    required_skills = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in job_requirements.get("required_skills", [])
    ][:8]

    questions = []
    for skill in required_skills:
        skill_lower = skill.lower()
        if skill_lower in SKILL_VERIFICATION_QUESTIONS:
            for q in SKILL_VERIFICATION_QUESTIONS[skill_lower]:
                if _difficulty_matches(q["difficulty"], seniority):
                    questions.append({**q, "skill": skill, "id": f"q_{len(questions)}"})
        else:
            questions.append({
                "id": f"q_{len(questions)}",
                "question": f"Describe your experience with {skill} and a project where you applied it.",
                "type": "scenario",
                "difficulty": seniority,
                "skill": skill,
            })

    questions.extend(BEHAVIORAL_TEMPLATES[:2])

    if seniority in ("senior", "lead", "principal"):
        questions.append({
            "id": f"q_{len(questions)}",
            "question": "Design a scalable system for processing 1M resumes per day. Walk through your architecture.",
            "type": "architecture",
            "difficulty": "senior",
            "skill": "system design",
        })

    return questions[:15]


def _difficulty_matches(q_diff: str, seniority: str) -> bool:
    levels = {"junior": 1, "mid": 2, "senior": 3, "lead": 4, "principal": 5}
    return levels.get(q_diff, 2) <= levels.get(seniority, 2) + 1


async def grade_test_responses(questions: list[dict], responses: list[dict]) -> dict:
    total = len(questions)
    if total == 0:
        return {"test_score": 0.5, "verification_score": 0.5, "graded": []}

    graded = []
    correct = 0
    for q in questions:
        qid = q.get("id")
        response = next((r for r in responses if r.get("question_id") == qid), None)
        answer = response.get("answer", "") if response else ""
        score = min(1.0, len(answer.split()) / 30) if answer else 0.0
        if len(answer) > 100:
            score = min(1.0, score + 0.2)
        graded.append({
            "question_id": qid,
            "question": q.get("question"),
            "answer": answer,
            "score": round(score, 2),
            "skill": q.get("skill"),
        })
        correct += score

    test_score = correct / total
    verification_score = test_score * 0.9 + 0.1
    return {
        "test_score": round(test_score, 4),
        "verification_score": round(verification_score, 4),
        "graded": graded,
    }


async def generate_interview_pack(
    job_requirements: dict,
    parsed_resume: dict,
    ranking_data: dict,
) -> dict:
    seniority = job_requirements.get("seniority", "mid")
    missing = ranking_data.get("missing_skills", ranking_data.get("must_have_missing", []))
    strengths = ranking_data.get("matched_skills", [])[:5]

    technical = []
    for skill in strengths[:5]:
        skill_lower = skill.lower() if isinstance(skill, str) else str(skill).lower()
        if skill_lower in SKILL_VERIFICATION_QUESTIONS:
            technical.extend(SKILL_VERIFICATION_QUESTIONS[skill_lower][:1])
        else:
            technical.append({
                "question": f"Walk me through your most significant project using {skill}.",
                "type": "technical",
                "skill": skill,
            })

    gap_questions = [
        {"question": f"Your resume doesn't show direct experience with {skill}. How would you approach learning it?", "type": "gap", "skill": skill}
        for skill in missing[:5]
    ]

    follow_ups = [
        {"question": "Can you elaborate on the scale and impact of that project?", "type": "follow_up"},
        {"question": "What would you do differently if you rebuilt it today?", "type": "follow_up"},
        {"question": "How did you handle technical disagreements on the team?", "type": "follow_up"},
    ]

    return {
        "technical_questions": technical[:8],
        "behavioral_questions": BEHAVIORAL_TEMPLATES[:5],
        "follow_up_questions": follow_ups,
        "gap_questions": gap_questions,
    }


async def generate_verification_questions(priority_skills: list[str]) -> list[dict]:
    questions = []
    for skill in priority_skills[:10]:
        skill_lower = skill.lower()
        if skill_lower in SKILL_VERIFICATION_QUESTIONS:
            questions.extend([{**q, "skill": skill} for q in SKILL_VERIFICATION_QUESTIONS[skill_lower][:2]])
        else:
            questions.append({
                "question": f"Explain a real-world scenario where you used {skill}.",
                "type": "verification",
                "skill": skill,
            })
    return questions
