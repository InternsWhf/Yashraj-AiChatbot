# 🚀 WHF AI Chatbot - Quick Start Guide

## ✅ Easy Startup (Recommended)

### Option 1: Double-Click Startup (Windows)
1. **Double-click** `start_whf.bat` file
2. Wait for the application to start
3. The website will open automatically in your browser

### Option 2: Command Line Startup
1. Open Command Prompt or PowerShell in this folder
2. Run: `python start_robust.py`
3. Wait for both services to start
4. The website will open automatically

## 🔧 Manual Startup (If needed)

### Start Backend Only:
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Start Frontend Only:
```bash
streamlit run frontend/enhanced_app.py --server.port 8501
```

## 🌐 Access the Application

- **Frontend (Main App)**: http://localhost:8501
- **Backend API**: http://localhost:8000

## 🔐 Login Credentials

- **Email**: `interns@whfpl.in`
- **Password**: `Yashraj`

## 🛠️ Troubleshooting

### If you see "This site can't be reached":
1. Make sure both services are running
2. Check that ports 8000 and 8501 are not blocked
3. Try restarting with `python start_robust.py`

### If login fails:
1. Run `python reset_auth.py` to reset the database
2. Use the credentials above

### If you get import errors:
1. Make sure you're in the virtual environment
2. Run `pip install -r requirements.txt`

## 📱 Features

- ✅ **Modern UI** with WHF branding
- ✅ **Document Upload** (PDF, Excel, Images)
- ✅ **Table Extraction** from documents
- ✅ **AI Chat** with context awareness
- ✅ **User Authentication**
- ✅ **Chat History**
- ✅ **Export Options**

## 🎯 Quick Test

1. Login with the credentials above
2. Upload a PDF or Excel file with tables
3. Ask: "Show me the tables in this document"
4. You should see formatted tables in the response!

---

**Need help?** Check the main README.md for detailed instructions. 