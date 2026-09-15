from __future__ import annotations

import logging
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from prompts.rag_prompt import get_rag_prompt
from config import settings
from models.responses import Source
from services.exceptions import LLMProviderError, LLMRateLimitError, LLMNotFoundError, LLMAuthenticationError


logger = logging.getLogger(__name__)


NOT_FOUND_MESSAGE = (
    "I couldn't find the answer in the provided documents."
)


class LLMService:
    """
    Service responsible for generating grounded answers from retrieved
    RAG documents.

    Supported providers:
    - OpenAI
    - Mistral
    - Gemini
    """

    _llm = None
    _prompt = None
    _chain = None

    @classmethod
    def get_llm(cls):
        """
        Create and cache the configured LLM.
        """

        if cls._llm is not None:
            return cls._llm

        provider = settings.LLM_PROVIDER.lower().strip()

        try:

            if provider == "openai":

                if not settings.OPENAI_API_KEY:
                    raise ValueError(
                        "OPENAI_API_KEY is not configured."
                    )

                cls._llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0,
                )

            elif provider == "mistral":

                if not settings.MISTRAL_API_KEY:
                    raise ValueError(
                        "MISTRAL_API_KEY is not configured."
                    )

                cls._llm = ChatMistralAI(
                    model="mistral-small-latest",
                    api_key=settings.MISTRAL_API_KEY,
                    temperature=0,
                )

            elif provider == "gemini":

                if not settings.GEMINI_API_KEY:
                    raise ValueError(
                        "GEMINI_API_KEY is not configured."
                    )

                cls._llm = ChatGoogleGenerativeAI(
                    model="gemini-3.6-flash",
                    google_api_key=settings.GEMINI_API_KEY,
                    temperature=0,
                )

            else:
                raise ValueError(
                    f"Unsupported LLM provider: {provider}"
                )

            logger.info(
                "LLM initialized successfully: %s",
                provider,
            )

            return cls._llm

        except Exception as error:

            logger.exception(
                "Failed to initialize LLM provider: %s",
                error,
            )

            cls._llm = None
            raise

    @classmethod
    def get_prompt(cls):
        """
        Create and cache the RAG prompt.
        """

        if cls._prompt is None:
            cls._prompt = get_rag_prompt()

        return cls._prompt

    @classmethod
    def get_chain(cls):
        """
        Create and cache the prompt → LLM chain.
        """

        if cls._chain is not None:
            return cls._chain

        llm = cls.get_llm()
        prompt = cls.get_prompt()

        cls._chain = prompt | llm

        return cls._chain

    @classmethod
    async def generate_answer(
        cls,
        question: str,
        documents: List[Document],
    ) -> Tuple[str, List[Source]]:
        """
        Generate a grounded answer using retrieved documents.

        The LLM receives only the retrieved document context.
        """

        if not question or not question.strip():
            return (
                "Please enter a question.",
                [],
            )

        if not documents:
            return (
                NOT_FOUND_MESSAGE,
                [],
            )

        question = question.strip()

        # Build context from retrieved documents.
        context_parts = []

        for index, document in enumerate(documents, start=1):

            source = document.metadata.get(
                "source",
                "Unknown source",
            )

            page = document.metadata.get(
                "page",
                "Unknown page",
            )

            context_parts.append(
                f"""
[Document Chunk {index}]
Source: {source}
Page: {page}

{document.page_content}
""".strip()
            )

        context = "\n\n---\n\n".join(context_parts)

        try:

            chain = cls.get_chain()

            response = await chain.ainvoke(
                {
                    "context": context,
                    "question": question,
                }
            )

            # Handle models that return a list of content blocks (like Gemini)
            if isinstance(response.content, list):
                text_parts = []
                for block in response.content:
                    if isinstance(block, dict) and "text" in block:
                        text_parts.append(block["text"])
                    elif isinstance(block, str):
                        text_parts.append(block)
                answer = "".join(text_parts).strip()
            else:
                answer = str(response.content).strip()

            if not answer:
                answer = NOT_FOUND_MESSAGE

        except Exception as error:

            logger.exception(
                "LLM Error: %s",
                error,
            )

            error_msg = str(error).lower()
            if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
                raise LLMRateLimitError("Mistral API rate limit exceeded. Please wait a moment and try again.")
            elif "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg:
                raise LLMAuthenticationError()
            elif "404" in error_msg and ("not found" in error_msg or "no longer available" in error_msg):
                raise LLMNotFoundError()
            elif "timeout" in error_msg or "network" in error_msg:
                raise LLMProviderError("LLM API network timeout. Please try again.", status_code=504)

            raise LLMProviderError(f"Error connecting to the LLM provider: {str(error)}", status_code=502)

        # Build source information.
        sources: List[Source] = []

        for document in documents:

            page = document.metadata.get(
                "page",
                0,
            )

            # PyPDFLoader usually stores pages as zero-indexed.
            # Convert to human-readable page number.
            if isinstance(page, int):
                page = page + 1

            excerpt = document.page_content.strip()

            if len(excerpt) > 250:
                excerpt = excerpt[:250] + "..."

            sources.append(
                Source(
                    source=document.metadata.get(
                        "source",
                        "Unknown",
                    ),
                    page=page,
                    excerpt=excerpt,
                )
            )

        return answer, sources

    @classmethod
    def reset(cls):
        """
        Reset cached LLM, prompt and chain.

        Useful when changing provider/configuration
        without restarting the application.
        """

        cls._llm = None
        cls._prompt = None
        cls._chain = None