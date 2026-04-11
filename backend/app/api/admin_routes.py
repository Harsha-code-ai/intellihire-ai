"""
Admin routes — statistics and user management (admin-only).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.resume import ResumeAnalysis
from app.models.interview import Interview
from app.security import get_current_user

router = APIRouter()


def _require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats", summary="Platform statistics (admin only)")
def stats(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    return {
        "total_users":     db.query(User).count(),
        "total_resumes":   db.query(ResumeAnalysis).count(),
        "total_interviews":db.query(Interview).count(),
        "avg_resume_score": db.query(ResumeAnalysis).with_entities(
            db.query(ResumeAnalysis.resume_score).as_scalar()
        ).scalar() or 0,
    }


@router.get("/users", summary="List all users (admin only)")
def list_users(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "is_admin": u.is_admin} for u in users]
