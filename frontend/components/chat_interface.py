"""
Chat Interface Component for SAFESPACE AI AGENT Streamlit Interface

This module provides the main chat interface with advanced features.
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from frontend.components.session_manager import SessionManager

from frontend.utils.config import ENDPOINTS, EMERGENCY_KEYWORDS, ERROR_MESSAGES
from frontend.utils.styling import create_alert


def render_chat_interface(session_manager: 'SessionManager'):
    """Render the main chat interface"""
    
    # Chat header
    render_chat_header(session_manager)
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        render_chat_messages(session_manager)
    
    # Chat input (always at bottom)
    render_chat_input(session_manager)


def render_chat_header(session_manager: 'SessionManager'):
    """Render the chat header with title and controls"""
    
    active_chat = session_manager.get_active_chat()
    session_type = active_chat.get('session_type', 'general')
    
    # Session type indicators
    session_icons = {
        'general': '💬',
        'therapy': '🧠',
        'emergency': '🚨', 
        'analysis': '📊'
    }
    
    session_colors = {
        'general': '#667eea',
        'therapy': '#9c27b0',
        'emergency': '#f44336',
        'analysis': '#ff9800'
    }
    
    icon = session_icons.get(session_type, '💬')
    color = session_colors.get(session_type, '#667eea')
    
    st.markdown(f"""
    <div class="main-header" style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);">
        <h1>{icon} SAFESPACE AI AGENT</h1>
        <p>Your Personal Mental Health Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat info bar
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        chat_title = active_chat.get('title', 'New Chat')
        st.markdown(f"**Current Chat:** {chat_title}")
    
    with col2:
        message_count = len(active_chat.get('history', []))
        st.metric("Messages", message_count)
    
    with col3:
        indexed_count = len(active_chat.get('indexed_items', set()))
        st.metric("Knowledge Items", indexed_count)


def render_chat_messages(session_manager: 'SessionManager'):
    """Render chat message history with interactive elements"""
    
    chat_history = session_manager.get_chat_history()
    
    if not chat_history:
        # Welcome message for empty chats
        render_welcome_message(session_manager)
        return
    
    # Render each message
    for i, message in enumerate(chat_history):
        render_single_message(message, i, session_manager)


def render_welcome_message(session_manager: 'SessionManager'):
    """Render welcome message for new chats"""
    
    active_chat = session_manager.get_active_chat()
    session_type = active_chat.get('session_type', 'general')
    
    welcome_messages = {
        'general': """
        👋 **Welcome to SAFESPACE AI AGENT!**
        
        I'm here to provide mental health support and guidance. You can:
        
        - 💬 Have a conversation about how you're feeling
        - 📷 Upload images for emotional analysis
        - 🎤 Record audio messages
        - 📚 Add documents to enhance our conversation
        - 🆘 Access emergency resources if needed
        
        How are you feeling today?
        """,
        'therapy': """
        🧠 **Welcome to your Therapy Session**
        
        This is a safe space for therapeutic conversation. I'm here to:
        
        - Listen without judgment
        - Provide evidence-based mental health support
        - Guide you through coping strategies
        - Help you explore your thoughts and feelings
        
        What would you like to talk about today?
        """,
        'emergency': """
        🚨 **Crisis Support Session**
        
        I understand you may be going through a difficult time right now. 
        You are not alone, and help is available.
        
        **Immediate Resources:**
        - Emergency: Call 911 or your local emergency number
        - Crisis Text Line: Text HOME to 741741
        - National Suicide Prevention Lifeline: 988
        
        Please tell me what's happening. I'm here to listen and help.
        """,
        'analysis': """
        📊 **Analysis Session**
        
        Welcome to your analysis session. I can help you:
        
        - Analyze uploaded images for emotional insights
        - Process audio recordings for mood assessment
        - Review documents for mental health patterns
        - Generate reports on your progress
        
        What would you like to analyze today?
        """
    }
    
    welcome_text = welcome_messages.get(session_type, welcome_messages['general'])
    
    with st.chat_message("assistant"):
        st.markdown(welcome_text)
        
        # Quick action buttons
        if session_type == 'general':
            render_quick_action_buttons(session_manager)


def render_quick_action_buttons(session_manager: 'SessionManager'):
    """Render quick action buttons in welcome message"""
    
    st.markdown("**Quick Actions:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🫁 Breathing Exercise", key="quick_breathing"):
            session_manager.add_message("user", "I need help with a breathing exercise")
            st.rerun()
    
    with col2:
        if st.button("✨ Daily Affirmation", key="quick_affirmation"):
            session_manager.add_message("user", "Can you give me a daily affirmation?")
            st.rerun()
    
    with col3:
        if st.button("🆘 Emergency Help", key="quick_emergency"):
            # Switch to emergency session
            emergency_chat_id = session_manager.create_new_chat("emergency")
            st.rerun()


def render_single_message(message: Dict[str, Any], index: int, session_manager: 'SessionManager'):
    """Render a single chat message with interactive elements"""
    
    role = message.get('role', 'user')
    content = message.get('content', '')
    timestamp = message.get('timestamp', '')
    metadata = message.get('metadata', {})
    
    with st.chat_message(role):
        # Message content
        st.markdown(content)
        
        # Timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%H:%M")
                st.caption(f"📅 {formatted_time}")
            except:
                pass
        
        # Metadata display
        if metadata:
            render_message_metadata(metadata)
        
        # Interactive buttons for assistant messages
        if role == "assistant" and index == len(session_manager.get_chat_history()) - 1:
            render_message_actions(message, index, session_manager)


def render_message_metadata(metadata: Dict[str, Any]):
    """Render message metadata information"""
    
    if metadata.get('tool_called'):
        st.info(f"🔧 Tool used: `{metadata['tool_called']}`")
    
    if metadata.get('confidence'):
        confidence = metadata['confidence']
        st.progress(confidence, text=f"Confidence: {confidence:.1%}")
    
    if metadata.get('priority') == 'high':
        st.error("⚠️ High Priority Message")
    
    if metadata.get('type') == 'crisis_support':
        st.warning("🚨 Crisis Support Active")


def render_message_actions(message: Dict[str, Any], index: int, session_manager: 'SessionManager'):
    """Render action buttons for assistant messages"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get the last user message for context
    chat_history = session_manager.get_chat_history()
    last_user_message = None
    
    for i in range(index - 1, -1, -1):
        if chat_history[i].get('role') == 'user':
            last_user_message = chat_history[i].get('content', '')
            break
    
    with col1:
        if st.button("🔄 Regenerate", key=f"regen_{index}"):
            if last_user_message:
                # Remove last assistant message and re-ask
                session_manager.get_chat_history().pop()
                session_manager.add_message("user", f"Please provide an alternative response for: {last_user_message}")
                st.rerun()
    
    with col2:
        if st.button("🌐 Web Search", key=f"web_{index}"):
            if last_user_message:
                session_manager.add_message("user", f"Please search the web for more information about: {last_user_message}")
                st.rerun()
    
    with col3:
        if st.button("🎤 Voice Response", key=f"voice_{index}"):
            # Generate voice for this message
            generate_voice_response(message.get('content', ''))
    
    with col4:
        if st.button("📋 Copy", key=f"copy_{index}"):
            # Copy message to clipboard (requires JavaScript)
            st.code(message.get('content', ''), language='text')


def render_chat_input(session_manager: 'SessionManager'):
    """Render the chat input with advanced features"""
    
    # Main chat input
    user_input = st.chat_input("What's on your mind today? Type your message here...")
    
    if user_input:
        # Check for emergency keywords
        if check_emergency_content(user_input):
            handle_emergency_message(user_input, session_manager)
        else:
            handle_normal_message(user_input, session_manager)


def check_emergency_content(message: str) -> bool:
    """Check if message contains emergency keywords"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in EMERGENCY_KEYWORDS)


def handle_emergency_message(message: str, session_manager: 'SessionManager'):
    """Handle messages that contain emergency indicators"""
    
    # Switch to emergency session if not already
    active_chat = session_manager.get_active_chat()
    if active_chat.get('session_type') != 'emergency':
        emergency_chat_id = session_manager.create_new_chat("emergency")
    
    # Add emergency context
    session_manager.add_message("user", message, {"priority": "high", "emergency_detected": True})
    
    # Show immediate emergency resources
    st.error("""
    🚨 **Emergency Support Detected**
    
    If you're in immediate danger, please call:
    - Emergency Services: 911
    - Crisis Text Line: Text HOME to 741741
    - National Suicide Prevention Lifeline: 988
    
    I'm here to help you through this. Please continue our conversation.
    """)
    
    st.rerun()


def handle_normal_message(message: str, session_manager: 'SessionManager'):
    """Handle normal chat messages"""
    
    # Add user message
    session_manager.add_message("user", message)
    
    # Update chat title if it's a new chat
    session_manager.update_chat_title(message)
    
    st.rerun()


def generate_voice_response(text: str):
    """Generate voice response for text"""
    
    try:
        with st.spinner("Generating voice response..."):
            response = requests.post(
                ENDPOINTS['generate_voice'],
                json={
                    "text": text,
                    "use_premium_voice": st.session_state.get('use_premium_voice', False)
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                audio_file = result.get('audio_file')
                
                if audio_file:
                    st.audio(audio_file)
                    st.success("🔊 Voice response generated!")
                else:
                    st.error("Failed to generate voice response")
            else:
                st.error(f"Voice generation failed: {response.status_code}")
                
    except Exception as e:
        st.error(f"Error generating voice: {str(e)}")


def process_ai_response(session_manager: 'SessionManager'):
    """Process AI response for the last user message"""
    
    chat_history = session_manager.get_chat_history()
    
    if not chat_history or chat_history[-1].get('role') != 'user':
        return
    
    last_message = chat_history[-1]
    user_message = last_message.get('content', '')
    session_id = st.session_state.active_chat_id
    
    try:
        with st.spinner("🤔 Thinking..."):
            # Check if it's an emergency session
            active_chat = session_manager.get_active_chat()
            is_emergency = active_chat.get('session_type') == 'emergency'
            
            # Prepare request
            request_data = {
                "message": user_message,
                "session_id": session_id,
                "modality": "text"
            }
            
            # Add emergency context if needed
            if is_emergency or last_message.get('metadata', {}).get('emergency_detected'):
                request_data["priority"] = 5
                request_data["emergency_context"] = True
            
            # Make API request
            response = requests.post(
                ENDPOINTS['ask'],
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'Sorry, I encountered an error.')
                tool_called = result.get('tool_called', 'none')
                confidence = result.get('confidence')
                
                # Add metadata
                metadata = {
                    'tool_called': tool_called,
                    'confidence': confidence,
                    'response_time': datetime.now().isoformat()
                }
                
                if is_emergency:
                    metadata['priority'] = 'high'
                    metadata['type'] = 'crisis_support'
                
                # Add assistant response
                session_manager.add_message("assistant", ai_response, metadata)
                
            else:
                error_msg = ERROR_MESSAGES.get('processing_error', 'An error occurred while processing your request.')
                session_manager.add_message("assistant", error_msg, {"error": True})
                
    except requests.exceptions.Timeout:
        error_msg = ERROR_MESSAGES.get('timeout_error', 'Request timed out.')
        session_manager.add_message("assistant", error_msg, {"error": True})
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        session_manager.add_message("assistant", error_msg, {"error": True})
    
    st.rerun()


# Auto-process AI response when there's a pending user message
# This will be handled by the main app properly