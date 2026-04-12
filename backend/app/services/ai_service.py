"""
AI Service — powered by OpenAI GPT.
Safe, production-ready, with full fallback support.
"""

import os
import json
import re
import logging
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("intellihire.ai")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client: OpenAI | None = None


def _get_client() -> OpenAI | None:
    global _client
    if not OPENAI_API_KEY:
        return None
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


# ================= CHAT ================= #

def _chat(system: str, user: str, temperature: float = 0.7, max_tokens: int = 1500) -> str | None:
    client = _get_client()

    if not client:
        logger.warning("No OpenAI API key — using fallback")
        return None

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not resp or not resp.choices:
            return None

        content = resp.choices[0].message.content
        if not content:
            return None

        return content.strip()

    except Exception as e:
        logger.error(f"OpenAI API failed: {e}")
        return None


# ================= CLEAN JSON ================= #

def _clean_json(text: str) -> dict | None:
    try:
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL).strip()
        return json.loads(text)
    except Exception:
        return None


# ================= RESUME ANALYSIS ================= #

def analyze_resume_ai(text: str) -> dict:
    try:
        result = _chat(
            "Analyze resume and return structured JSON.",
            f"Resume:\n{text[:6000]}",
            temperature=0.3
        )

        if result and isinstance(result, str) and len(result.strip()) > 10:
            data = _clean_json(result)

            if data:
                data["experience_years"] = float(data.get("experience_years", 0) or 0)
                data["resume_score"] = float(data.get("resume_score", 0) or 0)

                if not isinstance(data.get("skills"), list):
                    data["skills"] = []

                if not isinstance(data.get("education"), list):
                    data["education"] = []

                return data

        return _fallback_resume_analysis(text)

    except Exception as e:
        logger.error(f"Resume AI failed: {e}")
        return _fallback_resume_analysis(text)


def _fallback_resume_analysis(text: str) -> dict:
    text_lower = text.lower()

    keywords = ["python", "java", "react", "sql", "fastapi", "machine learning"]
    skills = [k for k in keywords if k in text_lower]

    return {
        "candidate_name": None,
        "candidate_email": None,
        "summary": "Fallback analysis used.",
        "skills": skills,
        "experience_years": 0,
        "education": [],
        "domain": "General Software",
        "resume_score": float(min(100, len(skills) * 10)),
        "score_breakdown": {
            "skills_relevance": 10,
            "experience_depth": 10,
            "education_quality": 10,
            "presentation_clarity": 10,
            "achievements_impact": 10,
        },
    }


# ================= JOB FIT ================= #

def compute_job_fit(resume_summary: str, skills: List[str], job_role: str, job_description: str) -> dict:
    result = _chat(
        "Evaluate candidate-job fit and return JSON.",
        f"{resume_summary}\n{job_description}",
        temperature=0.3
    )

    if result:
        data = _clean_json(result)
        if data:
            data["fit_score"] = float(data.get("fit_score", 0))
            return data

    return {
        "fit_score": 60,
        "fit_breakdown": {},
        "strengths": ["Basic skill match"],
        "gaps": ["Needs improvement"],
        "improvements": ["Add projects"],
    }


# ================= QUESTIONS ================= #

def generate_questions(role: str, skills: List[str], num_questions: int = 5) -> List[dict]:
    result = _chat(
        "Generate interview questions in JSON.",
        f"{role} {skills}",
        temperature=0.8
    )

    if result:
        data = _clean_json(result)
        if isinstance(data, list):
            return data[:num_questions]

    return [
        {"question": f"What is {role}?", "difficulty": "easy", "category": "technical"}
    ]


# ================= EVALUATION ================= #

def evaluate_answer(question: str, answer: str, role: str = "") -> dict:
    result = _chat(
        "Evaluate answer and return JSON.",
        f"{question}\n{answer}",
        temperature=0.4
    )

    if result:
        data = _clean_json(result)
        if data:
            data["score"] = float(data.get("score", 5))
            return data

    return {
        "score": 5,
        "is_correct": "partial",
        "feedback": "Basic answer.",
        "strengths": [],
        "weaknesses": ["Needs improvement"],
    }