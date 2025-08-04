#!/usr/bin/env python3
"""
WHF AI Chatbot - Simple Startup Script
=====================================
A reliable startup script for the WHF AI Chatbot with table extraction capabilities.
"""

import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def wait_for_backend(max_attempts=30):
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to start...")
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        print(f"⏳ Attempt {i+1}/{max_attempts}...")
        time.sleep(2)
    return False

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting WHF AI Chatbot Backend...")
    
    # Check if backend is already running
    if check_port(8000):
        print("✅ Backend is already running on port 8000")
        return True
    
    # Start backend
    try:
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for backend to start
        if wait_for_backend():
            return True
        else:
            print("❌ Backend failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting WHF AI Chatbot Frontend...")
    
    # Check if frontend is already running
    if check_port(8501):
        print("✅ Frontend is already running on port 8501")
        return True
    
    # Start frontend
    try:
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/enhanced_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for frontend to start...")
        time.sleep(5)
        
        if check_port(8501):
            print("✅ Frontend is ready!")
            return True
        else:
            print("❌ Frontend failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🏭 WHF AI Chatbot - Simple Edition")
    print("=" * 50)
    print("📊 Features: Login/Register, Chat History, Table Extraction")
    print("🔧 Starting services...")
    print()
    
    # Create necessary directories
    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    Path("data/exports").mkdir(parents=True, exist_ok=True)
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend
    if not start_frontend():
        print("❌ Failed to start frontend. Exiting.")
        sys.exit(1)
    
    print()
    print("🎉 WHF AI Chatbot is ready!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:8501")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print()
    print("💡 Features:")
    print("   ✅ User Authentication (Login/Register)")
    print("   ✅ Document Upload (PDF, Excel, Images)")
    print("   ✅ Table Extraction & Display")
    print("   ✅ Chat History")
    print("   ✅ Smart Search")
    print()
    print("🔄 Press Ctrl+C to stop the application")
    print()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down WHF AI Chatbot...")
        print("✅ Application stopped.")

if __name__ == "__main__":
    main() 