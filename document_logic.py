import os
from pypdf import PdfReader
import docx
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text content from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts all text content from a Word document."""
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def read_document_content(file_path: str) -> str:
    """Generic document reader for multi-modal analysis."""
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
        
    ext = Path(file_path).suffix.lower()
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif ext in [".txt", ".md", ".csv", ".json"]:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        return f"Unsupported file format: {ext}"

def summarize_document(file_path: str) -> str:
    """Helper for the AI to provide a high-level overview of a local file."""
    content = read_document_content(file_path)
    if content.startswith("Error"):
        return content
        
    # Return a snippet for the agent to process
    return f"FILE LOADED: {file_path}\nTotal Length: {len(content)} characters.\n\n[CONTENT START]\n{content[:10000]}\n[CONTENT END]\n\nYou can now summarize or analyze this document for the user."
