import os
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import json

# Import the real QA engine
try:
    from .qa_engine import QAEngine
    qa_engine = QAEngine()
    qa_available = True
except Exception as e:
    print(f"QA Engine not available: {e}")
    qa_available = False

# FastAPI App
app = FastAPI()

# Upload folder
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Simple in-memory storage for demo
documents = []

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    # Process file with QA engine if available
    if qa_available:
        try:
            success = await qa_engine.process_file(filepath, file.filename)
            if success:
                documents.append({
                    "filename": file.filename,
                    "content": f"Content from {file.filename}",
                    "source": "upload"
                })
                return {"message": f"{file.filename} uploaded and processed successfully!"}
            else:
                return {"message": f"{file.filename} uploaded but processing failed!"}
        except Exception as e:
            return {"message": f"{file.filename} uploaded but processing error: {str(e)}"}
    else:
        # Fallback to simple storage
        documents.append({
            "filename": file.filename,
            "content": f"Content from {file.filename}",
            "source": "upload"
        })
        return {"message": f"{file.filename} uploaded successfully!"}

# Chat API endpoint
class Question(BaseModel):
    question: str

@app.post("/ask/")
def ask_question(q: Question):
    if not documents and not qa_available:
        return {"answer": "No documents uploaded yet. Please upload some files first!"}
    
    # Use real QA engine if available
    if qa_available:
        try:
            answer = qa_engine.answer_question(q.question)
            return {"answer": answer}
        except Exception as e:
            return {"answer": f"Error processing question: {str(e)}"}
    else:
        # Fallback response
        return {"answer": f"You asked: '{q.question}'. I found {len(documents)} documents. Please enable the full AI features for better responses."}

@app.get("/")
def read_root():
    return {"message": "Company AI Chatbot Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "documents_count": len(documents), "qa_available": qa_available} 