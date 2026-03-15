# Document Q&A Application

A small full-stack app for uploading documents and asking questions about them with a local Ollama model.

## Architecture

```
├── frontend/              # React + Vite
│   ├── src/
│   │   ├── App.jsx       # Main app component
│   │   ├── components/   # DocumentUpload, QuestionAnswering
│   │   └── main.jsx
│   └── package.json
│
└── backend/              # Flask + Python
    ├── app.py            # Flask server
    ├── document_processor.py  # Text extraction
    ├── llm_service.py    # Ollama integration
    └── requirements.txt
```

## Quick Start

### Step 1: Install Ollama

1. Download Ollama from https://ollama.ai
2. Install and run it
3. Pull a model:
   ```bash
   ollama pull mistral
   ```
4. Keep Ollama running (it serves on `http://localhost:11434`)

### Step 2: Set Up Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
```

Server starts on `http://localhost:5001`

### Step 3: Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend starts on `http://localhost:3000`

### Step 4: Use the App

1. Open http://localhost:3000
2. Upload a document (PDF, TXT, or DOCX)
3. Ask questions about the document
4. Review the answer in the UI

## How It Works

### Document Upload Flow
1. User selects a file via drag-drop or file picker
2. Frontend sends file to backend /upload endpoint
3. Backend:
   - Saves the file
   - Extracts text from file
   - Stores document content
   - Returns document ID
4. Frontend displays success and enables Q&A

### Question Answering Flow
1. User enters a question
2. Frontend sends to backend /ask endpoint
3. Backend:
   - Retrieves document text
   - Creates a prompt
   - Sends prompt to Ollama API
   - Ollama runs the model and returns answer
4. Frontend displays answer and adds to history

## Notes

- Uploaded files are stored in `backend/uploads/`
- Extracted text and Q&A history are stored in `backend/data/document_qa.db`
- The backend trims and chunks document text before sending context to Ollama

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18, Vite, Axios |
| Backend | Flask, Python 3 |
| LLM | Ollama (local, free) |
| File Processing | PyPDF2, python-docx |
| Communication | HTTP REST API |

## Supported File Formats

- **PDF** - Extracted using PyPDF2
- **TXT** - Read as plain text
- **DOCX** - Extracted using python-docx

## Models

Any Ollama text model should work. A few easy options:

```bash
ollama pull mistral
ollama pull llama2
ollama pull neural-chat
ollama pull orca-mini
```

Switch models by changing `OLLAMA_MODEL` in `backend/.env`

## Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check it's on localhost:11434
- Try in terminal: `curl http://localhost:11434/api/tags`

### "Model not found"
- Pull the model: `ollama pull mistral`
- Check OLLAMA_MODEL in `backend/.env`

### Slow responses
- First request takes time as model loads
- Subsequent requests are faster
- Try a lighter model: `ollama pull neural-chat`

### File upload fails
- Check file size (max 10MB)
- Supported: PDF, TXT, DOCX
- Check `uploads/` folder has write permissions

## Deployment Notes

### Frontend
```bash
npm run build  # Creates dist/
# Deploy dist/ to Netlify, Vercel, or your server
```

### Backend
- Use Gunicorn instead of Flask dev server
- Store files in cloud storage (AWS S3, etc.)
- Use a real database
- Add authentication
- Deploy to Heroku, AWS, DigitalOcean, etc.

## Next Ideas

1. Add better retrieval with embeddings
2. Show citations or page references
3. Save document summaries
4. Add auth if you want multi-user support
