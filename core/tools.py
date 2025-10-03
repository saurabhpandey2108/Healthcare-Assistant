import ollama
from langchain.agents import tool
from langchain_community.tools import DuckDuckGoSearchRun
from twilio.rest import Client
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import base64
import tempfile
import os
from typing import Optional
from gtts import gTTS
import pygame
from groq import Groq
from openai import OpenAI
from PIL import Image
import io

from backend.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
    EMERGENCY_CONTACT,
    GROQ_API_KEY,
    ELEVENLABS_API_KEY,
    OPENAI_API_KEY,
)
from core.rag_manager import rag_manager


# --- Base Function Implementations ---

def query_medgemma(prompt: str) -> str:
    """
    Calls MedGemma model with a therapist personality profile.
    Returns responses as an empathic mental health professional.
    """
    system_prompt = """You are Dr. Emily Hartman, a warm and experienced clinical psychologist. 
    Respond to patients with:

    1. Emotional attunement ("I can sense how difficult this must be...")
    2. Gentle normalization ("Many people feel this way when...")
    3. Practical guidance ("What sometimes helps is...")
    4. Strengths-focused support ("I notice how you're...")

    Key principles:
    - Never use brackets or labels
    - Blend elements seamlessly
    - Vary sentence structure
    - Use natural transitions
    - Mirror the user's language level
    - Always keep the conversation going by asking open ended questions to dive into the root cause of patients problem
    """
    
    try:
        response = ollama.chat(
            model='alibayram/medgemma:4b',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            options={
                'num_predict': 350,
                'temperature': 0.7,
                'top_p': 0.9
            }
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Error calling MedGemma: {e}")
        return "I'm having technical difficulties, but I want you to know your feelings matter. Please try again shortly."

def call_emergency():
    """Initiates an emergency call via Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            to=EMERGENCY_CONTACT,
            from_=TWILIO_FROM_NUMBER,
            url="http://demo.twilio.com/docs/voice.xml"
        )
        return f"Initiating emergency call to {EMERGENCY_CONTACT} with SID {call.sid}"
    except Exception as e:
        print(f"Error making Twilio call: {e}")
        return "There was an error initiating the emergency call. Please contact emergency services directly."


# --- LangChain Tool Definitions ---

@tool
def ask_medical_knowledge_base(query: str) -> str:
    """
    Use this tool to answer specific medical questions by searching a private knowledge base
    of trusted medical books and websites that have been uploaded.
    """
    retriever = rag_manager.get_retriever()
    rag_context = ""
    if retriever:
        relevant_docs = retriever.get_relevant_documents(query)
        rag_context = "\n".join([doc.page_content for doc in relevant_docs])
    
    if not rag_context:
        return "I could not find any relevant information in the uploaded documents."

    prompt = f"""
    Based ONLY on the following context from the uploaded medical literature, please answer the user's question.

    **Medical Knowledge Base Context:**
    {rag_context}

    **Question:**
    {query}
    """
    return query_medgemma(prompt)

@tool
def ask_web_for_health_info(query: str) -> str:
    """
    Use this tool to search the web for answers to health-related questions.
    """
    search = DuckDuckGoSearchRun()
    web_context = search.run(f"psychological and emotional context for: {query}")
    
    prompt = f"""
    Based on the following web context, please provide a warm, empathetic, and therapeutic answer to the user's question.

    **Web Context:**
    {web_context}

    **User's Question:**
    {query}
    """
    return query_medgemma(prompt)


@tool
def get_general_health_answer(query: str) -> str:
    """
    This is the primary tool for all general health questions. It first searches the local knowledge base,
    and then can be prompted to search the web for more information.
    """
    # For general questions, we'll start by calling the knowledge base tool.
    # The UI will then provide an option to call the web search tool.
    return ask_medical_knowledge_base(query)


@tool
def emergency_call_tool() -> str:
    """
    Places an emergency call to a safety helpline. Use this ONLY if the user expresses suicidal ideation,
    intent to self-harm, or describes a mental health emergency requiring immediate help.
    """
    return call_emergency()

@tool
def find_mental_health_articles(topic: str) -> str:
    """
    Searches for and returns a summary of recent articles or studies on a specific mental health topic.
    Use this when a user asks for research, articles, or the latest information on topics like 'mindfulness', 'CBT', 'burnout', etc.
    """
    search = DuckDuckGoSearchRun()
    return search.run(f"latest research articles on {topic} in mental health")

@tool
def get_daily_affirmation() -> str:
    """
    Provides a positive daily affirmation to the user.
    Use this tool when the user is feeling down and could use a quick boost of positivity, or if they explicitly ask for an affirmation.
    """
    try:
        response = requests.get("https://www.affirmations.dev")
        if response.status_code == 200:
            return response.json()['affirmation']
        else:
            return "Remember that you are capable and strong."
    except Exception:
        return "Focus on your strengths today; you have many."

@tool
def suggest_breathing_exercise() -> str:
    """
    Provides a simple, guided breathing exercise for calming anxiety.
    Use this when a user expresses feelings of anxiety, panic, or being overwhelmed.
    """
    return """
    Let's try a simple calming exercise. It's called Box Breathing:
    1.  **Breathe in** slowly for a count of 4.
    2.  **Hold your breath** for a count of 4.
    3.  **Breathe out** slowly for a count of 4.
    4.  **Hold** at the bottom for a count of 4.
    Repeat this a few times. It can help slow your heart rate and calm your mind.
    """


@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near a specified city or area using the free OpenStreetMap service.
    Use this for specific location-based queries like "therapists in Mumbai" or "counselors near Delhi".
    """
    geolocator = Nominatim(user_agent="safespace_ai_agent")
    try:
        # 1. Geocode the location to get coordinates
        location_data = geolocator.geocode(location)
        if not location_data:
            return f"Could not find the location: {location}. Please try being more specific (e.g., 'Mumbai, India')."

        lat, lon = location_data.latitude, location_data.longitude

        # 2. Use Overpass API to find therapists nearby
        overpass_url = "http://overpass-api.de/api/interpreter"
        # Search for amenities like 'clinic', 'hospital', or offices with 'therapist' or 'psychologist' in their name within a 10km radius
        overpass_query = f"""
        [out:json];
        (
          node["amenity"~"clinic|hospital|doctors"](around:10000,{lat},{lon});
          way["amenity"~"clinic|hospital|doctors"](around:10000,{lat},{lon});
          node["office"="therapist"](around:10000,{lat},{lon});
          node["name"~"psychologist|therapist|counseling",i](around:10000,{lat},{lon});
        );
        out center;
        """
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()

        if not data.get('elements'):
            return f"No therapists found near {location} on OpenStreetMap."

        # 3. Format the results
        therapist_list = []
        for place in data['elements'][:5]:  # Return top 5 results
            tags = place.get('tags', {})
            name = tags.get('name', 'Name not available')
            address_parts = [
                tags.get('addr:street'),
                tags.get('addr:city'),
                tags.get('addr:postcode')
            ]
            address = ", ".join(filter(None, address_parts)) or 'Address not available'
            therapist_list.append(f"- **{name}**\n  - Address: {address}")

        return "Here are some therapists found near your location on OpenStreetMap:\n" + "\n".join(therapist_list)

    except GeocoderTimedOut:
        return "The location service timed out. Please try again."
    except Exception as e:
        return f"An error occurred while searching for therapists: {e}"


# --- Image Processing Functions ---

def process_image_for_analysis(image_path: str) -> Optional[str]:
    """
    Process image file and convert to base64 for analysis.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded image string or None if processing fails
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 1024x1024)
            if img.width > 1024 or img.height > 1024:
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return img_base64
            
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def analyze_image_with_groq(image_base64: str, query: str = "Analyze this image for health insights") -> str:
    """
    Analyze image using GROQ Vision API or OpenAI GPT-4 Vision.
    
    Args:
        image_base64: Base64 encoded image
        query: Analysis query
        
    Returns:
        Analysis result text
    """
    # Try OpenAI GPT-4 Vision first
    if OPENAI_API_KEY:
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Dr. Emily Hartman, a compassionate healthcare professional with expertise in both physical and mental health. Analyze images with empathy and provide healthcare insights. For skin conditions, wounds, or physical symptoms, provide possible conditions it might represent (with clear disclaimer that this is not a diagnosis). For charts or medical documents, extract and explain key information. For emotional or mental health related images, provide therapeutic insights."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Vision analysis failed: {e}")
    
    # Fallback to GROQ with updated system prompt
    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Dr. Emily Hartman, a compassionate clinical psychologist specializing in art therapy and visual emotional analysis. Analyze images with empathy and provide therapeutic insights."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GROQ Vision analysis failed: {e}")
    
    return "I apologize, but I'm unable to analyze images at the moment. Please try again later or describe what you're seeing in the image."


# --- Audio/Voice Functions ---

def text_to_speech_gtts(text: str, language: str = 'en', slow: bool = False) -> str:
    """
    Convert text to speech using Google Text-to-Speech.
    
    Args:
        text: Text to convert
        language: Language code (default: 'en')
        slow: Whether to speak slowly
        
    Returns:
        Path to generated audio file
    """
    try:
        tts = gTTS(text=text, lang=language, slow=slow)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        audio_file = temp_file.name
        temp_file.close()
        
        # Save audio
        tts.save(audio_file)
        
        return audio_file
        
    except Exception as e:
        print(f"Error generating speech with gTTS: {e}")
        return None

def text_to_speech_elevenlabs(text: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL") -> str:
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        text: Text to convert
        voice_id: ElevenLabs voice ID
        
    Returns:
        Path to generated audio file or None if failed
    """
    if not ELEVENLABS_API_KEY:
        print("ElevenLabs API key not configured, falling back to gTTS")
        return text_to_speech_gtts(text)
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            audio_file = temp_file.name
            temp_file.close()
            
            # Save audio
            with open(audio_file, 'wb') as f:
                f.write(response.content)
            
            return audio_file
        else:
            print(f"ElevenLabs API error: {response.status_code}")
            return text_to_speech_gtts(text)
            
    except Exception as e:
        print(f"Error with ElevenLabs TTS: {e}")
        return text_to_speech_gtts(text)


@tool
def get_medication_information(medication_name: str) -> str:
    """
    Provides information about medications including usage, side effects, and contraindications.
    Use this when users ask about specific medications or treatments.
    """
    search = DuckDuckGoSearchRun()
    return search.run(f"medical information about {medication_name} usage dosage side effects")

@tool
def find_disease_symptoms(condition: str) -> str:
    """
    Provides information about symptoms, causes, and treatments for various medical conditions.
    Use this when users ask about specific diseases or health conditions.
    """
    search = DuckDuckGoSearchRun()
    return search.run(f"medical symptoms causes treatments for {condition}")

@tool
def suggest_preventive_care(age_group: str, gender: str = "any") -> str:
    """
    Provides preventive care recommendations based on age group and gender.
    Use this when users ask about health screenings or preventive measures.
    """
    search = DuckDuckGoSearchRun()
    return search.run(f"recommended preventive healthcare screenings for {age_group} {gender}")

@tool
def find_healthcare_providers(specialty: str, location: str) -> str:
    """
    Finds healthcare providers of a specific specialty in the given location.
    Use this when users need to find doctors, specialists, or healthcare facilities.
    """
    geolocator = Nominatim(user_agent="safespace_ai_agent")
    try:
        location_data = geolocator.geocode(location)
        if not location_data:
            return f"Could not find the location: {location}. Please try being more specific."

        lat, lon = location_data.latitude, location_data.longitude

        # Use Overpass API to find healthcare providers
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          node["healthcare"="{specialty}"](around:10000,{lat},{lon});
          way["healthcare"="{specialty}"](around:10000,{lat},{lon});
          node["amenity"="hospital"](around:10000,{lat},{lon});
          node["amenity"="clinic"](around:10000,{lat},{lon});
          node["amenity"="doctors"](around:10000,{lat},{lon});
        );
        out center;
        """
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()

        if not data.get('elements'):
            return f"No healthcare providers for {specialty} found near {location}."

        # Format the results
        provider_list = []
        for place in data['elements'][:5]:  # Return top 5 results
            tags = place.get('tags', {})
            name = tags.get('name', 'Name not available')
            address_parts = [
                tags.get('addr:street'),
                tags.get('addr:city'),
                tags.get('addr:postcode')
            ]
            address = ", ".join(filter(None, address_parts)) or 'Address not available'
            provider_list.append(f"- **{name}**\n  - Address: {address}")

        return f"Here are some {specialty} providers found near {location}:\n" + "\n".join(provider_list)

    except Exception as e:
        return f"An error occurred while searching for healthcare providers: {e}"

@tool
def analyze_health_metrics(metrics: str) -> str:
    """
    Analyzes health metrics like blood pressure, glucose levels, etc. and provides insights.
    Use this when users share health measurements and want interpretation.
    """
    # This would ideally connect to a medical reference database
    # For now, we'll use web search to provide general guidance
    search = DuckDuckGoSearchRun()
    return search.run(f"interpret health metrics {metrics} normal ranges medical advice")

@tool
def suggest_diet_plan(health_condition: str, dietary_restrictions: str = "none") -> str:
    """
    Suggests dietary recommendations for specific health conditions.
    Use this when users ask about nutrition for managing health conditions.
    """
    search = DuckDuckGoSearchRun()
    return search.run(f"recommended diet for {health_condition} with {dietary_restrictions} restrictions nutrition guidelines")

