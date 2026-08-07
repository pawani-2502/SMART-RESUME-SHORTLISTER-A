"""Recruiter Copilot RAG - grounded Q&A over job data."""

import json
import re
from typing import Any
from backend.services.llm_service import llm_provider, extract_json_from_response


INTENT_PATTERNS = {
    "explain_ranking": r"why.*(rank|score|#?\d|top|first)",
    "compare": r"compar|versus|vs\.|difference between",
    "search_skill": r"who.*(know|has|experience|skill)|find.*candidate|candidates with",
    "recommend": r"who should|recommend|interview first|best candidate|shortlist",
    "analytics": r"how many|average|distribution|funnel|stats|metric",
    "gaps": r"missing|gap|lack|don't have|without",
}


def classify_intent(query: str) -> str:
    q = query.lower()
    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, q):
            return intent
    return "general"


def build_context(
    intent: str,
    query: str,
    job: dict,
    rankings: list[dict],
    candidates: list[dict],
) -> tuple[str, list[dict]]:
    citations = []
    parts = [f"Job: {job.get('title')}", f"Status: {job.get('status')}"]

    if intent in ("explain_ranking", "recommend", "general", "compare"):
        for r in rankings[:10]:
            name = r.get("candidate_name", "Unknown")
            parts.append(
                f"#{r.get('rank')} {name}: score={r.get('final_score', 0):.0%}, "
                f"confidence={r.get('confidence_level')}, "
                f"strengths={r.get('strengths', [])[:3]}, "
                f"weaknesses={r.get('weaknesses', [])[:2]}"
            )
            citations.append({
                "source": f"ranking:{r.get('candidate_id')}",
                "snippet": r.get("explanation", "")[:200],
            })

    if intent == "search_skill":
        skill_match = re.search(r"(python|react|java|aws|docker|kubernetes|sql|node|fastapi|ml|ai)", query, re.I)
        skill = skill_match.group(1) if skill_match else ""
        for c in candidates:
            skills = [s.get("name", s) if isinstance(s, dict) else s for s in c.get("parsed_data", {}).get("skills", [])]
            if skill and any(skill.lower() in str(s).lower() for s in skills):
                parts.append(f"{c.get('name')}: has {skill}")
                citations.append({"source": f"candidate:{c.get('id')}", "snippet": f"Skills: {skills[:5]}"})

    if intent == "gaps":
        all_missing: dict[str, int] = {}
        for r in rankings:
            for m in r.get("missing_requirements", []):
                all_missing[m] = all_missing.get(m, 0) + 1
        top_gaps = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:10]
        parts.append(f"Common skill gaps in pool: {top_gaps}")

    if intent == "analytics":
        eligible = sum(1 for r in rankings if r.get("eligibility_status") == "eligible")
        avg = sum(r.get("final_score", 0) or 0 for r in rankings) / max(len(rankings), 1)
        parts.append(f"Total ranked: {len(rankings)}, Eligible: {eligible}, Avg score: {avg:.0%}")

    return "\n".join(parts), citations


def _sanitize_answer(raw: str, intent: str, rankings: list[dict], candidates: list[dict], query: str) -> str:
    """Ensure copilot never returns resume-parse JSON to the user."""
    text = raw.strip()
    if not text:
        return _fallback_answer(intent, rankings, candidates, query)

    if text.startswith("{") or text.startswith("["):
        parsed = extract_json_from_response(text)
        if parsed.get("answer"):
            return str(parsed["answer"]).strip()
        if parsed.get("summary") and not parsed.get("skills"):
            return str(parsed["summary"]).strip()
        # Resume-shaped JSON — discard and use rule-based answer
        if parsed.get("name") or parsed.get("skills"):
            return _fallback_answer(intent, rankings, candidates, query)
        return text

    return text


async def copilot_chat(
    query: str,
    job: dict,
    rankings: list[dict],
    candidates: list[dict],
) -> dict:
    intent = classify_intent(query)
    context, citations = build_context(intent, query, job, rankings, candidates)

    prompt = f"""You are a recruitment AI copilot. Answer ONLY using the provided context.
If the context lacks information, say "I don't have sufficient evidence in the current job data."

Context:
{context}

Recruiter question: {query}

Reply in 2-4 sentences of plain English. Reference candidates by name. Do NOT return JSON."""

    try:
        answer = await llm_provider.complete_text(
            prompt,
            system="You are a helpful recruitment copilot. Reply in plain text only. Never return JSON or code blocks.",
        )
        answer = _sanitize_answer(answer, intent, rankings, candidates, query)
    except Exception:
        answer = _fallback_answer(intent, rankings, candidates, query)

    return {
        "answer": answer,
        "intent": intent,
        "citations": citations[:5],
    }


def _fallback_answer(intent: str, rankings: list[dict], candidates: list[dict], query: str) -> str:
    if intent == "recommend" and rankings:
        top = rankings[0]
        return (
            f"I recommend interviewing {top.get('candidate_name', 'the top candidate')} first "
            f"with a score of {top.get('final_score', 0):.0%} and {top.get('confidence_level', 'unknown')} confidence."
        )
    if intent == "compare" and len(rankings) >= 2:
        a, b = rankings[0], rankings[1]
        return (
            f"{a.get('candidate_name')} leads at {a.get('final_score', 0):.0%} vs "
            f"{b.get('candidate_name')} at {b.get('final_score', 0):.0%}. "
            f"Use the Comparison page for a detailed side-by-side view."
        )
    if intent == "explain_ranking" and rankings:
        top = rankings[0]
        strengths = ", ".join((top.get("strengths") or [])[:3])
        return (
            f"{top.get('candidate_name')} ranks #1 at {top.get('final_score', 0):.0%} because of "
            f"strong fit: {strengths or 'high overall scores across ranking factors'}."
        )
    if intent == "analytics":
        eligible = sum(1 for r in rankings if r.get("eligibility_status") == "eligible")
        avg = sum(r.get("final_score", 0) or 0 for r in rankings) / max(len(rankings), 1)
        return f"There are {len(candidates)} candidates, {len(rankings)} ranked, {eligible} eligible, with an average score of {avg:.0%}."
    if rankings:
        return f"The top candidate is {rankings[0].get('candidate_name')} with score {rankings[0].get('final_score', 0):.0%}."
    return "Upload candidates and run ranking first to get insights."
