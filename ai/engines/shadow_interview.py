"""Shadow Interview System - Multi-agent simulation."""

from ai.engines.evidence import find_evidence_for_skill
from backend.services.llm_service import llm_provider, extract_json_from_response

INTERVIEW_QUESTIONS_BY_SENIORITY = {
    "junior": [
        "Tell me about yourself and your technical background.",
        "Describe a project you're most proud of.",
        "What technologies are you most comfortable with?",
        "How do you approach debugging a problem?",
        "Where do you see yourself in 3 years?",
    ],
    "mid": [
        "Walk me through your most impactful project and your specific contributions.",
        "How do you prioritize technical debt vs new features?",
        "Describe a time you had to collaborate with cross-functional teams.",
        "What's your approach to code review and quality?",
        "How do you stay current with technology trends?",
    ],
    "senior": [
        "Describe a system you architected end-to-end. What were the key decisions?",
        "How do you mentor junior engineers while delivering on deadlines?",
        "Tell me about a time you had to make a difficult technical tradeoff.",
        "How do you drive technical strategy across teams?",
        "Describe a production incident you led the resolution for.",
    ],
}


def _grounded_answer(question: str, parsed_resume: dict) -> tuple[str, list[dict]]:
    evidence_refs = []
    q_lower = question.lower()

    for exp in parsed_resume.get("experience", []):
        title = exp.get("title", "")
        company = exp.get("company", "")
        desc = exp.get("description", "")
        achievements = exp.get("achievements", [])

        if any(kw in q_lower for kw in ["project", "impact", "architect", "system", "proud"]):
            if desc or achievements:
                snippet = achievements[0] if achievements else desc[:200]
                evidence_refs.append({
                    "section": "experience",
                    "source": f"{title} at {company}",
                    "snippet": snippet[:300],
                })
                return (
                    f"At {company} as {title}, I worked on {desc[:150]}. "
                    f"{'Key achievement: ' + achievements[0] if achievements else ''}",
                    evidence_refs,
                )

    for skill_data in parsed_resume.get("skills", [])[:5]:
        skill = skill_data.get("name", skill_data) if isinstance(skill_data, dict) else skill_data
        if str(skill).lower() in q_lower or "technolog" in q_lower:
            ev = find_evidence_for_skill(str(skill), parsed_resume)
            if ev:
                evidence_refs.append(ev[0])
                return f"I have experience with {skill}. {ev[0]['snippet'][:200]}", evidence_refs

    if "yourself" in q_lower or "background" in q_lower:
        summary = parsed_resume.get("summary", "")
        if summary:
            evidence_refs.append({"section": "summary", "source": "resume summary", "snippet": summary[:300]})
            return summary[:300], evidence_refs

    return "Not evidenced in resume", evidence_refs


async def run_shadow_interview(
    parsed_resume: dict,
    job_requirements: dict,
    num_questions: int = 5,
) -> dict:
    seniority = job_requirements.get("seniority", "mid")
    questions = INTERVIEW_QUESTIONS_BY_SENIORITY.get(seniority, INTERVIEW_QUESTIONS_BY_SENIORITY["mid"])
    questions = questions[:num_questions]

    transcript = []
    total_evidence = 0
    red_flags = []
    strengths = []
    weaknesses = []

    for q in questions:
        answer, evidence = _grounded_answer(q, parsed_resume)
        entry = {
            "role": "interviewer",
            "content": q,
            "evidence": [],
        }
        transcript.append(entry)

        candidate_entry = {
            "role": "candidate",
            "content": answer,
            "evidence": evidence,
        }
        transcript.append(candidate_entry)

        if answer == "Not evidenced in resume":
            red_flags.append(f"Could not answer: {q[:80]}")
            weaknesses.append(f"No resume evidence for: {q[:60]}")
        else:
            total_evidence += len(evidence)
            if evidence:
                strengths.append(f"Strong evidence for: {q[:60]}")

    evidence_ratio = total_evidence / max(len(questions), 1)
    readiness = min(1.0, evidence_ratio / 2 + 0.3)
    communication = min(1.0, 0.5 + len([t for t in transcript if t["role"] == "candidate" and len(t["content"]) > 50]) / len(questions) * 0.3)
    confidence = readiness * 0.6 + communication * 0.4

    follow_ups = []
    for flag in red_flags[:3]:
        follow_ups.append({
            "question": f"Can you provide more details about: {flag}?",
            "reason": "Missing resume evidence",
        })

    return {
        "transcript": transcript,
        "readiness_score": round(readiness, 4),
        "communication_score": round(communication, 4),
        "confidence_score": round(confidence, 4),
        "red_flags": red_flags,
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:5],
        "follow_up_questions": follow_ups,
    }
