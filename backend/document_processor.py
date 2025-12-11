"""
Document processing module.
Handles text extraction from various file formats.
"""

from PyPDF2 import PdfReader
from docx import Document as DocxDocument

def extract_text_from_pdf(filepath):
    """
    Extract text from PDF file.
    
    Args:
        filepath: Path to the PDF file
    
    Returns:
        Extracted text as a string
    """
    text = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text

def extract_text_from_txt(filepath):
    """
    Extract text from TXT file.
    
    Args:
        filepath: Path to the TXT file
    
    Returns:
        File content as a string
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        raise Exception(f"Error reading TXT: {str(e)}")
    
    return text

def extract_text_from_docx(filepath):
    """
    Extract text from DOCX file.
    
    Args:
        filepath: Path to the DOCX file
    
    Returns:
        Extracted text as a string
    """
    text = ""
    try:
        doc = DocxDocument(filepath)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")
    
    return text

def extract_text_from_file(filepath):
    """
    Extract text from a file based on its extension.
    
    Args:
        filepath: Path to the file
    
    Returns:
        Extracted text as a string
    """
    file_extension = filepath.rsplit('.', 1)[1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(filepath)
    elif file_extension == 'txt':
        return extract_text_from_txt(filepath)
    elif file_extension in ['docx', 'doc']:
        return extract_text_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
