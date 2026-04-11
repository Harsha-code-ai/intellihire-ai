"""
Resume routes:
  POST /api/resume/upload-resume   — upload + extract text + AI analysis
  POST /api/resume/analyze         — analyze already-extracted text
  POST /api/resume/job-fit         — match resume to a job description
  GET  /api/resume/history         — list past analyses for current user
  GET  /api/resume/{id}            — get a single analysis
"""

import json
import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.resume import ResumeAnalysis
from app.models.user import User
from app.services.resume_service import extract_text
from app.services.ai_service import analyze_resume_ai, compute_job_fit
from app.security import get_optional_user

router = APIRouter()
logger = logging.getLogger("intellihire.resume")

ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword", "text/plain"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload-resume", summary="Upload a resume file for full AI analysis")
async def upload_resume(
    file: UploadFile = File(...),
    job_role: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    # Validate file
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max size is 5 MB.")
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    # Extract text
    try:
        text = extract_text(contents, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not text or len(text.strip()) < 50:
        raise HTTPException(status_code=422, detail="Could not extract meaningful text from the resume.")

    # AI analysis
    analysis = analyze_resume_ai(text)

    # Job fit if provided
    fit_data = {}
    if job_role and job_description:
        fit_data = compute_job_fit(
            resume_summary=analysis.get("summary", ""),
            skills=analysis.get("skills", []),
            job_role=job_role,
            job_description=job_description,
        )

    # Persist to DB
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

    return _serialize(record, analysis, fit_data)


@router.post("/job-fit", summary="Compute job fit for an existing analysis")
def job_fit(
    analysis_id: int,
    job_role: str,
    job_description: str,
    db: Session = Depends(get_db),
):
    record = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    skills = json.loads(record.skills or "[]")
    fit_data = compute_job_fit(record.summary or "", skills, job_role, job_description)

    record.job_role = job_role
    record.job_description = job_description
    record.fit_score = fit_data.get("fit_score", 0)
    record.fit_breakdown = json.dumps(fit_data.get("fit_breakdown", {}))
    record.improvements = json.dumps(fit_data.get("improvements", []))
    db.commit()
    db.refresh(record)

    return {
        "analysis_id": record.id,
        "job_role": job_role,
        "fit_score": fit_data.get("fit_score"),
        "fit_breakdown": fit_data.get("fit_breakdown"),
        "strengths": fit_data.get("strengths", []),
        "gaps": fit_data.get("gaps", []),
        "improvements": fit_data.get("improvements", []),
    }


@router.get("/history", summary="Get resume analysis history for current user")
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    if not current_user:
        return []
    records = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.user_id == current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(20)
        .all()
    )
    return [_serialize_summary(r) for r in records]


@router.get("/{analysis_id}", summary="Get full resume analysis by ID")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    record = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _serialize(record, {}, {})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serialize(record: ResumeAnalysis, ai_data: dict, fit_data: dict) -> dict:
    score_breakdown = ai_data.get("score_breakdown", {})
    return {
        "id":               record.id,
        "filename":         record.filename,
        "candidate_name":   record.candidate_name,
        "candidate_email":  record.candidate_email,
        "summary":          record.summary,
        "skills":           json.loads(record.skills or "[]"),
        "experience_years": record.experience_years,
        "education":        json.loads(record.education or "[]"),
        "domain":           record.domain,
        "resume_score":     record.resume_score,
        "score_breakdown":  score_breakdown,
        "job_role":         record.job_role,
        "fit_score":        record.fit_score,
        "fit_breakdown":    json.loads(record.fit_breakdown or "{}"),
        "improvements":     json.loads(record.improvements or "[]"),
        "strengths":        fit_data.get("strengths", []),
        "gaps":             fit_data.get("gaps", []),
        "created_at":       record.created_at.isoformat() if record.created_at else None,
    }


def _serialize_summary(record: ResumeAnalysis) -> dict:
    return {
        "id":           record.id,
        "filename":     record.filename,
        "domain":       record.domain,
        "resume_score": record.resume_score,
        "fit_score":    record.fit_score,
        "job_role":     record.job_role,
        "created_at":   record.created_at.isoformat() if record.created_at else None,
    }
