from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):

    # LLM
    LLM_PROVIDER: str = "gemini"

    MISTRAL_API_KEY: Optional[str] = ""
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Retrieval defaults
    RETRIEVER_K: int = 5
    RETRIEVER_FETCH_K: int = 20
    RETRIEVER_LAMBDA_MULT: float = 0.5

    # Distance threshold
    MAX_DISTANCE_THRESHOLD: float = 1.2

    # ChromaDB
    PERSIST_DIRECTORY: str = str(BASE_DIR / "chroma_db")

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()