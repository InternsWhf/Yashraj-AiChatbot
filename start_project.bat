@echo off
title WHF AI Chatbot - Complete Startup
color 0A

echo.
echo ========================================
echo    WHF AI Chatbot - Complete Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Set OpenAI API Key
echo Setting OpenAI API Key...
set OPENAI_API_KEY=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

REM Install dependencies (if needed)
if not exist "requirements_installed.txt" (
    echo Installing dependencies...
    pip install fastapi uvicorn PyMuPDF pdfplumber pandas openpyxl opencv-python Pillow openai weaviate-client streamlit python-multipart python-dotenv requests pymongo firebase-admin pyjwt PyPDF2 reportlab sendgrid plotly numpy python-jose passlib bcrypt
    if errorlevel 1 (
        echo WARNING: Some dependencies failed to install, but continuing...
    )
    echo. > requirements_installed.txt
)

REM Kill any existing Python processes
echo Stopping any existing services...
taskkill /f /im python.exe >nul 2>&1

REM Start backend
echo Starting backend service...
start "Backend" cmd /k "call venv\Scripts\activate.bat && set OPENAI_API_KEY=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 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend
echo Starting frontend service...
start "Frontend" cmd /k "call venv\Scripts\activate.bat && python -m streamlit run frontend/enhanced_app.py --server.port 8501"

REM Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

REM Open browser
echo Opening application in browser...
start http://localhost:8501

echo.
echo ========================================
echo    WHF AI Chatbot is Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Login Credentials:
echo Email:    interns@whfpl.in
echo Password: Yashraj
echo.
echo Press any key to close this window...
pause >nul 