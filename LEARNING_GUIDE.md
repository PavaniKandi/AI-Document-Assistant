# Code Learning Guide

## Project Overview

This application demonstrates:
- React: Component-based UI, state management, HTTP requests
- Python/Flask: REST API, file handling, server-side logic
- LLM Integration: Using local models via Ollama
- Full-stack development: Frontend-backend communication

---

## Learning Concepts

### React Frontend

#### **State Management**
Location: `frontend/src/App.jsx`

```jsx
const [documentId, setDocumentId] = useState(null);
const [documentName, setDocumentName] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```

**What's happening:**
- `useState()` creates reactive state variables
- When state changes, component re-renders
- UI updates automatically based on state

#### **HTTP Requests with Axios**
```jsx
const response = await axios.post('/api/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

**What's happening:**
- `axios.post()` sends a POST request to Flask backend
- `await` waits for response
- `/api/upload` is proxied to `http://localhost:5000/upload`
- `formData` contains the file

#### **Conditional Rendering**
```jsx
{!documentId ? (
  <DocumentUpload onUpload={handleDocumentUpload} loading={loading} />
) : (
  <>
    <div className="document-info">...</div>
    <QuestionAnswering documentId={documentId} />
  </>
)}
```

**What's happening:**
- If no document: show upload component
- If document loaded: show Q&A component
- This pattern controls what the user sees

#### **Component Props**
```jsx
function DocumentUpload({ onUpload, loading }) {
  // onUpload is a callback function passed from parent
  // loading is a boolean indicating upload status
}
```

**Key Learning:**
- Parent passes data down via props
- Child components are reusable
- Props are read-only in child

### Python Backend

#### **Flask Routes**
Location: `backend/app.py`

```python
@app.route('/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    text_content = extract_text_from_file(filepath)
    documents_store[document_id] = {'text_content': text_content}
    return jsonify({'document_id': document_id})
```

**What's happening:**
1. `@app.route()` decorator defines HTTP endpoint
2. `request.files['file']` gets uploaded file
3. File is saved to disk
4. Text is extracted from file
5. Data stored in memory dictionary
6. `jsonify()` returns JSON response

#### **File Upload Handling**
```python
file = request.files['file']
filename = secure_filename(file.filename)  # Prevents path traversal attacks
filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
file.save(filepath)
```

**Security Concepts:**
- `secure_filename()` prevents malicious filenames
- Files saved outside public web root
- File type validation (check extension)

#### **In-Memory Data Store**
```python
documents_store = {}  # Global dictionary

documents_store[document_id] = {
    'filename': filename,
    'text_content': text_content
}
```

**Key Learning:**
- Simple storage for demo (use database in production!)
- Each document has a unique ID
- Fast access via dictionary

### Document Processing

Location: `backend/document_processor.py`

```python
def extract_text_from_pdf(filepath):
    with open(filepath, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text
```

**What's happening:**
- Uses PyPDF2 library to read PDF
- Loops through all pages
- Extracts text from each page
- Concatenates into single string

**Why different functions?**
- Each file format requires different parsing
- PDF: binary format, needs PyPDF2
- DOCX: XML format, needs python-docx
- TXT: plain text, just read file

### LLM Integration (The Core Feature)

Location: `backend/llm_service.py`

```python
def answer_question(question, document_text):
    prompt = f"""Based on the following document, answer the question:

Document:
{document_text[:MAX_CONTEXT_LENGTH]}

Question: {question}

Answer: """
    
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt}
    )
    return response.json()['response']
```

**The Prompt Engineering:**
- Format matters! The model expects structure
- Provide context (document text)
- Clearly state the question
- "Answer: " tells model where to start writing

**Ollama API Call:**
- POST to `http://localhost:11434/api/generate`
- Send model name and prompt
- Get back generated text
- This is how you use local LLMs!

---

## Request/Response Flow

### Document Upload Flow
```
User selects file
        ↓
React: handleDocumentUpload() → axios.post('/api/upload')
        ↓
Flask: @app.route('/upload') receives file
        ↓
Extract text with PyPDF2/python-docx
        ↓
Store in documents_store[document_id]
        ↓
Return JSON: {document_id, filename}
        ↓
React: setState(documentId)
        ↓
UI Updates: Show Q&A component
```

### Question Answering Flow
```
User types question and clicks "Ask"
        ↓
React: handleAsk() → axios.post('/api/ask')
        ↓
Flask: @app.route('/ask') receives {document_id, question}
        ↓
Retrieve document_text from documents_store
        ↓
Create prompt with question + document text
        ↓
Ollama: requests.post() to http://localhost:11434/api/generate
        ↓
LLM generates answer using local model
        ↓
Return JSON: {answer}
        ↓
React: setState(answer), add to history
        ↓
UI: Display answer in answer box
```

---

## Key Concepts to Master

### 1. **Component Lifecycle**
```jsx
function MyComponent() {
  // Runs every render
  const [count, setCount] = useState(0);
  
  // Update state
  const handleClick = () => setCount(count + 1);
  
  // JSX is returned and rendered
  return <button onClick={handleClick}>{count}</button>;
}
```

### 2. **Props vs State**
```jsx
// Props: passed from parent, read-only
function Child({ name }) {  // name is a prop
  // name = "John"
}

// State: owned by component, can change
function Parent() {
  const [name, setName] = useState("John");
  return <Child name={name} />;
}
```

### 3. **Async/Await Pattern**
```jsx
const handleUpload = async (file) => {
  try {
    const response = await axios.post('/api/upload', formData);
    // Use response here
    setDocumentId(response.data.document_id);
  } catch (err) {
    setError(err.message);
  }
};
```

### 4. **REST API Design**
```
GET  /documents       - List all documents
POST /upload          - Create new document
GET  /documents/{id}  - Get specific document
POST /ask             - Ask question about document
```

### 5. **Error Handling**
```python
try:
    # Attempt operation
    text = extract_text_from_file(filepath)
except Exception as e:
    # Handle gracefully
    return jsonify({'error': str(e)}), 500
```

---

## How to Modify the Code

### Add a New Supported File Format

**Step 1:** Add extraction function (`backend/document_processor.py`)
```python
def extract_text_from_docx(filepath):
    doc = DocxDocument(filepath)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text
```

**Step 2:** Update main function
```python
def extract_text_from_file(filepath):
    file_extension = filepath.rsplit('.', 1)[1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(filepath)
    elif file_extension == 'docx':
        return extract_text_from_docx(filepath)  # NEW!
    # ... more types
```

**Step 3:** Update allowed extensions (`backend/app.py`)
```python
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}  # Add 'doc'
```

### Improve Question Answering

**Current approach:** Use first 4000 characters of document

**Better approach:** Use semantic search
```python
def prepare_context(question, document_text):
    # Find relevant paragraphs using keyword matching
    # Or use embeddings for semantic similarity
    # Include only most relevant parts
```

### Add Document Chat History to Backend

**Current approach:** History stored only in frontend

**Better approach:** Store in backend database
```python
# In app.py
@app.route('/history/<document_id>', methods=['GET'])
def get_history(document_id):
    # Return all questions and answers for this document
    history = documents_store[document_id].get('history', [])
    return jsonify({'history': history})
```

---

## Exercises for Learning

### Exercise 1: Add a Reset Button
**Task:** Add button to clear Q&A history without uploading new document

**Solution:** Add state and button in `QuestionAnswering.jsx`
```jsx
const [history, setHistory] = useState([]);

const handleReset = () => setHistory([]);

return (
  <>
    <button onClick={handleReset}>Clear History</button>
    {/* ... rest of component */}
  </>
);
```

### Exercise 2: Add Character Count
**Task:** Show how many characters were extracted from document

**Solution:** In `App.jsx`
```jsx
const [characterCount, setCharacterCount] = useState(0);

const handleDocumentUpload = async (file) => {
  const response = await axios.post('/api/upload', formData);
  // Call backend endpoint to get character count
  setCharacterCount(response.data.char_count);
};

return <p>{characterCount} characters loaded</p>;
```

### Exercise 3: Add Loading Spinner
**Task:** Show animated spinner while waiting for answer

**Solution:** In `QuestionAnswering.jsx`
```jsx
{loading && <div className="spinner">⏳ Thinking...</div>}
```

### Exercise 4: Switch LLM Models
**Task:** Allow user to select between Mistral and Llama2

**Solution:** Add model selection in frontend, pass to backend
```jsx
<select value={model} onChange={(e) => setModel(e.target.value)}>
  <option>mistral</option>
  <option>llama2</option>
</select>
```

---

## Dependencies Explained

### Frontend (package.json)
- react: UI library
- react-dom: Renders React in browser
- axios: HTTP client
- vite: Fast build tool

### Backend (requirements.txt)
- flask: Web framework
- flask-cors: Enable cross-origin requests
- PyPDF2: Extract text from PDFs
- python-docx: Extract text from DOCX files
- requests: HTTP client for calling Ollama

---

## Next Learning Steps

1. **Run the app** - See how all pieces work together
2. **Modify the UI** - Change colors, layout, add features
3. **Improve prompts** - Better question answering
4. **Add persistence** - Use SQLite instead of in-memory storage
5. **Deploy** - Put on production server

## Useful Resources

- React Docs: https://react.dev
- Flask Docs: https://flask.palletsprojects.com
- Ollama Models: https://ollama.ai/library
- Axios Docs: https://axios-http.com

Happy learning!
