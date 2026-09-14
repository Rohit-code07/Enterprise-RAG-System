from langchain_mistralai import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv 
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)
retriverse = vectorstore.as_retriever(
    search_type = "mmr",
    search_kwargs ={
        "k":4,
        "fetch_k" : 10,
"lambda_mult": 0.5
    }
)

LLM_model = ChatMistralAI(model = "mistral-small-2603")

prompt = ChatPromptTemplate.from_messages([
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
"""
    ),
    (
        "human",
        """Context:
{context}

Question:
{input}

Answer the question using only the context."""
    )
])



while True:
    query = input("you : ")
    if query == "0":
        break
    docs = retriverse.invoke(query)

    context = [doc.page_content for doc in docs]
    
    final_prompt = prompt.invoke({
        "context": context,
        "input": query
    })
    
    response = LLM_model.invoke(final_prompt)
    print("Assistant:", response.content)
    

