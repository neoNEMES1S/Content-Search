# app/utils/db.py
import psycopg2
from psycopg2.extensions import connection
from psycopg2 import sql
from core.config import settings
# from app.core.config import settings

print(settings.POSTGRES_HOST)

def get_connection() -> connection:
    """Create and return a psycopg2 connection to PostgreSQL."""
    conn = psycopg2.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
    )
    return conn

def init_db():
    """Create the pdf_documents table if it doesn't exist, 
       including a tsvector column and GIN index for full-text search."""
    conn = get_connection()
    cur = conn.cursor()

    # Create table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pdf_documents (
        id SERIAL PRIMARY KEY,
        file_uuid VARCHAR(36) NOT NULL,  -- e.g. to link if you want
        filename TEXT NOT NULL,
        content TEXT,
        tsv_content tsvector
    );
    """)

    # Create GIN index for tsv_content column
    cur.execute("""
    CREATE INDEX IF NOT EXISTS pdf_documents_tsv_idx
    ON pdf_documents
    USING GIN(tsv_content);
    """)

    # Create the zip_uploads table if needed:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS zip_uploads (
        id SERIAL PRIMARY KEY,
        zip_hash VARCHAR(64) NOT NULL UNIQUE,
        folder_id VARCHAR(36) NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()