import os
import tempfile
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.responses import UploadResponse, PreviewResponse, PreviewChunk
from vectorstore.chroma_service import chroma_service

class DocumentService:
    @staticmethod
    def _split_pdf(temp_path: str, filename: str, chunk_size: int, chunk_overlap: int, document_id: str):
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
        
        if not documents:
            raise HTTPException(status_code=400, detail="No readable text was found in this PDF.")
            
        # RecursiveCharacterTextSplitter with sensible separators
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="PDF resulted in empty chunks.")
            
        # Inject metadata
        for i, chunk in enumerate(chunks):
            # PyPDFLoader usually puts page number in metadata['page'] (0-indexed)
            page_num = chunk.metadata.get('page', 0) + 1
            chunk.metadata.update({
                "document_id": document_id,
                "source": filename,
                "page": page_num,
                "chunk_index": i,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            })
            
        return chunks

    @staticmethod
    async def process_and_store_pdf(file: UploadFile, chunk_size: int, chunk_overlap: int) -> UploadResponse:
        suffix = Path(file.filename or "document.pdf").suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            
        document_id = str(uuid.uuid4())
        
        try:
            chunks = DocumentService._split_pdf(temp_path, file.filename, chunk_size, chunk_overlap, document_id)
            chroma_service.add_documents(chunks)
            
            return UploadResponse(
                document_id=document_id,
                filename=file.filename or "course-material.pdf",
                chunks_added=len(chunks),
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=422, detail=f"Unable to process this PDF: {error}") from error
        finally:
            os.unlink(temp_path)

    @staticmethod
    async def preview_chunks(file: UploadFile, chunk_size: int, chunk_overlap: int) -> PreviewResponse:
        suffix = Path(file.filename or "document.pdf").suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            
        document_id = "preview_doc"
        
        try:
            chunks = DocumentService._split_pdf(temp_path, file.filename, chunk_size, chunk_overlap, document_id)
            
            # Return first 5 chunks for preview
            preview_chunks = []
            for chunk in chunks[:5]:
                preview_chunks.append(
                    PreviewChunk(
                        chunk_index=chunk.metadata["chunk_index"],
                        page=chunk.metadata["page"],
                        text=chunk.page_content
                    )
                )
                
            return PreviewResponse(
                total_chunks=len(chunks),
                preview=preview_chunks
            )
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=422, detail=f"Unable to preview this PDF: {error}") from error
        finally:
            os.unlink(temp_path)
