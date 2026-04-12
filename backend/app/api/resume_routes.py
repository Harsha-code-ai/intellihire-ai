"""
Resume routes:
Upload + AI analysis + job fit + history
SAFE VERSION (no crashes)
"""

import json
import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.database import get_db
from app.models.resume import ResumeAnalysis
from app.models.user import User
from app.services.resume_service import extract_text
from app.services.ai_service import analyze_resume_ai, compute_job_fit
from app.security import get_optional_user

router = APIRouter()
logger = logging.getLogger("intellihire.resume")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload-resume", summary="Upload resume for AI analysis")
async def upload_resume(
    file: UploadFile = File(...),
    job_role: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    try:
        # ================= FILE READ ================= #
        contents = await file.read()

        if not contents:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 5MB)")

        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename missing")

        # ================= TEXT EXTRACTION ================= #
        text = extract_text(contents, file.filename)

        if not text or len(text.strip()) < 30:
            raise HTTPException(status_code=422, detail="Could not extract meaningful text")

        # ================= AI ANALYSIS ================= #
        try:
            analysis = analyze_resume_ai(text)
        except Exception as e:
            logger.error(f"AI failed: {e}")
            analysis = {
                "summary": "Fallback analysis used",
                "skills": [],
                "experience_years": 0,
                "education": [],
                "domain": "General",
                "resume_score": 50
            }

        # ================= JOB FIT ================= #
        fit_data = {}
        if job_role and job_description:
            try:
                fit_data = compute_job_fit(
                    analysis.get("summary", ""),
                    analysis.get("skills", []),
                    job_role,
                    job_description
                )
            except Exception as e:
                logger.warning(f"Job fit failed: {e}")
                fit_data = {}

        # ================= SAVE TO DB ================= #
        record = ResumeAnalysis(
            user_id=current_user.id if current_user else None,
            filename=file.filename,
            candidate_name=analysis.get("candidate_name"),
            candidate_email=analysis.get("candidate_email"),
            extracted_text=text[:10000],
            summary=analysis.get("summary"),
            skills=json.dumps(analysis.get("skills", [])),
            experience_years=analysis.get("experience_years", 0),
            education=json.dumps(analysis.get("education", [])),
            domain=analysis.get("domain"),
            resume_score=analysis.get("resume_score", 0),
            job_role=job_role,
            job_description=job_description,
            fit_score=fit_data.get("fit_score", 0),
            fit_breakdown=json.dumps(fit_data.get("fit_breakdown", {})),
            improvements=json.dumps(
                fit_data.get("improvements", []) or analysis.get("improvements", [])
            ),
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "id": record.id,
            "filename": record.filename,
            "summary": record.summary,
            "skills": json.loads(record.skills or "[]"),
            "resume_score": record.resume_score,
            "fit_score": record.fit_score,
            "message": "Resume processed successfully"
        }

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Resume processing failed")


# ================= HISTORY ================= #

@router.get("/history")
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return []

    records = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == current_user.id
    ).all()

    return [
        {
            "id": r.id,
            "filename": r.filename,
            "score": r.resume_score
        } for r in records
    ]