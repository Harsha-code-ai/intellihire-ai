from sqlalchemy import Column, Integer, Text, ForeignKey
from app.database import Base

class ResumeAnalysis(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    extracted_text = Column(Text)
    skills_detected = Column(Text)
    role_match = Column(Integer)
    suggestions = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))