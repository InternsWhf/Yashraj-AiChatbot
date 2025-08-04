#!/usr/bin/env python3
"""
Start script for the Simple Company AI Chatbot Backend (No Authentication)
"""
import uvicorn
import os
import sys

def main():
    print("🚀 Starting Simple Company AI Chatbot Backend...")
    print("📁 Working directory:", os.getcwd())
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("Please create a .env file with your OPENAI_API_KEY")
        sys.exit(1)
    
    # Check if OPENAI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in .env file!")
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully")
    print("🌐 Starting server on http://localhost:8000")
    print("📖 API docs will be available at http://localhost:8000/docs")
    print("🔓 No authentication required - simple mode")
    
    try:
        uvicorn.run(
            "backend.simple_main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 