import ollama
from langchain.agents import tool
from langchain_community.tools import DuckDuckGoSearchRun
from twilio.rest import Client
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from backend.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
    EMERGENCY_CONTACT,
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

