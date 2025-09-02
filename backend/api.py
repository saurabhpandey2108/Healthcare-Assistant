from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from fastapi.responses import FileResponse
from typing import Optional, List
import logging
import asyncio
import tempfile
import os
from datetime import datetime

# Import the proper models
from models.api_models import (
    Query, 
    ImageAnalysisRequest, 
    AudioProcessRequest, 
    VoiceGenerationRequest,
    ChatResponse,
    ImageAnalysisResponse,
    AudioProcessResponse,
    SessionHistoryResponse,
    SystemStatusResponse
)
from models.business_models import (
    TherapeuticResponse,
    ImageAnalysisResult,
    VoiceAnalysisResult
)
from controllers.mental_health_controller import mental_health_controller
from core.rag_manager import rag_manager
from backend.config import OPENAI_API_KEY, GROQ_API_KEY, ELEVENLABS_API_KEY

router = APIRouter()
logger = logging.getLogger("SAFESPACE_API")

# Store for chat history (in production, use Redis or database)
chat_history = {}

@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SAFESPACE AI AGENT API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/ask",
            "/analyze-image", 
            "/process-audio",
            "/generate-voice",
            "/upload",
            "/system/status",
            "/docs"
        ]
    }

@router.get("/system/status")
async def get_system_status():
    """Get system status and health check"""
    logger.info("System status check requested")
    
    try:
        # Check API key configurations
        openai_status = "configured" if OPENAI_API_KEY else "missing"
        groq_status = "configured" if GROQ_API_KEY else "missing"
        elevenlabs_status = "configured" if ELEVENLABS_API_KEY else "missing"
        
        # Check core services
        services_status = {
            "mental_health_controller": "online",
            "rag_manager": "online",
            "openai_api": openai_status,
            "groq_api": groq_status,
            "elevenlabs_api": elevenlabs_status
        }
        
        overall_status = "online" if openai_status == "configured" or groq_status == "configured" else "warning"
        
        status_dict = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": services_status,
            "memory_usage": "N/A",
            "active_sessions": len(chat_history)
        }
        
        logger.info(f"System status: {overall_status}")
        return status_dict
        
    except Exception as e:
        logger.error(f"Error checking system status: {e}")
        raise HTTPException(status_code=500, detail="System status check failed")

@router.post("/ask")
async def ask_question(query: Query):
    """Process text-based questions"""
    logger.info(f"Text query received - Session: {query.session_id}, Message length: {len(query.message)}")
    
    try:
        # Process through mental health controller
        response = await mental_health_controller.process_text_interaction(query)
        
        logger.info(f"Text response generated - Session: {query.session_id}, Tools used: {response.tools_used}")
        
        # Return in the format expected by frontend
        return {
            "response": response.content,
            "tool_called": response.tools_used[0] if response.tools_used else "None",
            "emergency_flag": response.emergency_flag,
            "confidence": response.confidence
        }
        
    except Exception as e:
        logger.error(f"Error processing text query: {e}")
        return {
            "response": "I apologize, but I encountered an error processing your message. Please try again.",
            "tool_called": "error_handler",
            "emergency_flag": False,
            "confidence": 0.0
        }

@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...), query: str = "Analyze this image for mental health insights"):
    """Analyze uploaded image"""
    logger.info(f"Image analysis requested - File: {file.filename}, Query: {query[:50] if query else 'No query'}...")
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file_path = temp_file.name
        
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        temp_file.write(content)
        temp_file.close()
        
        logger.info(f"Temporary file created: {temp_file_path} ({len(content)} bytes)")
        
        # Create analysis request
        request = ImageAnalysisRequest(
            image_path=temp_file_path,
            query=query or "Analyze this image for mental health insights",
            session_id="image_analysis"
        )
        
        # Process through controller
        response, analysis_result = await mental_health_controller.process_image_interaction(request)
        
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except Exception as cleanup_error:
            logger.warning(f"Could not clean up temp file: {cleanup_error}")
        
        logger.info(f"Image analysis completed - Confidence: {analysis_result.confidence_score}")
        
        return {
            "success": True,
            "analysis": response.content,
            "emotional_indicators": analysis_result.emotional_indicators,
            "therapeutic_insights": analysis_result.therapeutic_insights,
            "confidence": analysis_result.confidence_score,
            "tools_used": response.tools_used
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.post("/process-audio")
async def process_audio(file: UploadFile = File(...), transcription_only: bool = False):
    """Process uploaded audio file"""
    logger.info(f"Audio processing requested - File: {file.filename}, Transcription only: {transcription_only}")
    
    try:
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        temp_file_path = temp_file.name
        
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Create audio processing request
        request = AudioProcessRequest(
            audio_path=temp_file_path,
            session_id="audio_processing",
            transcription_only=transcription_only
        )
        
        # Process through controller
        response, voice_analysis = await mental_health_controller.process_voice_interaction(request)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        logger.info(f"Audio processing completed - Transcription: {voice_analysis.transcription[:50]}...")
        
        return {
            "transcription": voice_analysis.transcription,
            "response": response.content if not transcription_only else None,
            "urgency_level": voice_analysis.urgency_level,
            "emotional_tone": voice_analysis.emotional_tone,
            "tools_used": response.tools_used if not transcription_only else []
        }
        
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

@router.post("/generate-voice")
async def generate_voice(request: VoiceGenerationRequest):
    """Generate voice from text"""
    logger.info(f"Voice generation requested - Text length: {len(request.text)}, Premium: {request.use_premium_voice}")
    
    try:
        # Generate voice through controller
        audio_file = await mental_health_controller.generate_voice_response(
            request.text, 
            request.use_premium_voice
        )
        
        if audio_file and os.path.exists(audio_file):
            logger.info(f"Voice generated successfully: {audio_file}")
            return FileResponse(
                path=audio_file,
                media_type="audio/mpeg",
                filename="voice_response.mp3"
            )
        else:
            logger.warning("Voice generation failed - no audio file produced")
            raise HTTPException(status_code=500, detail="Voice generation failed")
            
    except Exception as e:
        logger.error(f"Error generating voice: {e}")
        raise HTTPException(status_code=500, detail=f"Voice generation failed: {str(e)}")

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload document to knowledge base"""
    logger.info(f"Document upload requested - File: {file.filename}")
    
    try:
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        temp_file_path = temp_file.name
        
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Add to knowledge base
        rag_manager.add_document(temp_file_path)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        logger.info(f"Document uploaded successfully: {file.filename}")
        return {"message": f"Document '{file.filename}' added to the knowledge base successfully."}
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Get session chat history"""
    logger.info(f"Session history requested: {session_id}")
    
    try:
        # Get session from controller
        session = mental_health_controller.conversation_manager.get_session(session_id)
        
        if session:
            return {
                "session_id": session_id,
                "interactions": session.interactions,
                "risk_level": session.risk_level,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
        else:
            return {
                "session_id": session_id,
                "interactions": [],
                "risk_level": 1,
                "message": "Session not found"
            }
            
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session history")

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session chat history"""
    logger.info(f"Session clear requested: {session_id}")
    
    try:
        # Clear session through controller
        mental_health_controller.clear_session(session_id)
        
        # Also clear from local chat history
        if session_id in chat_history:
            del chat_history[session_id]
        
        logger.info(f"Session cleared: {session_id}")
        return {"message": f"Session {session_id} cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear session")