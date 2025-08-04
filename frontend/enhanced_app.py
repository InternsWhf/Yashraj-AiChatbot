import streamlit as st
import requests
import time
from datetime import datetime
import os
import json
import base64
import tempfile

# Page configuration
st.set_page_config(
    page_title="WESTERN HEAT & FORGE AI Assistant & Knowledge Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state with proper defaults
def initialize_session_state():
    """Initialize all session state variables with proper defaults"""
    defaults = {
        "messages": [],
        "chat_sessions": {},
        "current_chat_id": None,
        "user": None,
        "auth_token": None,
        "chat_history": [],
        "uploaded_files": [],
        "current_page": "login",
        "sessions_loaded": False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Initialize session state
initialize_session_state()

# Backend connection check with timeout
def check_backend_connection():
    """Check if backend is accessible with proper error handling"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException):
        return False
    except Exception:
        return False

# Show connection status
if not check_backend_connection():
    st.error("⚠️ Backend service is not running. Please ensure the backend is started.")
    st.info("💡 If you're running this for the first time, use the startup script: `python start_robust.py`")
    st.stop()

# Clean CSS styling with cache busting
st.markdown("""
<style>
    /* Main styling */
    .main {
        background: #f5f5f5;
    }
    
    /* Header styling */
    .header {
        background: #FF6B35;
        color: white;
        padding: 1rem 2rem;
        border-radius: 0 0 10px 10px;
        margin-bottom: 2rem;
    }
    
    .nav-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .nav-btn {
        background: rgba(255, 255, 255, 0.2);
        color: black;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        border: none;
    }
    
    /* Chat styling */
    .chat-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    
    .chat-message {
        background: #f0f0f0;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .ai-message {
        background: white !important;
        color: #333 !important;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .user-message {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: right;
    }
    
    /* Input styling */
    .input-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #FF6B35;
        margin-top: 2rem;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# API request helper with comprehensive error handling
def api_request(method, endpoint, data=None, files=None):
    """Make authenticated API request with comprehensive error handling"""
    headers = {}
    if st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    
    try:
        if method == "GET":
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=120)
        elif method == "POST":
            if files:
                response = requests.post(f"http://localhost:8000{endpoint}", headers=headers, files=files, timeout=120)
            else:
                response = requests.post(f"http://localhost:8000{endpoint}", headers=headers, json=data, timeout=120)
        elif method == "DELETE":
            response = requests.delete(f"http://localhost:8000{endpoint}", headers=headers, timeout=120)
        
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server. Please ensure the backend is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. The server is taking too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 Network error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None

# Authentication functions with proper error handling
def login_user(email, password):
    """Login user with proper error handling"""
    try:
        response = api_request("POST", "/auth/login", data={"email": email, "password": password})
        
        if response and response.status_code == 200:
            data = response.json()
            st.session_state.auth_token = data.get("access_token")
            st.session_state.user = data.get("user")
            return True
        elif response and response.status_code == 401:
            st.error("❌ Invalid email or password. Please try again.")
            return False
        else:
            st.error("❌ Login failed. Please try again.")
            return False
    except Exception as e:
        st.error(f"❌ Login error: {e}")
        return False

def logout_user():
    """Logout user and clear session"""
    st.session_state.auth_token = None
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.chat_sessions = {}
    st.session_state.current_chat_id = "default"
    st.rerun()

def register_user(name, email, password):
    """Register user with proper error handling"""
    try:
        response = api_request("POST", "/auth/register", data={
            "name": name,
            "email": email,
            "password": password
        })
        
        if response and response.status_code == 200:
            return True
        elif response and response.status_code == 400:
            st.error("❌ Registration failed. Email might already be in use.")
            return False
        else:
            st.error("❌ Registration failed. Please try again.")
            return False
    except Exception as e:
        st.error(f"❌ Registration error: {e}")
        return False

# Chat session management (ChatGPT-style)
def create_new_chat():
    """Create a new chat session"""
    import uuid
    chat_id = str(uuid.uuid4())
    
    # Save current chat if it has messages
    if st.session_state.messages and st.session_state.current_chat_id:
        current_chat_id = st.session_state.current_chat_id
        if current_chat_id in st.session_state.chat_sessions:
            st.session_state.chat_sessions[current_chat_id]["messages"] = st.session_state.messages.copy()
            st.session_state.chat_sessions[current_chat_id]["last_updated"] = datetime.now().isoformat()
            
            # Save to database
            title = st.session_state.chat_sessions[current_chat_id].get("title", "New Chat")
            save_chat_session_to_db(current_chat_id, title, st.session_state.messages)
    
    # Create new chat session
    st.session_state.chat_sessions[chat_id] = {
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "title": "New Chat"
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []

def switch_to_chat(chat_id):
    """Switch to a specific chat session"""
    if chat_id in st.session_state.chat_sessions:
        # Save current chat
        if st.session_state.messages and st.session_state.current_chat_id:
            current_chat_id = st.session_state.current_chat_id
            if current_chat_id in st.session_state.chat_sessions:
                st.session_state.chat_sessions[current_chat_id]["messages"] = st.session_state.messages.copy()
                st.session_state.chat_sessions[current_chat_id]["last_updated"] = datetime.now().isoformat()
                
                # Save to database
                title = st.session_state.chat_sessions[current_chat_id].get("title", "New Chat")
                save_chat_session_to_db(current_chat_id, title, st.session_state.messages)
        
        # Switch to selected chat
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chat_sessions[chat_id]["messages"].copy()

def delete_chat_session(chat_id):
    """Delete a chat session"""
    if chat_id in st.session_state.chat_sessions:
        # Delete from database
        delete_chat_session_from_db(chat_id)
        
        # Delete from session state
        del st.session_state.chat_sessions[chat_id]
        
        # If this was the current chat, create a new one
        if chat_id == st.session_state.current_chat_id:
            create_new_chat()

def update_chat_title(chat_id, title):
    """Update chat title based on first message"""
    if chat_id in st.session_state.chat_sessions:
        st.session_state.chat_sessions[chat_id]["title"] = title

def load_chat_sessions_from_db():
    """Load chat sessions from database"""
    if not st.session_state.auth_token or st.session_state.sessions_loaded:
        return
    
    try:
        response = api_request("GET", "/chat/sessions")
        if response and response.status_code == 200:
            sessions_data = response.json().get("sessions", [])
            
            # Convert database format to session state format
            for session in sessions_data:
                session_id = session["session_id"]
                st.session_state.chat_sessions[session_id] = {
                    "messages": session["messages"],
                    "created_at": session["created_at"],
                    "last_updated": session["last_updated"],
                    "title": session["title"]
                }
            
            st.session_state.sessions_loaded = True
            print(f"Loaded {len(sessions_data)} chat sessions from database")
    except Exception as e:
        print(f"Error loading chat sessions: {e}")

def save_chat_session_to_db(chat_id, title, messages):
    """Save chat session to database"""
    if not st.session_state.auth_token:
        return
    
    try:
        session_data = {
            "session_id": chat_id,
            "title": title,
            "messages": messages
        }
        
        response = api_request("POST", "/chat/sessions", data=session_data)
        if response and response.status_code == 200:
            print(f"Saved chat session {chat_id} to database")
        else:
            print(f"Failed to save chat session {chat_id}")
    except Exception as e:
        print(f"Error saving chat session: {e}")

def delete_chat_session_from_db(chat_id):
    """Delete chat session from database"""
    if not st.session_state.auth_token:
        return
    
    try:
        response = api_request("DELETE", f"/chat/sessions/{chat_id}")
        if response and response.status_code == 200:
            print(f"Deleted chat session {chat_id} from database")
        else:
            print(f"Failed to delete chat session {chat_id}")
    except Exception as e:
        print(f"Error deleting chat session: {e}")

# Sidebar with user info and controls
with st.sidebar:
    st.markdown("### 🔧 Debug Info")
    st.write(f"Auth Token: {'✅ Set' if st.session_state.auth_token else '❌ Not Set'}")
    st.write(f"User: {'✅ Set' if st.session_state.user else '❌ Not Set'}")
    
    if st.button("🔄 Clear Session (Debug)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()
        st.rerun()
    
    if st.session_state.auth_token:
        # Load chat sessions from database on first load
        load_chat_sessions_from_db()
        st.markdown("---")
        st.markdown(f"### 👤 Welcome, {st.session_state.user.get('name', 'User')}!")
        
        if st.button("🚪 Logout"):
            logout_user()
        
        st.markdown("---")
        
        # Document management
        st.markdown("### 📄 Documents")
        
        # Upload documents - Support multiple files and all formats
        uploaded_files = st.file_uploader(
            "Upload documents (PDF, Excel, Images, CSV, Word, PowerPoint, Text)",
            type=['pdf', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'csv', 'txt', 'doc', 'docx', 'ppt', 'pptx'],
            accept_multiple_files=True,
            help="Upload up to 30 documents. The AI will read and understand ALL content including text, tables, images, and data."
        )
        
        if uploaded_files:
            # Process multiple files efficiently
            new_files = [f for f in uploaded_files if f not in st.session_state.uploaded_files]
            
            if new_files:
                st.info(f"📤 Processing {len(new_files)} new files...")
                
                for uploaded_file in new_files:
                    st.session_state.uploaded_files.append(uploaded_file)
                    
                    # Upload to backend with comprehensive processing
                    with st.spinner(f"📄 Processing {uploaded_file.name} (extracting all content)..."):
                        try:
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            response = api_request("POST", "/upload", files=files)
                            
                            if response and response.status_code == 200:
                                result = response.json()
                                if result.get("processed", False):
                                    st.success(f"✅ {uploaded_file.name} - Fully processed for AI understanding!")
                                else:
                                    st.success(f"✅ {uploaded_file.name} - Uploaded successfully!")
                            else:
                                st.error(f"❌ Failed to upload {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"❌ Upload error for {uploaded_file.name}: {e}")
                
                st.success(f"🎉 All {len(new_files)} files processed! You can now ask questions about any content.")
        
        # Enhanced Document Management Section
        st.markdown("### 📁 Document Management")
        
        # Load and display previously uploaded files from backend
        try:
            response = api_request("GET", "/documents")
            if response and response.status_code == 200:
                documents_data = response.json().get("documents", [])
                
                if documents_data:
                    st.markdown("**🗂️ Previously Uploaded Files:**")
                    
                    for doc in documents_data:
                        filename = doc.get('filename', 'Unknown')
                        file_size = doc.get('file_size', 0)
                        upload_time = doc.get('upload_time', 'Unknown')
                        file_type = doc.get('file_type', 'Unknown')
                        
                        # Format file size
                        if file_size > 1024 * 1024:
                            size_str = f"{file_size / (1024 * 1024):.1f} MB"
                        elif file_size > 1024:
                            size_str = f"{file_size / 1024:.1f} KB"
                        else:
                            size_str = f"{file_size} bytes"
                        
                        # Format upload time
                        try:
                            if upload_time != 'Unknown':
                                upload_dt = datetime.fromisoformat(upload_time.replace('Z', '+00:00'))
                                time_str = upload_dt.strftime("%b %d, %I:%M %p")
                            else:
                                time_str = "Unknown"
                        except:
                            time_str = "Unknown"
                        
                        # Create expandable section for each file
                        with st.expander(f"📄 {filename}", expanded=False):
                            st.markdown(f"**File Details:**")
                            st.markdown(f"- **Type:** {file_type}")
                            st.markdown(f"- **Size:** {size_str}")
                            st.markdown(f"- **Uploaded:** {time_str}")
                            
                            # Create columns for actions
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                if st.button("👁️ View Details", key=f"view_{filename}", use_container_width=True):
                                    st.info(f"""
                                    **📄 File Information:**
                                    - **Name:** {filename}
                                    - **Type:** {file_type}
                                    - **Size:** {size_str}
                                    - **Uploaded:** {time_str}
                                    - **Status:** ✅ Available for AI processing
                                    """)
                            
                            with col2:
                                if st.button("🗑️ Delete File", key=f"delete_{filename}", use_container_width=True, type="secondary"):
                                    # Delete file from backend
                                    delete_response = api_request("DELETE", f"/documents/{filename}")
                                    if delete_response and delete_response.status_code == 200:
                                        st.success(f"✅ {filename} deleted successfully!")
                                        # Refresh the page to update the list
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to delete {filename}")
                    
                    st.markdown("---")
                    
                    # Clear all documents button
                    if st.button("🗑️ Clear All Documents", type="secondary", use_container_width=True):
                        clear_response = api_request("DELETE", "/documents")
                        if clear_response and clear_response.status_code == 200:
                            st.success("✅ All documents cleared successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to clear documents")
                else:
                    st.markdown("*📭 No files uploaded yet*")
                    st.markdown("*Upload files above to see them here*")
            else:
                st.markdown("*❌ Unable to load files from server*")
        except Exception as e:
            st.markdown(f"*❌ Error loading files: {str(e)}*")
        
        st.markdown("---")
        
        # Chat Sessions Management
        st.markdown("### 💬 Chat Sessions")
        
        if st.button("🆕 New Chat", type="primary", use_container_width=True):
            create_new_chat()
            st.rerun()
        
        # Display existing chat sessions (ChatGPT-style)
        if st.session_state.chat_sessions:
            st.markdown("**💬 Chat History:**")
            for chat_id, session_data in st.session_state.chat_sessions.items():
                # Get chat title
                chat_title = session_data.get("title", "New Chat")
                if session_data["messages"]:
                    first_msg = session_data["messages"][0]["content"][:50]
                    if len(first_msg) == 50:
                        first_msg += "..."
                    chat_title = first_msg
                
                # Show current indicator
                current_indicator = " 🔵" if chat_id == st.session_state.current_chat_id else ""
                
                # Format timestamp
                created_time = datetime.fromisoformat(session_data["created_at"]).strftime("%b %d, %I:%M %p")
                
                # Create columns for chat button and delete button
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    if st.button(f"📝 {chat_title}{current_indicator}", key=f"chat_{chat_id}", use_container_width=True):
                        switch_to_chat(chat_id)
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Delete this chat"):
                        delete_chat_session(chat_id)
                        st.rerun()
                
                # Show timestamp in smaller text
                st.caption(f"   {created_time}")

# Authentication check
st.write(f"🔍 Auth Check: {'❌ Not authenticated' if not st.session_state.auth_token else '✅ Authenticated'}")

if not st.session_state.auth_token:
    # Login Page
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="color: #FF6B35;">WESTERN HEAT & FORGE</h1>
        <p style="color: #666;">AI Assistant & Knowledge Hub</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add tabs for login and register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("""
                <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h2 style="text-align: center; color: #FF6B35;">🔐 Secure Login</h2>
                    <p style="text-align: center; color: #666; margin-bottom: 20px;">Access your WHF AI Assistant</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form("login_form"):
                    email = st.text_input("📧 Email", placeholder="Enter your email address")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        login_button = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
                    with col2:
                        demo_button = st.form_submit_button("🎯 Demo Login", use_container_width=True)
                    
                    if login_button and email and password:
                        if login_user(email, password):
                            st.success("✅ Welcome back! Login successful!")
                            # Create new chat session on login
                            create_new_chat()
                            st.rerun()
                    
                    if demo_button:
                        if login_user("interns@whfpl.in", "Yashraj"):
                            st.success("✅ Demo login successful! Welcome!")
                            # Create new chat session on login
                            create_new_chat()
                            st.rerun()
    
    with tab2:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("""
                <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h2 style="text-align: center; color: #FF6B35;">🌟 Create Account</h2>
                    <p style="text-align: center; color: #666; margin-bottom: 20px;">Join WHF AI Assistant</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form("register_form"):
                    name = st.text_input("👤 Full Name", placeholder="Enter your full name")
                    email = st.text_input("📧 Email", placeholder="Enter your email address")
                    password = st.text_input("🔒 Password", type="password", placeholder="Create a password (min 6 chars)")
                    confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                    
                    register_button = st.form_submit_button("🎉 Create Account", type="primary", use_container_width=True)
                    
                    if register_button:
                        if not name or not email or not password:
                            st.error("❌ Please fill in all fields")
                        elif password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(password) < 6:
                            st.error("❌ Password must be at least 6 characters long")
                        else:
                            if register_user(name, email, password):
                                st.success("🎉 Account created successfully! Please log in.")
                        st.rerun()
    
    st.stop()

# Main application (after authentication)
# WHF Header
st.markdown("""
<div class="header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 40px; height: 40px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #FF6B35;">W</div>
            <div>
                <h1 style="margin: 0; font-size: 24px;">WESTERN HEAT & FORGE</h1>
                <p style="margin: 0; opacity: 0.9;">AI Assistant & Knowledge Hub</p>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 15px; font-size: 12px; font-weight: bold;">Est. 1982 • API Certified</div>
    </div>
    <div class="nav-buttons">
        <button class="nav-btn">Forging</button>
        <button class="nav-btn">Heat Treatment</button>
        <button class="nav-btn">Machining</button>
        <button class="nav-btn">Coating</button>
        <button class="nav-btn">Cladding</button>
        <button class="nav-btn">Lab Testing</button>
    </div>
</div>
""", unsafe_allow_html=True)

# AI Assistant Panel
st.markdown("""
<div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 2rem; border-left: 4px solid #FF6B35;">
    <div style="display: flex; align-items: center; gap: 1rem;">
        <div style="font-size: 20px;">📄</div>
        <h3 style="margin: 0;">WHF AI Assistant</h3>
        <div style="margin-left: auto; display: flex; gap: 0.5rem;">
            <button style="background: #f0f0f0; border: none; border-radius: 15px; padding: 0.5rem; cursor: pointer;">🎤</button>
            <button style="background: #FF6B35; border: none; border-radius: 15px; padding: 0.5rem; cursor: pointer; color: white;">🔊</button>
            <button style="background: #28a745; border: none; border-radius: 15px; padding: 0.5rem; cursor: pointer; color: white;">Ready</button>
        </div>
    </div>
    <p style="margin: 0; color: #666;">Ask me anything about Western Heat & Forge.</p>
</div>
""", unsafe_allow_html=True)

# Chat Interface
st.markdown("""
<div class="chat-container">
    <h3 style="color: #FF6B35; margin-bottom: 1.5rem; text-align: center;">💬 WHF AI Chat</h3>
    <div style="max-height: 400px; overflow-y: auto; margin-bottom: 2rem;">
""", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f"""
        <div class="ai-message">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <div style="width: 25px; height: 25px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #FF6B35; font-weight: bold;">🤖</div>
                <strong>WHF AI Assistant</strong>
            </div>
            {message["content"]}
            <div style="margin-top: 0.5rem; font-size: 11px; opacity: 0.8;">
                {datetime.now().strftime("%I:%M %p")} 😊 🔊
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong><br/>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    
# Welcome message if no chat history
if not st.session_state.messages:
    st.markdown(f"""
    <div class="ai-message">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <div style="width: 25px; height: 25px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #FF6B35; font-weight: bold;">🤖</div>
            <strong>WHF AI Assistant</strong>
        </div>
        Hello! I'm your WHF AI assistant. I can help you with any questions about your company documents and processes. Try uploading some documents first!
        <div style="margin-top: 0.5rem; font-size: 11px; opacity: 0.8;">
            {datetime.now().strftime("%I:%M %p")} 😊 🔊
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("</div></div>", unsafe_allow_html=True)

# Chat input section
st.markdown("""
<div class="input-container">
    <h4 style="margin-bottom: 1rem; color: #FF6B35;">💬 Ask Your Question:</h4>
    <p style="color: #666; margin-bottom: 1rem; font-size: 14px;">Type your question below and press Enter to get an answer from the WHF AI Assistant.</p>
""", unsafe_allow_html=True)

if prompt := st.chat_input("Type your question here... (e.g., 'What is the 2nd step in 2T hammering?')"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Update chat title if this is the first message
    if len(st.session_state.messages) == 1:
        update_chat_title(st.session_state.current_chat_id, prompt[:50])
    
    # Save to current session and database
    if st.session_state.current_chat_id in st.session_state.chat_sessions:
        st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"] = st.session_state.messages.copy()
        st.session_state.chat_sessions[st.session_state.current_chat_id]["last_updated"] = datetime.now().isoformat()
        
        # Save to database
        title = st.session_state.chat_sessions[st.session_state.current_chat_id].get("title", "New Chat")
        save_chat_session_to_db(st.session_state.current_chat_id, title, st.session_state.messages)
    
    # Display user message
    st.markdown(f"""
    <div class="user-message">
        <strong>You:</strong><br/>
        {prompt}
    </div>
    """, unsafe_allow_html=True)
    
    # Get AI response
    with st.spinner("🤔 Thinking..."):
        try:
            # Make API request
            response = api_request("POST", "/ask", data={"question": prompt})
            
            if response and response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "Sorry, I couldn't process your request.")
                source_files = data.get("source_files", [])
                has_context = data.get("has_context", False)
                
                # Display the answer
                st.markdown(f"""
                <div class="ai-message">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 25px; height: 25px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #FF6B35; font-weight: bold;">🤖</div>
                        <strong>WHF AI Assistant</strong>
                    </div>
                    {answer}
                    <div style="margin-top: 0.5rem; font-size: 11px; opacity: 0.8;">
                        {datetime.now().strftime("%I:%M %p")} 😊 🔊
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Save to current session and database
                if st.session_state.current_chat_id in st.session_state.chat_sessions:
                    st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"] = st.session_state.messages.copy()
                    st.session_state.chat_sessions[st.session_state.current_chat_id]["last_updated"] = datetime.now().isoformat()
                    
                    # Update chat title if this is the first exchange
                    if len(st.session_state.messages) == 2:
                        first_question = st.session_state.messages[0]["content"][:50]
                        update_chat_title(st.session_state.current_chat_id, first_question)
                    
                    # Save to database
                    title = st.session_state.chat_sessions[st.session_state.current_chat_id].get("title", "New Chat")
                    save_chat_session_to_db(st.session_state.current_chat_id, title, st.session_state.messages)
                
                # Show source files if available
                if source_files:
                    st.markdown("---")
                    st.markdown("**📄 Sources:** " + ", ".join(source_files))
            
            else:
                error_msg = "Sorry, I'm having trouble connecting right now. Please try again later."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                # Save to current session
                if st.session_state.current_chat_id in st.session_state.chat_sessions:
                    st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"] = st.session_state.messages.copy()
                    st.session_state.chat_sessions[st.session_state.current_chat_id]["last_updated"] = datetime.now().isoformat()
                    
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            # Save to current session
            if st.session_state.current_chat_id in st.session_state.chat_sessions:
                    st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"] = st.session_state.messages.copy()
                    st.session_state.chat_sessions[st.session_state.current_chat_id]["last_updated"] = datetime.now().isoformat()
                
st.markdown("</div>", unsafe_allow_html=True)

# Clean Footer
st.markdown("""
<div style="position: fixed; bottom: 10px; right: 10px; background: rgba(255, 107, 53, 0.9); color: white; padding: 8px 12px; border-radius: 8px; font-size: 12px; font-weight: bold; z-index: 999;">
    Made by Yashraj 
</div>
""", unsafe_allow_html=True) 