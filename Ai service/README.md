## CourseMate AI

The project has two ways to use the same course-material RAG workflow:

- `Ui.py` is the original Streamlit interface.
- `api.py` powers the React interface in `../frontend`.

### Run the React app

1. In `Ai service`, create an `.env` file with `MISTRAL_API_KEY`.
2. Install the Python dependencies, then start the API:

   ```bash
   uvicorn api:app --reload --port 8000
   ```

3. In `frontend`, install the JavaScript dependencies and start Vite:

   ```bash
   npm install
   npm run dev
   ```

The UI is served at `http://localhost:5173`, and calls the FastAPI service at
`http://localhost:8000`. Set `VITE_API_URL` in `frontend/.env` if the API runs elsewhere.
