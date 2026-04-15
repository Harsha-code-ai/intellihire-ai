import json
import logging
import os
import re
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("intellihire.ai")

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1").strip() or "https://openrouter.ai/api/v1"
MODEL           = os.getenv("OPENAI_MODEL", "mistralai/mistral-7b-instruct:free")
REQUEST_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "45"))

_client = None


# ================= CLIENT =================

def _get_client():
    global _client
    if not OPENAI_API_KEY:
        logger.warning("❌ OPENAI_API_KEY is not set — AI disabled")
        return None
    if _client is None:
        try:
            from openai import OpenAI
            _client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                default_headers={
                    "HTTP-Referer": "https://intellihire.app",
                    "X-Title": "IntelliHire Pro",
                },
                http_client=httpx.Client(timeout=REQUEST_TIMEOUT),
            )
            logger.info(f"✅ OpenRouter client initialized | model={MODEL}")
        except Exception as e:
            logger.error(f"Client init failed: {e}", exc_info=True)
            return None
    return _client


# ================= CHAT =================

def _chat(system: str, user: str, temperature: float = 0.7) -> Optional[str]:
    client = _get_client()
    if not client:
        return None
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        if not resp or not resp.choices:
            return None
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"❌ API call failed: {e}", exc_info=True)
        return None


# ================= JSON CLEAN =================

def _clean_json(text: str):
    if not text:
        return None
    try:
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except Exception:
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        return None


# ================= INTERVIEW QUESTIONS =================

def generate_questions(
    role: str,
    skills: list,
    num_questions: int = 5,
    difficulty: str = "medium",
    include_behavioral: bool = False   # ✅ FIX ADDED
):
    logger.info(f"generate_questions | role={role} | difficulty={difficulty} | behavioral={include_behavioral}")

    # safety: convert skills if string
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    try:
        result = _chat(
            system=(
                "You are an expert interviewer. "
                "Generate ROLE-SPECIFIC interview questions. "
                "Adjust difficulty level as requested. "
                "Include behavioral questions if requested. "
                "Return ONLY JSON array:\n"
                '[{"question": "text"}]'
            ),
            user=f"Role: {role}\nSkills: {', '.join(skills)}\nDifficulty: {difficulty}\nBehavioral: {include_behavioral}",
            temperature=0.9,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, list) and len(data) > 0:
                return data[:num_questions]

    except Exception as e:
        logger.error(f"generate_questions error: {e}", exc_info=True)

    # fallback
    return [
        {"question": f"What are key responsibilities of a {role}?"},
        {"question": f"Explain important skills required for {role}."},
        {"question": "How do you solve technical problems?"},
    ]


# ================= RESUME =================

def analyze_resume_ai(text: str) -> dict:
    return {
        "summary": "Resume processed",
        "skills": [],
        "experience_years": 0,
    }


def compute_job_fit(resume_summary: str, skills: list, job_role: str, job_description: str) -> dict:
    return {
        "fit_score": 60,
        "strengths": [],
        "gaps": [],
    }


# ================= EVALUATE =================

def evaluate_answer(question: str, answer: str) -> dict:
    try:
        result = _chat(
            system="Evaluate answer. Return JSON.",
            user=f"Q: {question}\nA: {answer}",
            temperature=0.3,
        )
        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.error(f"evaluate_answer error: {e}", exc_info=True)

    return {
        "score": 5,
        "feedback": "Basic evaluation",
        "correct": True
    }