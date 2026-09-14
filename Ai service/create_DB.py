from dotenv import load_dotenv 
from langchain_community.document_loaders import PyPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
load_dotenv()

file_path = r"C:\Users\rohit\Projects\CourseMate Ai\Document loader\Deep+Learning+Ian+Goodfellow.pdf"
data = PyPDFLoader(file_path=file_path)
docs = data.load()
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 2000,
    chunk_overlap = 300
)
chunks = splitter.split_documents(docs)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
vectorstores = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory = "chroma_db"
)
