# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "pdf_search_db"

    class Config:
        env_file = ".env"

# IMPORTANT: Instantiate your Settings class!
settings = Settings()
