from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    question = Column(Text)
    answer = Column(Text)
    score = Column(Integer)
    feedback = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))