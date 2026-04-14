"""
AI Service — powered by OpenAI GPT.
Production-safe: every public function returns a value, never raises.

FIX NOTES
---------
* generate_questions() previously called with kwargs (difficulty,
  include_behavioral) that weren't in the function signature → TypeError.
  Now accepts and uses them.
* Added timeout to OpenAI calls (30 s) to prevent hanging requests.
* _clean_json now handles markdown fences and trailing commas robustly.
* All public functions have try/except at top level and return fallbacks.
"""

import json
import logging
import os
import re
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("intellihire.ai")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL          = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
REQUEST_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))  # seconds

_client = None  # lazy singleton


def _get_client():
    global _client
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set — AI features will use fallbacks")
        return None
    if _client is None:
        try:
            from openai import OpenAI
            _client = OpenAI(api_key=OPENAI_API_KEY, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            logger.error(f"OpenAI client init failed: {e}", exc_info=True)
            return None
    return _client


# ─── Core chat helper ─────────────────────────────────────────────────────────

def _chat(
    system: str,
    user: str,
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> Optional[str]:
    """
    Call the OpenAI chat API.
    Returns the response text, or None on any failure.
    """
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
            logger.warning("OpenAI returned empty choices")
            return None

        content = resp.choices[0].message.content
        return content.strip() if content else None

    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}", exc_info=True)
        return None


# ─── JSON parser ──────────────────────────────────────────────────────────────

def _clean_json(text: str) -> Optional[dict | list]:
    """
    Strip markdown code fences and parse JSON.
    Returns parsed object or None.
    """
    if not text:
        return None
    try:
        # Remove ```json ... ``` or ``` ... ``` fences
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
        # Remove trailing commas before ] or } (common GPT mistake)
        text = re.sub(r",\s*([}\]])", r"\1", text)
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find first JSON object/array inside the text
        for pattern in (r"\{.*\}", r"\[.*\]"):
            m = re.search(pattern, text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except Exception:
                    pass
    except Exception:
        pass
    return None


# ─── Resume Analysis ──────────────────────────────────────────────────────────

def analyze_resume_ai(text: str) -> dict:
    try:
        result = _chat(
            system=(
                "You are a professional resume analyser. "
                "Respond ONLY with valid JSON matching this schema exactly:\n"
                '{"candidate_name": str|null, "candidate_email": str|null, '
                '"summary": str, "skills": [str], "experience_years": float, '
                '"education": [str], "domain": str, "resume_score": float, '
                '"score_breakdown": {"skills_relevance": float, '
                '"experience_depth": float, "education_quality": float, '
                '"presentation_clarity": float, "achievements_impact": float}}'
            ),
            user=f"Analyse this resume:\n\n{text[:6000]}",
            temperature=0.3,
            max_tokens=1200,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                data["experience_years"] = _safe_float(data.get("experience_years"))
                data["resume_score"]     = _safe_float(data.get("resume_score"))
                if not isinstance(data.get("skills"), list):
                    data["skills"] = []
                if not isinstance(data.get("education"), list):
                    data["education"] = []
                return data

    except Exception as e:
        logger.error(f"analyze_resume_ai error: {e}", exc_info=True)

    return _fallback_resume_analysis(text)


def _fallback_resume_analysis(text: str) -> dict:
    text_lower = text.lower()
    keywords = [
        "python", "java", "javascript", "react", "node", "sql",
        "fastapi", "django", "machine learning", "aws", "docker",
    ]
    skills = [k for k in keywords if k in text_lower]
    score  = min(100.0, float(len(skills) * 10 + 20))
    return {
        "candidate_name":   None,
        "candidate_email":  None,
        "summary":          "Automated analysis unavailable — manual review recommended.",
        "skills":           skills,
        "experience_years": 0.0,
        "education":        [],
        "domain":           "General Software",
        "resume_score":     score,
        "score_breakdown": {
            "skills_relevance":    10.0,
            "experience_depth":    10.0,
            "education_quality":   10.0,
            "presentation_clarity":10.0,
            "achievements_impact": 10.0,
        },
    }


# ─── Job Fit ──────────────────────────────────────────────────────────────────

def compute_job_fit(
    resume_summary: str,
    skills: list[str],
    job_role: str,
    job_description: str,
) -> dict:
    try:
        result = _chat(
            system=(
                "You are a recruitment expert. "
                "Respond ONLY with valid JSON:\n"
                '{"fit_score": float, "fit_breakdown": {str: float}, '
                '"strengths": [str], "gaps": [str], "improvements": [str]}'
            ),
            user=(
                f"Role: {job_role}\n"
                f"Job Description: {job_description[:2000]}\n"
                f"Candidate Summary: {resume_summary[:1000]}\n"
                f"Skills: {', '.join(skills[:30])}"
            ),
            temperature=0.3,
            max_tokens=800,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                data["fit_score"] = _safe_float(data.get("fit_score", 60))
                return data

    except Exception as e:
        logger.error(f"compute_job_fit error: {e}", exc_info=True)

    return {
        "fit_score":    60.0,
        "fit_breakdown": {},
        "strengths":    ["Candidate has relevant technical skills"],
        "gaps":         ["Further evaluation needed"],
        "improvements": ["Add more project examples", "Quantify achievements"],
    }


# ─── Interview Questions ──────────────────────────────────────────────────────

def generate_questions(
    role: str,
    skills: list[str],
    num_questions: int = 5,
    difficulty: str = "mixed",
    include_behavioral: bool = True,
) -> list[dict]:
    """
    Generate interview questions for a role.

    Args:
        role: Job role/title
        skills: List of candidate skills
        num_questions: How many questions to generate (1–20)
        difficulty: "easy" | "medium" | "hard" | "mixed"
        include_behavioral: Whether to include behavioural questions
    """
    num_questions = max(1, min(20, num_questions))

    behavioral_note = (
        "Include a mix of technical and behavioural questions."
        if include_behavioral
        else "Focus on technical questions only."
    )

    try:
        result = _chat(
            system=(
                "You are an expert technical interviewer. "
                f"Generate exactly {num_questions} interview questions for the given role. "
                f"Difficulty: {difficulty}. {behavioral_note} "
                "Respond ONLY with a valid JSON array:\n"
                '[{"question": str, "difficulty": "easy"|"medium"|"hard", '
                '"category": "technical"|"behavioral"|"situational"}]'
            ),
            user=(
                f"Role: {role}\n"
                f"Relevant skills: {', '.join(skills[:20]) if skills else 'general'}"
            ),
            temperature=0.8,
            max_tokens=1500,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, list) and data:
                validated = []
                for q in data[:num_questions]:
                    if isinstance(q, dict) and q.get("question"):
                        validated.append({
                            "question":   str(q.get("question", "")),
                            "difficulty": str(q.get("difficulty", "medium")),
                            "category":   str(q.get("category", "technical")),
                        })
                if validated:
                    return validated

    except Exception as e:
        logger.error(f"generate_questions error: {e}", exc_info=True)

    # Fallback questions
    return _fallback_questions(role, num_questions, include_behavioral)


def _fallback_questions(role: str, n: int, include_behavioral: bool) -> list[dict]:
    technical = [
        {"question": f"Describe your experience with the core technologies used in a {role} role.",
         "difficulty": "medium", "category": "technical"},
        {"question": f"What is the most complex problem you solved as a {role}?",
         "difficulty": "hard", "category": "technical"},
        {"question": "Explain how you approach debugging a production issue.",
         "difficulty": "medium", "category": "technical"},
        {"question": "How do you ensure code quality in your projects?",
         "difficulty": "medium", "category": "technical"},
        {"question": "Describe your experience with version control and CI/CD pipelines.",
         "difficulty": "easy", "category": "technical"},
    ]
    behavioral = [
        {"question": "Tell me about a time you had to learn a new technology quickly.",
         "difficulty": "medium", "category": "behavioral"},
        {"question": "Describe a conflict with a teammate and how you resolved it.",
         "difficulty": "medium", "category": "behavioral"},
    ]
    pool = technical + (behavioral if include_behavioral else [])
    return pool[:n]


# ─── Answer Evaluation ────────────────────────────────────────────────────────

def evaluate_answer(question: str, answer: str, role: str = "") -> dict:
    try:
        result = _chat(
            system=(
                "You are a senior technical interviewer. "
                "Evaluate the candidate's answer and respond ONLY with valid JSON:\n"
                '{"score": float (0-10), "is_correct": "correct"|"partial"|"incorrect", '
                '"feedback": str, "strengths": [str], "weaknesses": [str]}'
            ),
            user=(
                f"Role: {role or 'Software Engineer'}\n"
                f"Question: {question}\n"
                f"Answer: {answer[:2000]}"
            ),
            temperature=0.4,
            max_tokens=600,
        )

        if result:
            data = _clean_json(result)
            if isinstance(data, dict):
                data["score"] = max(0.0, min(10.0, _safe_float(data.get("score", 5))))
                return data

    except Exception as e:
        logger.error(f"evaluate_answer error: {e}", exc_info=True)

    return {
        "score":      5.0,
        "is_correct": "partial",
        "feedback":   "Answer received. Manual review recommended.",
        "strengths":  [],
        "weaknesses": ["Could not perform automated evaluation"],
    }


# ─── Util ─────────────────────────────────────────────────────────────────────

def _safe_float(val, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default