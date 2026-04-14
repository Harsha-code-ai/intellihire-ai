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
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()  # ✅ NEW
MODEL           = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b")  # ✅ DEFAULT FREE MODEL
REQUEST_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))

_client = None


def _get_client():
    global _client
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set — AI features will use fallbacks")
        return None
    if _client is None:
        try:
            from openai import OpenAI
            _client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,  # ✅ IMPORTANT FIX
                http_client=httpx.Client(timeout=REQUEST_TIMEOUT),
            )
            logger.info("✅ OpenAI/OpenRouter client initialized")
        except Exception as e:
            logger.error(f"Client init failed: {e}", exc_info=True)
            return None
    return _client


def _chat(system: str, user: str, temperature: float = 0.7, max_tokens: int = 1500) -> Optional[str]:
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
            max_tokens=max_tokens,
        )
        if not resp or not resp.choices:
            return None
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"API call failed: {e}", exc_info=True)
        return None


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
                "You are an expert technical interviewer. "
                "Generate HIGH-QUALITY, ROLE-SPECIFIC interview questions. "
                "Do NOT give generic questions. Use the skills provided."
                "Respond ONLY in JSON array format:\n"
                '[{"question": str}]'
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

    # fallback (only if API fails)
    return [
        {"question": f"What are key responsibilities of a {role}?"},
        {"question": f"Explain important skills required for {role}."},
        {"question": "How do you solve technical problems?"},
    ]


# ================= UTIL =================

def _safe_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default