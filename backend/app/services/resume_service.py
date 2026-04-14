import logging
from io import BytesIO

from PyPDF2 import PdfReader
from docx import Document

logger = logging.getLogger("intellihire.resume")


# ================= EXTRACT TEXT =================

def extract_text(file_content: bytes, filename: str) -> str:
    try:
        text = ""

        # PDF
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(BytesIO(file_content))
            for page in reader.pages:
                text += page.extract_text() or ""

        # DOCX (with tables)
        elif filename.lower().endswith(".docx"):
            doc = Document(BytesIO(file_content))

            # paragraphs
            for para in doc.paragraphs:
                text += para.text + "\n"

            # tables (IMPORTANT FIX)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "

        # TXT
        else:
            text = file_content.decode("utf-8", errors="ignore")

        # clean text (IMPORTANT)
        clean_text = " ".join(text.split())

        return clean_text

    except Exception as e:
        logger.error(f"extract_text error: {e}")
        return ""


# ================= PROCESS RESUME =================

def process_resume(file_content: bytes, filename: str):
    text = extract_text(file_content, filename)

    return {
        "text": text,
        "length": len(text),
        "status": "processed" if text else "failed"
    }