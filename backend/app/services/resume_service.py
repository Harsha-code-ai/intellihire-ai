"""
Resume parsing service.
Supports PDF (via pdfplumber) and DOCX (via python-docx).
"""

import os
import io
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger("intellihire.resume")


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from an uploaded resume file.
    Supports .pdf and .docx.
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _extract_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_bytes)
    else:
        # Try as plain text
        try:
            return file_bytes.decode("utf-8", errors="replace")
        except Exception:
            raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(data: bytes) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except ImportError:
        logger.warning("pdfplumber not installed; trying pypdf")
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")

    # Fallback: pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError("Could not extract text from PDF. Ensure the file is not scanned/image-only.")


def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise ValueError(f"Could not extract text from DOCX: {e}")
