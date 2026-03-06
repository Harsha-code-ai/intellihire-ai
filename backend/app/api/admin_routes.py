from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.interview import Interview
from app.models.resume import ResumeAnalysis

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/admin/stats")
def get_stats(db: Session = Depends(get_db)):

    total_users = db.query(User).count()
    total_interviews = db.query(Interview).count()
    total_resumes = db.query(ResumeAnalysis).count()

    return {
        "total_users": total_users,
        "total_interviews": total_interviews,
        "total_resumes": total_resumes
    }