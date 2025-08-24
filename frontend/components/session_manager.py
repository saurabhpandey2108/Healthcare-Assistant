"""
Session Manager for SAFESPACE AI AGENT Streamlit Interface

This module handles session state management, chat history, and user interactions.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional


class SessionManager:
    """Manages user sessions and chat history"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        # Multi-chat system
        if 'all_chats' not in st.session_state:
            st.session_state.all_chats = {}
        
        if 'active_chat_id' not in st.session_state:
            new_chat_id = str(uuid.uuid4())
            st.session_state.active_chat_id = new_chat_id
            st.session_state.all_chats[new_chat_id] = {
                "title": "New Chat",
                "history": [],
                "indexed_items": set(),
                "session_type": "general",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        
        # Multimodal state
        if 'uploaded_images' not in st.session_state:
            st.session_state.uploaded_images = {}
        
        if 'uploaded_audio' not in st.session_state:
            st.session_state.uploaded_audio = {}
        
        if 'generated_audio' not in st.session_state:
            st.session_state.generated_audio = {}
        
        # UI state
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = "chat"
        
        if 'show_advanced_options' not in st.session_state:
            st.session_state.show_advanced_options = False
        
        # System configuration
        if 'backend_status' not in st.session_state:
            st.session_state.backend_status = "unknown"
    
    def create_new_chat(self, session_type: str = "general") -> str:
        """Create a new chat session"""
        new_chat_id = str(uuid.uuid4())
        st.session_state.active_chat_id = new_chat_id
        st.session_state.all_chats[new_chat_id] = {
            "title": "New Chat",
            "history": [],
            "indexed_items": set(),
            "session_type": session_type,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        return new_chat_id
    
    def switch_chat(self, chat_id: str):
        """Switch to a different chat session"""
        if chat_id in st.session_state.all_chats:
            st.session_state.active_chat_id = chat_id
            st.rerun()
    
    def get_active_chat(self) -> Dict[str, Any]:
        """Get the currently active chat"""
        return st.session_state.all_chats.get(st.session_state.active_chat_id, {})
    
    def update_chat_title(self, message: str):
        """Update chat title based on first message"""
        active_chat = self.get_active_chat()
        if active_chat.get("title") == "New Chat":
            # Use first 30 characters as title
            title = message[:30] + "..." if len(message) > 30 else message
            st.session_state.all_chats[st.session_state.active_chat_id]["title"] = title
            st.session_state.all_chats[st.session_state.active_chat_id]["last_updated"] = datetime.now().isoformat()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the active chat"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        active_chat_id = st.session_state.active_chat_id
        st.session_state.all_chats[active_chat_id]["history"].append(message)
        st.session_state.all_chats[active_chat_id]["last_updated"] = datetime.now().isoformat()
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get the history of the active chat"""
        active_chat = self.get_active_chat()
        return active_chat.get("history", [])
    
    def clear_chat_history(self):
        """Clear the history of the active chat"""
        active_chat_id = st.session_state.active_chat_id
        st.session_state.all_chats[active_chat_id]["history"] = []
        st.session_state.all_chats[active_chat_id]["last_updated"] = datetime.now().isoformat()
    
    def delete_chat(self, chat_id: str):
        """Delete a chat session"""
        if chat_id in st.session_state.all_chats:
            del st.session_state.all_chats[chat_id]
            
            # If we deleted the active chat, create a new one
            if chat_id == st.session_state.active_chat_id:
                self.create_new_chat()
    
    def add_indexed_item(self, item_name: str):
        """Add an item to the knowledge base for the active chat"""
        active_chat_id = st.session_state.active_chat_id
        st.session_state.all_chats[active_chat_id]["indexed_items"].add(item_name)
    
    def get_indexed_items(self) -> set:
        """Get indexed items for the active chat"""
        active_chat = self.get_active_chat()
        return active_chat.get("indexed_items", set())
    
    def export_chat_history(self, format: str = "json") -> str:
        """Export chat history in specified format"""
        active_chat = self.get_active_chat()
        
        if format == "json":
            import json
            return json.dumps(active_chat, indent=2, default=str)
        elif format == "markdown":
            history = active_chat.get("history", [])
            markdown = f"# {active_chat.get('title', 'Chat Export')}\n\n"
            
            for msg in history:
                role = "**User**" if msg["role"] == "user" else "**Assistant**"
                timestamp = msg.get("timestamp", "")
                content = msg.get("content", "")
                markdown += f"{role} ({timestamp}):\n{content}\n\n---\n\n"
            
            return markdown
        
        return str(active_chat)