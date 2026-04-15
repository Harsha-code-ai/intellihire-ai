"""
AI Service using Groq API
Fast, reliable, production-ready
"""

import json
import logging
import os
import re
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("intellihire.ai")

# ================= CONFIG =================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


# ================= CLIENT =================
def _get_client():
    global _client

    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set")
        return None

    if _client is None:
        try:
            from groq import Groq
            _client = Groq(api_key=GROQ_API_KEY)
            logger.info(f"✅ Groq client initialized | model={MODEL}")
        except Exception as e:
            logger.error(f"Client init failed: {e}", exc_info=True)
            return None

    return _client


# ================= CHAT =================
def _chat(system: str, user: str, temperature: float = 0.7) -> Optional[str]:
    client = _get_client()
    if not client:
        return None

    for attempt in range(3):  # ✅ better retry
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=1024,
            )

            if response and response.choices:
                return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"Retry {attempt+1} failed: {e}")

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


# ================= QUESTIONS =================
def generate_questions(role, skills, num_questions=5, difficulty="medium", include_behavioral=False):
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]

    result = _chat(
        system=(
            "You are an expert interviewer. Generate high-quality interview questions. "
            "Return ONLY JSON array: [{\"question\":\"text\"}]"
        ),
        user=f"Role: {role}\nSkills: {', '.join(skills)}\nDifficulty: {difficulty}\nBehavioral: {include_behavioral}",
        temperature=0.8,
    )

    if result:
        data = _clean_json(result)
        if isinstance(data, list):
            return data[:num_questions]

    return [
        {"question": f"What are responsibilities of a {role}?"},
        {"question": "Explain key concepts related to your skills."},
        {"question": "How do you debug issues?"},
    ]


# ================= EVALUATE =================
def evaluate_answer(question, answer, role=None):
    result = _chat(
        system="Evaluate answer and return JSON.",
        user=f"Q: {question}\nA: {answer}\nRole: {role}",
        temperature=0.3,
    )

    if result:
        data = _clean_json(result)
        if isinstance(data, dict):
            return data

    return {"score": 5, "feedback": "Basic evaluation", "correct": True}


# ================= RESUME =================
def analyze_resume_ai(text: str) -> dict:
    result = _chat(
        system="Analyze resume and return JSON.",
        user=text[:3000],
        temperature=0.3,
    )

    if result:
        data = _clean_json(result)
        if isinstance(data, dict):
            return data

    return {
        "summary": "Resume processed",
        "skills": [],
        "experience_years": 0,
    }


# ================= JOB FIT =================
def compute_job_fit(resume_summary, skills, job_role, job_description):
    result = _chat(
        system="Evaluate job fit and return JSON.",
        user=f"{resume_summary}\n{skills}\n{job_role}\n{job_description}",
        temperature=0.3,
    )

    if result:
        data = _clean_json(result)
        if isinstance(data, dict):
            return data

    return {"fit_score": 60, "strengths": [], "gaps": []}


# ================= HEALTH =================
def check_ai_status():
    test = _chat("Say OK", "Test")
    return {"status": "working" if test else "failed"}