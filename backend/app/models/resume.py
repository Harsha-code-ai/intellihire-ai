from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename         = Column(String(255))
    candidate_name   = Column(String(120))
    candidate_email  = Column(String(255))
    extracted_text   = Column(Text)

    # AI-generated fields
    summary          = Column(Text)
    skills           = Column(Text)          # JSON list
    experience_years = Column(Float, default=0)
    education        = Column(Text)          # JSON list
    domain           = Column(String(100))   # "AI/ML", "Web Dev", etc.
    resume_score     = Column(Float, default=0)   # 0–100

    # Job matching
    job_role         = Column(String(255))
    job_description  = Column(Text)
    fit_score        = Column(Float, default=0)
    fit_breakdown    = Column(Text)          # JSON
    improvements     = Column(Text)          # JSON list

    created_at       = Column(DateTime(timezone=True), server_default=func.now())
