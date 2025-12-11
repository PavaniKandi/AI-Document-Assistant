"""
LLM Service module.
Handles communication with Ollama for question answering.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
MAX_CONTEXT_LENGTH = 4000  # Maximum characters to send as context

def prepare_context(question, document_text):
    """
    Prepare the context for the LLM by selecting relevant parts of the document.
    
    Args:
        question: The user's question
        document_text: The full document text
    
    Returns:
        A string containing the question and relevant context
    """
    # Simple approach: use the first MAX_CONTEXT_LENGTH characters
    # In production, you'd use more sophisticated methods like semantic search
    context = document_text[:MAX_CONTEXT_LENGTH]
    
    prompt = f"""Based on the following document, answer the question:

Document:
{context}

Question: {question}

Answer: """
    
    return prompt

def answer_question(question, document_text):
    """
    Get an answer to a question based on document content using Ollama.
    
    Args:
        question: The question to answer
        document_text: The document content to base the answer on
    
    Returns:
        The answer as a string
    """
    try:
        # Prepare the prompt
        prompt = prepare_context(question, document_text)
        
        # Call Ollama API
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")
        
        result = response.json()
        answer = result.get('response', '').strip()
        
        if not answer:
            return "I couldn't generate an answer. Please try a different question."
        
        return answer
    
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure Ollama is running on http://localhost:11434"
    except requests.exceptions.Timeout:
        return "Error: Request to Ollama timed out. The model might be taking too long."
    except Exception as e:
        return f"Error: {str(e)}"
