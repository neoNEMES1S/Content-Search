# PDF Search with Apache Tika and Postgres

This FastAPI project lets you:

1. Upload a .zip of PDFs.
2. Extract text via Apache Tika.
3. Store the extracted text in Postgres with a full-text index.
4. Search via Postgres tsvector.

## Setup
1. Create a database in Postgres:
   ```sql
   CREATE DATABASE pdf_search_db;