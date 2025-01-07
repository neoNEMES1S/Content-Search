# app/routers/search.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
from utils.db import get_connection

router = APIRouter()

@router.get("/search")
def search_pdfs(keyword: str = Query(..., min_length=1)):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Modified query to show content and make the search more flexible
        cur.execute("""
            SELECT id, file_uuid, filename, content
            FROM pdf_documents
            WHERE tsv_content @@ plainto_tsquery('english', %s)
            LIMIT 10
        """, [keyword])
        
        rows = cur.fetchall()
        
        # Single results processing
        results = [{
            "id": row[0],
            "file_uuid": row[1],
            "filename": row[2],
            "content_preview": row[3][:200] if row[3] else "",  # Preview first 200 chars
            "download_url": f"/files/{row[2]}"
        } for row in rows]

        return JSONResponse({
            "keyword": keyword, 
            "results": results,
            "count": len(results)
        })

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.get("/debug/documents")
def list_documents():
    """Debug endpoint to list all documents in the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, file_uuid, filename, 
                   LEFT(content, 100) as content_preview, 
                   LENGTH(content) as content_length
            FROM pdf_documents
            LIMIT 5
        """)
        
        rows = cur.fetchall()
        return {
            "document_count": len(rows),
            "samples": [{
                "id": row[0],
                "file_uuid": row[1],
                "filename": row[2],
                "content_preview": row[3],
                "content_length": row[4]
            } for row in rows]
        }
    finally:
        cur.close()
        conn.close()
