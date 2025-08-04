#!/usr/bin/env python3
"""
Start script for the Company AI Chatbot Frontend
"""
import subprocess
import sys
import os

def main():
    print("🎨 Starting Company AI Chatbot Frontend...")
    print("📁 Working directory:", os.getcwd())
    
    # Check if backend is running
    try:
        import requests
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print("✅ Backend server is running")
    except:
        print("⚠️  Warning: Backend server doesn't seem to be running")
        print("   Please start the backend first with: python start_backend.py")
        print("   Or run: uvicorn backend.main:app --reload")
    
    print("🌐 Starting Streamlit frontend...")
    print("📱 Frontend will be available at http://localhost:8501")
    
    try:
        # Change to frontend directory and run streamlit
        os.chdir("frontend")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "enhanced_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 