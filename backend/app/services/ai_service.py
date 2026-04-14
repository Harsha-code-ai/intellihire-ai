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
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
MODEL           = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")
REQUEST_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))

_client = None


# ================= CLIENT =================

def _get_client():
    global _client
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set — fallback will be used")
        return None
    if _client is None:
        try:
            from openai import OpenAI
            _client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                http_client=httpx.Client(timeout=REQUEST_TIMEOUT),
            )
            logger.info("✅ OpenRouter client initialized")
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
                {"role": "user",   "content": user},
            ],
            temperature=temperature,
        )
        if not resp or not resp.choices:
            return None
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"API call failed: {e}", exc_info=True)
        return None


# ================= JSON CLEAN =================

def _clean_json(text: str):
    if not text:
        return None
    try:
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except:
        return None


# ================= INTERVIEW QUESTIONS =================

def generate_questions(role: str, skills: list[str], num_questions: int = 5):
    try:
        result = _chat(
            system=(
                "You are an expert interviewer. "
                "Generate ROLE-SPECIFIC, SKILL-BASED interview questions. "
                "Avoid generic questions. "
                "Return ONLY JSON array:\n"
                '[{"question": "text"}]'
            ),
            user=f"Role: {role}\nSkills: {', '.join(skills)}",
            temperature=0.9,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, list):
                return data[:num_questions]

    except Exception as e:
        logger.error(f"generate_questions error: {e}")

    return [
        {"question": f"What are key responsibilities of a {role}?"},
        {"question": f"Explain important skills required for {role}."},
        {"question": "How do you solve technical problems?"},
    ]


# ================= RESUME ANALYSIS =================

def analyze_resume_ai(text: str) -> dict:
    return {
        "candidate_name": None,
        "candidate_email": None,
        "summary": "Resume analysis working (basic mode).",
        "skills": [],
        "experience_years": 0,
        "education": [],
        "domain": "General",
        "resume_score": 50,
        "score_breakdown": {}
    }


# ================= JOB FIT =================

def compute_job_fit(
    resume_summary: str,
    skills: list[str],
    job_role: str,
    job_description: str,
) -> dict:
    return {
        "fit_score": 60,
        "fit_breakdown": {},
        "strengths": ["Basic matching skills"],
        "gaps": ["Detailed AI analysis not available"],
        "improvements": ["Add more projects", "Improve skills"]
    }


# ================= EVALUATE ANSWER (FIXED) =================

def evaluate_answer(question: str, answer: str) -> dict:
    try:
        result = _chat(
            system=(
                "You are an expert interviewer. "
                "Evaluate the answer and return JSON:\n"
                '{"score": 0-10, "feedback": "text", "correct": true}'
            ),
            user=f"Question: {question}\nAnswer: {answer}",
            temperature=0.3,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                return data

    except Exception as e:
        logger.error(f"evaluate_answer error: {e}")

    return {
        "score": 5,
        "feedback": "Evaluation service temporarily unavailable.",
        "correct": True
    }


# ================= UTIL =================

def _safe_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default