from typing import List, Dict, Any, Tuple
from langchain_chroma import Chroma
from langchain_core.documents import Document
from config import settings
from services.embedding_service import get_embeddings
import chromadb
from chromadb.config import Settings as ChromaSettings

class ChromaService:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.persist_directory = settings.PERSIST_DIRECTORY
        
        # We use a persistent client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection_name = "coursemate_collection"
        
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )

    def add_documents(self, documents: List[Document]) -> None:
        self.vectorstore.add_documents(documents)

    def delete_document(self, document_id: str) -> bool:
        """Deletes all chunks associated with a document_id."""
        try:
            collection = self.client.get_collection(self.collection_name)
            collection.delete(where={"document_id": document_id})
            return True
        except Exception:
            return False

    def get_all_documents_info(self) -> List[Dict[str, Any]]:
        """Returns aggregated info about all uploaded documents."""
        try:
            collection = self.client.get_collection(self.collection_name)
            # Fetch all metadatas to aggregate unique documents
            results = collection.get(include=["metadatas"])
            metadatas = results.get("metadatas", [])
            
            doc_map = {}
            for meta in metadatas:
                doc_id = meta.get("document_id")
                if not doc_id:
                    continue
                if doc_id not in doc_map:
                    doc_map[doc_id] = {
                        "document_id": doc_id,
                        "filename": meta.get("source", "Unknown"),
                        "total_chunks": 0,
                        "chunk_size": meta.get("chunk_size"),
                        "chunk_overlap": meta.get("chunk_overlap")
                    }
                doc_map[doc_id]["total_chunks"] += 1
                
            return list(doc_map.values())
        except Exception:
            return []

    def get_retriever(self, search_kwargs: Dict[str, Any], filter_kwargs: Dict[str, Any] = None):
        """Returns a retriever object configured with MMR."""
        # Using MMR for diversity
        if filter_kwargs:
            search_kwargs["filter"] = filter_kwargs
            
        return self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs
        )
        
    def similarity_search_with_score(self, query: str, k: int, filter_kwargs: Dict[str, Any] = None) -> List[Tuple[Document, float]]:
        """Returns documents and their L2 distance scores. Lower score is better (closer)."""
        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter_kwargs)

chroma_service = ChromaService()
