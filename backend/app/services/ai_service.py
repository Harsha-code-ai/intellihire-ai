"""
AI Service — powered by OpenAI GPT.
All prompts are versioned and modular for easy tuning.
Falls back to heuristic logic when the API is unavailable.
"""

import os
import json
import re
import logging
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("intellihire.ai")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL           = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client: OpenAI | None = None


def _get_client() -> OpenAI | None:
    global _client
    if not OPENAI_API_KEY:
        return None
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def _chat(system: str, user: str, temperature: float = 0.7, max_tokens: int = 1500) -> str | None:
    """Low-level chat wrapper. Returns text or None on failure."""
    client = _get_client()
    if not client:
        logger.warning("OpenAI client not available — falling back to heuristics")
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
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None


# ---------------------------------------------------------------------------
# Resume analysis
# ---------------------------------------------------------------------------

RESUME_SYSTEM_PROMPT = """
You are an expert HR analyst and technical recruiter with 15+ years of experience.
Analyze the provided resume text and return a JSON object with EXACTLY these keys:
{
  "candidate_name": string or null,
  "candidate_email": string or null,
  "summary": string (2-3 sentence professional summary),
  "skills": [list of technical and soft skills],
  "experience_years": number (estimated total years),
  "education": [list of degrees/certifications],
  "domain": string (primary domain: "AI/ML", "Web Development", "Data Science",
            "DevOps", "Mobile Development", "Cybersecurity", "Backend", "Frontend",
            "Full Stack", "Cloud", "Embedded Systems", or "General Software"),
  "resume_score": number 0-100 (holistic quality score),
  "score_breakdown": {
    "skills_relevance": 0-25,
    "experience_depth": 0-25,
    "education_quality": 0-20,
    "presentation_clarity": 0-15,
    "achievements_impact": 0-15
  }
}
Return ONLY valid JSON, no markdown fences, no extra text.
""".strip()


def analyze_resume_ai(text: str) -> dict:
    """Use AI to deeply analyze resume text. Returns structured dict."""
    result = _chat(RESUME_SYSTEM_PROMPT, f"Resume text:\n\n{text[:6000]}", temperature=0.3)
    if result:
        try:
            data = json.loads(result)
            # Coerce types
            data["experience_years"] = float(data.get("experience_years", 0) or 0)
            data["resume_score"]     = float(data.get("resume_score", 0) or 0)
            if not isinstance(data.get("skills"), list):
                data["skills"] = []
            if not isinstance(data.get("education"), list):
                data["education"] = []
            return data
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI resume analysis JSON")
    return _fallback_resume_analysis(text)


def _fallback_resume_analysis(text: str) -> dict:
    """Heuristic resume analysis when AI is unavailable."""
    text_lower = text.lower()
    skill_keywords = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "react", "vue", "angular", "node.js", "fastapi", "django", "flask",
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "git",
        "rest api", "graphql", "microservices", "linux", "html", "css",
    ]
    skills = [s for s in skill_keywords if s in text_lower]
    score = min(100, len(skills) * 5 + 20)

    # Try to detect domain
    domain_map = {
        "AI/ML": ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "computer vision"],
        "Web Development": ["react", "vue", "angular", "html", "css", "javascript", "frontend"],
        "DevOps": ["docker", "kubernetes", "ci/cd", "terraform", "ansible"],
        "Data Science": ["pandas", "numpy", "data analysis", "visualization", "statistics"],
        "Backend": ["fastapi", "django", "flask", "node.js", "spring", "rest api"],
    }
    domain = "General Software"
    best = 0
    for d, kws in domain_map.items():
        count = sum(1 for k in kws if k in text_lower)
        if count > best:
            best, domain = count, d

    return {
        "candidate_name":   None,
        "candidate_email":  None,
        "summary":          "Resume analysis completed using heuristic mode. Configure OpenAI API key for AI-powered analysis.",
        "skills":           skills,
        "experience_years": 0,
        "education":        [],
        "domain":           domain,
        "resume_score":     float(score),
        "score_breakdown":  {
            "skills_relevance": min(25, len(skills) * 2),
            "experience_depth": 10,
            "education_quality": 10,
            "presentation_clarity": 10,
            "achievements_impact": 10,
        },
    }


# ---------------------------------------------------------------------------
# Job fit scoring
# ---------------------------------------------------------------------------

JOB_FIT_SYSTEM_PROMPT = """
You are an expert hiring manager. Given a candidate's resume summary and a job description,
evaluate how well the candidate fits the role.
Return ONLY valid JSON with EXACTLY these keys:
{
  "fit_score": number 0-100,
  "fit_breakdown": {
    "skills_match": 0-40,
    "experience_match": 0-30,
    "domain_alignment": 0-20,
    "culture_fit": 0-10
  },
  "strengths": [list of 3-5 candidate strengths for this role],
  "gaps":      [list of 2-4 areas where candidate doesn't match],
  "improvements": [list of 3-5 concrete resume improvement suggestions]
}
""".strip()


def compute_job_fit(resume_summary: str, skills: List[str], job_role: str, job_description: str) -> dict:
    user_msg = (
        f"Job Role: {job_role}\n\n"
        f"Job Description:\n{job_description[:2000]}\n\n"
        f"Candidate Summary: {resume_summary}\n"
        f"Candidate Skills: {', '.join(skills[:30])}"
    )
    result = _chat(JOB_FIT_SYSTEM_PROMPT, user_msg, temperature=0.3)
    if result:
        try:
            data = json.loads(result)
            data["fit_score"] = float(data.get("fit_score", 0) or 0)
            return data
        except json.JSONDecodeError:
            pass
    return _fallback_job_fit(skills, job_role, job_description)


def _fallback_job_fit(skills: List[str], job_role: str, job_description: str) -> dict:
    jd_lower = job_description.lower()
    matched = [s for s in skills if s.lower() in jd_lower]
    fit_score = min(100, int((len(matched) / max(len(skills), 1)) * 80 + 10))
    return {
        "fit_score": float(fit_score),
        "fit_breakdown": {
            "skills_match": min(40, len(matched) * 5),
            "experience_match": 15,
            "domain_alignment": 10,
            "culture_fit": 5,
        },
        "strengths": [f"Proficient in {s}" for s in matched[:3]],
        "gaps": ["Configure OpenAI API key for detailed gap analysis"],
        "improvements": [
            "Quantify your achievements with metrics",
            "Add a professional summary tailored to this role",
            "Highlight relevant project outcomes",
        ],
    }


# ---------------------------------------------------------------------------
# Interview question generation
# ---------------------------------------------------------------------------

QUESTION_GEN_SYSTEM_PROMPT = """
You are a senior technical interviewer with expertise across all software engineering domains.
Generate interview questions as a JSON array of objects.
Each object must have:
{
  "question": "the question text",
  "difficulty": "easy" | "medium" | "hard",
  "category": "technical" | "behavioral"
}
Return ONLY the JSON array, no markdown, no extra text.
""".strip()


def generate_questions(
    role: str,
    skills: List[str],
    num_questions: int = 5,
    difficulty: str = "mixed",
    include_behavioral: bool = True,
) -> List[dict]:
    skill_str = ", ".join(skills[:10]) if skills else "general programming"
    diff_note = (
        f"Mix of easy, medium, and hard questions."
        if difficulty == "mixed"
        else f"All questions should be {difficulty} difficulty."
    )
    behavioral_note = (
        "Include 1-2 behavioral questions (STAR method)."
        if include_behavioral
        else "Only technical questions."
    )

    user_msg = (
        f"Role: {role}\n"
        f"Relevant skills: {skill_str}\n"
        f"Number of questions: {num_questions}\n"
        f"{diff_note}\n"
        f"{behavioral_note}\n\n"
        "Generate diverse, thoughtful questions that test both depth and breadth."
    )

    result = _chat(QUESTION_GEN_SYSTEM_PROMPT, user_msg, temperature=0.8)
    if result:
        try:
            # Strip potential code fences
            clean = re.sub(r"```[a-z]*\n?", "", result).strip()
            questions = json.loads(clean)
            if isinstance(questions, list) and questions:
                return questions[:num_questions]
        except json.JSONDecodeError:
            pass
    return _fallback_questions(role, num_questions, include_behavioral)


def _fallback_questions(role: str, num: int, include_behavioral: bool) -> List[dict]:
    role_l = role.lower()
    bank = {
        "technical": [
            {"question": f"Explain the core concepts you use most in {role}.", "difficulty": "easy",   "category": "technical"},
            {"question": f"Describe a challenging {role} problem you solved and how.", "difficulty": "medium", "category": "technical"},
            {"question": f"How do you ensure code quality and maintainability in {role} projects?", "difficulty": "medium", "category": "technical"},
            {"question": f"What design patterns do you commonly apply as a {role}?", "difficulty": "hard", "category": "technical"},
            {"question": "How do you approach performance optimization in your projects?", "difficulty": "hard", "category": "technical"},
            {"question": "Describe your testing strategy for complex features.", "difficulty": "medium", "category": "technical"},
        ],
        "behavioral": [
            {"question": "Describe a time you disagreed with a teammate. How did you resolve it?", "difficulty": "medium", "category": "behavioral"},
            {"question": "Tell me about a project you're most proud of and your contribution.", "difficulty": "easy", "category": "behavioral"},
        ],
    }

    questions = bank["technical"][:num]
    if include_behavioral and len(questions) < num:
        questions += bank["behavioral"][: num - len(questions)]
    return questions[:num]


# ---------------------------------------------------------------------------
# Answer evaluation
# ---------------------------------------------------------------------------

EVAL_SYSTEM_PROMPT = """
You are an experienced technical interviewer evaluating a candidate's answer.
Return ONLY valid JSON with EXACTLY these keys:
{
  "score": number 0-10,
  "is_correct": "yes" | "partial" | "no",
  "feedback": "2-3 sentence constructive feedback",
  "strengths": [list of 1-3 things done well],
  "weaknesses": [list of 1-2 areas to improve]
}
Be fair, specific, and constructive.
""".strip()


def evaluate_answer(question: str, answer: str, role: str = "") -> dict:
    user_msg = (
        f"Role being interviewed for: {role or 'Software Engineer'}\n"
        f"Question: {question}\n\n"
        f"Candidate's Answer:\n{answer}"
    )
    result = _chat(EVAL_SYSTEM_PROMPT, user_msg, temperature=0.4)
    if result:
        try:
            clean = re.sub(r"```[a-z]*\n?", "", result).strip()
            data = json.loads(clean)
            data["score"] = float(data.get("score", 5) or 5)
            return data
        except json.JSONDecodeError:
            pass
    return _fallback_evaluate(answer)


def _fallback_evaluate(answer: str) -> dict:
    length = len(answer.strip())
    if length > 300:
        score, verdict, fb = 8.0, "yes", "Detailed, well-structured answer demonstrating good understanding."
    elif length > 100:
        score, verdict, fb = 6.0, "partial", "Answer covers the basics but could use more depth and examples."
    else:
        score, verdict, fb = 4.0, "no", "Answer is too brief. Provide more detail and concrete examples."
    return {
        "score":      score,
        "is_correct": verdict,
        "feedback":   fb,
        "strengths":  ["Responded to the question"] if length > 50 else [],
        "weaknesses": ["Add more specific examples", "Elaborate on key concepts"],
    }
