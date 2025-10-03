# Gradio Healthcare Interface

## Overview

The Gradio interface provides a comprehensive web-based healthcare assistant with the following features:

## Healthcare Capabilities

### 🩺 Comprehensive Health Domains
- **Mental Health**: Therapy, crisis intervention, emotional support
- **General Health**: Symptom analysis, health advice, wellness tips  
- **Nutrition**: Dietary guidance, meal planning, food analysis
- **Fitness**: Exercise plans, physical wellness, activity tracking
- **Medical Consultation**: Information lookup, treatment guidance, medication info

### 🖥️ Interface Features

#### 💬 Text Chat
- Real-time conversation with AI healthcare assistant
- Emergency detection and crisis intervention
- Quick healthcare tools:
  - Daily affirmations
  - Breathing exercises  
  - Health check consultations
  - Symptom analysis
  - Nutrition advice
  - Fitness planning
  - Sleep guidance

#### 🖼️ Healthcare Image Analysis
- **Analysis Types**:
  - General Health Assessment
  - Mental Health & Emotional Analysis
  - Nutritional Analysis (Food/Meals)
  - Fitness & Exercise Analysis
  - Medical Image Review
  - Symptom Visual Assessment
  - Wellness Environment Analysis

#### 🎤 Voice Healthcare Consultation
- Audio upload for healthcare queries
- Speech-to-text transcription
- Voice response generation
- Premium voice synthesis with ElevenLabs

#### 🏥 Healthcare Tools
- Find nearby healthcare providers
- Mental health resources
- Nutrition consultation
- Fitness assessment
- Medical information lookup
- Emergency contacts
- Health article search
- Medication information

## Running the Interface

### Prerequisites
1. Copy `.env.template` to `.env` and add your API keys
2. Ensure the virtual environment is activated
3. Install all dependencies from `pyproject.toml`

### Launch Commands

```bash
# From project root
python views/gradio_ui.py

# Or using the main launcher
python main.py  # Select option 3 for Gradio
```

### Access
- **Local URL**: http://localhost:7860
- **Debug Mode**: Enabled by default
- **Public Sharing**: Disabled by default (set share=True to enable)

## Configuration

### API Keys Required
- **OpenAI**: Primary AI service (required)
- **GROQ**: Fallback AI service (recommended)
- **ElevenLabs**: Premium voice synthesis (optional)

### Healthcare Focus Areas
The interface supports these healthcare domains:
- Mental health counseling and crisis intervention
- General health advice and symptom analysis
- Nutritional guidance and meal planning
- Fitness planning and physical wellness
- Medical information and treatment guidance

## Features

### 🔒 Privacy & Security
- Local processing when possible
- Secure API communications
- Session-based conversation management
- No permanent data storage

### 🎯 AI Service Priority
1. **Image Analysis**: OpenAI GPT-4 Vision → GROQ Llama Vision
2. **Speech Transcription**: OpenAI Whisper → GROQ Whisper → Google Speech
3. **Voice Synthesis**: ElevenLabs → Google TTS
4. **Text Generation**: OpenAI GPT-4o

### 📱 User Experience
- Responsive design for all devices
- Real-time processing indicators
- Error handling with helpful messages
- Copy-to-clipboard functionality
- File upload with progress tracking

## Important Notes

⚠️ **Medical Disclaimer**: This tool provides supportive health information but is not a replacement for professional medical care. Always consult healthcare professionals for serious medical concerns.

🚨 **Emergency Features**: The system includes crisis detection and can provide emergency contact information when mental health emergencies are detected.

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure you're running from the project root
2. **API Errors**: Check your `.env` file has valid API keys
3. **Port Conflicts**: Default port 7860, change if needed
4. **Module Not Found**: Activate virtual environment first

### Getting Help
- Check the main README.md for detailed setup instructions
- Verify all dependencies are installed
- Ensure API keys are properly configured
- Check terminal output for specific error messages