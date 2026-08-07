"""LangGraph-style Shadow Interview Orchestrator."""

from typing import TypedDict, Any
from ai.engines.shadow_interview import run_shadow_interview, _grounded_answer, INTERVIEW_QUESTIONS_BY_SENIORITY


class InterviewState(TypedDict, total=False):
    job_requirements: dict
    parsed_resume: dict
    questions: list[str]
    transcript: list[dict]
    current_index: int
    readiness_score: float
    communication_score: float
    confidence_score: float
    red_flags: list[str]
    strengths: list[str]
    weaknesses: list[str]
    follow_up_questions: list[dict]
    status: str


async def run_interview_graph(
    parsed_resume: dict,
    job_requirements: dict,
    num_questions: int = 5,
) -> dict:
    """Multi-step interview simulation with evidence validation at each turn."""
    seniority = job_requirements.get("seniority", "mid")
    questions = INTERVIEW_QUESTIONS_BY_SENIORITY.get(seniority, INTERVIEW_QUESTIONS_BY_SENIORITY["mid"])
    questions = questions[:num_questions]

    state: InterviewState = {
        "job_requirements": job_requirements,
        "parsed_resume": parsed_resume,
        "questions": questions,
        "transcript": [],
        "current_index": 0,
        "red_flags": [],
        "strengths": [],
        "weaknesses": [],
        "follow_up_questions": [],
        "status": "running",
    }

    total_evidence = 0
    for q in questions:
        state["transcript"].append({"role": "interviewer", "content": q, "evidence": []})

        answer, evidence = _grounded_answer(q, parsed_resume)

        if answer == "Not evidenced in resume":
            state["red_flags"].append(f"Could not answer: {q[:80]}")
            state["weaknesses"].append(f"No evidence for: {q[:60]}")
            state["follow_up_questions"].append({
                "question": f"Please elaborate on: {q}",
                "reason": "Not evidenced in resume",
            })
        else:
            total_evidence += len(evidence)
            if evidence:
                state["strengths"].append(f"Evidence for: {q[:60]}")

        state["transcript"].append({
            "role": "candidate",
            "content": answer,
            "evidence": evidence,
            "validated": answer != "Not evidenced in resume",
        })
        state["current_index"] += 1

    evidence_ratio = total_evidence / max(len(questions), 1)
    state["readiness_score"] = round(min(1.0, evidence_ratio / 2 + 0.3), 4)
    state["communication_score"] = round(min(1.0, 0.5 + len([
        t for t in state["transcript"] if t["role"] == "candidate" and len(t["content"]) > 50
    ]) / len(questions) * 0.3), 4)
    state["confidence_score"] = round(state["readiness_score"] * 0.6 + state["communication_score"] * 0.4, 4)
    state["status"] = "completed"

    return {
        "transcript": state["transcript"],
        "readiness_score": state["readiness_score"],
        "communication_score": state["communication_score"],
        "confidence_score": state["confidence_score"],
        "red_flags": state["red_flags"],
        "strengths": state["strengths"][:5],
        "weaknesses": state["weaknesses"][:5],
        "follow_up_questions": state["follow_up_questions"],
    }
