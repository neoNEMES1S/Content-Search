# app/utils/pdf_extractor.py
import os
import tempfile
from tika import parser  # pip install tika
from typing import Optional

# Optional: If you see warnings about the Java VM, do this once:
# from tika import initVM
# initVM()

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text from a PDF using Apache Tika.
    Returns the extracted text or None on error.
    """
    try:
        parsed = parser.from_file(pdf_path)
        return parsed.get("content", "") or ""
    except Exception as e:
        print(f"Error extracting text with Tika: {e}")
        return None
