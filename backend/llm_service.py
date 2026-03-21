import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
MAX_CONTEXT_LENGTH = 5000
CHUNK_SIZE = 1100
CHUNK_OVERLAP = 180
TOP_CHUNKS = 4
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'do', 'for', 'from',
    'how', 'in', 'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to',
    'was', 'what', 'when', 'where', 'which', 'who', 'why', 'with'
}


def normalize_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def tokenize(text):
    return [
        token for token in re.findall(r'[a-zA-Z0-9]+', text.lower())
        if token not in STOP_WORDS and len(token) > 1
    ]


def chunk_document(document_text):
    cleaned_text = normalize_text(document_text)

    if len(cleaned_text) <= CHUNK_SIZE:
        return [cleaned_text]

    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
    chunks = []
    current_chunk = ''

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if not current_chunk:
            current_chunk = sentence
            continue

        candidate = f'{current_chunk} {sentence}'
        if len(candidate) <= CHUNK_SIZE:
            current_chunk = candidate
        else:
            chunks.append(current_chunk)
            overlap_text = current_chunk[-CHUNK_OVERLAP:].strip()
            current_chunk = f'{overlap_text} {sentence}'.strip()

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def score_chunk(question_terms, chunk):
    chunk_terms = tokenize(chunk)

    if not chunk_terms:
        return 0

    unique_chunk_terms = set(chunk_terms)
    overlap_score = sum(3 for term in question_terms if term in unique_chunk_terms)
    frequency_score = sum(chunk_terms.count(term) for term in question_terms)

    return overlap_score + frequency_score


def select_relevant_context(question, document_text):
    chunks = chunk_document(document_text)
    question_terms = tokenize(question)

    if not question_terms:
        selected_chunks = chunks[:2]
        context = '\n\n'.join(
            f'Section {index + 1}:\n{chunk}'
            for index, chunk in enumerate(selected_chunks)
        )
        return context[:MAX_CONTEXT_LENGTH]

    scored_chunks = []
    for index, chunk in enumerate(chunks):
        score = score_chunk(question_terms, chunk)
        scored_chunks.append((score, index, chunk))

    scored_chunks.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    selected_chunks = [chunk for score, _, chunk in scored_chunks[:TOP_CHUNKS] if score > 0]

    if not selected_chunks:
        selected_chunks = chunks[:2]

    context = '\n\n'.join(
        f'Section {index + 1}:\n{chunk}'
        for index, chunk in enumerate(selected_chunks)
    )

    return context[:MAX_CONTEXT_LENGTH]


def prepare_context(question, document_text):
    context = select_relevant_context(question, document_text)

    return f"""Answer the question using only the document sections below.

If the answer is implied but not stated word for word, explain the most likely answer based on the text.
If the text only gives part of the answer, say that clearly.
Only say the document does not mention something when the sections below really do not cover it.

Document:
{context}

Question: {question}

Answer:"""


def answer_question(question, document_text):
    try:
        prompt = prepare_context(question, document_text)
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
            },
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")

        result = response.json()
        answer = result.get('response', '').strip()

        if not answer:
            return {
                'ok': False,
                'answer': "I couldn't generate an answer. Please try a different question.",
            }

        return {
            'ok': True,
            'answer': answer,
        }

    except requests.exceptions.ConnectionError:
        return {
            'ok': False,
            'answer': 'Error: Cannot connect to Ollama. Make sure Ollama is running on http://localhost:11434',
        }
    except requests.exceptions.Timeout:
        return {
            'ok': False,
            'answer': 'Error: Request to Ollama timed out. The model might be taking too long.',
        }
    except Exception as e:
        return {
            'ok': False,
            'answer': f'Error: {str(e)}',
        }
