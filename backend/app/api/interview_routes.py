"""
Interview routes:
  POST /api/interview/generate-questions  — generate AI questions
  POST /api/interview/evaluate-answer     — evaluate a candidate answer
  POST /api/interview/save                — persist an interview record
  GET  /api/interview/history             — list past interviews
  DELETE /api/interview/{id}              — delete a record
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.interview import Interview
from app.models.user import User
from app.schemas.schemas import (
    GenerateQuestionsRequest,
    QuestionOut,
    EvaluateAnswerRequest,
    EvaluationOut,
    SaveInterviewRequest,
    InterviewOut,
)
from app.services.ai_service import generate_questions, evaluate_answer
from app.security import get_optional_user

router = APIRouter()
logger = logging.getLogger("intellihire.interview")


@router.post("/generate-questions", response_model=List[QuestionOut], summary="Generate AI interview questions")
def gen_questions(
    data: GenerateQuestionsRequest,
    current_user: Optional[User] = Depends(get_optional_user),
):
    questions = generate_questions(
        role=data.role,
        skills=data.skills or [],
        num_questions=data.num_questions or 5,
        difficulty=data.difficulty or "mixed",
        include_behavioral=data.include_behavioral if data.include_behavioral is not None else True,
    )
    return [
        QuestionOut(
            question=q.get("question", ""),
            difficulty=q.get("difficulty", "medium"),
            category=q.get("category", "technical"),
        )
        for q in questions
    ]


@router.post("/evaluate-answer", response_model=EvaluationOut, summary="AI evaluation of a candidate answer")
def eval_answer(data: EvaluateAnswerRequest):
    result = evaluate_answer(
        question=data.question,
        answer=data.answer,
        role=data.role or "",
    )
    return EvaluationOut(
        score=result.get("score", 5),
        feedback=result.get("feedback", ""),
        is_correct=result.get("is_correct", "partial"),
        strengths=result.get("strengths", []),
        weaknesses=result.get("weaknesses", []),
    )


@router.post("/save", response_model=InterviewOut, summary="Save an interview Q&A record")
def save_interview(
    data: SaveInterviewRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    record = Interview(
        user_id=current_user.id if current_user else None,
        role=data.role,
        question=data.question,
        difficulty=data.difficulty or "medium",
        category=data.category or "technical",
        answer=data.answer,
        score=data.score,
        feedback=data.feedback,
        is_correct=data.is_correct or "partial",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.get("/history", response_model=List[InterviewOut], summary="Get interview history")
def get_history(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
    limit: int = 50,
):
    query = db.query(Interview)
    if current_user:
        query = query.filter(Interview.user_id == current_user.id)
    records = query.order_by(Interview.created_at.desc()).limit(limit).all()
    return [_serialize(r) for r in records]


@router.delete("/{interview_id}", summary="Delete an interview record")
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    record = db.query(Interview).filter(Interview.id == interview_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    if current_user and record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(record)
    db.commit()
    return {"message": "Deleted successfully"}


def _serialize(r: Interview) -> dict:
    return {
        "id":         r.id,
        "role":       r.role,
        "question":   r.question,
        "difficulty": r.difficulty,
        "category":   r.category,
        "answer":     r.answer,
        "score":      r.score,
        "feedback":   r.feedback,
        "is_correct": r.is_correct,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
