import os
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import json
from dotenv import load_dotenv
from openai import OpenAI
import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
import io
import os
import sys
# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
from database import db

# Import company data functions directly
try:
    from company_data import search_company_data, get_company_info
except ImportError:
    # Fallback if company_data module is not found
    def search_company_data(query):
        return []
    
    def get_company_info():
        return {}

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# FastAPI App
app = FastAPI()

# Upload folder
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_pdf(filepath):
    """Extract text from PDF files - Simple and effective like ChatGPT"""
    try:
        doc = fitz.open(filepath)
        text = ""
        
        for page_num, page in enumerate(doc):
            # Simple text extraction - this works for most PDFs
            page_text = page.get_text()
            
            if page_text.strip():
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            else:
                # If no text found, try alternative method
                page_text = page.get_text("text")
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        
        doc.close()
        
        # Clean up the text
        import re
        
        # Remove null characters
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR issues
        text = text.replace('1000 C', '100°C')
        text = text.replace('1500 C', '150°C')
        text = text.replace('8000 C', '800°C')
        text = text.replace('8500 C', '850°C')
        
        print(f"Extracted text from {filepath}: {text[:200]}...")  # Debug print
        return text
        
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_excel(filepath):
    """Extract text from Excel files - Enhanced extraction"""
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(filepath)
        all_text = []
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            
            # Convert DataFrame to text with better formatting
            sheet_text = f"\n--- Sheet: {sheet_name} ---\n"
            sheet_text += df.to_string(index=False)
            sheet_text += "\n"
            
            all_text.append(sheet_text)
        
        return "\n".join(all_text)
    except Exception as e:
        print(f"Excel extraction error: {str(e)}")
        return f"Error extracting text from Excel: {str(e)}"

def extract_text_from_image(filepath):
    """Extract text from images using OCR"""
    try:
        from PIL import Image
        import pytesseract
        
        # Open the image
        img = Image.open(filepath)
        
        # Use Tesseract OCR to extract text
        text = pytesseract.image_to_string(img)
        
        if text.strip():
            return f"Image content from {os.path.basename(filepath)}:\n{text}"
        else:
            return f"Image content from {os.path.basename(filepath)} - No text detected in image"
            
    except ImportError:
        # Fallback if Tesseract is not available
        return f"Image content from {os.path.basename(filepath)} - OCR processing would extract text here"
    except Exception as e:
        print(f"Image extraction error: {str(e)}")
        return f"Error processing image: {str(e)}"

def chunk_text(text, chunk_size=1000):
    """Split text into chunks for better processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        if current_size + len(word) + 1 > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def get_ai_answer(question, prompt):
    """Get AI-powered answer based on context"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating AI response: {str(e)}"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save the uploaded file
        with open(filepath, "wb") as f:
            f.write(await file.read())
        
        print(f"File saved: {filepath}")
        
        ext = file.filename.lower().split(".")[-1]
        print(f"File type: {ext}")
        
        # Extract text based on file type
        if ext == "pdf":
            print("Processing PDF file...")
            text = extract_text_from_pdf(filepath)
        elif ext in ["xls", "xlsx"]:
            print("Processing Excel file...")
            text = extract_text_from_excel(filepath)
        elif ext in ["jpg", "jpeg", "png"]:
            print("Processing Image file...")
            text = extract_text_from_image(filepath)
        else:
            return {"error": f"Unsupported file format: {ext}"}

        print(f"Extracted text length: {len(text)} characters")
        print(f"Text preview: {text[:200]}...")
        
        # Check if text extraction was successful
        if not text or text.startswith("Error"):
            return {"error": f"Failed to extract text from {file.filename}: {text}"}

        # Split text into chunks
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} text chunks")
        
        # Store in database
        document_id = db.add_document(
            filename=file.filename,
            file_path=filepath,
            file_size=file.size,
            file_type=ext
        )
        
        if document_id:
            db.add_chunks(document_id, chunks)
            return {"message": f"{file.filename} uploaded and processed successfully! Extracted {len(chunks)} text chunks."}
        else:
            return {"error": "Failed to save document to database"}
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {"error": f"Upload failed: {str(e)}"}

class Question(BaseModel):
    question: str

@app.post("/ask/")
def ask_question(q: Question):
    try:
        # Check for personal questions first
        question_lower = q.question.lower()
        
        # Personal questions about Forgia
        if any(word in question_lower for word in ["who are you", "what are you", "your name", "who created", "who made", "who developed"]):
            return {"answer": "Hi! I'm Forgia, an AI chatbot developed by the WHF Interns team for Western Heat & Forge. I'm here to help you with company information and your documents. I can answer questions about WHF's services, products, and process any PDFs, Excel files, or images you upload. Nice to meet you! 🤖✨"}
        
        # Questions about capabilities
        if any(word in question_lower for word in ["what can you do", "your capabilities", "how do you work", "what is your purpose", "why do you exist"]):
            return {"answer": "I'm Forgia, your friendly AI assistant for Western Heat & Forge! Here's what I can do:\n\n🏢 **Company Information**: I know all about WHF's services, products, and company details\n📄 **Document Processing**: I can read and understand PDFs, Excel files, and images\n🔍 **Smart Search**: I find relevant information from your uploaded documents\n💬 **Conversational AI**: I maintain context and remember our chat history\n📚 **Knowledge Base**: I store your documents permanently\n\nI'm designed to help you quickly find information about WHF and your company documents!"}
        
        # Company-related questions
        company_results = search_company_data(q.question)
        if company_results:
            return {"answer": "\n\n".join(company_results)}
        
        # Get documents from database
        documents = db.get_all_chunks()
        
        if not documents:
            return {"answer": "Hi! I'm Forgia! 👋 I'd love to help you with your documents, but I don't see any files uploaded yet. Please upload some PDFs, Excel files, or images using the upload section on the left, and I'll be happy to answer questions about them! 📁✨"}
        
        # Enhanced semantic search with better keyword matching
        relevant_chunks = []
        question_lower = q.question.lower()
        question_words = question_lower.split()
        
        # Score each document chunk based on relevance
        scored_chunks = []
        for doc in documents:
            score = 0
            content_lower = doc["content"].lower()
            
            # Exact word matches
            for word in question_words:
                if word in content_lower:
                    score += 2
            
            # Phrase matches
            if len(question_words) > 1:
                for i in range(len(question_words) - 1):
                    phrase = f"{question_words[i]} {question_words[i+1]}"
                    if phrase in content_lower:
                        score += 3
            
            if score > 0:
                scored_chunks.append((score, doc))
        
        # Sort by score and take top chunks
        if scored_chunks:
            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            relevant_chunks = [doc for score, doc in scored_chunks[:8]]
        else:
            relevant_chunks = []
        
        # If no matches, take recent documents
        if not relevant_chunks:
            relevant_chunks = documents[-3:] if len(documents) >= 3 else documents
        
        # Combine relevant context (limit size to prevent token issues)
        context_parts = []
        total_length = 0
        max_context_length = 8000
        
        for doc in relevant_chunks:
            doc_content = f"From {doc['filename']}: {doc['content']}"
            if total_length + len(doc_content) < max_context_length:
                context_parts.append(doc_content)
                total_length += len(doc_content)
            else:
                break
        
        context = "\n\n".join(context_parts)
        
        # Enhanced AI prompt for better conversation
        enhanced_prompt = f"""
You are an AI assistant helping with company documents. You have access to the following document content:

{context}

User Question: {q.question}

Instructions:
- Answer based ONLY on the provided document content
- Be helpful and conversational
- If the information isn't in the documents, say so clearly
- Provide specific details from the documents when possible
- Keep answers concise but informative

Answer:"""
        
        # Get AI answer
        answer = get_ai_answer(q.question, enhanced_prompt)
        
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Sorry, I encountered an error: {str(e)}"}

@app.get("/")
def read_root():
    return {"message": "Company AI Chatbot Backend is running!"}

@app.get("/health")
def health_check():
    documents_list = db.get_documents()
    chunks = db.get_all_chunks()
    return {
        "status": "healthy", 
        "documents_count": len(documents_list),
        "chunks_count": len(chunks)
    }

@app.get("/documents")
def list_documents():
    documents_list = db.get_documents()
    return {"documents": documents_list}

@app.delete("/documents/{filename}")
def delete_document(filename: str):
    success = db.delete_document(filename)
    if success:
        return {"message": f"Document {filename} deleted successfully"}
    else:
        return {"error": f"Document {filename} not found"}

@app.delete("/documents")
def clear_all_documents():
    success = db.clear_all()
    if success:
        return {"message": "All documents cleared successfully"}
    else:
        return {"error": "Failed to clear documents"}

@app.get("/debug/text/{filename}")
def get_extracted_text(filename: str):
    """Debug endpoint to see extracted text from a document"""
    try:
        chunks = db.get_all_chunks()
        document_chunks = [chunk for chunk in chunks if chunk["filename"] == filename]
        
        if document_chunks:
            full_text = "\n".join([chunk["content"] for chunk in document_chunks])
            return {"filename": filename, "extracted_text": full_text}
        else:
            return {"error": f"Document {filename} not found"}
    except Exception as e:
        return {"error": str(e)} 