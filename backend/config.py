# in backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")

# Supported file formats (extensions with dots for backend validation)
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"]

# Supported formats for frontend file uploaders (no dots)
FRONTEND_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
FRONTEND_AUDIO_FORMATS = ["mp3", "wav", "m4a", "aac", "ogg", "flac"]

# Model configurations
OPENAI_MODEL = "gpt-4o"
GROQ_MODEL = "llama-3.2-90b-vision-preview"
WHISPER_MODEL = "whisper-1"

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
RECORD_SECONDS = 30

# Audio settings for backwards compatibility
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 1024
AUDIO_FORMAT = "int16"

# Vector database settings
VECTOR_DB_PATH = "./data/vector_db"
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_TOKENS = 150000