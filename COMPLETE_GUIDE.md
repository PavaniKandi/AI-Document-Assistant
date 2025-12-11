# Complete Setup and Learning Guide

## Pre-Requirements

Before you start, make sure you have:

1. **Python 3.8+** - Check with: `python3 --version`
2. **Node.js & npm** - Check with: `node --version` and `npm --version`
3. **Ollama** - Download from https://ollama.ai
4. **A terminal** - Mac: Terminal, Windows: Command Prompt or PowerShell

---

## Complete Step-by-Step Setup

### Step 1: Download and Install Ollama

**macOS/Linux:**
1. Go to https://ollama.ai
2. Download and install
3. Run in terminal: `ollama serve`

**Windows:**
1. Download from https://ollama.ai
2. Install the application
3. Ollama will run as a service automatically

### Step 2: Pull an LLM Model

Open a NEW terminal while Ollama is running:

```bash
# Pull Mistral (recommended - fast, good quality)
ollama pull mistral

# Alternative options:
ollama pull llama2          # Meta's Llama 2 - more capable but slower
ollama pull neural-chat     # Good for conversations
ollama pull orca-mini       # Lightweight, faster
```

**What's happening:**
- Downloading model from ollama.ai (~3-7GB depending on model)
- Storing locally on your machine
- Can now run offline!

### Step 3: Navigate to Project

```bash
cd /Users/Pavani/Documents/python/doc-qa-app
```

### Step 4: Run Setup Script

**macOS/Linux:**
```bash
chmod +x setup.sh    # Make script executable
./setup.sh           # Run setup
```

**Windows:**
```bash
setup.bat
```

**What the script does:**
- Checks if Ollama is running
- Creates Python virtual environment
- Installs Python dependencies
- Installs Node.js dependencies

### Step 5: Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate    # macOS/Linux
# or
venv\Scripts\activate       # Windows

python app.py
```

You should see:
```
WARNING: This is a development server. Do not use it in production.
Running on http://127.0.0.1:5000
```

### Step 6: Start Frontend (Terminal 2 - NEW TERMINAL)

```bash
cd frontend
npm run dev
```

You should see:
```
Local:   http://localhost:3000/
```

### Step 7: Open the Application

1. Open your browser
2. Go to: **http://localhost:3000**
3. You should see the upload interface!

---

## 🧪 Testing the Application

### Test Document Upload

1. Create a test file `test_document.txt`:
   ```
   Python is a powerful programming language.
   It is widely used for web development, data science, and AI.
   The language emphasizes code readability and simplicity.
   ```

2. In the app:
   - Click "Browse Files" or drag-drop the file
   - Wait for upload confirmation
   - You should see "✅ Loaded: test_document.txt"

### Test Question Answering

1. Ask a question like: "What is Python used for?"
2. Click "Ask"
3. Wait for answer (first request takes ~30 seconds as model loads)
4. You should see a response about Python

**Expected flow:**
```
User Input: "What is Python used for?"
         ↓
Frontend sends to Backend
         ↓
Backend sends to Ollama
         ↓
Ollama runs the model
         ↓
Answer appears in UI
```

---

## Understanding the Code

### Project Structure

```
doc-qa-app/
├── frontend/                 # React app
│   ├── src/
│   │   ├── App.jsx          # Main component - manages state
│   │   ├── components/      # Reusable components
│   │   │   ├── DocumentUpload.jsx   # File upload UI
│   │   │   └── QuestionAnswering.jsx # Q&A UI
│   │   ├── App.css          # Styling
│   │   └── main.jsx         # Entry point
│   ├── index.html           # HTML template
│   ├── package.json         # Dependencies
│   └── vite.config.js       # Build config
│
├── backend/                  # Flask server
│   ├── app.py               # Main Flask app - API endpoints
│   ├── document_processor.py # Extract text from files
│   ├── llm_service.py       # Ollama integration
│   ├── .env                 # Configuration
│   ├── requirements.txt      # Python dependencies
│   └── uploads/             # Uploaded files stored here
│
├── README.md                # Project overview
├── LEARNING_GUIDE.md        # Code concepts explained
├── setup.sh / setup.bat     # Quick setup script
└── .gitignore              # Git configuration
```

### Key Files Explained

#### `frontend/src/App.jsx` - The Brain
```jsx
// State: What the app remembers
const [documentId, setDocumentId] = useState(null);
const [documentName, setDocumentName] = useState(null);

// When user uploads: send to backend
const handleDocumentUpload = async (file) => {
  const response = await axios.post('/api/upload', formData);
  // Store the document ID
  setDocumentId(response.data.document_id);
};

// Conditional rendering: show different UI based on state
return (
  {!documentId ? <DocumentUpload /> : <QuestionAnswering />}
);
```

#### `backend/app.py` - The Server
```python
# Endpoint 1: Receive uploaded file
@app.route('/upload', methods=['POST'])
def upload_document():
    file = request.files['file']  # Get file from frontend
    text = extract_text_from_file(file)  # Process file
    documents_store[doc_id] = {'text': text}  # Store
    return {'document_id': doc_id}  # Send back to frontend

# Endpoint 2: Answer question
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json  # Get question from frontend
    text = documents_store[data['document_id']]['text']  # Get document
    answer = answer_question(data['question'], text)  # Call Ollama
    return {'answer': answer}  # Send back answer
```

#### `backend/llm_service.py` - The Magic
```python
def answer_question(question, document_text):
    # Create a prompt the LLM will understand
    prompt = f"""Document: {document_text}
    Question: {question}
    Answer:"""
    
    # Send to Ollama running locally
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt}
    )
    
    # Return the generated answer
    return response.json()['response']
```

---

## Customization Examples

### Change the LLM Model

Edit `backend/.env`:
```env
OLLAMA_MODEL=mistral      # Change to llama2, neural-chat, etc
```

Then restart the backend.

### Change Colors

Edit `frontend/src/App.css`:
```css
.app-container h1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* Change the color hex codes ^ */
}
```

### Improve Answer Quality

Edit `backend/llm_service.py`, improve the prompt:
```python
def prepare_context(question, document_text):
    # Current: uses first 4000 characters
    # Better: find most relevant paragraphs
    # Best: use semantic search
    
    prompt = f"""You are an expert assistant analyzing documents.
    
Document:
{context}

Question: {question}

Provide a clear, concise answer based only on the document content.
Answer:"""
    
    return prompt
```

### Add More File Types

Edit `backend/document_processor.py`:
```python
def extract_text_from_html(filepath):
    # Add HTML extraction
    pass

def extract_text_from_file(filepath):
    # Add 'html' to supported formats
    if file_extension == 'html':
        return extract_text_from_html(filepath)
```

---

## Troubleshooting

### "Cannot connect to Ollama"
**Problem:** Backend says Ollama is not running
**Solution:**
```bash
# In a separate terminal, run:
ollama serve

# Check it's working:
curl http://localhost:11434/api/tags
```

### "Model not found"
**Problem:** Ollama says model isn't installed
**Solution:**
```bash
# Pull the model:
ollama pull mistral

# Verify:
ollama list
```

### "ModuleNotFoundError: No module named 'flask'"
**Problem:** Python dependencies not installed
**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "npm: command not found"
**Problem:** Node.js not installed
**Solution:**
1. Download from nodejs.org
2. Install Node.js (includes npm)
3. Verify: `node --version`

### App is slow/freezing
**Problem:** Model is too large or system is overloaded
**Solution:**
```bash
# Use a lighter model:
ollama pull neural-chat
# Update backend/.env to use it
OLLAMA_MODEL=neural-chat
```

### File upload fails
**Problem:** File type not allowed or too large
**Solution:**
- Use: PDF, TXT, or DOCX files
- Max size: 10MB
- Check `uploads/` folder permissions

---

## Learning Progression

### Level 1: Understand (Week 1)
- [ ] Read through all code files
- [ ] Understand the data flow
- [ ] Run the app and test it
- [ ] Read LEARNING_GUIDE.md

### Level 2: Modify (Week 2)
- [ ] Change UI colors
- [ ] Add a new button with a function
- [ ] Try different LLM models
- [ ] Customize the prompt

### Level 3: Extend (Week 3)
- [ ] Add a new file type (HTML, Excel, etc.)
- [ ] Save documents to a real database (SQLite)
- [ ] Add user authentication
- [ ] Implement semantic search for better context

### Level 4: Deploy (Week 4)
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Deploy backend to Heroku/Railway
- [ ] Set up environment variables
- [ ] Test production app

---

## What You've Learned

By building this app, you understand:

1. **Frontend** - React, components, state, HTTP requests
2. **Backend** - Flask, API design, file handling
3. **Full-Stack** - How frontend and backend communicate
4. **LLMs** - How to integrate AI models into apps
5. **Architecture** - Project structure and best practices
6. **Deployment** - How to put apps on the internet

---

## Next Projects

1. Chat App - Real-time chat with WebSockets
2. Todo App - Full CRUD operations with database
3. Image Gallery - Upload and display images
4. Weather App - API integration and data visualization
5. Blog - Full CMS with user authentication

## Resources

| Topic | Resource |
|-------|----------|
| React | https://react.dev |
| Flask | https://flask.palletsprojects.com |
| LLMs | https://ollama.ai |
| Python | https://python.org |
| JavaScript | https://developer.mozilla.org/en-US/docs/Web/JavaScript |

## Getting Help

1. Check error messages - They usually tell you what's wrong
2. Google the error - Usually someone had the same issue
3. Check LEARNING_GUIDE.md - Detailed code explanations
4. Review the comments - Code files have helpful comments
