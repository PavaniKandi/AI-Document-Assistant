from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from database import (
    get_document,
    get_question_history,
    init_db,
    list_documents,
    save_document,
    save_question_history,
)
from document_processor import extract_text_from_file
from llm_service import answer_question

load_dotenv()

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CORS(app, resources={
    r"/documents": {"origins": ["http://localhost:3000"]},
    r"/upload": {"origins": ["http://localhost:3000"]},
    r"/ask": {"origins": ["http://localhost:3000"]},
    r"/history/*": {"origins": ["http://localhost:3000"]},
    r"/health": {"origins": ["http://localhost:3000"]},
    r"/*": {"origins": "*"}
}, supports_credentials=True)

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PDF, TXT, or DOCX'}), 400
        
        document_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_{filename}")
        
        file.save(filepath)
        text_content = extract_text_from_file(filepath)
        
        save_document(
            document_id=document_id,
            filename=filename,
            filepath=filepath,
            text_content=text_content
        )
        
        return jsonify({
            'document_id': document_id,
            'filename': filename,
            'message': 'Document uploaded successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400

        document_id = data.get('document_id')
        question = data.get('question')
        
        if not document_id or not question:
            return jsonify({'error': 'Missing document_id or question'}), 400
        
        document = get_document(document_id)

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        text_content = document['text_content']
        result = answer_question(question, text_content)
        if not result.get('ok', False):
            return jsonify({
                'error': result['answer']
            }), 502

        answer = result['answer']
        sources = result.get('sources', [])

        save_question_history(document_id, question, answer)
        
        return jsonify({
            'answer': answer,
            'question': question,
            'sources': sources
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


@app.route('/documents', methods=['GET'])
def get_documents():
    return jsonify({
        'documents': list_documents()
    }), 200


@app.route('/history/<document_id>', methods=['GET'])
def get_document_history(document_id):
    document = get_document(document_id)

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    history = get_question_history(document_id)
    return jsonify({
        'document_id': document_id,
        'history': history
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='localhost')
