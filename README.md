# 🌟 SAFESPACE AI AGENT - Multimodal Health Assistant

## 📋 Overview

SAFESPACE AI AGENT is a comprehensive multimodal health assistant built with proper **MVC (Model-View-Controller) architecture**. The system provides empathetic mental health support through **text**, **images**, and **voice** interactions, with **OpenAI as the primary AI provider** and GROQ as fallback.

The system features two modern web interfaces:
- **Gradio Interface**: Advanced multimodal web interface with real-time processing
- **Enhanced Streamlit Interface**: Professional UI with comprehensive features and file management

## 🏗️ **MVC Architecture**

### **Model Layer** (`models/`)
- **`api_models.py`**: Pydantic models for API requests/responses
- **`business_models.py`**: Business logic models, data structures, and session management

### **View Layer** (`views/` & `frontend/`)
- **`gradio_ui.py`**: Modern Gradio-based multimodal web interface
- **`streamlit_app.py`**: Enhanced Streamlit interface with advanced features
- **`app.py`**: Original Streamlit interface (maintained for compatibility)

### **Controller Layer** (`controllers/`)
- **`mental_health_controller.py`**: Core business logic controller orchestrating all interactions

### **Core Services** (`core/`)
- **`agent.py`**: LangGraph-based AI agent (using OpenAI GPT-4o)
- **`tools.py`**: AI tools for various mental health functions
- **`audio_processor.py`**: Comprehensive audio processing service
- **`rag_manager.py`**: Document retrieval and knowledge management

### **Backend API** (`backend/`)
- **`api.py`**: FastAPI REST endpoints following MVC patterns
- **`main.py`**: FastAPI server configuration
- **`config.py`**: Centralized configuration management

## 🚀 **Key Features**

### **🎯 AI Service Priority**
1. **Image Analysis**: OpenAI GPT-4 Vision → GROQ Llama Vision
2. **Speech Transcription**: OpenAI Whisper → GROQ Whisper → Google Speech Recognition
3. **Text Generation**: OpenAI GPT-4o (primary)
4. **Voice Synthesis**: ElevenLabs → Google TTS

### **📱 Multimodal Capabilities**
- **Text Conversations**: Full therapeutic chat with emergency detection
- **Image Analysis**: Art therapy, emotional assessment, visual therapeutic insights  
- **Voice Interactions**: Speech-to-text, voice responses, hands-free conversations
- **Emergency Protocols**: Multi-modal crisis detection and intervention

### **🔒 Robust Architecture**
- **Separation of Concerns**: Clear MVC boundaries
- **Error Handling**: Comprehensive fallback systems
- **Session Management**: Multi-user session support
- **API Documentation**: Interactive OpenAPI docs
- **Type Safety**: Full Pydantic validation

## 📸 Screenshots

### Main Dashboard
![Main Dashboard]("C:\Users\saura\Pictures\Screenshots\Screenshot 2025-09-03 021046.png")

### Voice Interface
![Voice Interface]("C:\Users\saura\Pictures\Screenshots\Screenshot 2025-09-03 021046.png")


## 📁 **Project Structure**

```
SAFESPACE AI AGENT/
├── models/                     # 📊 MODEL LAYER
│   ├── __init__.py
│   ├── api_models.py          # API request/response models
│   └── business_models.py     # Business logic models
├── controllers/               # 🎮 CONTROLLER LAYER  
│   ├── __init__.py
│   └── mental_health_controller.py  # Main business logic
├── views/                     # 👁️ VIEW LAYER
│   ├── __init__.py
│   └── gradio_ui.py          # Modern multimodal interface
├── core/                      # 🔧 CORE SERVICES
│   ├── agent.py              # OpenAI GPT-4o based agent
│   ├── tools.py              # Mental health AI tools
│   ├── audio_processor.py    # Audio processing service  
│   └── rag_manager.py        # Knowledge management
├── backend/                   # 🌐 API LAYER
│   ├── api.py                # REST endpoints
│   ├── main.py               # FastAPI server
│   ├── config.py             # Configuration
│   └── models.py             # Legacy models (deprecated)
├── frontend/                  # 📱 UI COMPONENTS
│   ├── components/           # Streamlit UI components
│   ├── utils/                # UI utilities and styling
│   ├── app.py                # Original Streamlit interface
│   └── streamlit_app.py      # Enhanced Streamlit interface
├── main.py                   # 🚀 UNIFIED LAUNCHER
├── demo_multimodal.py        # 🎯 COMPREHENSIVE DEMO
├── requirements.txt          # 📦 DEPENDENCIES
├── .env.template             # ⚙️ CONFIGURATION TEMPLATE
└── README.md                 # 📖 THIS FILE
```

## 🛠️ **Installation & Setup**

### **1. Prerequisites**
```bash
# Ensure Python 3.10+ is installed
python --version  # Should be 3.10+
```

### **2. Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# For Windows users having PyAudio issues:
pip install pipwin
pipwin install pyaudio
```

### **3. Configure API Keys**
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your API keys:
# Required:
OPENAI_API_KEY=your_openai_api_key_here

# Optional but recommended:
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# For emergency features:
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_NUMBER=your_twilio_number
EMERGENCY_CONTACT=emergency_phone_number
```

### **4. Launch the Application**
```bash
# Launch everything (recommended)
python main.py all

# Or launch specific components:
python main.py gradio    # Modern multimodal web interface
python main.py api       # Backend API server  
python main.py demo      # Comprehensive demo
python main.py streamlit # Enhanced Streamlit interface
python main.py help      # Show all options
```

## 📱 **Web Interface Options**

### **Gradio Interface (Modern Multimodal)**
- **URL**: http://localhost:7860
- **Features**: Real-time processing, tabs for different modalities
- **Best For**: Quick multimodal interactions, voice recording
- **Launch**: `python main.py gradio`

### **Enhanced Streamlit Interface (Professional)**
- **URL**: http://localhost:8501
- **Features**: Advanced UI, session management, file uploads
- **Best For**: Comprehensive conversations, document management
- **Launch**: `python main.py streamlit`

## 🎯 **Usage Examples**

### **Gradio Interface Usage**
1. **Launch**: `python main.py gradio`
2. **Open**: http://localhost:7860
3. **Use tabs**: Switch between Text, Image, Audio, and Voice modes
4. **Real-time processing**: Immediate multimodal interactions

### **Enhanced Streamlit Interface Usage**
1. **Launch**: `python main.py streamlit`
2. **Open**: http://localhost:8501
3. **Professional features**: Session management, file uploads, advanced UI

### **API Integration**
```python
import requests

# Text conversation
response = requests.post("http://localhost:8000/ask", json={
    "message": "I'm feeling anxious about work",
    "session_id": "user123"
})

# Image analysis
response = requests.post("http://localhost:8000/analyze-image", json={
    "image_path": "/path/to/image.jpg",
    "query": "Analyze the emotional content",
    "session_id": "user123"
})

# Voice processing
response = requests.post("http://localhost:8000/process-audio", json={
    "audio_path": "/path/to/audio.wav", 
    "session_id": "user123"
})
```

### **Direct Controller Usage**
```python
from controllers.mental_health_controller import mental_health_controller
from models.api_models import Query

# Process text interaction
query = Query(message="I need help with anxiety", session_id="test")
response = await mental_health_controller.process_text_interaction(query)
print(response.content)
```

## 🔧 **API Endpoints**

### **Core Endpoints**
- `POST /ask` - Text-based conversation
- `POST /analyze-image` - Image analysis for therapy
- `POST /process-audio` - Voice message processing
- `POST /generate-voice` - Text-to-speech generation
- `POST /multimodal-query` - Combined multimodal processing

### **Session Management**  
- `GET /session/{session_id}/history` - Get conversation history
- `DELETE /session/{session_id}` - Clear session data
- `GET /system/status` - System health and configuration

### **File Upload**
- `POST /upload-image` - Upload image files
- `POST /upload-audio` - Upload audio files
- `GET /download-audio/{filename}` - Download generated audio

**📚 Interactive API Docs**: http://localhost:8000/docs

## 🎭 **Mental Health Tools Available**

### **Core Therapeutic Tools**
- `get_general_health_answer`: Primary mental health conversation
- `ask_medical_knowledge_base`: Knowledge base queries
- `emergency_call_tool`: Crisis intervention
- `suggest_breathing_exercise`: Anxiety management
- `get_daily_affirmation`: Positive reinforcement

### **Multimodal Tools**  
- `analyze_uploaded_image`: Visual therapy analysis
- `emotional_image_analysis`: Deep emotional assessment
- `process_voice_message`: Voice interaction processing
- `generate_voice_response`: Therapeutic voice responses

### **Support Tools**
- `find_nearby_therapists_by_location`: Local resource finding
- `find_mental_health_articles`: Research and information
- `ask_web_for_health_info`: Real-time web search

## 🚨 **Emergency Features**

### **Multi-Modal Crisis Detection**
- **Text Analysis**: Keyword detection for suicidal ideation
- **Voice Analysis**: Emotional tone assessment
- **Risk Scoring**: 1-5 scale risk assessment
- **Automatic Escalation**: Emergency contact integration

### **Emergency Protocols**
1. **Immediate Response**: Crisis intervention messaging
2. **Resource Provision**: Emergency hotlines and contacts
3. **Professional Referral**: Human intervention recommendations
4. **Call Integration**: Twilio-based emergency calling

## 🧪 **Testing & Validation**

### **Run Comprehensive Demo**
```bash
python main.py demo
```
This will test:
- Text conversation capabilities
- Image analysis simulation  
- Voice processing features
- API endpoint functionality
- Configuration validation

### **Manual Testing**
1. **Web Interface**: Test all tabs in Gradio UI or Streamlit components
2. **API Testing**: Use interactive docs at `/docs`
3. **Voice Testing**: Upload audio files and test transcription
4. **Image Testing**: Upload images for analysis

## 🔒 **Privacy & Security**

- **Local Processing**: Conversations stored locally during session
- **API Security**: Secure connections to AI services  
- **Emergency Protocols**: Crisis detection with professional resources
- **Privacy Maintained**: No permanent storage unless exported

## 🛠️ **Troubleshooting**

### **Common Issues**
```bash
# Backend connection errors
python main.py api  # Check if backend running
python main.py demo # Verify configuration

# Audio/voice issues
# Ensure API keys configured and dependencies installed
```

### **Getting Help**
- **System Status**: Check sidebar in Streamlit or demo mode
- **Built-in Help**: Documentation in interface
- **Logs**: Console output for detailed errors

## ⚙️ **Configuration**

### **AI Service Configuration**
```python
# In backend/config.py
OPENAI_API_KEY = "sk-..."        # Primary AI service
GROQ_API_KEY = "gsk_..."         # Fallback AI service  
ELEVENLABS_API_KEY = "..."       # Premium voice synthesis
```

### **Audio Settings**
```python
AUDIO_SAMPLE_RATE = 16000        # Audio quality
AUDIO_CHUNK_SIZE = 1024          # Processing buffer
AUDIO_FORMAT = "wav"             # Default format
```

### **Image Settings**
```python
MAX_IMAGE_SIZE = (1024, 1024)    # Max dimensions
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "bmp", "gif"]
```

## 🌟 **What's New in MVC Architecture**

### **✨ Major Improvements**
1. **Clean Architecture**: Proper MVC separation of concerns
2. **OpenAI Priority**: Better AI consistency with OpenAI as primary
3. **Enhanced Error Handling**: Comprehensive fallback systems
4. **Type Safety**: Full Pydantic validation throughout
5. **Session Management**: Professional session handling
6. **API Documentation**: Interactive OpenAPI documentation
7. **Scalable Design**: Ready for enterprise deployment

### **🔧 Technical Enhancements**
- **Modular Controllers**: Business logic separation
- **Typed Models**: Pydantic models for all data
- **Service Layer**: Clean service abstraction
- **Async Support**: Full async/await support
- **Error Recovery**: Graceful degradation

## 🎯 **Production Deployment**

### **Environment Setup**
```bash
# Production environment variables
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk-..."
export ELEVENLABS_API_KEY="..."

# Run in production mode
python main.py api  # API server
python main.py gradio  # Web interface
```

---

## 🚀 **Quick Start Summary**

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Copy `.env.template` to `.env` and add your OpenAI API key
3. **Launch**: `python main.py all`
4. **Access**: http://localhost:7860 for Gradio or http://localhost:8501 for Streamlit
5. **Test**: Try the different tabs for multimodal interactions

**🎯 Your SAFESPACE AI AGENT is now running with professional MVC architecture, OpenAI integration, and comprehensive multimodal support!**

*Remember: This system is designed to complement, not replace, professional mental health care.*


