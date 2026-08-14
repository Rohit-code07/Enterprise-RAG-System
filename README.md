# 📚 CourseMate AI

CourseMate AI is a strict RAG (Retrieval-Augmented Generation) course assistant.
Upload your course PDFs, and ask questions — answers are generated **only** from
the content you've uploaded, with no outside knowledge or hallucination.

Built with **Streamlit**, **LangChain**, **Mistral AI**, **HuggingFace embeddings**,
and **Chroma** as the vector store.

---

## ✨ Features

- 📄 Upload one or more PDFs directly from the browser
- 🔍 Automatic chunking + embedding into a persistent Chroma vector database
- 💬 Chat interface with full conversation history
- 🧠 MMR (Maximal Marginal Relevance) retrieval for diverse, relevant context
- 📎 "Sources" panel under each answer showing exactly which chunks (file + page)
  were used
- 🚫 Refuses to answer when the material doesn't contain the answer, instead of guessing

---

## 🗂️ Project Structure

```
.
├── app.py              # Streamlit app (upload + chat UI)
├── requirements.txt    # Python dependencies
├── chroma_db/          # Persistent vector store (created automatically)
└── .env                # Your API keys (not committed)
```

---

## ⚙️ Setup

### 1. Clone / copy the project files

Make sure `app.py` and `requirements.txt` are in the same folder.

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_mistral_api_key_here
```

> Get a key from [console.mistral.ai](https://console.mistral.ai/).

### 5. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## 🚀 Usage

1. Open the app in your browser.
2. In the **sidebar**, upload one or more PDF files (e.g. lecture notes, textbooks).
3. Adjust **chunk size** / **chunk overlap** if needed (defaults: 2000 / 300).
4. Click **"Process & Add to Knowledge Base"** — this splits the PDF and stores
   its embeddings in `chroma_db/`.
5. Type a question in the chat box at the bottom of the main panel.
6. Expand **Sources** under any answer to see which parts of the document were used.

Uploaded documents persist across sessions since they're saved to `chroma_db/`
on disk — you don't need to re-upload every time you restart the app.

---

## 🧠 How it works

1. **Ingestion**: `PyPDFLoader` extracts text from the PDF → `RecursiveCharacterTextSplitter`
   splits it into overlapping chunks → `HuggingFaceEmbeddings`
   (`sentence-transformers/all-mpnet-base-v2`) embeds each chunk → chunks are stored
   in a local **Chroma** vector database.
2. **Retrieval**: On each question, the retriever runs an **MMR search** (`k=4`,
   `fetch_k=10`, `lambda_mult=0.5`) to fetch relevant, non-redundant chunks.
3. **Generation**: The retrieved chunks are inserted into a strict system prompt
   and sent to `mistral-small-2603` via `ChatMistralAI`, which is instructed to
   answer **only** from the given context.

---

## 🛠️ Tech Stack

| Component        | Tool                                            |
|-------------------|--------------------------------------------------|
| UI                | Streamlit                                        |
| LLM               | Mistral AI (`mistral-small-2603`)                |
| Embeddings        | `sentence-transformers/all-mpnet-base-v2`        |
| Vector store      | Chroma (persisted locally)                       |
| PDF parsing       | `pypdf` via `PyPDFLoader`                        |
| Orchestration     | LangChain                                        |

---

## 📌 Notes / Troubleshooting

- **No answer / "couldn't find the answer"**: Make sure you've uploaded and
  processed a relevant PDF first — an empty `chroma_db` has no context to draw from.
- **Slow first run**: The embedding model downloads on first use; subsequent
  runs are faster and cached via `@st.cache_resource`.
- **API errors**: Confirm `MISTRAL_API_KEY` is set correctly in `.env` and that
  `.env` sits next to `app.py`.
- **Resetting the knowledge base**: Delete the `chroma_db/` folder to start fresh.

---

## 📄 License

For personal/educational use. Adapt as needed for your own course material.
