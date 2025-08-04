# WHF AI Chatbot - Forgia

## 🚀 **Quick Start - IMPORTANT**

### **For Authentication & Full Features (RECOMMENDED)**
```bash
python start_perfect.py
```
**Features**: Login/Register, Chat History, Analytics, Export, 3D Avatar

### **Alternative Startup Scripts**
```bash
python start_enhanced.py  # Enhanced version
python start_simple.py    # Simple version
```

### **For Simple Version (No Authentication)**
```bash
python start_simple.py
```
**Features**: Basic chat without login

---

## 📋 **Available Startup Scripts**

| Script | App File | Features | Authentication |
|--------|----------|----------|----------------|
| `start_perfect.py` | `frontend/enhanced_app.py` | ✅ Full features | ✅ Yes |
| `start_enhanced.py` | `frontend/enhanced_app.py` | ✅ Full features | ✅ Yes |
| `start_simple.py` | `frontend/enhanced_app.py` | ✅ Full features | ✅ Yes |
| `start_frontend.py` | `frontend/enhanced_app.py` | ✅ Full features | ✅ Yes |
| `start_simple_backend.py` | - | Backend only | - |

## 🔐 **Login Credentials**

**Demo Account:**
- Email: `demo@whf.com`
- Password: `demo123`

**Or create a new account** using the registration form.

## 🌐 **Access URLs**

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Analytics Dashboard**: http://localhost:8501/analytics_dashboard

## 🎯 **Key Features**

### ✅ **Authentication System**
- User registration and login
- JWT token-based authentication
- Demo login option
- Secure session management

### ✅ **Document Processing**
- Multi-format support (PDF, Excel, Images)
- Cross-document search
- Source file citations
- Persistent storage

### ✅ **Chat Interface**
- Multiple chat sessions
- Chat history management
- Export to PDF/Email
- Voice input support

### ✅ **3D Avatar (Forgia)**
- Interactive 3D character
- Emotional responses
- User interaction

### ✅ **Analytics Dashboard**
- Usage statistics
- Document management
- User activity tracking

## 🛠️ **Troubleshooting**

### **If login page doesn't appear:**
1. Make sure you're running `start_enhanced.py`
2. Check that `frontend/enhanced_app.py` is being used
3. Clear browser cache and restart

### **If features are missing:**
- Always use `start_enhanced.py` for full features
- The old `app.py` has basic features only
- `enhanced_app.py` has all authentication and advanced features

## 📁 **File Structure**

```
frontend/
├── enhanced_app.py    # ✅ Full features with authentication
├── app.py            # ❌ Old version (basic features only)
├── avatar.py         # 3D avatar functionality
└── pages/
    └── analytics_dashboard.py

backend/
├── main.py           # Main API endpoints
├── auth.py           # Authentication system
├── qa_engine.py      # AI response engine
└── database.py       # Database management
```

## 🔧 **Development**

To run individual components:

```bash
# Backend only
python start_backend.py

# Frontend only (requires backend running)
python start_frontend.py
```

---

**Made by Yashraj and Ashwin** 🚀 