import streamlit as st
import time

def show_avatar(state="idle", message=""):
    """
    Display AI chatbot avatar with different states and animations
    """
    
    # Avatar CSS with modern design
    avatar_css = """
        <style>
    .ai-avatar-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
    .ai-avatar {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        position: relative;
        animation: float 3s ease-in-out infinite;
        border: 3px solid #ffffff;
    }
    
    .ai-avatar:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
    }
    
    .ai-avatar::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
            border-radius: 50%;
        z-index: -1;
        animation: rotate 3s linear infinite;
    }
    
    .avatar-face {
            display: flex;
        flex-direction: column;
            align-items: center;
        gap: 4px;
        }
        
        .avatar-eyes {
            display: flex;
            gap: 8px;
        margin-bottom: 4px;
    }
    
    .eye {
        width: 8px;
        height: 8px;
        background: #ffffff;
            border-radius: 50%;
        animation: blink 4s infinite;
    }
    
    .avatar-mouth {
        width: 16px;
        height: 6px;
        background: #ffffff;
        border-radius: 0 0 8px 8px;
        animation: talk 2s ease-in-out infinite;
    }
    
    .avatar-antenna {
            position: absolute;
        top: -8px;
            left: 50%;
            transform: translateX(-50%);
        width: 2px;
        height: 12px;
        background: #ffffff;
        border-radius: 1px;
    }
    
    .avatar-antenna::after {
            content: '';
            position: absolute;
        top: -4px;
            left: 50%;
            transform: translateX(-50%);
        width: 6px;
        height: 6px;
        background: #00ff88;
            border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .chat-bubble {
        position: absolute;
        bottom: 90px;
        right: 0;
        background: #ffffff;
        border: 2px solid #667eea;
        border-radius: 15px;
        padding: 12px 16px;
        max-width: 200px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        opacity: 1;
        transform: translateY(0);
        font-size: 12px;
        color: #333;
        line-height: 1.4;
    }
    
    .chat-bubble::after {
        content: '';
            position: absolute;
        bottom: -8px;
        right: 20px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid #667eea;
    }
    
    .chat-bubble::before {
        content: '';
            position: absolute;
        bottom: -6px;
        right: 20px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid #ffffff;
    }
    
    /* Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes blink {
        0%, 90%, 100% { opacity: 1; }
        95% { opacity: 0; }
    }
    
    @keyframes talk {
        0%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(1.5); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.2); }
    }
    
    /* State-specific animations */
    .ai-avatar.thinking .avatar-eyes {
        animation: thinking 2s ease-in-out infinite;
    }
    
    .ai-avatar.happy .avatar-mouth {
        background: #00ff88;
        border-radius: 8px;
        animation: smile 2s ease-in-out infinite;
    }
    
    .ai-avatar.sad .avatar-mouth {
        background: #ff6b6b;
        border-radius: 8px 8px 0 0;
        animation: frown 2s ease-in-out infinite;
    }
    
    .ai-avatar.waving .ai-avatar {
        animation: wave 1s ease-in-out infinite;
    }
    
    @keyframes thinking {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-2px); }
        75% { transform: translateX(2px); }
    }
    
    @keyframes smile {
        0%, 100% { border-radius: 8px; }
        50% { border-radius: 12px; }
    }
    
    @keyframes frown {
        0%, 100% { border-radius: 8px 8px 0 0; }
        50% { border-radius: 12px 12px 0 0; }
        }
        
        @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(-5deg); }
        75% { transform: rotate(5deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .ai-avatar-container {
            bottom: 10px;
            right: 10px;
        }
        
        .ai-avatar {
            width: 60px;
            height: 60px;
        }
        
        .chat-bubble {
            max-width: 150px;
            font-size: 11px;
            padding: 10px 12px;
        }
        }
        </style>
        """

    # Avatar HTML without JavaScript
    avatar_html = f"""
    {avatar_css}
    <div class="ai-avatar-container">
        <div class="ai-avatar {state}">
            <div class="avatar-antenna"></div>
            <div class="avatar-face">
                        <div class="avatar-eyes">
                    <div class="eye"></div>
                    <div class="eye"></div>
                </div>
                <div class="avatar-mouth"></div>
            </div>
        </div>
        {f'<div class="chat-bubble">{message}</div>' if message else ''}
    </div>
    """
    
    # Display the avatar
    st.markdown(avatar_html, unsafe_allow_html=True)

def update_avatar_state(new_state, duration=3, message=""):
    """
    Update avatar state and display message
    """
    if 'avatar_state' not in st.session_state:
        st.session_state.avatar_state = "idle"
    
    if 'avatar_message' not in st.session_state:
        st.session_state.avatar_message = ""
    
    if 'avatar_state_timer' not in st.session_state:
        st.session_state.avatar_state_timer = 0
    
    # Update state and message
    st.session_state.avatar_state = new_state
    st.session_state.avatar_message = message
    st.session_state.avatar_state_timer = time.time() + duration 