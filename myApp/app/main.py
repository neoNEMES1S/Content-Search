# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from routers import search, upload
from utils.db import init_db

from pathlib import Path

app = FastAPI(title="PDF Search with Clickable URLs")

UPLOADS_DIR = Path("uploaded_pdfs")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# 1) Mount the uploaded_pdfs folder as /files
app.mount("/files", StaticFiles(directory=UPLOADS_DIR), name="files")

# Initialize the DB (creates table, index if needed)
#@app.on_event("startup")
#def on_startup():
#    init_db()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
      <head><title>PDF Search with Clickable URLs</title></head>
      <body>
        <h1>Welcome!</h1>
        <p>Try <a href="/docs">/docs</a> to upload a ZIP and then search your PDFs.</p>
      </body>
    </html>
    """

# Register the routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(search.router, prefix="/api", tags=["search"])
