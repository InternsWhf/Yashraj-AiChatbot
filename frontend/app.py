import streamlit as st
import requests
import time
from datetime import datetime
import speech_recognition as sr
import io
import wave
import numpy as np
import tempfile
import os

# Import avatar functionality
try:
    from avatar import show_avatar, update_avatar_state
    avatar_available = True
except ImportError:
    avatar_available = False
    def show_avatar(state="idle", message=""):
        pass
    def update_avatar_state(new_state, duration=3, message=""):
        pass

# Initialize session state for chat history and avatar
if "messages" not in st.session_state:
    st.session_state.messages = []

if "avatar_state" not in st.session_state:
    st.session_state.avatar_state = "idle"

if "avatar_message" not in st.session_state:
    st.session_state.avatar_message = ""

if "avatar_clicked" not in st.session_state:
    st.session_state.avatar_clicked = False

# Speech recognition function
def speech_to_text(audio_file):
    """Convert speech audio to text using speech recognition"""
    try:
        # Create recognizer instance
        recognizer = sr.Recognizer()
        
        # Use the audio file directly
        with sr.AudioFile(audio_file) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Record the audio
            audio = recognizer.record(source)
        
        # Recognize speech
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        st.error(f"Speech recognition error: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None

# AI Assistant response function
def get_ai_assistant_response(prompt):
    """Get AI assistant response with voice-like characteristics"""
    try:
        response = requests.post("http://localhost:8000/ask/", json={"question": prompt})
        if response.status_code == 200:
            answer = response.json()['answer']
            
            # Add AI assistant-like characteristics
            if any(keyword in prompt.lower() for keyword in ["hello", "hi", "hey", "greetings"]):
                return f"Hello! I'm Forgia, your AI assistant. {answer}"
            elif any(keyword in prompt.lower() for keyword in ["thank", "thanks", "appreciate"]):
                return f"You're very welcome! I'm here to help. {answer}"
            else:
                return f"Here's what I found for you: {answer}"
        else:
            return f"I'm sorry, I encountered an error: {response.text}"
    except Exception as e:
        return f"I'm having trouble connecting right now. Please try again later. Error: {str(e)}"

# Page configuration
st.set_page_config(
    page_title="Forgia - WHF AI Assistant", 
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display avatar if available
if avatar_available:
    # Get current avatar state
    current_state = st.session_state.avatar_state
    current_message = st.session_state.avatar_message
    
    # Check if avatar state timer has expired and reset to idle
    if hasattr(st.session_state, 'avatar_state_timer'):
        if time.time() > st.session_state.avatar_state_timer:
            current_state = "idle"
            current_message = ""
            st.session_state.avatar_state = "idle"
            st.session_state.avatar_message = ""
    
    # Show the actual animated avatar
    show_avatar(current_state, current_message)
    
    # Place avatar status in sidebar for better control
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 Forgia Status")
        
        # Show avatar state and message
        if current_state == "thinking":
            st.info("🤔 Thinking...")
        elif current_state == "happy":
            st.success("😊 Happy!")
        elif current_state == "sad":
            st.error("😔 Sad")
        elif current_state == "waving":
            st.success("👋 Hello!")
        else:
            st.info("🤖 Idle")
        
        # Show message if exists
        if current_message:
            st.markdown(f"**Message:** {current_message}")

# Removed uploaded_files session state since we're using database

# Custom CSS for professional styling with 3D animations
st.markdown("""
<style>
    /* 3D Animated Background */
    .main {
        background: linear-gradient(45deg, #0f172a, #1e293b, #334155);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        position: relative;
        overflow: hidden;
    }
    
    .main::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        animation: float 20s ease-in-out infinite;
        z-index: -1;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    /* WHF Logo Styling */
    .whf-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .logo-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #000 0%, #333 50%, #ff6600 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        margin-right: 1rem;
        box-shadow: 0 8px 32px rgba(255, 102, 0, 0.3);
        animation: logoGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes logoGlow {
        0% { box-shadow: 0 8px 32px rgba(255, 102, 0, 0.3); }
        100% { box-shadow: 0 8px 32px rgba(255, 102, 0, 0.6); }
    }
    
    .logo-text {
        text-align: left;
    }
    
    .logo-text h1 {
        color: #333;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
        font-family: 'Georgia', serif;
    }
    
    .logo-text .tagline {
        color: #ff6600;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 0;
        font-family: 'Arial', sans-serif;
    }
    
    .logo-text .separator {
        width: 100%;
        height: 2px;
        background: #ff6600;
        margin: 0.2rem 0;
    }
    
    /* Main Header */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInDown 1s ease-out;
    }
    
    @keyframes slideInDown {
        from { transform: translateY(-50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .ai-assistant {
        font-size: 1.3rem;
        color: #ff6600;
        font-weight: bold;
        margin-top: 1rem;
        text-align: center;
    }
    
    /* Sidebar Styling */
    .sidebar-header {
        background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 10px 20px rgba(255, 102, 0, 0.3);
        animation: slideInLeft 1s ease-out;
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Chat Container */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        animation: fadeIn 1s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Floating Elements */
    .floating-element {
        position: absolute;
        width: 100px;
        height: 100px;
        background: rgba(255, 102, 0, 0.1);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
        z-index: -1;
    }
    
    .floating-element:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
    .floating-element:nth-child(2) { top: 20%; right: 15%; animation-delay: 2s; }
    .floating-element:nth-child(3) { bottom: 30%; left: 20%; animation-delay: 4s; }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 102, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 102, 0, 0.4);
    }
    
    /* Chat Input Styling */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid #ff6600;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff8533;
        box-shadow: 0 0 20px rgba(255, 102, 0, 0.3);
        transform: scale(1.02);
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        border-radius: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="chatMessage"]:has(.stMarkdown) {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 204, 0.1) 100%);
        border-left: 4px solid #00d4ff;
    }
    
    /* User message styling */
    .stChatMessage[data-testid="chatMessage"]:has(.stMarkdown) {
        background: linear-gradient(135deg, rgba(255, 102, 0, 0.1) 0%, rgba(255, 133, 51, 0.1) 100%);
        border-left: 4px solid #ff6600;
    }
    
    /* Voice input styling */
    .voice-input-container {
        background: linear-gradient(135deg, rgba(135, 206, 235, 0.1) 0%, rgba(70, 130, 180, 0.1) 100%);
        border: 2px solid #87CEEB;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .voice-input-title {
        color: #4682B4;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }
    
    .voice-instructions {
        color: #666;
        font-size: 14px;
        text-align: center;
        margin-bottom: 15px;
    }
    
    /* ChatGPT-like styling */
    .chatgpt-style {
        background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
        border: 1px solid #d0d0d0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .ai-response {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #007bff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Floating background elements for 3D effect
st.markdown("""
<div class="floating-element"></div>
<div class="floating-element"></div>
<div class="floating-element"></div>
""", unsafe_allow_html=True)

# Main header with WHF logo and branding
st.markdown("""
<div class="main-header">
    <div class="whf-logo">
        <div class="logo-icon">W</div>
        <div class="logo-text">
            <h1>WESTERN</h1>
            <div class="separator"></div>
            <div class="tagline">HEAT & FORGE</div>
        </div>
    </div>
    <div class="ai-assistant">🤖 Forgia - AI Assistant</div>
</div>
""", unsafe_allow_html=True)

# Sidebar for file uploads and status
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h3>📁 WHF Document Hub</h3>
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Upload & Process Documents</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("📁 Upload Documents")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF, Excel, or Image files", 
        type=["pdf", "xlsx", "xls", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    
    # Upload button
    if uploaded_files and st.button("📤 Upload All Files"):
        with st.spinner("Uploading files..."):
            for uploaded_file in uploaded_files:
                try:
                    res = requests.post("http://localhost:8000/upload/", files={"file": uploaded_file})
                    if res.status_code == 200:
                        st.success(f"✅ {uploaded_file.name}")
                    else:
                        st.error(f"❌ {uploaded_file.name}: {res.text}")
                except Exception as e:
                    st.error(f"❌ {uploaded_file.name}: {str(e)}")
            
            # Refresh the page to show updated documents
            st.rerun()
    
    # Show uploaded files from database
    try:
        documents_response = requests.get("http://localhost:8000/documents")
        if documents_response.status_code == 200:
            documents = documents_response.json()["documents"]
            if documents:
                st.markdown("---")
                st.subheader("📚 Stored Documents")
                for doc in documents:
                    st.write(f"📄 {doc['filename']} ({doc['file_size']} bytes)")
                    st.caption(f"Uploaded: {doc['upload_time']}")
                
                # Clear all documents button
                if st.button("🗑️ Clear All Documents"):
                    clear_response = requests.delete("http://localhost:8000/documents")
                    if clear_response.status_code == 200:
                        st.success("All documents cleared!")
                        st.rerun()
                    else:
                        st.error("Failed to clear documents")
    except:
        st.info("📚 No documents stored yet")
    
    # Backend status
    st.markdown("---")
    st.subheader("🔧 Backend Status")
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success(f"✅ Backend Online")
            st.info(f"📄 Documents: {health_data.get('documents_count', 0)}")
            if 'chunks_count' in health_data:
                st.info(f"📝 Chunks: {health_data['chunks_count']}")
            if 'qa_available' in health_data:
                qa_status = "✅ Available" if health_data['qa_available'] else "❌ Not Available"
                st.info(f"🤖 AI Engine: {qa_status}")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
    
    # Clear chat button
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Voice input section
st.markdown("---")
st.markdown("""
<div class="voice-input-container">
    <div class="voice-input-title">🎤 Voice Input (Like ChatGPT)</div>
    <div class="voice-instructions">Upload an audio file or type your question below!</div>
</div>
""", unsafe_allow_html=True)

# Create a nice voice input container
with st.container():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File uploader for audio files
        uploaded_audio = st.file_uploader(
            "🎤 Upload audio file (WAV, MP3, M4A)",
            type=['wav', 'mp3', 'm4a'],
            help="Record your question using your phone/computer and upload it here"
        )
        
        if uploaded_audio:
            st.audio(uploaded_audio, format=f"audio/{uploaded_audio.type}")
    
    with col2:
        st.markdown("**📝 OR Type below**")
        st.markdown("Use the chat input at the bottom 👇")

# Process voice input
if uploaded_audio is not None:
    with st.spinner("🎤 Converting speech to text..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.type}") as tmp_file:
            tmp_file.write(uploaded_audio.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Convert speech to text
            voice_text = speech_to_text(tmp_file_path)
            
            if voice_text:
                st.success(f"🎤 **You said:** {voice_text}")
                # Use the voice input as the prompt
                prompt = voice_text
            else:
                st.error("🎤 Could not understand the speech. Please try again or type your question.")
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)

# Chat input
if prompt := st.chat_input("Ask Forgia anything about your documents... 🤖"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Update avatar state for user input
    if avatar_available:
        update_avatar_state("thinking", 2, "Processing your question...")
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Processing user input...
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                # Get AI assistant response with voice-like characteristics
                answer = get_ai_assistant_response(prompt)
                
                # Special handling for creator question
                if "who created this chatbot" in prompt.lower() or "who made this chatbot" in prompt.lower():
                    answer = "I am an AI chatbot namely Forgia developed by WHF Interns team"
                    if avatar_available:
                        update_avatar_state("happy", 4, "I'm Forgia! 🤖")
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Update avatar state based on response
                if avatar_available:
                    if any(keyword in prompt.lower() for keyword in ["hello", "hi", "hey", "greetings"]):
                        update_avatar_state("happy", 3, "Hello! 👋")
                    elif any(keyword in prompt.lower() for keyword in ["thank", "thanks", "appreciate"]):
                        update_avatar_state("happy", 3, "You're welcome! 😊")
                    elif any(keyword in answer.lower() for keyword in ["sorry", "error", "not sure", "don't know", "cannot", "unable"]):
                        update_avatar_state("sad", 3, "Let me try a different approach...")
                    else:
                        update_avatar_state("happy", 3, "Found helpful information! ✅")
                
                # Add AI assistant-like feedback
                if any(keyword in prompt.lower() for keyword in ["hello", "hi", "hey", "greetings"]):
                    st.success("👋 Hello! I'm here to help you with WHF documents!")
                elif any(keyword in prompt.lower() for keyword in ["thank", "thanks", "appreciate"]):
                    st.success("😊 You're welcome! I'm glad I could help!")
                elif any(keyword in answer.lower() for keyword in ["sorry", "error", "not sure", "don't know", "cannot", "unable"]):
                    st.info("🤔 Let me try to help you with a different approach...")
                else:
                    st.success("✅ I've found some helpful information for you!")
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                # Update avatar state for error
                if avatar_available:
                    update_avatar_state("sad", 3, "Connection error...")

# Welcome message if no chat history
if not st.session_state.messages:
    # Update avatar state for initial load
    if avatar_available:
        update_avatar_state("waving", 5, "Hello! I'm Forgia, your AI assistant! 👋")
    
    st.markdown("""
    <div class="chat-container">
        <h3>👋 Welcome to Western Heat & Forge AI Assistant!</h3>
        <p>I'm <strong>Forgia</strong>, your intelligent AI assistant. I can help you with:</p>
        <ul>
            <li>🏢 <strong>Company Information</strong> - Ask about WHF's services, products, and company details</li>
            <li>📄 <strong>Document Processing</strong> - Upload PDFs, Excel files, and images for analysis</li>
            <li>🔍 <strong>Smart Search</strong> - Find information from your uploaded documents</li>
            <li>💬 <strong>Conversational AI</strong> - I remember our chat history</li>
        </ul>
        <p><strong>Try asking:</strong> "What services does WHF offer?" or "Tell me about WHF's certifications"</p>
        <div style="text-align: center; margin-top: 20px; padding: 15px; background: rgba(0, 212, 255, 0.1); border-radius: 10px; border: 1px solid rgba(0, 212, 255, 0.3);">
            <p style="margin: 0; color: #0099cc; font-weight: bold;">💡 <strong>Pro Tip:</strong> Click on Forgia (the AI avatar) for a surprise! 🤖</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer with creator information
st.markdown("""
<div style="position: fixed; bottom: 10px; left: 10px; background: rgba(255, 255, 255, 0.9); padding: 8px 12px; border-radius: 8px; font-size: 12px; color: #666; z-index: 999;">
    made by Yashraj and Ashwin
</div>
""", unsafe_allow_html=True)
