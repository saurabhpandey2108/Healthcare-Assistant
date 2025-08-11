from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from backend.config import OPENAI_API_KEY
from core.tools import (
    get_general_health_answer,  # Corrected import
    ask_web_for_health_info,    # Corrected import
    emergency_call_tool,
    find_nearby_therapists_by_location,
    ask_medical_knowledge_base,
    find_mental_health_articles,
    get_daily_affirmation,
    suggest_breathing_exercise
)

# Use the corrected tool names in the list
tools = [
    get_general_health_answer,
    ask_web_for_health_info,
    emergency_call_tool,
    find_nearby_therapists_by_location,
    ask_medical_knowledge_base,
    find_mental_health_articles, # new
    get_daily_affirmation,       # new
    suggest_breathing_exercise
]

llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=OPENAI_API_KEY)

# Update the system prompt to accurately describe the new primary tool
SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations...
You have access to these tools:

1. `get_general_health_answer`: Use this for all general health and emotional queries.
2. `ask_medical_knowledge_base`: Use for specific medical questions from uploaded documents.
3. `ask_web_for_health_info`: Use when a user wants more info from the web.
4. `find_nearby_therapists_by_location`: Use if the user asks about nearby therapists.
5. `emergency_call_tool`: Use immediately for suicidal thoughts or self-harm intentions.
6. `find_mental_health_articles`: Use to find recent articles and research on a topic.
7. `get_daily_affirmation`: Use to provide a positive affirmation.
8. `suggest_breathing_exercise`: Use when the user feels anxious or overwhelmed.

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