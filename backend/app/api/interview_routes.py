from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import generate_question, evaluate_answer

router = APIRouter()

class RoleRequest(BaseModel):
    role: str

class AnswerRequest(BaseModel):
    answer: str


@router.post("/generate-question")
def get_question(data: RoleRequest):

    question = generate_question(data.role)

    return {
        "role": data.role,
        "question": question
    }


@router.post("/evaluate-answer")
def evaluate(data: AnswerRequest):

    result = evaluate_answer(data.answer)

    return result