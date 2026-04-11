"""
Pydantic schemas for request / response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    name:     str   = Field(..., min_length=2, max_length=120)
    email:    EmailStr
    password: str   = Field(..., min_length=6)


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    id:       int
    name:     str
    email:    str
    is_admin: bool

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserOut


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------

class ResumeAnalysisOut(BaseModel):
    id:               int
    filename:         str
    candidate_name:   Optional[str]
    candidate_email:  Optional[str]
    summary:          Optional[str]
    skills:           Optional[List[str]]
    experience_years: Optional[float]
    education:        Optional[List[str]]
    domain:           Optional[str]
    resume_score:     Optional[float]
    job_role:         Optional[str]
    fit_score:        Optional[float]
    fit_breakdown:    Optional[dict]
    improvements:     Optional[List[str]]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Interview
# ---------------------------------------------------------------------------

class GenerateQuestionsRequest(BaseModel):
    role:             str  = Field(..., min_length=2)
    skills:           Optional[List[str]] = []
    difficulty:       Optional[str]       = "mixed"   # easy | medium | hard | mixed
    num_questions:    Optional[int]       = Field(5, ge=1, le=20)
    include_behavioral: Optional[bool]   = True


class QuestionOut(BaseModel):
    question:   str
    difficulty: str
    category:   str


class EvaluateAnswerRequest(BaseModel):
    question: str
    answer:   str
    role:     Optional[str] = ""


class EvaluationOut(BaseModel):
    score:      float
    feedback:   str
    is_correct: str
    strengths:  Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []


class SaveInterviewRequest(BaseModel):
    role:       str
    question:   str
    difficulty: Optional[str] = "medium"
    category:   Optional[str] = "technical"
    answer:     str
    score:      float
    feedback:   str
    is_correct: Optional[str] = "partial"


class InterviewOut(BaseModel):
    id:         int
    role:       str
    question:   str
    difficulty: str
    category:   str
    answer:     Optional[str]
    score:      Optional[float]
    feedback:   Optional[str]
    is_correct: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True
