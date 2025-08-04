# 🚀 WHF AI Chatbot - Tomorrow's Startup Guide

## ✅ **Quick Start (Choose One)**

### Option 1: Double-Click Startup (Easiest)
1. **Double-click** `start_project.bat` 
2. Wait for both services to start
3. Browser will open automatically

### Option 2: PowerShell Startup (Recommended)
1. **Right-click** `start_project.ps1`
2. Select "Run with PowerShell"
3. Wait for both services to start
4. Browser will open automatically

### Option 3: Manual Commands (If needed)
```powershell
# 1. Open PowerShell in this folder
# 2. Activate virtual environment
venv\Scripts\Activate.ps1

# 3. Set OpenAI API Key
$env:OPENAI_API_KEY = "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"

# 4. Start Backend (in new terminal)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 5. Start Frontend (in another new terminal)
python -m streamlit run frontend/enhanced_app.py --server.port 8501

# 6. Open browser
Start-Process "http://localhost:8501"
```

## 🔐 **Login Credentials**
- **Email:** `interns@whfpl.in`
- **Password:** `Yashraj`

## 🌐 **Access URLs**
- **Main App:** http://localhost:8501
- **Backend API:** http://localhost:8000

## 🛠️ **Troubleshooting**

### If you get "connection refused":
1. Make sure both services are running
2. Check that ports 8000 and 8501 are not blocked
3. Try restarting with the batch file

### If login fails:
1. Run `python reset_auth.py` to reset the database
2. Use the credentials above

### If you get import errors:
1. Make sure you're in the virtual environment
2. Run: `pip install -r requirements.txt`

## 📱 **Features Available**
- ✅ **Modern UI** with WHF branding
- ✅ **Document Upload** (PDF, Excel, Images)
- ✅ **Table Extraction** from documents
- ✅ **AI Chat** with context awareness
- ✅ **User Authentication**
- ✅ **Chat History**
- ✅ **Export Options**

## 🎯 **Quick Test**
1. Login with the credentials above
2. Upload a PDF or Excel file with tables
3. Ask: "Show me the tables in this document"
4. You should see formatted tables in the response!

---

**Happy coding tomorrow! 🎉** 