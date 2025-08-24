"""
SAFESPACE AI AGENT - Enhanced Streamlit Application

This module provides the main entry point for the advanced Streamlit interface
with multimodal capabilities, file uploads, and proper MVC integration.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import UI components
from frontend.components.sidebar import render_sidebar
from frontend.components.chat_interface import render_chat_interface
from frontend.components.knowledge_base import render_knowledge_base
from frontend.components.multimodal_panel import render_multimodal_panel
from frontend.components.session_manager import SessionManager
from frontend.utils.styling import apply_custom_styles
from frontend.utils.config import BACKEND_URL

# Configure Streamlit page
st.set_page_config(
    page_title="🧠 SAFESPACE AI AGENT",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🧠"
)

# Apply custom styling
apply_custom_styles()

# Initialize session manager
session_manager = SessionManager()

def main():
    """Main application entry point"""
    # Initialize session manager
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = session_manager
    
    session_manager_instance = st.session_state.session_manager
    
    # Initialize session state
    session_manager_instance.initialize_session_state()
    
    # Render sidebar with navigation and chat history
    with st.sidebar:
        render_sidebar(session_manager_instance)
    
    # Create main layout columns
    col1, col2, col3 = st.columns([2, 1, 1])
    
    # Main chat interface
    with col1:
        render_chat_interface(session_manager_instance)
        
        # Check if we need to process AI response
        chat_history = session_manager_instance.get_chat_history()
        if chat_history and chat_history[-1].get('role') == 'user':
            # Import and call the AI response processor
            from frontend.components.chat_interface import process_ai_response
            process_ai_response(session_manager_instance)
    
    # Multimodal interaction panel
    with col2:
        render_multimodal_panel(session_manager_instance)
    
    # Knowledge base management
    with col3:
        render_knowledge_base(session_manager_instance)

if __name__ == "__main__":
    main()