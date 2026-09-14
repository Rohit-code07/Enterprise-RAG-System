from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingService:
    _instance = None

    @classmethod
    def get_embeddings(cls) -> HuggingFaceEmbeddings:
        if cls._instance is None:
            # Load embedding model only once
            cls._instance = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )
        return cls._instance

get_embeddings = EmbeddingService.get_embeddings
