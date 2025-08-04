#!/usr/bin/env python3
"""
Simple Startup Script for WHF AI Chatbot
========================================
This script starts both backend and frontend services.
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path

def print_status(message, status="INFO"):
    """Print status message with color coding"""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    print(f"{colors.get(status, '')}[{status}] {message}{colors['RESET']}")

def start_backend():
    """Start the backend service"""
    print_status("Starting backend service...", "INFO")
    
    try:
        # Start backend with uvicorn
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "backend.main:app",
            "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for backend to start
        time.sleep(5)
        print_status("✅ Backend is running on http://localhost:8000", "SUCCESS")
        return backend_process
            
    except Exception as e:
        print_status(f"Failed to start backend: {e}", "ERROR")
        return False

def start_frontend():
    """Start the frontend service"""
    print_status("Starting frontend service...", "INFO")
    
    try:
        # Start frontend with streamlit
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/enhanced_app.py",
            "--server.port", "8501", "--server.address", "0.0.0.0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for frontend to start
        time.sleep(10)
        print_status("✅ Frontend is running on http://localhost:8501", "SUCCESS")
        return frontend_process
            
    except Exception as e:
        print_status(f"Failed to start frontend: {e}", "ERROR")
        return False

def open_browser():
    """Open the application in browser"""
    time.sleep(15)  # Wait for both services to be ready
    try:
        webbrowser.open("http://localhost:8501")
        print_status("🌐 Opening application in browser...", "SUCCESS")
    except Exception as e:
        print_status(f"Could not open browser automatically: {e}", "WARNING")
        print_status("Please open http://localhost:8501 manually", "INFO")

def main():
    """Main function"""
    print_status("🚀 Starting WHF AI Chatbot...", "INFO")
    print_status("Login: interns@whfpl.in / Password: Yashraj", "INFO")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print_status("🎉 Application is starting up!", "SUCCESS")
    print_status("Frontend: http://localhost:8501", "INFO")
    print_status("Backend: http://localhost:8000", "INFO")
    print_status("Press Ctrl+C to stop the application", "INFO")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_status("🛑 Stopping application...", "INFO")
        sys.exit(0)

if __name__ == "__main__":
    main() 