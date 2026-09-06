import io
from pathlib import Path

from docx import Document
from fastapi import HTTPException
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def extract_text(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        document = Document(io.BytesIO(data))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    if suffix == ".doc":
        raise HTTPException(status_code=415, detail="Legacy .doc files are not supported. Save it as .docx first.")
    raise HTTPException(status_code=415, detail="Upload a PDF or DOCX file.")
