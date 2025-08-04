# WHF AI Chatbot - Complete Startup Script (PowerShell)
# Run this script to start the entire application

Write-Host "========================================" -ForegroundColor Green
Write-Host "   WHF AI Chatbot - Complete Startup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Set OpenAI API Key
Write-Host "Setting OpenAI API Key..." -ForegroundColor Yellow
$env:OPENAI_API_KEY = "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"

# Install dependencies (if needed)
if (-not (Test-Path "requirements_installed.txt")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn PyMuPDF pdfplumber pandas openpyxl opencv-python Pillow openai weaviate-client streamlit python-multipart python-dotenv requests pymongo firebase-admin pyjwt PyPDF2 reportlab sendgrid plotly numpy python-jose passlib bcrypt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ WARNING: Some dependencies failed to install, but continuing..." -ForegroundColor Yellow
    }
    New-Item -ItemType File -Name "requirements_installed.txt" -Force | Out-Null
}

# Kill any existing Python processes
Write-Host "Stopping any existing services..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Start backend
Write-Host "Starting backend service..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'venv\Scripts\Activate.ps1'; `$env:OPENAI_API_KEY='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'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend
Write-Host "Starting frontend service..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'venv\Scripts\Activate.ps1'; python -m streamlit run frontend/enhanced_app.py --server.port 8501" -WindowStyle Normal

# Wait for frontend to start
Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Open browser
Write-Host "Opening application in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    WHF AI Chatbot is Starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Yellow
Write-Host "Email:    interns@whfpl.in" -ForegroundColor White
Write-Host "Password: Yashraj" -ForegroundColor White
Write-Host ""
Write-Host "✅ Application should open in your browser automatically!" -ForegroundColor Green
Write-Host "Press Enter to close this window..." -ForegroundColor Gray
Read-Host 