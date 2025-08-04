#!/usr/bin/env python3
"""
Perfect WHF AI Chatbot Startup Script
Ensures both backend and frontend start correctly with authentication
"""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting WHF AI Chatbot Backend...")
    
    try:
        # Start backend server
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Backend server is starting...")
        
        # Wait for backend to be ready
        max_attempts = 30
        for attempt in range(max_attempts):
            if check_backend_health():
                print("✅ Backend is healthy and ready!")
                return backend_process
            time.sleep(2)
            print(f"⏳ Waiting for backend... ({attempt + 1}/{max_attempts})")
        
        print("❌ Backend failed to start properly")
        backend_process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🌐 Starting WHF AI Chatbot Frontend...")
    
    try:
        # Start frontend
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/enhanced_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Frontend is starting...")
        time.sleep(5)  # Give frontend time to start
        
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🏭 WHF AI Chatbot - Perfect Edition")
    print("=" * 60)
    
    print("\n🔧 Starting WHF AI Chatbot with Authentication...")
    print("📊 Features: Login/Register, Chat History, Analytics, Export, 3D Avatar")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Backend failed to start")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        print("❌ Frontend failed to start")
        sys.exit(1)
    
    print("\n🎉 WHF AI Chatbot is running perfectly!")
    print("=" * 60)
    print("📱 Frontend: http://localhost:8501")
    print("🔧 Backend API: http://localhost:8000")
    print("📊 Analytics: http://localhost:8501/analytics_dashboard")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("🔐 Login Credentials:")
    print("   Demo Account: demo@whf.com / demo123")
    print("   Or create a new account using the registration form")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(5)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
            
            # Check backend health periodically
            if not check_backend_health():
                print("⚠️  Backend health check failed")
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down WHF AI Chatbot...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("👋 WHF AI Chatbot stopped successfully")

if __name__ == "__main__":
    main() 