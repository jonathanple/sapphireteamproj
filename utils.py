import fitz
import os

def extract_text_from_multiple_pdfs(file_paths):
    documents_text = {}

    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"🚫 PDF not found at: {file_path}")

        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()

        documents_text[file_path] = text

    return documents_text
