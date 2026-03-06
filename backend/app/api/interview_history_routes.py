from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.interview import Interview

router = APIRouter()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/save-interview")

def save_interview(data: dict, db: Session = Depends(get_db)):

    interview = Interview(

        role=data["role"],
        question=data["question"],
        answer=data["answer"],
        score=data["score"],
        feedback=data["feedback"]
    )

    db.add(interview)
    db.commit()

    return {"message": "Interview saved"}


@router.get("/interview-history")

def get_history(db: Session = Depends(get_db)):

    interviews = db.query(Interview).all()

    return interviews