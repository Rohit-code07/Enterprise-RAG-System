import asyncio
from vectorstore.chroma_service import chroma_service

def test():
    results = chroma_service.similarity_search_with_score("which problem is solved in PPT?", k=5)
    for doc, score in results:
        print(f"Score: {score:.4f}, Source: {doc.metadata.get('source')}, Content: {doc.page_content[:100]}")

test()
