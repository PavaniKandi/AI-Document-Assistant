# Customization and Advanced Features

## How to Improve Answers with Better Prompts

### The Current Prompt (Basic)
```python
# In backend/llm_service.py - prepare_context()
prompt = f"""Based on the following document, answer the question:

Document:
{context}

Question: {question}

Answer: """
```

This works, but can be improved!

---

## Advanced Prompt Strategies

### Strategy 1: Role-Based Prompts
```python
def prepare_context_with_role(question, document_text):
    prompt = f"""You are an expert document analyst. Your task is to answer 
questions about the provided document accurately and concisely.

Only use information from the document. Do not use outside knowledge.

Document:
{document_text[:MAX_CONTEXT_LENGTH]}

Question: {question}

Answer:"""
    return prompt
```

**Why it works:**
- Tells the LLM what role to play
- Sets expectations for accuracy
- Emphasizes document-only answers

### Strategy 2: Structured Output
```python
def prepare_context_structured(question, document_text):
    prompt = f"""Document:
{document_text[:MAX_CONTEXT_LENGTH]}

Question: {question}

Please provide your answer in this format:
1. Direct Answer: [Answer the question directly in 1-2 sentences]
2. Supporting Evidence: [Quote from document that supports this]
3. Confidence: [Low/Medium/High]

Answer:"""
    return prompt
```

**Why it works:**
- Forces structured thinking
- Provides evidence
- Includes confidence level

### Strategy 3: Question Classification
```python
def prepare_context_smart(question, document_text):
    # Determine question type
    if any(word in question.lower() for word in ['what', 'who']):
        style = "factual"
        instruction = "Answer with specific facts from the document."
    elif any(word in question.lower() for word in ['why', 'how']):
        style = "explanatory"
        instruction = "Provide a detailed explanation based on the document."
    elif any(word in question.lower() for word in ['which', 'compare']):
        style = "comparative"
        instruction = "Compare and contrast using document content."
    else:
        style = "general"
        instruction = "Answer thoroughly using the document."
    
    prompt = f"""{instruction}

Document:
{document_text[:MAX_CONTEXT_LENGTH]}

Question: {question}

Answer:"""
    return prompt
```

**Why it works:**
- Tailors response to question type
- More natural answers
- Better contextual understanding

---

## Context Selection Improvements

### Current Approach
```python
# Use first 4000 characters - TOO SIMPLE
context = document_text[:MAX_CONTEXT_LENGTH]
```

### Better: Find Relevant Paragraphs
```python
def find_relevant_paragraphs(question, document_text, num_paragraphs=3):
    """Find paragraphs most similar to the question"""
    paragraphs = document_text.split('\n\n')
    
    # Simple keyword matching
    question_words = set(question.lower().split())
    
    scored_paragraphs = []
    for para in paragraphs:
        # Count matching words
        para_words = set(para.lower().split())
        match_count = len(question_words & para_words)
        scored_paragraphs.append((match_count, para))
    
    # Sort by relevance
    scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
    
    # Return top paragraphs
    context = '\n\n'.join([para for _, para in scored_paragraphs[:num_paragraphs]])
    return context[:MAX_CONTEXT_LENGTH]

# Use in prompt:
relevant_context = find_relevant_paragraphs(question, document_text)
prompt = f"""...\n\nRelevant Document Sections:\n{relevant_context}\n\nQuestion: ..."""
```

### Advanced: Semantic Search (Requires Embeddings)
```python
# This requires installing: pip install sentence-transformers

from sentence_transformers import SentenceTransformer, util

def find_relevant_paragraphs_semantic(question, document_text):
    """Find paragraphs using semantic similarity"""
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast model
    
    paragraphs = document_text.split('\n\n')
    
    # Get embeddings
    question_embedding = model.encode(question, convert_to_tensor=True)
    paragraph_embeddings = model.encode(paragraphs, convert_to_tensor=True)
    
    # Calculate similarity
    cos_scores = util.pytorch_cos_sim(question_embedding, paragraph_embeddings)[0]
    
    # Get top paragraphs
    top_results = util.semantic_search(question_embedding, paragraph_embeddings, top_k=3)
    
    context = '\n\n'.join([paragraphs[idx] for idx, _ in top_results[0]])
    return context[:MAX_CONTEXT_LENGTH]
```

---

## Frontend Customization

### Change Colors

Edit `frontend/src/App.css`:

```css
/* Original - Purple gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Modern - Blue gradient */
background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%);

/* Warm - Orange gradient */
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Cool - Cyan gradient */
background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);

/* Dark mode - Dark gradient */
background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
```

### Add Dark Mode Toggle

```jsx
// In App.jsx
import { useState } from 'react'

function App() {
  const [darkMode, setDarkMode] = useState(false)
  
  return (
    <div className={darkMode ? 'dark-mode' : 'light-mode'}>
      <button onClick={() => setDarkMode(!darkMode)}>
        {darkMode ? '☀️ Light' : '🌙 Dark'}
      </button>
      {/* Rest of app */}
    </div>
  )
}
```

```css
/* In App.css */
.light-mode {
  background: white;
  color: #333;
}

.light-mode .app-container {
  background: white;
}

.dark-mode {
  background: #1a202c;
  color: #e2e8f0;
}

.dark-mode .app-container {
  background: #2d3748;
}
```

### Add Custom Fonts

```html
<!-- In frontend/index.html -->
<head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
</head>

<!-- In App.css -->
body {
  font-family: 'Poppins', sans-serif;
}
```

---

## Backend Enhancements

### Add Response Caching

```python
# backend/app.py - add at top
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_answer(question_hash, document_hash):
    """Cache frequently asked questions"""
    # Implementation
    pass

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    
    # Create cache key
    q_hash = hashlib.md5(data['question'].encode()).hexdigest()
    doc_hash = data['document_id']
    
    # Check cache first
    cached = cached_answer(q_hash, doc_hash)
    if cached:
        return jsonify({'answer': cached, 'cached': True})
    
    # Get answer if not cached
    answer = answer_question(data['question'], text)
    # Cache it
    cached_answer(q_hash, doc_hash)
    
    return jsonify({'answer': answer})
```

### Add Request Validation

```python
from marshmallow import Schema, fields, validate

class AskQuestionSchema(Schema):
    document_id = fields.Str(required=True, validate=validate.Length(min=1))
    question = fields.Str(required=True, validate=validate.Length(min=3, max=500))

@app.route('/ask', methods=['POST'])
def ask_question():
    schema = AskQuestionSchema()
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # Process valid request
```

### Add Logging

```python
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/upload', methods=['POST'])
def upload_document():
    logger.info(f"Upload request received: {request.files['file'].filename}")
    try:
        # ... process ...
        logger.info(f"Upload successful: {document_id}")
        return jsonify({'document_id': document_id})
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

---

## Analytics and Monitoring

### Track Usage Statistics

```python
# backend/analytics.py
from datetime import datetime

class Analytics:
    def __init__(self):
        self.stats = {
            'total_uploads': 0,
            'total_questions': 0,
            'documents': {},
        }
    
    def log_upload(self, doc_id, filename):
        self.stats['total_uploads'] += 1
        self.stats['documents'][doc_id] = {
            'filename': filename,
            'uploaded_at': datetime.now(),
            'questions': 0,
        }
    
    def log_question(self, doc_id):
        self.stats['total_questions'] += 1
        self.stats['documents'][doc_id]['questions'] += 1
    
    def get_stats(self):
        return self.stats

analytics = Analytics()

# In app.py endpoints:
@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify(analytics.get_stats())
```

---

## Model Configuration

### Fine-Tuning Ollama Responses

Different models have different behaviors:

```python
# backend/llm_service.py

def get_model_config(model_name):
    """Get optimal parameters for each model"""
    configs = {
        'mistral': {
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 40,
            'repeat_penalty': 1.1
        },
        'llama2': {
            'temperature': 0.8,
            'top_p': 0.95,
            'top_k': 40,
            'repeat_penalty': 1.0
        },
        'neural-chat': {
            'temperature': 0.6,
            'top_p': 0.9,
            'top_k': 40,
            'repeat_penalty': 1.2
        }
    }
    
    return configs.get(model_name, configs['mistral'])

def answer_question(question, document_text):
    prompt = prepare_context(question, document_text)
    config = get_model_config(OLLAMA_MODEL)
    
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            **config  # Spread config parameters
        },
        timeout=60
    )
```

### Understanding Parameters:
- **temperature** (0-1): Higher = more creative, lower = more focused
- **top_p** (0-1): Nucleus sampling - diversity of choices
- **top_k**: Only consider top K most likely next tokens
- **repeat_penalty**: Penalize repeating same tokens

---

## Security Enhancements

### Sanitize File Names

```python
import re

def sanitize_filename(filename):
    """Remove potentially dangerous characters"""
    # Keep only alphanumeric, dots, and underscores
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
```

### Limit File Size

```python
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

@app.route('/upload', methods=['POST'])
def upload_document():
    if request.content_length > app.config['MAX_CONTENT_LENGTH']:
        return jsonify({'error': 'File too large'}), 413
```

### Validate User Input

```python
from flask import escape

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    
    # Escape HTML special characters
    question = escape(data.get('question', ''))
    
    # Validate length
    if len(question) > 1000:
        return jsonify({'error': 'Question too long'}), 400
    
    if len(question) < 3:
        return jsonify({'error': 'Question too short'}), 400
```

---

## Performance Optimization

### Lazy Load Components

```jsx
// frontend/src/App.jsx
import { lazy, Suspense } from 'react'

const DocumentUpload = lazy(() => import('./components/DocumentUpload'))
const QuestionAnswering = lazy(() => import('./components/QuestionAnswering'))

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      {!documentId ? <DocumentUpload /> : <QuestionAnswering />}
    </Suspense>
  )
}
```

### Debounce Requests

```jsx
// frontend/src/utils/debounce.js
export function debounce(func, delay) {
  let timeoutId
  return function (...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

// In QuestionAnswering.jsx
import { debounce } from '../utils/debounce'

const debouncedAsk = debounce(handleAsk, 300)
```

---

## Prompt Examples for Different Tasks

### For Summarization
```
Summarize the following document in 3 bullet points:
{document}

Summary:
```

### For Key Points
```
Extract the 5 most important points from this document:
{document}

Key Points:
1.
2.
3.
4.
5.
```

### For Sentiment Analysis
```
Analyze the sentiment of the following text. Rate it as positive, negative, or neutral.
{document}

Sentiment: [Positive/Negative/Neutral]
Reasoning:
```

### For Q&A with Examples
```
Answer questions based on this document. Provide evidence from the text.

Document:
{document}

Example:
Q: What is AI?
A: AI is mentioned as... (provide quote)

Question: {question}
Answer:
```

---

These examples show how flexible you can make the application. Mix and match to create your solution.
