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
# Fallback to OpenRouter URL if env var is missing/empty
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1").strip() or "https://openrouter.ai/api/v1"
# ✅ FIX: Use a real, free OpenRouter model
MODEL           = os.getenv("OPENAI_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
REQUEST_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "45"))

_client = None


# ================= CLIENT =================

def _get_client():
    global _client
    if not OPENAI_API_KEY:
        logger.warning("❌ OPENAI_API_KEY is not set — AI features disabled")
        return None
    if _client is None:
        try:
            from openai import OpenAI
            _client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                # ✅ FIX: OpenRouter requires these headers
                default_headers={
                    "HTTP-Referer": "https://intellihire.app",   # your site URL
                    "X-Title": "IntelliHire Pro",                # your app name
                },
                http_client=httpx.Client(timeout=REQUEST_TIMEOUT),
            )
            logger.info(f"✅ OpenRouter client initialized | base_url={OPENAI_BASE_URL} | model={MODEL}")
        except Exception as e:
            logger.error(f"Client init failed: {e}", exc_info=True)
            return None
    return _client


# ================= CHAT =================

def _chat(system: str, user: str, temperature: float = 0.7) -> Optional[str]:
    client = _get_client()
    if not client:
        logger.warning("_chat skipped: no client available")
        return None
    try:
        logger.debug(f"Calling OpenRouter | model={MODEL} | base_url={OPENAI_BASE_URL}")
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=temperature,
        )
        if not resp or not resp.choices:
            logger.warning("OpenRouter returned empty response / no choices")
            return None

        content = resp.choices[0].message.content
        logger.info(f"✅ OpenRouter response received ({len(content or '')} chars)")
        return content.strip() if content else None

    except Exception as e:
        # ✅ FIX: Log the FULL error details so you can see exactly what went wrong
        logger.error(f"❌ OpenRouter API call failed: {type(e).__name__}: {e}", exc_info=True)
        return None


# ================= JSON CLEAN =================

def _clean_json(text: str):
    if not text:
        return None
    try:
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except Exception:
        # Try to extract JSON substring
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        return None


# ================= INTERVIEW QUESTIONS =================

def generate_questions(role: str, skills: list, num_questions: int = 5):
    logger.info(f"generate_questions called | role={role} | skills={skills} | model={MODEL}")
    try:
        result = _chat(
            system=(
                "You are an expert interviewer. "
                "Generate ROLE-SPECIFIC, SKILL-BASED interview questions. "
                "Avoid generic questions. "
                "Return ONLY a valid JSON array with no extra text:\n"
                '[{"question": "text"}]'
            ),
            user=f"Role: {role}\nSkills: {', '.join(skills)}",
            temperature=0.9,
        )

        if result:
            logger.debug(f"Raw AI response: {result[:300]}")
            data = _clean_json(result)
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"✅ Generated {len(data)} questions from AI")
                return data[:num_questions]
            else:
                logger.warning(f"JSON parse failed or empty list. Raw: {result[:200]}")
        else:
            logger.warning("generate_questions: _chat returned None")

    except Exception as e:
        logger.error(f"generate_questions error: {e}", exc_info=True)

    # Fallback questions
    logger.info("Using fallback questions")
    return [
        {"question": f"What are key responsibilities of a {role}?"},
        {"question": f"Explain the most important skills required for {role}."},
        {"question": "How do you approach solving complex technical problems?"},
        {"question": f"Describe a challenging project related to {', '.join(skills[:2]) if skills else role}."},
        {"question": "How do you stay updated with industry trends?"},
    ][:num_questions]


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
    skills: list,
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


# ================= EVALUATE ANSWER =================

def evaluate_answer(question: str, answer: str) -> dict:
    try:
        result = _chat(
            system=(
                "You are an expert interviewer. "
                "Evaluate the candidate's answer and return ONLY valid JSON:\n"
                '{"score": <0-10>, "feedback": "<text>", "correct": <true|false>}'
            ),
            user=f"Question: {question}\nAnswer: {answer}",
            temperature=0.3,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, dict) and "score" in data:
                return data

    except Exception as e:
        logger.error(f"evaluate_answer error: {e}", exc_info=True)

    return {
        "score": 5,
        "feedback": "Evaluation service temporarily unavailable.",
        "correct": True
    }


# ================= UTIL =================

def _safe_float(val, default=0.0):
    try:
        return float(val)
    except Exception:
        return default