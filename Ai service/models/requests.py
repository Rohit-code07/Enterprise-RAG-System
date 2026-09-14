from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_id: Optional[str] = None

class PreviewRequest(BaseModel):
    chunk_size: int = Field(1000, ge=300, le=3000)
    chunk_overlap: int = Field(150, ge=0, le=500)
