from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=True)
    role         = Column(String(255), nullable=False)
    question     = Column(Text, nullable=False)
    difficulty   = Column(String(20), default="medium")   # easy | medium | hard
    category     = Column(String(50), default="technical") # technical | behavioral
    answer       = Column(Text)
    score        = Column(Float)
    feedback     = Column(Text)
    is_correct   = Column(String(10))   # yes | partial | no
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
