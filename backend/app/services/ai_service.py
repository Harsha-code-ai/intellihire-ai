"""
AI Service using Groq API
Fast, reliable, production-ready
"""

import json
import logging
import os
import re
import time
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger("intellihire.ai")

# ================= CONFIG =================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "20"))

_client = None


# ================= CLIENT =================

def _get_client():
    global _client
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set")
        return None

    if _client is None:
        try:
            _client = Groq(api_key=GROQ_API_KEY)
            logger.info(f"✅ Groq client initialized | model={MODEL}")
        except Exception as e:
            logger.error(f"Client init failed: {e}", exc_info=True)
            return None

    return _client


# ================= CHAT (WITH RETRY) =================

def _chat(system: str, user: str, temperature: float = 0.7) -> Optional[str]:
    client = _get_client()
    if not client:
        return None

    for attempt in range(2):  # retry 2 times
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
            )

            if response and response.choices:
                return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(1)

    logger.error("❌ All attempts failed")
    return None


# ================= JSON CLEAN =================

def _clean_json(text: str):
    if not text:
        return None

    try:
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
        return json.loads(text)
    except:
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
    include_behavioral: bool = False
):
    logger.info(f"generate_questions | role={role} | difficulty={difficulty} | behavioral={include_behavioral}")

    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    try:
        result = _chat(
            system=(
                "You are an expert interviewer. "
                "Generate high-quality, role-specific interview questions. "
                "Adjust difficulty and include behavioral questions if requested. "
                "Return ONLY JSON array:\n"
                '[{"question": "text"}]'
            ),
            user=f"Role: {role}\nSkills: {', '.join(skills)}\nDifficulty: {difficulty}\nBehavioral: {include_behavioral}",
            temperature=0.8,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, list):
                return data[:num_questions]

    except Exception as e:
        logger.error(f"generate_questions error: {e}", exc_info=True)

    # fallback
    return [
        {"question": f"What are key responsibilities of a {role}?"},
        {"question": f"Explain important skills required for {role}."},
        {"question": "How do you solve technical problems?"},
    ]


# ================= EVALUATE ANSWER =================

def evaluate_answer(question: str, answer: str) -> dict:
    try:
        result = _chat(
            system=(
                "You are an expert interviewer. "
                "Evaluate the answer and return JSON:\n"
                '{"score": 0-10, "feedback": "text", "correct": true/false}'
            ),
            user=f"Question: {question}\nAnswer: {answer}",
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
        "feedback": "Evaluation unavailable",
        "correct": True
    }


# ================= HEALTH CHECK =================

def check_ai_status():
    test = _chat("Say OK", "Test")
    return {"status": "working" if test else "failed"}