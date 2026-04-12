"""
Resume parsing service.
Supports PDF (via pdfplumber) and DOCX (via python-docx).
Safe version with error handling (no 500 crashes).
"""

import io
import logging
from pathlib import Path

logger = logging.getLogger("intellihire.resume")


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from an uploaded resume file.
    Supports .pdf and .docx.
    """
    try:
        if not file_bytes:
            raise ValueError("Empty file received")

        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            text = _extract_pdf(file_bytes)
        elif ext in (".docx", ".doc"):
            text = _extract_docx(file_bytes)
        else:
            # fallback: try plain text
            text = file_bytes.decode("utf-8", errors="replace")

        # 🔥 Ensure we always return something
        if not text or len(text.strip()) < 20:
            raise ValueError("No readable text found in file")

        return text

    except Exception as e:
        logger.error(f"Resume extraction failed: {e}")
        # ✅ Never crash → return fallback text
        return "Could not extract resume content. Please upload a proper PDF/DOCX file."


# ================= PDF ================= #

def _extract_pdf(data: bytes) -> str:
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                try:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
                except Exception:
                    continue

        if text_parts:
            return "\n".join(text_parts)

    except ImportError:
        logger.warning("pdfplumber not installed; trying pypdf")

    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")

    # 🔁 Fallback: pypdf
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(p.extract_text() or "" for p in reader.pages)

        if text.strip():
            return text

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")

    return ""


# ================= DOCX ================= #

def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document

        doc = Document(io.BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

        if text.strip():
            return text

    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")

    return ""