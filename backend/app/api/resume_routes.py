from fastapi import APIRouter, UploadFile, File
import tempfile

from app.services.resume_service import extract_text_from_pdf, analyze_resume

router = APIRouter()

@router.post("/analyze-resume")
async def analyze_resume_api(file: UploadFile = File(...)):

    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        temp_path = tmp.name

    text = extract_text_from_pdf(temp_path)

    result = analyze_resume(text)

    return result