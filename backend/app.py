from flask import Flask, jsonify, request, session
from flask_cors import CORS
import os
import uuid

from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import (
    create_user,
    get_document,
    get_question_history,
    get_user_by_email,
    get_user_by_id,
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
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}
MAX_FILE_SIZE = 10 * 1024 * 1024

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(
    app,
    resources={
        r"/auth/*": {"origins": ["http://localhost:3000"]},
        r"/upload": {"origins": ["http://localhost:3000"]},
        r"/ask": {"origins": ["http://localhost:3000"]},
        r"/documents": {"origins": ["http://localhost:3000"]},
        r"/history/*": {"origins": ["http://localhost:3000"]},
        r"/health": {"origins": ["http://localhost:3000"]},
        r"/*": {"origins": "*"},
    },
    supports_credentials=True,
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return get_user_by_id(user_id)


def require_auth():
    user = current_user()
    if not user:
        return None, (jsonify({'error': 'Authentication required'}), 401)
    return user, None


@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if get_user_by_email(email):
        return jsonify({'error': 'Email already registered'}), 409

    user_id = create_user(email, generate_password_hash(password, method='pbkdf2:sha256'))
    session['user_id'] = user_id

    return jsonify({'user': {'id': user_id, 'email': email}}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = get_user_by_email(email)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user['id']
    return jsonify({'user': {'id': user['id'], 'email': user['email']}}), 200


@app.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200


@app.route('/auth/me', methods=['GET'])
def me():
    user = current_user()
    if not user:
        return jsonify({'user': None}), 200
    return jsonify({'user': {'id': user['id'], 'email': user['email']}}), 200


@app.route('/upload', methods=['POST'])
def upload_document():
    user, error_response = require_auth()
    if error_response:
        return error_response

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
            user_id=user['id'],
            filename=filename,
            filepath=filepath,
            text_content=text_content,
        )

        return jsonify({
            'document_id': document_id,
            'filename': filename,
            'message': 'Document uploaded successfully',
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ask', methods=['POST'])
def ask_question():
    user, error_response = require_auth()
    if error_response:
        return error_response

    try:
        data = request.get_json(silent=True) or {}
        document_id = data.get('document_id')
        question = data.get('question')

        if not document_id or not question:
            return jsonify({'error': 'Missing document_id or question'}), 400

        document = get_document(document_id, user['id'])
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        result = answer_question(question, document['text_content'])
        if not result.get('ok', False):
            return jsonify({'error': result['answer']}), 502

        answer = result['answer']
        save_question_history(document_id, question, answer)

        return jsonify({'answer': answer, 'question': question}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/history/<document_id>', methods=['GET'])
def history(document_id):
    user, error_response = require_auth()
    if error_response:
        return error_response

    document = get_document(document_id, user['id'])
    if not document:
        return jsonify({'error': 'Document not found'}), 404

    return jsonify({'document_id': document_id, 'history': get_question_history(document_id)}), 200


@app.route('/documents', methods=['GET'])
def documents():
    user, error_response = require_auth()
    if error_response:
        return error_response

    return jsonify({'documents': list_documents(user['id'])}), 200


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='localhost')
