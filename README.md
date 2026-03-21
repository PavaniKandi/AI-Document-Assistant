# Document Q&A

Document Q&A is a full-stack app for uploading documents and asking questions about their contents with a locally running Ollama model. It supports PDF, TXT, DOCX, and DOC files, keeps uploaded documents and question history in SQLite, and includes sign-in so each user sees their own saved work.

## Stack

- Frontend: React, Vite, Axios
- Backend: Flask, Python
- Database: SQLite
- Local model runtime: Ollama
- Document parsing: PyPDF2, python-docx

## Features

- Email/password sign-in
- Upload support for PDF, TXT, DOCX, and DOC
- Question answering against uploaded documents
- Saved document list in the left panel
- Per-document question history in the right panel
- SQLite-backed persistence for users, documents, and chat history

## Project Structure

```text
frontend/
  src/
    App.jsx
    components/
backend/
  app.py
  database.py
  document_processor.py
  llm_service.py
```

## Running Locally

### 1. Start Ollama

Install Ollama, then pull a model and start the service:

```bash
ollama pull mistral
ollama serve
```

The backend expects Ollama at `http://localhost:11434`.

### 2. Start the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The Flask server runs on `http://localhost:5001`.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:3000`.

## Notes

- Uploaded files are stored under `backend/uploads/`.
- SQLite data is stored under `backend/data/`.
- This project is set up for local development and demo use.
