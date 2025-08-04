#!/usr/bin/env python3
"""
Robust Startup Script for WHF AI Chatbot
========================================
This script ensures both backend and frontend start properly with comprehensive error handling.
"""

import os
import sys
import time
import subprocess
import requests
import threading
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

def check_port(port, timeout=30):
    """Check if a port is listening"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def start_backend():
    """Start the backend service"""
    print_status("Starting backend service...", "INFO")
    
    # Ensure backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_status("Backend directory not found!", "ERROR")
        return False
    
    try:
        # Start backend with uvicorn
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "backend.main:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for backend to start
        print_status("Waiting for backend to start...", "INFO")
        if check_port(8000, timeout=30):
            print_status("✅ Backend is running on http://localhost:8000", "SUCCESS")
            return backend_process
        else:
            print_status("❌ Backend failed to start", "ERROR")
            backend_process.terminate()
            return False
            
    except Exception as e:
        print_status(f"Failed to start backend: {e}", "ERROR")
        return False

def start_frontend():
    """Start the frontend service"""
    print_status("Starting frontend service...", "INFO")
    
    # Ensure frontend file exists
    frontend_file = Path("frontend/enhanced_app.py")
    if not frontend_file.exists():
        print_status("Frontend file not found!", "ERROR")
        return False
    
    try:
        # Start frontend with streamlit
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/enhanced_app.py",
            "--server.port", "8501", "--server.address", "0.0.0.0",
            "--server.headless", "true", "--browser.gatherUsageStats", "false"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for frontend to start
        print_status("Waiting for frontend to start...", "INFO")
        time.sleep(10)  # Give streamlit time to start
        
        # Check if frontend is accessible
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print_status("✅ Frontend is running on http://localhost:8501", "SUCCESS")
                return frontend_process
            else:
                print_status(f"❌ Frontend returned status {response.status_code}", "ERROR")
                frontend_process.terminate()
                return False
        except requests.exceptions.RequestException:
            print_status("❌ Frontend is not accessible", "ERROR")
            frontend_process.terminate()
            return False
            
    except Exception as e:
        print_status(f"Failed to start frontend: {e}", "ERROR")
        return False

def open_browser():
    """Open the application in the default browser"""
    import webbrowser
    print_status("Opening application in browser...", "INFO")
    webbrowser.open("http://localhost:8501")

def main():
    """Main startup function"""
    print_status("🚀 Starting WHF AI Chatbot...", "INFO")
    print_status("=" * 50, "INFO")
    
    # Kill any existing processes
    print_status("Cleaning up existing processes...", "INFO")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                      capture_output=True, check=False)
        time.sleep(2)
    except:
        pass
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print_status("❌ Failed to start backend. Exiting.", "ERROR")
        return False
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print_status("❌ Failed to start frontend. Stopping backend.", "ERROR")
        backend_process.terminate()
        return False
    
    # Success message
    print_status("=" * 50, "SUCCESS")
    print_status("🎉 WHF AI Chatbot is now running!", "SUCCESS")
    print_status("📱 Frontend: http://localhost:8501", "SUCCESS")
    print_status("🔧 Backend: http://localhost:8000", "SUCCESS")
    print_status("=" * 50, "SUCCESS")
    
    # Open browser
    open_browser()
    
    # Keep processes running
    try:
        print_status("Press Ctrl+C to stop the application", "INFO")
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_process.poll() is not None:
                print_status("❌ Backend process stopped unexpectedly", "ERROR")
                break
            if frontend_process.poll() is not None:
                print_status("❌ Frontend process stopped unexpectedly", "ERROR")
                break
    except KeyboardInterrupt:
        print_status("Stopping application...", "INFO")
        backend_process.terminate()
        frontend_process.terminate()
        print_status("✅ Application stopped", "SUCCESS")

if __name__ == "__main__":
    main() 