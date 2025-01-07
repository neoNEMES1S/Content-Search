# app/routers/upload.py
import uuid
import shutil
import zipfile
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from utils.db import get_connection
from utils.pdf_extractor import extract_text_from_pdf
import hashlib

router = APIRouter()

UPLOADS_DIR = Path("uploaded_pdfs")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

def compute_zip_hash(file_path: Path) -> str:
    """
    Compute SHA256 of the entire zip file so we can detect duplicates.
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

@router.post("/upload_zip")
async def upload_zip(archive: UploadFile = File(...)):
    """
    1. Receives a .zip file containing PDFs.
    2. Extracts them to a new folder (uuid).
    3. For each PDF, extracts text with Tika and inserts into Postgres.
    4. Returns the folder_id (uuid).
    """
    if not archive.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file.")

    folder_id = str(uuid.uuid4())
    extract_path = UPLOADS_DIR / folder_id
    extract_path.mkdir(parents=True, exist_ok=True)

    temp_zip_path = extract_path / "temp.zip"

    # 1) Save the zip
    try:
        with open(temp_zip_path, "wb") as tmp:
            chunk_size = 1024 * 1024
            while True:
                chunk = await archive.read(chunk_size)
                if not chunk:
                    break
                tmp.write(chunk)
    except Exception as e:
        shutil.rmtree(extract_path, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error saving zip: {str(e)}")

    # 2) Extract the zip
    try:
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
    except Exception as e:
        shutil.rmtree(extract_path, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error extracting zip: {str(e)}")
    finally:
        temp_zip_path.unlink(missing_ok=True)

    # 3) For each PDF, extract text and insert in DB
    pdf_files = list(extract_path.glob("**/*.pdf"))
    conn = get_connection()
    cur = conn.cursor()

    for pdf_file in pdf_files:
        pdf_text = extract_text_from_pdf(str(pdf_file))
        if pdf_text is None:
            pdf_text = ""  # or skip
        rel_name = pdf_file.relative_to(extract_path)
        file_uuid = str(uuid.uuid4())  # Each PDF can have its own UUID if desired

        # Insert into Postgres
        # We'll create tsv_content on the fly using to_tsvector
        cur.execute("""
            INSERT INTO pdf_documents (file_uuid, filename, content, tsv_content)
            VALUES (%s, %s, %s, to_tsvector('english', %s))
        """, (file_uuid, str(rel_name), pdf_text, pdf_text))

    conn.commit()
    cur.close()
    conn.close()

    return {"folder_id": folder_id, "pdf_count": len(pdf_files), "message": "Uploaded & extracted successfully"}
