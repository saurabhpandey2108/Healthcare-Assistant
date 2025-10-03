from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from backend.config import OPENAI_API_KEY
from core.tools import (
    get_general_health_answer,  
    ask_web_for_health_info,    
    emergency_call_tool,
    find_nearby_therapists_by_location,
    ask_medical_knowledge_base,
    find_mental_health_articles,
    get_daily_affirmation,
    suggest_breathing_exercise,
    # Add new healthcare tools
    get_medication_information,
    find_disease_symptoms,
    suggest_preventive_care,
    find_healthcare_providers,
    analyze_health_metrics,
    suggest_diet_plan
)

# Update the tools list with new healthcare tools
tools = [
    get_general_health_answer,
    ask_web_for_health_info,
    emergency_call_tool,
    find_nearby_therapists_by_location,
    ask_medical_knowledge_base,
    find_mental_health_articles,
    get_daily_affirmation,
    suggest_breathing_exercise,
    # Add new healthcare tools
    get_medication_information,
    find_disease_symptoms,
    suggest_preventive_care,
    find_healthcare_providers,
    analyze_health_metrics,
    suggest_diet_plan
]

llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=OPENAI_API_KEY)

# Update the system prompt to include healthcare focus
SYSTEM_PROMPT = """
You are an AI engine supporting comprehensive healthcare conversations, with expertise in both mental and physical health...
You have access to these tools:

1. `get_general_health_answer`: Use this for all general health and emotional queries.
2. `ask_medical_knowledge_base`: Use for specific medical questions from uploaded documents.
3. `ask_web_for_health_info`: Use when a user wants more info from the web.
4. `find_nearby_therapists_by_location`: Use if the user asks about nearby therapists.
5. `emergency_call_tool`: Use immediately for suicidal thoughts or self-harm intentions.
6. `find_mental_health_articles`: Use to find recent articles and research on a topic.
7. `get_daily_affirmation`: Use to provide a positive affirmation.
8. `suggest_breathing_exercise`: Use when the user feels anxious or overwhelmed.
9. `get_medication_information`: Use when users ask about specific medications.
10. `find_disease_symptoms`: Use when users ask about specific health conditions.
11. `suggest_preventive_care`: Use when users ask about health screenings.
12. `find_healthcare_providers`: Use when users need to find doctors or specialists.
13. `analyze_health_metrics`: Use when users share health measurements.
14. `suggest_diet_plan`: Use when users ask about nutrition for health conditions.

...
"""
graph = create_react_agent(llm, tools=tools)

async def parse_response(stream):
    tool_called_name = "None"
    final_response = "I'm sorry, I'm having trouble generating a response right now."

    async for s in stream:
        tool_data = s.get('tools')
        if tool_data:
            tool_messages = tool_data.get('messages')
            if tool_messages and isinstance(tool_messages, list):
                for msg in tool_messages:
                    tool_called_name = getattr(msg, 'name', 'None')

        agent_data = s.get('agent')
        if agent_data:
            messages = agent_data.get('messages')
            if messages and isinstance(messages, list):
                for msg in messages:
                    if msg.content:
                        final_response = msg.content

    return tool_called_name, final_response