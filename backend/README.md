# Backend Documentation

This is the Flask backend for the Document Q&A application.

## Setup Instructions

### 1. Install Ollama (Free LLM)

Ollama allows you to run LLMs locally for free. Download it from: https://ollama.ai

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

The backend will start on http://localhost:5000

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

## How It Works

1. Document Upload: Users upload a document (PDF, TXT, DOCX)
2. Text Extraction: The backend extracts text from the uploaded document
3. Storage: Document content is stored in memory (use a database in production)
4. Question Processing: When a question is asked:
   - Relevant context is extracted from the document
   - A prompt is created with the question and context
   - The prompt is sent to Ollama (running locally)
   - The LLM generates an answer
   - The answer is returned to the frontend

## Notes

- Ollama runs locally, so no API keys are needed
- The model runs on your machine (private and free)
- First request might take a while as the model loads
- Supports PDF, TXT, and DOCX files
