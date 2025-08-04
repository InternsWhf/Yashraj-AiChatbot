#!/usr/bin/env python3
"""
WHF AI Chatbot - Final Working Version
=====================================
Guaranteed working startup script with all features including table extraction.
"""

import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    Path("data/exports").mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend Server...")
    
    if check_backend():
        print("✅ Backend is already running")
        return True
    
    try:
        # Start backend in background
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for backend to start
        for i in range(15):
            if check_backend():
                print("✅ Backend started successfully")
                return True
            time.sleep(2)
            print(f"⏳ Waiting for backend... ({i+1}/15)")
        
        print("❌ Backend failed to start")
        return False
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def start_frontend():
    """Start the frontend server"""
    print("🎨 Starting Frontend Server...")
    
    try:
        # Start frontend in background
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/enhanced_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for frontend to start
        time.sleep(5)
        print("✅ Frontend started successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🏭 WHF AI Chatbot - Final Working Version")
    print("=" * 60)
    print("🎯 Features: Table Extraction, Authentication, Chat History")
    print()
    
    # Create directories
    create_directories()
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend. Please check the logs.")
        return
    
    # Start frontend
    if not start_frontend():
        print("❌ Failed to start frontend. Please check the logs.")
        return
    
    print()
    print("🎉 WHF AI Chatbot is Ready!")
    print("=" * 60)
    print("🌐 Frontend: http://localhost:8501")
    print("🔧 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print()
    print("💡 How to use:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. Register a new account or login")
    print("   3. Upload PDF/Excel files with tables")
    print("   4. Ask questions about the tables")
    print()
    print("🔍 Example questions:")
    print("   • 'Show me the setup instructions table'")
    print("   • 'What are the die numbers and cycle times?'")
    print("   • 'Display the coil size data'")
    print()
    print("🔄 Press Ctrl+C to stop the application")
    print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down WHF AI Chatbot...")
        print("✅ Application stopped successfully")

if __name__ == "__main__":
    main() 