import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

PERSIST_DIR = "chroma_db"

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="CourseMate AI",
    page_icon="📚",
    layout="wide",
)

# --------------------------------------------------------------------------
# Cached resources (loaded once per session, not on every rerun)
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


@st.cache_resource(show_spinner=False)
def get_llm():
    return ChatMistralAI(model="mistral-small-2603")


@st.cache_resource(show_spinner=False)
def get_vectorstore(_embeddings):
    return Chroma(persist_directory=PERSIST_DIR, embedding_function=_embeddings)


embeddings = get_embeddings()
LLM_model = get_llm()
vectorstore = get_vectorstore(embeddings)

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are CourseMate AI, a strict RAG-based course assistant.

Answer the user's question ONLY using the provided context.

Rules:
- The context is your only source of truth.
- Never use outside knowledge.
- Never hallucinate or make assumptions.
- If the answer cannot be found in the context, say:
  "I couldn't find the answer in the provided course material."
- If only part of the answer is supported, provide only that supported information.
- You may summarize and explain the context, but do not add unsupported facts.
- Keep the answer clear and relevant.
""",
        ),
        (
            "human",
            """Context:
{context}

Question:
{input}

Answer the question using only the context.""",
        ),
    ]
)


def get_retriever():
    # Re-created each call so it always reflects the latest vectorstore state
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 10, "lambda_mult": 0.5},
    )


def ingest_pdf(uploaded_file, chunk_size=2000, chunk_overlap=300):
    """Save the uploaded PDF to a temp file, split it, and add it to Chroma."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(file_path=tmp_path)
        docs = loader.load()

        # Restore the original filename in metadata (temp files get a random name)
        for doc in docs:
            doc.metadata["source"] = uploaded_file.name

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = splitter.split_documents(docs)

        vectorstore.add_documents(chunks)
        return len(chunks)
    finally:
        os.remove(tmp_path)


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "ingested_files" not in st.session_state:
    st.session_state.ingested_files = set()

# --------------------------------------------------------------------------
# Sidebar — PDF upload
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("📄 Course Material")
    st.caption("Upload PDFs to add them to CourseMate's knowledge base.")

    uploaded_files = st.file_uploader(
        "Upload PDF(s)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.number_input("Chunk size", value=2000, min_value=200, step=100)
    with col2:
        chunk_overlap = st.number_input("Chunk overlap", value=300, min_value=0, step=50)

    if st.button("Process & Add to Knowledge Base", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one PDF first.")
        else:
            for f in uploaded_files:
                if f.name in st.session_state.ingested_files:
                    st.info(f"'{f.name}' already ingested this session — skipping.")
                    continue
                with st.spinner(f"Processing '{f.name}'..."):
                    try:
                        n_chunks = ingest_pdf(f, chunk_size, chunk_overlap)
                        st.session_state.ingested_files.add(f.name)
                        st.success(f"Added '{f.name}' ({n_chunks} chunks).")
                    except Exception as e:
                        st.error(f"Failed to process '{f.name}': {e}")

    if st.session_state.ingested_files:
        st.divider()
        st.caption("Ingested this session:")
        for name in sorted(st.session_state.ingested_files):
            st.write(f"✅ {name}")

    st.divider()
    if st.button("🗑️ Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --------------------------------------------------------------------------
# Main — Chat interface
# --------------------------------------------------------------------------
st.title("📚 CourseMate AI")
st.caption("Ask questions about your uploaded course material. Answers are grounded strictly in the retrieved context.")

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Sources"):
                for i, src in enumerate(msg["sources"], start=1):
                    st.markdown(f"**Chunk {i}** — `{src['source']}` (page {src['page']})")
                    st.text(src["excerpt"])

# Chat input
if query := st.chat_input("Ask a question about your course material..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            retriever = get_retriever()
            docs = retriever.invoke(query)

            if not docs:
                answer = "I couldn't find the answer in the provided course material."
                sources = []
            else:
                context = "\n\n".join(doc.page_content for doc in docs)
                final_prompt = RAG_PROMPT.invoke({"context": context, "input": query})
                response = LLM_model.invoke(final_prompt)
                answer = response.content
                sources = [
                    {
                        "source": doc.metadata.get("source", "unknown"),
                        "page": doc.metadata.get("page", "?"),
                        "excerpt": doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""),
                    }
                    for doc in docs
                ]

            st.markdown(answer)
            if sources:
                with st.expander("Sources"):
                    for i, src in enumerate(sources, start=1):
                        st.markdown(f"**Chunk {i}** — `{src['source']}` (page {src['page']})")
                        st.text(src["excerpt"])

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})