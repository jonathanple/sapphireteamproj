import fitz
import os

def extract_pdf_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"🚫 PDF not found at: {file_path}")
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text
