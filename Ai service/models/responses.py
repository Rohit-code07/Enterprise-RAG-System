from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    source: str
    page: int
    excerpt: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_added: int
    chunk_size: int
    chunk_overlap: int

class PreviewChunk(BaseModel):
    chunk_index: int
    page: int
    text: str

class PreviewResponse(BaseModel):
    total_chunks: int
    preview: List[PreviewChunk]

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    total_chunks: int
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
