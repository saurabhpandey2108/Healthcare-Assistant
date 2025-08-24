"""
Configuration and Constants for SAFESPACE AI AGENT Streamlit Interface

This module provides configuration settings and constants for the Streamlit application.
"""

import os
from pathlib import Path

# Backend Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_TIMEOUT = 30

# File Upload Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Image Configuration
IMAGE_UPLOAD_DIR = UPLOAD_DIR / "images"
IMAGE_UPLOAD_DIR.mkdir(exist_ok=True)
SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg", "gif", "bmp", "webp"]
MAX_IMAGE_SIZE_MB = 10

# Audio Configuration  
AUDIO_UPLOAD_DIR = UPLOAD_DIR / "audio"
AUDIO_UPLOAD_DIR.mkdir(exist_ok=True)
SUPPORTED_AUDIO_FORMATS = ["wav", "mp3", "m4a", "ogg", "flac"]
MAX_AUDIO_SIZE_MB = 50
MAX_RECORDING_DURATION = 300  # 5 minutes

# Document Configuration
DOCS_UPLOAD_DIR = UPLOAD_DIR / "documents"
DOCS_UPLOAD_DIR.mkdir(exist_ok=True)
SUPPORTED_DOC_FORMATS = ["pdf", "txt", "docx", "md"]
MAX_DOC_SIZE_MB = 100

# Chat Configuration
MAX_CHAT_HISTORY = 100
DEFAULT_SESSION_TYPE = "general"

# UI Configuration
CHAT_CONTAINER_HEIGHT = 400
SIDEBAR_WIDTH = 300

# API Endpoints
ENDPOINTS = {
    "ask": f"{BACKEND_URL}/ask",
    "upload_image": f"{BACKEND_URL}/upload-image",
    "upload_audio": f"{BACKEND_URL}/upload-audio", 
    "analyze_image": f"{BACKEND_URL}/analyze-image",
    "process_audio": f"{BACKEND_URL}/process-audio",
    "generate_voice": f"{BACKEND_URL}/generate-voice",
    "multimodal_query": f"{BACKEND_URL}/multimodal-query",
    "upload_document": f"{BACKEND_URL}/upload",
    "session_history": f"{BACKEND_URL}/session",
    "system_status": f"{BACKEND_URL}/system/status"
}

# Session Types
SESSION_TYPES = {
    "general": "💬 General Chat",
    "therapy": "🧠 Therapy Session", 
    "emergency": "🚨 Emergency Support",
    "analysis": "📊 Analysis Session"
}

# Emergency Keywords
EMERGENCY_KEYWORDS = [
    "suicide", "kill myself", "end it all", "want to die",
    "harm myself", "hurt myself", "emergency", "crisis",
    "help me", "can't go on", "no point", "hopeless"
]

# Mental Health Resources
EMERGENCY_CONTACTS = {
    "US": {
        "name": "National Suicide Prevention Lifeline",
        "number": "988",
        "text": "Text HOME to 741741"
    },
    "UK": {
        "name": "Samaritans",
        "number": "116 123",
        "text": "Text SHOUT to 85258"
    },
    "International": {
        "name": "Crisis Text Line",
        "number": "Various by country",
        "text": "Visit findahelpline.com"
    }
}

# Therapeutic Tools
THERAPEUTIC_TOOLS = [
    {
        "name": "Breathing Exercise",
        "icon": "🫁",
        "description": "Guided breathing to reduce anxiety",
        "tool": "suggest_breathing_exercise"
    },
    {
        "name": "Daily Affirmation", 
        "icon": "✨",
        "description": "Positive affirmations for mental wellness",
        "tool": "get_daily_affirmation"
    },
    {
        "name": "Find Therapists",
        "icon": "👨‍⚕️", 
        "description": "Locate mental health professionals nearby",
        "tool": "find_nearby_therapists_by_location"
    },
    {
        "name": "Health Articles",
        "icon": "📚",
        "description": "Research-based mental health information", 
        "tool": "find_mental_health_articles"
    },
    {
        "name": "Web Search",
        "icon": "🌐",
        "description": "Search for current health information",
        "tool": "ask_web_for_health_info"
    }
]

# Voice Synthesis Options
VOICE_OPTIONS = {
    "gTTS": {
        "name": "Google Text-to-Speech",
        "description": "Free, basic voice synthesis",
        "premium": False
    },
    "ElevenLabs": {
        "name": "ElevenLabs AI Voice",
        "description": "Premium, natural-sounding voices",
        "premium": True,
        "voices": {
            "pNInz6obpgDQGcFmaJgB": "Adam (Male, Deep)",
            "EXAVITQu4vr4xnSDxMaL": "Bella (Female, Soft)",
            "VR6AewLTigWG4xSOukaG": "Arnold (Male, Strong)",
            "MF3mGyEYCl7XYWbV9V6O": "Elli (Female, Young)",
            "TxGEqnHWrfWFTfGW9XjX": "Josh (Male, Natural)"
        }
    }
}

# Image Analysis Types
IMAGE_ANALYSIS_TYPES = [
    {
        "type": "general",
        "name": "General Analysis", 
        "description": "Overall emotional and visual analysis"
    },
    {
        "type": "emotional",
        "name": "Emotional Analysis",
        "description": "Focus on emotional expression and mood"
    },
    {
        "type": "therapeutic", 
        "name": "Therapeutic Insights",
        "description": "Art therapy and psychological insights"
    },
    {
        "type": "artistic",
        "name": "Artistic Elements",
        "description": "Color, composition, and artistic techniques"
    }
]

# System Status Messages
STATUS_MESSAGES = {
    "online": "🟢 System Online",
    "offline": "🔴 System Offline", 
    "warning": "🟡 Limited Functionality",
    "maintenance": "🔧 Under Maintenance"
}

# Help Documentation
HELP_SECTIONS = {
    "getting_started": {
        "title": "Getting Started",
        "content": """
        Welcome to SAFESPACE AI AGENT! Here's how to get started:
        
        1. **Start a Conversation**: Type your message in the chat box
        2. **Upload Content**: Use the knowledge base panel to add documents
        3. **Multimodal Input**: Upload images or audio for analysis
        4. **Emergency Support**: Access crisis resources when needed
        """
    },
    "features": {
        "title": "Features Overview", 
        "content": """
        **Chat Features:**
        - Multi-session management
        - Emergency detection and support
        - Therapeutic tool integration
        
        **Multimodal Capabilities:**
        - Image analysis for emotional insights
        - Audio transcription and voice interaction
        - Document upload and knowledge base integration
        
        **Mental Health Tools:**
        - Breathing exercises and affirmations
        - Therapist finder and resource location
        - Crisis intervention and emergency contacts
        """
    },
    "privacy": {
        "title": "Privacy & Security",
        "content": """
        Your privacy and security are our top priorities:
        
        - All conversations are encrypted
        - No personal data is stored permanently
        - Emergency features only activate with explicit indicators
        - You can clear your chat history at any time
        
        This system complements but does not replace professional mental health care.
        """
    }
}

# Error Messages
ERROR_MESSAGES = {
    "backend_offline": "❌ Backend service is not available. Please check if the API server is running.",
    "upload_failed": "❌ File upload failed. Please try again with a smaller file.",
    "invalid_format": "❌ Unsupported file format. Please check the allowed formats.",
    "size_exceeded": "❌ File size exceeds the maximum limit.",
    "processing_error": "❌ Error processing your request. Please try again.",
    "timeout_error": "❌ Request timed out. The server may be busy.",
    "auth_error": "❌ Authentication failed. Please check your API keys."
}