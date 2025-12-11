from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import document processing and LLM modules
from document_processor import extract_text_from_file
from llm_service import answer_question

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Configure CORS properly for file uploads
CORS(app, resources={
    r"/upload": {"origins": ["http://localhost:3000"]},
    r"/ask": {"origins": ["http://localhost:3000"]},
    r"/health": {"origins": ["http://localhost:3000"]},
    r"/*": {"origins": "*"}
}, supports_credentials=True)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# In-memory storage of documents (in production, use a database)
documents_store = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload a document and extract its text content.
    
    Returns:
        JSON with document_id and filename
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PDF, TXT, or DOCX'}), 400
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_{filename}")
        
        # Save file
        file.save(filepath)
        
        # Extract text from document
        text_content = extract_text_from_file(filepath)
        
        # Store document info
        documents_store[document_id] = {
            'filename': filename,
            'filepath': filepath,
            'text_content': text_content
        }
        
        return jsonify({
            'document_id': document_id,
            'filename': filename,
            'message': 'Document uploaded successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Ask a question about an uploaded document.
    
    Request body:
        - document_id: ID of the uploaded document
        - question: The question to ask
    
    Returns:
        JSON with the answer
    """
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        question = data.get('question')
        
        if not document_id or not question:
            return jsonify({'error': 'Missing document_id or question'}), 400
        
        if document_id not in documents_store:
            return jsonify({'error': 'Document not found'}), 404
        
        # Get document text
        document = documents_store[document_id]
        text_content = document['text_content']
        
        # Get answer from LLM
        answer = answer_question(question, text_content)
        
        return jsonify({
            'answer': answer,
            'question': question
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='localhost')
