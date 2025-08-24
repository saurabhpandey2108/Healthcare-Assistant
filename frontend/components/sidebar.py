"""
Sidebar Component for SAFESPACE AI AGENT Streamlit Interface

This module provides the sidebar navigation, chat history, and quick actions.
"""

import streamlit as st
import requests
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frontend.components.session_manager import SessionManager

from frontend.utils.config import (
    ENDPOINTS, SESSION_TYPES, THERAPEUTIC_TOOLS, 
    EMERGENCY_CONTACTS, HELP_SECTIONS, STATUS_MESSAGES
)
from frontend.utils.styling import get_status_indicator, create_alert


def render_sidebar(session_manager: 'SessionManager'):
    """Render the complete sidebar interface"""
    
    # Header and branding
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #dee2e6; margin-bottom: 1rem;">
        <h2 style="margin: 0; color: #667eea;">🧠 SAFESPACE</h2>
        <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">AI Mental Health Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System status
    render_system_status()
    
    st.markdown("---")
    
    # Chat management
    render_chat_management(session_manager)
    
    st.markdown("---")
    
    # Quick therapeutic tools
    render_quick_tools()
    
    st.markdown("---")
    
    # Emergency resources
    render_emergency_section()
    
    st.markdown("---")
    
    # Settings and help
    render_settings_help()
    
    # Footer
    st.markdown("""
    <div style="position: fixed; bottom: 10px; left: 10px; right: 10px; text-align: center; font-size: 0.8rem; color: #6c757d;">
        Crafted with ❤️ by SAURABH PANDEY
    </div>
    """, unsafe_allow_html=True)


def render_system_status():
    """Render system status indicator"""
    try:
        response = requests.get(f"{ENDPOINTS['system_status']}", timeout=5)
        if response.status_code == 200:
            status = "online"
            message = STATUS_MESSAGES["online"]
        else:
            status = "warning"
            message = STATUS_MESSAGES["warning"]
    except:
        status = "offline"
        message = STATUS_MESSAGES["offline"]
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; padding: 0.5rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px; margin-bottom: 1rem;">
        {get_status_indicator(status)}
        <span style="font-size: 0.9rem;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def render_chat_management(session_manager: 'SessionManager'):
    """Render chat management section"""
    st.subheader("💬 Conversations")
    
    # New chat button with session type selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("➕ New Chat", use_container_width=True, key="new_chat_btn"):
            session_manager.create_new_chat()
            st.rerun()
    
    with col2:
        if st.button("⚙️", use_container_width=True, key="chat_settings_btn"):
            st.session_state.show_chat_settings = not st.session_state.get('show_chat_settings', False)
    
    # Session type selector (shown when settings clicked)
    if st.session_state.get('show_chat_settings', False):
        st.selectbox(
            "Session Type",
            options=list(SESSION_TYPES.keys()),
            format_func=lambda x: SESSION_TYPES[x],
            key="new_session_type",
            help="Choose the type of conversation session"
        )
        
        if st.button("Create Specialized Session", use_container_width=True):
            session_type = st.session_state.get('new_session_type', 'general')
            session_manager.create_new_chat(session_type)
            st.session_state.show_chat_settings = False
            st.rerun()
    
    # Active chat info
    active_chat = session_manager.get_active_chat()
    if active_chat:
        session_type_label = SESSION_TYPES.get(active_chat.get('session_type', 'general'), '💬 General')
        st.markdown(f"**Current:** {session_type_label}")
        st.markdown(f"*{active_chat.get('title', 'New Chat')}*")
    
    # Chat history
    st.markdown("**Recent Chats:**")
    
    # Sort chats by last updated
    sorted_chats = sorted(
        st.session_state.all_chats.items(),
        key=lambda x: x[1].get('last_updated', ''),
        reverse=True
    )
    
    for chat_id, chat_data in sorted_chats[:10]:  # Show last 10 chats
        is_active = chat_id == st.session_state.active_chat_id
        title = chat_data.get('title', 'New Chat')
        session_type = chat_data.get('session_type', 'general')
        
        # Truncate long titles
        display_title = title[:25] + "..." if len(title) > 25 else title
        
        # Chat item with icon based on session type
        session_icon = {
            'general': '💬',
            'therapy': '🧠', 
            'emergency': '🚨',
            'analysis': '📊'
        }.get(session_type, '💬')
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if st.button(
                f"{session_icon} {display_title}",
                key=f"chat_{chat_id}",
                use_container_width=True,
                disabled=is_active
            ):
                session_manager.switch_chat(chat_id)
        
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                session_manager.delete_chat(chat_id)
                st.rerun()


def render_quick_tools():
    """Render quick therapeutic tools"""
    st.subheader("🛠️ Quick Tools")
    
    for tool in THERAPEUTIC_TOOLS:
        if st.button(
            f"{tool['icon']} {tool['name']}", 
            use_container_width=True,
            key=f"quick_tool_{tool['tool']}",
            help=tool['description']
        ):
            # Add tool request to chat
            session_manager = st.session_state.get('session_manager')
            if session_manager:
                session_manager.add_message("user", f"Please use the {tool['name'].lower()} tool")
                st.rerun()


def render_emergency_section():
    """Render emergency resources section"""
    st.subheader("🚨 Emergency Support")
    
    # Emergency button
    if st.button(
        "🆘 EMERGENCY HELP",
        use_container_width=True,
        key="emergency_btn",
        help="Access immediate crisis resources"
    ):
        st.session_state.show_emergency_resources = True
    
    # Show emergency resources if requested
    if st.session_state.get('show_emergency_resources', False):
        st.markdown("### Crisis Resources")
        
        for region, contact in EMERGENCY_CONTACTS.items():
            st.markdown(f"""
            **{region}**
            - {contact['name']}
            - Phone: {contact['number']}
            - Text: {contact['text']}
            """)
        
        if st.button("Close", key="close_emergency"):
            st.session_state.show_emergency_resources = False
            st.rerun()
    
    # Crisis chat option
    if st.button(
        "💬 Start Crisis Chat",
        use_container_width=True,
        key="crisis_chat_btn"
    ):
        session_manager = st.session_state.get('session_manager')
        if session_manager:
            chat_id = session_manager.create_new_chat("emergency")
            session_manager.add_message(
                "assistant", 
                "I'm here to help you through this crisis. You are not alone. Please tell me what's happening.",
                {"priority": "high", "type": "crisis_support"}
            )
            st.rerun()


def render_settings_help():
    """Render settings and help section"""
    st.subheader("⚙️ Settings & Help")
    
    # Export chat history
    if st.button("📥 Export Chat", use_container_width=True):
        session_manager = st.session_state.get('session_manager')
        if session_manager:
            # Show export options
            st.session_state.show_export_options = True
    
    if st.session_state.get('show_export_options', False):
        export_format = st.selectbox(
            "Export Format",
            ["json", "markdown"],
            key="export_format"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export", key="do_export"):
                session_manager = st.session_state.get('session_manager')
                if session_manager:
                    exported_data = session_manager.export_chat_history(export_format)
                    st.download_button(
                        "Download",
                        exported_data,
                        file_name=f"chat_export.{export_format}",
                        mime=f"application/{export_format}"
                    )
        
        with col2:
            if st.button("Cancel", key="cancel_export"):
                st.session_state.show_export_options = False
                st.rerun()
    
    # Clear chat history
    if st.button("🗑️ Clear History", use_container_width=True):
        session_manager = st.session_state.get('session_manager')
        if session_manager:
            session_manager.clear_chat_history()
            st.success("Chat history cleared!")
            st.rerun()
    
    # Help sections
    with st.expander("ℹ️ Help & Documentation"):
        for section_key, section in HELP_SECTIONS.items():
            st.markdown(f"### {section['title']}")
            st.markdown(section['content'])
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        st.checkbox("Enable Debug Mode", key="debug_mode")
        st.checkbox("Auto-save Conversations", key="auto_save", value=True)
        st.slider("Chat History Limit", 10, 500, 100, key="history_limit")
        
        if st.button("Reset All Settings"):
            for key in ["debug_mode", "auto_save", "history_limit"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Settings reset to defaults!")
            st.rerun()