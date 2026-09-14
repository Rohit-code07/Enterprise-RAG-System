from typing import List
from langchain_core.documents import Document
from vectorstore.chroma_service import chroma_service
from config import settings
import logging

logger = logging.getLogger(__name__)

class RetrievalService:
    @staticmethod
    async def retrieve_relevant_chunks(query: str, document_id: str = None) -> List[Document]:
        filter_kwargs = {"document_id": document_id} if document_id else None
        
        # 1. We fetch K documents with scores to do relevance filtering.
        # Chroma similarity_search_with_score returns (Document, float).
        # For L2 distance, lower is more similar.
        results = chroma_service.similarity_search_with_score(
            query=query, 
            k=settings.RETRIEVER_FETCH_K,
            filter_kwargs=filter_kwargs
        )
        
        if not results:
            return []
        
        # Remove aggressive threshold filtering. We log the best score instead.
        best_score = min(score for doc, score in results)
        
        # Log retrieval debugging info
        logger.info(f"\n--- RETRIEVAL DEBUGGING ---")
        logger.info(f"Question: {query}")
        logger.info(f"Retrieved documents: {len(results)}")
        for idx, (doc, score) in enumerate(results, 1):
            logger.info(f"\nResult {idx}:")
            logger.info(f"score: {score:.4f}")
            logger.info(f"page: {doc.metadata.get('page', 'unknown')}")
            logger.info(f"source: {doc.metadata.get('source', 'unknown')}")
            logger.info(f"content: {doc.page_content[:200]}...")
        logger.info(f"---------------------------\n")
            
        # Now we do the actual MMR retrieval to get diverse results
        search_kwargs = {
            "k": settings.RETRIEVER_K,
            "fetch_k": settings.RETRIEVER_FETCH_K,
            "lambda_mult": settings.RETRIEVER_LAMBDA_MULT
        }
        retriever = chroma_service.get_retriever(search_kwargs=search_kwargs, filter_kwargs=filter_kwargs)
        
        # ainvoke will do MMR
        mmr_docs = await retriever.ainvoke(query)
        
        # Note: mmr_docs doesn't have scores, but we know there's at least one good match.
        return mmr_docs
