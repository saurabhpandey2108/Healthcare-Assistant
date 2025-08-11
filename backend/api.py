from fastapi import APIRouter
from core.agent import graph, SYSTEM_PROMPT, parse_response
from core.rag_manager import rag_manager
from backend.models import Query, FileUpload
from langchain_core.messages import HumanMessage, SystemMessage

router = APIRouter()

chat_history = {}

@router.post("/ask")
async def ask(query: Query):
    session_id = query.session_id
    if session_id not in chat_history:
        chat_history[session_id]=[SystemMessage(content=SYSTEM_PROMPT)]
    chat_history[session_id].append(HumanMessage(content=query.message))

    inputs= {"messages": chat_history[session_id]}
    stream = graph.astream(inputs, stream_mode="updates")
    tool_called_name, final_response = await parse_response(stream)

    chat_history[session_id].append(HumanMessage(content=final_response))

    return {"response": final_response, "tool_called": tool_called_name}

@router.post("/upload")
async def upload_file(file: FileUpload):
    rag_manager.add_document(file.file_path)
    return {"message": "File added to the knowledge base."}