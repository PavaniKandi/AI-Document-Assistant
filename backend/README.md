# Backend Documentation

Flask backend for the document Q&A app.

## Setup Instructions

### 1. Install Ollama

Download Ollama from: https://ollama.ai

**After installation, pull a model:**
```bash
ollama pull mistral
# or
ollama pull llama2
```

**Start Ollama (it runs on localhost:11434):**
```bash
ollama serve
```

### 2. Set up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Flask Server

```bash
python app.py
```

The backend will start on http://localhost:5001

## API Endpoints

### POST /upload
Upload a document (PDF, TXT, DOCX)

**Request:**
```
POST /upload
Content-Type: multipart/form-data

file: [document file]
```

**Response:**
```json
{
  "document_id": "uuid-here",
  "filename": "document.pdf"
}
```

### POST /ask
Ask a question about a document

**Request:**
```json
{
  "document_id": "uuid-here",
  "question": "What is the main topic?"
}
```

**Response:**
```json
{
  "answer": "The main topic is...",
  "question": "What is the main topic?"
}
```

### GET /health
Health check endpoint

### GET /history/<document_id>
Get saved Q&A history for a document

## How It Works

1. Upload a document
2. Extract text from the file
3. Save the file metadata, text, and Q&A history in SQLite
4. Build a prompt from the question and the most relevant text chunks
5. Send the prompt to Ollama and return the answer

## Notes

- Ollama runs locally, so no API keys are needed
- First request might take a while as the model loads
- Supports PDF, TXT, and DOCX files
- Default database path: `backend/data/document_qa.db`
