from fastapi import APIRouter, UploadFile, File
from app.services.resume_service import extract_text_from_pdf, analyze_resume

router = APIRouter()

@router.post("/analyze-resume")
async def analyze_resume_api(file: UploadFile = File(...)):

    contents = await file.read()

    with open("temp_resume.pdf", "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf("temp_resume.pdf")

    result = analyze_resume(text)

    return result