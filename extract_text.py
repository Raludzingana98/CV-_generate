import os
import pdfplumber
import docx
from PIL import Image
import pytesseract

def extract_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_from_image(file_path):
    
    return pytesseract.image_to_string(Image.open(file_path))

def universal_extractor(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == ".pdf":
            return extract_from_pdf(file_path)
        elif ext == ".docx":
            return extract_from_docx(file_path)
        elif ext in [".jpg", ".jpeg", ".png"]:
            return extract_from_image(file_path)
        elif ext == ".txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"Error: Extension {ext} not supported."
    except Exception as e:
        return f"Error processing file: {str(e)}"

if __name__ == "__main__":
    
    filename = "uploads/CV TEMPLATE.pdf" 
    if os.path.exists(filename):
        raw_text = universal_extractor(filename)
        print("--- EXTRACTED CONTENT ---")
        print(raw_text)
    else:
        print(f"Please put a file named '{filename}' in the folder to test.")