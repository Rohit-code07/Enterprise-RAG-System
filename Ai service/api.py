from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import logging

from config import settings
from models.requests import ChatRequest
from models.responses import ChatResponse, UploadResponse, PreviewResponse, DocumentInfo
from services.document_service import DocumentService
from services.retrieval_service import RetrievalService
from services.llm_service import LLMService
from services.embedding_service import get_embeddings
from vectorstore.chroma_service import chroma_service
from services.exceptions import LLMProviderError

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CourseMate AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Load embeddings on startup
    get_embeddings()
    LLMService.get_llm()

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/documents", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(150)
):
    if chunk_overlap >= chunk_size:
        raise HTTPException(status_code=400, detail="chunk_overlap must be less than chunk_size")
        
    return await DocumentService.process_and_store_pdf(file, chunk_size, chunk_overlap)

@app.post("/api/documents/preview", response_model=PreviewResponse)
async def preview_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(150)
):
    if chunk_overlap >= chunk_size:
        raise HTTPException(status_code=400, detail="chunk_overlap must be less than chunk_size")
        
    return await DocumentService.preview_chunks(file, chunk_size, chunk_overlap)

@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    return chroma_service.get_all_documents_info()

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    success = chroma_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    return {"status": "success", "message": "Document deleted"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please enter a question.")
        
    documents = await RetrievalService.retrieve_relevant_chunks(question, request.document_id)
    
    try:
        answer, sources = await LLMService.generate_answer(question, documents)
    except LLMProviderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    
    return ChatResponse(answer=answer, sources=sources)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
