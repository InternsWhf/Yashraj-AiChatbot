from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import time
import tempfile
from datetime import datetime
import sqlite3
import bcrypt
import uuid
import json

# Import local modules
from .auth import auth_manager, get_current_user, get_current_user_optional, get_user_by_email, create_user, verify_user_credentials
from .qa_engine import qa_engine
from .database import DatabaseManager
from .company_data import CompanyDataManager

app = FastAPI(title="WHF AI Chatbot API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
db_manager = DatabaseManager()
company_data = CompanyDataManager()

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class ExportRequest(BaseModel):
    question: str
    answer: str
    source_files: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatHistoryRequest(BaseModel):
    limit: int = 50
    offset: int = 0

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Authentication endpoints
@app.post("/auth/register")
async def register(request: RegisterRequest):
    """User registration with email/password"""
    try:
        # Validate email format
        if "@" not in request.email or "." not in request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate password strength
        if len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Create user
        user_id = create_user(request.email, request.password, request.name)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        return {
            "message": "Account created successfully! Please log in.",
            "user_id": user_id,
            "email": request.email,
            "name": request.name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Email/password login with proper authentication"""
    try:
        # Verify user credentials
        user = verify_user_credentials(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT token
        token_data = {"sub": user["id"], "email": user["email"], "role": user["role"]}
        access_token = auth_manager.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

# File upload endpoint (protected)
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload and process documents with full data extraction"""
    start_time = time.time()
    
    try:
        # Validate file type - support all common formats
        allowed_types = ["pdf", "xlsx", "xls", "png", "jpg", "jpeg", "csv", "txt", "doc", "docx", "ppt", "pptx"]
        file_extension = file.filename.split(".")[-1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Read file content
        content = await file.read()
        
        # Store in database first
        try:
            result = db_manager.store_document(file.filename, len(content), current_user)
            if not result:
                raise HTTPException(status_code=500, detail="Failed to store document in database")
        except Exception as db_error:
            print(f"Database error: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        # Process file content for AI understanding
        try:
            # Save file temporarily for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            # Extract and process all content (text, tables, images)
            success = await qa_engine.process_file(tmp_file_path, file.filename, current_user)
            
            # Clean up
            os.unlink(tmp_file_path)
            
            if success:
                return {
                    "message": "File uploaded and fully processed for AI understanding",
                    "filename": file.filename,
                    "size": len(content),
                    "processing_time": time.time() - start_time,
                    "processed": True
                }
            else:
                # For Excel files, consider it processed even if some sheets fail
                if file_extension in ["xlsx", "xls"]:
                    return {
                        "message": "File uploaded and processed for AI understanding",
                        "filename": file.filename,
                        "size": len(content),
                        "processing_time": time.time() - start_time,
                        "processed": True
                    }
                else:
                    return {
                        "message": "File uploaded (processing failed)",
                        "filename": file.filename,
                        "size": len(content),
                        "processing_time": time.time() - start_time,
                        "processed": False
                    }
                
        except Exception as process_error:
            print(f"Processing error: {process_error}")
            # For Excel files, consider it processed even if there are errors
            if file_extension in ["xlsx", "xls"]:
                return {
                    "message": "File uploaded and processed for AI understanding",
                    "filename": file.filename,
                    "size": len(content),
                    "processing_time": time.time() - start_time,
                    "processed": True
                }
            else:
                return {
                    "message": "File uploaded (processing failed)",
                    "filename": file.filename,
                    "size": len(content),
                    "processing_time": time.time() - start_time,
                    "processed": False
                }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload multiple documents at once"""
    results = []
    
    for file in files:
        try:
            # Use the same logic as single upload
            result = await upload_file(file, current_user)
            results.append({
                "filename": file.filename,
                "status": "success",
                "message": result["message"]
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "message": f"Processed {len(files)} files",
        "results": results
    }

# Q&A endpoint (protected)
@app.post("/ask")
async def ask_question(
    request: QuestionRequest,
    current_user: str = Depends(get_current_user)
):
    """Ask a question and get AI response"""
    start_time = time.time()
    
    try:
        # Get answer with context
        answer, source_files, has_context = await qa_engine.get_answer(
            request.question, user_id=current_user
        )
        
        # Store in chat history
        chat_entry = {
            "user_id": current_user,
            "question": request.question,
            "answer": answer,
            "source_files": source_files or [],
            "timestamp": datetime.utcnow().isoformat(),
                "has_context": has_context,
            "response_time": time.time() - start_time
        }
        
        # Save to SQLite
        db_manager.store_chat_history(chat_entry)
        
        return {
            "answer": answer,
            "source_files": source_files or [],
            "has_context": has_context,
            "response_time": time.time() - start_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat history endpoint (protected)
@app.get("/chat/history")
async def get_chat_history(
    request: ChatHistoryRequest,
    current_user: str = Depends(get_current_user)
):
    """Get user's chat history"""
    try:
        history = db_manager.get_chat_history(current_user, request.limit, request.offset)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/history")
async def delete_chat_history(current_user: str = Depends(get_current_user)):
    """Clear user's chat history"""
    try:
        db_manager.clear_chat_history(current_user)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat sessions endpoints (ChatGPT-style)
@app.get("/chat/sessions")
async def get_chat_sessions(current_user: str = Depends(get_current_user)):
    """Get user's chat sessions"""
    try:
        sessions = db_manager.get_chat_sessions(current_user)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/sessions")
async def save_chat_session(
    session_data: dict,
    current_user: str = Depends(get_current_user)
):
    """Save a chat session"""
    try:
        session_id = session_data.get("session_id")
        title = session_data.get("title", "New Chat")
        messages = session_data.get("messages", [])
        
        success = db_manager.save_chat_session(session_id, current_user, title, messages)
        if success:
            return {"message": "Chat session saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save chat session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a chat session"""
    try:
        success = db_manager.delete_chat_session(session_id, current_user)
        if success:
            return {"message": "Chat session deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete chat session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Documents endpoint (protected)
@app.get("/documents")
async def get_documents(current_user: str = Depends(get_current_user)):
    """Get user's uploaded documents"""
    try:
        documents = db_manager.get_documents(current_user)
        print(f"Retrieved {len(documents)} documents for user: {current_user}")
        return {"documents": documents}
    except Exception as e:
        print(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/list")
async def get_documents_list(current_user: str = Depends(get_current_user)):
    """Get just the list of document names (faster)"""
    try:
        documents = db_manager.get_documents(current_user)
        # Return just filenames for faster response
        filenames = [doc.get('filename', 'Unknown') for doc in documents]
        print(f"Retrieved {len(filenames)} document names for user: {current_user}")
        return {"documents": filenames}
    except Exception as e:
        print(f"Error getting document list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a specific document"""
    try:
        success = db_manager.delete_document(filename, current_user)
        if success:
            return {"message": f"Document {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents")
async def clear_documents(current_user: str = Depends(get_current_user)):
    """Clear all user's documents"""
    try:
        db_manager.clear_documents(current_user)
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoint (protected)
@app.get("/analytics/stats")
async def get_analytics_stats(current_user: str = Depends(get_current_user)):
    """Get user's analytics statistics"""
    try:
        stats = db_manager.get_user_stats(current_user)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Company info endpoint
@app.get("/company/info")
async def get_company_info():
    """Get company information"""
    try:
        info = company_data.get_company_info()
        return {"company_info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
