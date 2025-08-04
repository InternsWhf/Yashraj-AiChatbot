import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_pdf(file_path):
    """Parse PDF file and extract text content"""
    try:
        return extract_text_from_pdf(file_path)
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
        return ""

def chunk_text(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
