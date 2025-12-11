# Document Q&A Application

A full-stack application for uploading documents and asking questions about them using a local LLM (Ollama).

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

### Step 1: Install Ollama (Free Local LLM)

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

Server starts on `http://localhost:5000`

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
4. Get answers powered by your local LLM!

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

## Key Code Concepts

### Frontend - React Component Pattern
```jsx
// App.jsx manages document state
const [documentId, setDocumentId] = useState(null);

const handleDocumentUpload = async (file) => {
  const response = await axios.post('/api/upload', formData);
  setDocumentId(response.data.document_id);
};
```

### Backend - Flask Endpoints
```python
@app.route('/upload', methods=['POST'])
def upload_document():
    # Extract file, save it, extract text, store in memory
    return jsonify({'document_id': doc_id})

@app.route('/ask', methods=['POST'])
def ask_question():
    # Get question and document ID
    # Create prompt with context
    # Call Ollama
    # Return answer
```

### Document Processing
```python
def extract_text_from_file(filepath):
    # Handles .pdf, .txt, .docx
    # Returns extracted text as string
```

### LLM Integration (Ollama)
```python
def answer_question(question, document_text):
    # Prepare prompt with question + context
    # POST to http://localhost:11434/api/generate
    # Get LLM response
```

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

## Free LLM Models You Can Use

With Ollama, you can use any of these free models:

```bash
ollama pull mistral      # Recommended - fast, good quality
ollama pull llama2       # Meta's Llama 2
ollama pull neural-chat  # Good for conversations
ollama pull orca-mini    # Lighter weight
```

Switch models by changing `OLLAMA_MODEL` in `backend/.env`

## Learning Path

### Phase 1: Understand the Components
1. Read through `frontend/src/App.jsx` - understand React state management
2. Read through `backend/app.py` - understand Flask endpoints
3. Read through `backend/llm_service.py` - understand LLM integration

### Phase 2: Modify & Extend
1. Add more file formats (Word, Excel, etc.)
2. Improve prompt engineering in `llm_service.py`
3. Add conversation history (currently only in frontend)
4. Add semantic search instead of simple context selection
5. Store documents in a real database (SQLite, PostgreSQL)

### Phase 3: Advanced Features
1. Add authentication (user accounts)
2. Implement RAG (Retrieval Augmented Generation)
3. Add document chunking for better context
4. Use embeddings for semantic search
5. Add web scraping to ask about web pages

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

## Production Deployment

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

## Next Steps

1. ✅ Run locally and test with a sample document
2. 🔧 Customize the UI colors/styling
3. 📚 Add more document types
4. 🔍 Improve question answering with better prompts
5. 📊 Add document analytics
6. 🔐 Add user authentication

Happy coding! 🚀
