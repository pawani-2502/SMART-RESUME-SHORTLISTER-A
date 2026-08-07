import json
import re
import httpx
from typing import Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config import get_settings

settings = get_settings()

JD_PARSE_PROMPT = """Analyze this job description and extract structured information.

Job Description:
{text}

Return ONLY valid JSON with this structure:
{{
  "required_skills": [{{"name": "skill", "classification": "must_have"}}],
  "nice_to_have_skills": [{{"name": "skill", "classification": "preferred"}}],
  "optional_skills": [{{"name": "skill", "classification": "optional"}}],
  "responsibilities": ["..."],
  "technologies": ["..."],
  "seniority": "junior|mid|senior|lead|principal",
  "certifications": ["..."],
  "experience_years_min": 0,
  "experience_years_max": null,
  "domain_requirements": ["..."],
  "education_requirements": ["..."],
  "hidden_requirements": [
    {{"requirement": "ownership", "evidence": "quote from JD", "confidence": 0.8}}
  ],
  "ideal_candidate_profile": {{
    "summary": "...",
    "key_traits": ["..."],
    "experience_pattern": "..."
  }},
  "borderline_candidate_profile": {{
    "summary": "...",
    "acceptable_gaps": ["..."],
    "risk_factors": ["..."]
  }},
  "high_risk_candidate_profile": {{
    "summary": "...",
    "red_flags": ["..."],
    "deal_breakers": ["..."]
  }}
}}"""

RESUME_PARSE_PROMPT = """Parse this resume into structured JSON.

Resume:
{text}

Return ONLY valid JSON:
{{
  "name": "...",
  "email": "...",
  "phone": "...",
  "location": "...",
  "summary": "...",
  "skills": [{{"name": "...", "category": "technical|soft|domain", "years_used": null}}],
  "experience": [
    {{
      "title": "...",
      "company": "...",
      "location": "...",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or present",
      "description": "...",
      "achievements": ["..."],
      "technologies": ["..."]
    }}
  ],
  "projects": [
    {{
      "name": "...",
      "description": "...",
      "technologies": ["..."],
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM"
    }}
  ],
  "education": [
    {{
      "degree": "...",
      "institution": "...",
      "field": "...",
      "graduation_year": "YYYY"
    }}
  ],
  "certifications": [{{"name": "...", "issuer": "...", "date": "YYYY-MM"}}],
  "publications": ["..."],
  "awards": ["..."]
}}"""


class LLMProvider:
    def __init__(self):
        self.providers = [p.strip() for p in settings.llm_provider_order.split(",")]

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4))
    async def complete(self, prompt: str, system: str = "You are an expert recruitment AI assistant. Return only valid JSON.") -> str:
        return await self._complete_internal(prompt, system, json_mode=True)

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4))
    async def complete_text(self, prompt: str, system: str = "You are a helpful recruitment assistant. Reply in plain text only.") -> str:
        return await self._complete_internal(prompt, system, json_mode=False)

    async def _complete_internal(self, prompt: str, system: str, json_mode: bool) -> str:
        errors = []
        for provider in self.providers:
            try:
                if provider == "groq" and settings.groq_api_key:
                    return await self._call_groq(prompt, system, json_mode=json_mode)
                elif provider == "gemini" and settings.gemini_api_key:
                    return await self._call_gemini(prompt, system, json_mode=json_mode)
                elif provider == "ollama":
                    return await self._call_ollama(prompt, system, json_mode=json_mode)
            except Exception as e:
                errors.append(f"{provider}: {e}")
        return self._rule_based_fallback(prompt, json_mode=json_mode)

    async def _call_groq(self, prompt: str, system: str, json_mode: bool = True) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                json={
                    "model": settings.default_llm_model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _call_gemini(self, prompt: str, system: str, json_mode: bool = True) -> str:
        async with httpx.AsyncClient(timeout=90) as client:
            model = settings.gemini_model
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={settings.gemini_api_key}"
            )
            generation_config: dict[str, Any] = {"temperature": 0.1}
            if json_mode:
                generation_config["responseMimeType"] = "application/json"
            resp = await client.post(
                url,
                json={
                    "systemInstruction": {"parts": [{"text": system}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": generation_config,
                },
            )
            if resp.status_code != 200:
                # Fallback without JSON mode for older models
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-1.5-flash:generateContent?key={settings.gemini_api_key}",
                    json={
                        "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
                        "generationConfig": {"temperature": 0.1},
                    },
                )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_ollama(self, prompt: str, system: str, json_mode: bool = True) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    def _rule_based_fallback(self, prompt: str, json_mode: bool = True) -> str:
        text = prompt.lower()

        # Copilot chat — return plain text, never resume JSON
        if not json_mode or "recruiter question:" in text:
            return self._copilot_rule_fallback(prompt)

        # Resume parsing
        if "parse this resume" in text:
            return json.dumps(self._parse_resume_rules(prompt))

        skills = []
        tech_keywords = [
            "python", "javascript", "typescript", "react", "node", "java", "aws",
            "docker", "kubernetes", "sql", "postgresql", "mongodb", "fastapi",
            "machine learning", "deep learning", "pytorch", "tensorflow", "git",
            "agile", "scrum", "leadership", "communication", "rest", "api",
        ]
        for kw in tech_keywords:
            if kw in text:
                skills.append({"name": kw.title(), "classification": "must_have"})

        seniority = "mid"
        if any(w in text for w in ["senior", "lead", "principal", "staff"]):
            seniority = "senior"
        elif any(w in text for w in ["junior", "entry", "graduate", "intern"]):
            seniority = "junior"

        years_match = re.search(r"(\d+)\+?\s*years?", text)
        exp_min = int(years_match.group(1)) if years_match else 2

        return json.dumps({
            "required_skills": skills[:8],
            "nice_to_have_skills": skills[8:12],
            "optional_skills": [],
            "responsibilities": [],
            "technologies": [s["name"] for s in skills[:6]],
            "seniority": seniority,
            "certifications": [],
            "experience_years_min": exp_min,
            "experience_years_max": None,
            "domain_requirements": [],
            "education_requirements": ["Bachelor's degree"],
            "hidden_requirements": [
                {"requirement": "communication", "evidence": "inferred", "confidence": 0.6},
                {"requirement": "adaptability", "evidence": "inferred", "confidence": 0.5},
            ],
            "ideal_candidate_profile": {"summary": "Strong technical fit with relevant experience", "key_traits": [], "experience_pattern": ""},
            "borderline_candidate_profile": {"summary": "Partial skill match", "acceptable_gaps": [], "risk_factors": []},
            "high_risk_candidate_profile": {"summary": "Significant gaps", "red_flags": [], "deal_breakers": []},
        })

    def _copilot_rule_fallback(self, prompt: str) -> str:
        """Plain-text fallback when LLM providers are unavailable."""
        for line in prompt.splitlines():
            if line.startswith("#1 "):
                return (
                    f"Based on current rankings: {line}. "
                    "I recommend interviewing the top-ranked candidate first."
                )
        if "compare" in prompt.lower():
            return "Compare candidates using the Comparison page for side-by-side scores and skill overlap."
        return (
            "I don't have sufficient evidence in the current job data to answer that precisely. "
            "Try asking about the top candidate, skill gaps, or who to interview first."
        )

    def _parse_resume_rules(self, prompt: str) -> dict:
        text = prompt
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        phone_match = re.search(r"\+?[\d\s\-().]{10,}", text)
        name = text.split("\n")[0].strip()[:100] if text else "Unknown"

        skills = []
        for kw in ["python", "javascript", "react", "java", "aws", "docker", "sql", "fastapi", "node"]:
            if kw in text.lower():
                skills.append({"name": kw.title(), "category": "technical", "years_used": None})

        return {
            "name": name,
            "email": email_match.group() if email_match else None,
            "phone": phone_match.group().strip() if phone_match else None,
            "location": None,
            "summary": text[:500],
            "skills": skills,
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
            "publications": [],
            "awards": [],
        }


def extract_json_from_response(response: str) -> dict:
    response = response.strip()
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
    if json_match:
        response = json_match.group(1)
    start = response.find("{")
    end = response.rfind("}") + 1
    if start >= 0 and end > start:
        response = response[start:end]
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {}


llm_provider = LLMProvider()


async def parse_job_description(text: str) -> dict:
    prompt = JD_PARSE_PROMPT.format(text=text[:8000])
    response = await llm_provider.complete(prompt)
    return extract_json_from_response(response)


async def parse_resume(text: str) -> dict:
    prompt = RESUME_PARSE_PROMPT.format(text=text[:8000])
    response = await llm_provider.complete(prompt)
    return extract_json_from_response(response)
