#!/usr/bin/env python3
"""
Enhanced WHF AI Chatbot Startup Script
Runs the complete system with authentication, analytics, and export features
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit', 'fastapi', 'uvicorn', 'openai', 'weaviate_client',
        'pandas', 'plotly', 'speech_recognition', 'pyaudio', 'firebase_admin',
        'pymongo', 'reportlab', 'sendgrid'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting WHF AI Chatbot Backend...")
    print("📁 Working directory:", os.getcwd())
    
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
        time.sleep(3)  # Wait for backend to start
        
        return backend_process
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
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🏭 WHF AI Chatbot - Enhanced Edition")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🔧 Starting Enhanced WHF AI Chatbot...")
    print("📊 Features: Authentication, Analytics, Chat History, Export")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 WHF AI Chatbot Enhanced Edition is running!")
    print("=" * 50)
    print("📱 Frontend: http://localhost:8501")
    print("🔧 Backend API: http://localhost:8000")
    print("📊 Analytics: http://localhost:8501/analytics_dashboard")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("🔐 Login with: demo@whf.com / demo123")
    print("👤 Or create a new account")
    print("=" * 50)
    print("🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
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