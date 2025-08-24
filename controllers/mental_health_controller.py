"""
Mental Health Controller

This controller handles the business logic for mental health interactions,
orchestrating between different services and maintaining session state.
Following MVC architecture, this contains the core business logic.
"""

import asyncio
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from models.business_models import (
    UserSession, 
    TherapeuticResponse, 
    EmergencyAssessment,
    ImageAnalysisResult,
    VoiceAnalysisResult,
    ConversationManager,
    RiskAssessment,
    MentalHealthCondition,
    EmotionalState,
    InteractionType
)
from models.api_models import (
    Query,
    ImageAnalysisRequest,
    AudioProcessRequest,
    MultimodalRequest,
    EmergencyRequest
)
from core.agent import graph, SYSTEM_PROMPT, parse_response
from core.audio_processor import audio_processor
from core.tools import (
    analyze_image_with_groq,
    process_image_for_analysis,
    text_to_speech_elevenlabs,
    text_to_speech_gtts
)
from langchain_core.messages import HumanMessage, SystemMessage


class MentalHealthController:
    """
    Main controller for mental health interactions.
    Handles session management, risk assessment, and multimodal processing.
    """
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.chat_history: Dict[str, List] = {}
    
    def _get_or_create_session(self, session_id: str, session_type: str = "general") -> UserSession:
        """Get existing session or create new one"""
        session = self.conversation_manager.get_session(session_id)
        if not session:
            session = self.conversation_manager.create_session(session_id, session_type)
            # Initialize chat history with system prompt
            self.chat_history[session_id] = [SystemMessage(content=SYSTEM_PROMPT)]
        return session
    
    def _assess_risk_level(self, content: str, modality: str = "text") -> int:
        """Assess risk level for the given content"""
        if modality == "text":
            return RiskAssessment.assess_text_risk(content)
        # Additional risk assessment for other modalities can be added here
        return 1
    
    def _handle_emergency(self, session_id: str, content: str) -> EmergencyAssessment:
        """Handle emergency situations"""
        assessment = EmergencyAssessment(
            session_id=session_id,
            risk_level=5,
            indicators=["Suicidal ideation detected", "Immediate intervention needed"],
            recommended_actions=[
                "Contact emergency services",
                "Engage emergency call tool",
                "Provide crisis resources"
            ],
            emergency_contacts=["Emergency Services: 911", "Crisis Hotline: 988"],
            immediate_response="I'm very concerned about you right now. Your safety is the most important thing.",
            requires_human_intervention=True
        )
        return assessment
    
    async def process_text_interaction(self, request: Query) -> TherapeuticResponse:
        """Process text-based mental health interaction"""
        try:
            # Get or create session
            session = self._get_or_create_session(request.session_id)
            
            # Assess risk level
            risk_level = self._assess_risk_level(request.message)
            session.risk_level = max(session.risk_level, risk_level)
            
            # Handle emergency situations
            if risk_level >= 4:
                emergency_assessment = self._handle_emergency(request.session_id, request.message)
                
                # Still process through agent but prioritize emergency response
                self.chat_history[request.session_id].append(HumanMessage(content=request.message))
                inputs = {"messages": self.chat_history[request.session_id]}
                stream = graph.astream(inputs, stream_mode="updates")
                tool_called, ai_response = await parse_response(stream)
                
                # Combine emergency response with AI response
                combined_response = f"{emergency_assessment.immediate_response}\\n\\n{ai_response}"
                
                response = TherapeuticResponse(
                    content=combined_response,
                    response_type=InteractionType.CRISIS_INTERVENTION,
                    tools_used=[tool_called, "emergency_assessment"],
                    emergency_flag=True,
                    confidence=0.95
                )
            else:
                # Normal processing
                self.chat_history[request.session_id].append(HumanMessage(content=request.message))
                inputs = {"messages": self.chat_history[request.session_id]}
                stream = graph.astream(inputs, stream_mode="updates")
                tool_called, ai_response = await parse_response(stream)
                
                self.chat_history[request.session_id].append(HumanMessage(content=ai_response))
                
                response = TherapeuticResponse(
                    content=ai_response,
                    response_type=InteractionType.CONVERSATION,
                    tools_used=[tool_called],
                    confidence=0.8
                )
            
            # Add interaction to session
            session.add_interaction(
                InteractionType.CONVERSATION,
                request.message,
                "text"
            )
            
            return response
            
        except Exception as e:
            # Error handling
            error_response = TherapeuticResponse(
                content=f"I apologize, but I encountered an issue processing your message. Please try again, and if you're in crisis, please contact emergency services immediately.",
                response_type=InteractionType.CONVERSATION,
                tools_used=["error_handler"],
                confidence=0.0,
                emergency_flag=True
            )
            return error_response
    
    async def process_image_interaction(self, request: ImageAnalysisRequest) -> Tuple[TherapeuticResponse, ImageAnalysisResult]:
        """Process image-based therapeutic interaction"""
        try:
            session = self._get_or_create_session(request.session_id)
            
            # Process image
            image_base64 = process_image_for_analysis(request.image_path)
            if not image_base64:
                raise ValueError("Could not process the uploaded image")
            
            # Analyze with GROQ
            analysis_text = analyze_image_with_groq(image_base64, request.query)
            
            # Create image analysis result
            analysis_result = ImageAnalysisResult(
                image_path=request.image_path,
                analysis_text=analysis_text,
                emotional_indicators=[],  # Could be extracted from analysis
                therapeutic_insights=[],  # Could be extracted from analysis
                confidence_score=0.8
            )
            
            # Create therapeutic response
            response = TherapeuticResponse(
                content=analysis_text,
                response_type=InteractionType.ART_THERAPY,
                modality="visual",
                tools_used=["analyze_uploaded_image"],
                confidence=0.8
            )
            
            # Add interaction to session
            session.add_interaction(
                InteractionType.ART_THERAPY,
                f"Image analysis: {request.query}",
                "image"
            )
            
            return response, analysis_result
            
        except Exception as e:
            error_response = TherapeuticResponse(
                content=f"I had trouble analyzing your image. Could you try uploading it again or describe what you'd like me to help you with?",
                response_type=InteractionType.ART_THERAPY,
                tools_used=["error_handler"],
                confidence=0.0
            )
            
            error_analysis = ImageAnalysisResult(
                image_path=request.image_path,
                analysis_text="Error occurred during analysis",
                confidence_score=0.0
            )
            
            return error_response, error_analysis
    
    async def process_voice_interaction(self, request: AudioProcessRequest) -> Tuple[TherapeuticResponse, VoiceAnalysisResult]:
        """Process voice-based therapeutic interaction"""
        try:
            session = self._get_or_create_session(request.session_id)
            
            # Transcribe audio
            transcription = audio_processor.transcribe_with_groq(request.audio_path)
            if not transcription:
                raise ValueError("Could not transcribe the audio")
            
            # Assess risk from transcription
            risk_level = self._assess_risk_level(transcription)
            session.risk_level = max(session.risk_level, risk_level)
            
            # Create voice analysis result
            voice_analysis = VoiceAnalysisResult(
                audio_path=request.audio_path,
                transcription=transcription,
                urgency_level=risk_level
            )
            
            if not request.transcription_only:
                # Process transcribed text through agent
                text_request = Query(message=transcription, session_id=request.session_id)
                therapeutic_response = await self.process_text_interaction(text_request)
                
                voice_analysis.therapeutic_response = therapeutic_response.content
                
                response = TherapeuticResponse(
                    content=therapeutic_response.content,
                    response_type=InteractionType.VOICE_THERAPY,
                    modality="audio",
                    tools_used=["process_voice_message"] + therapeutic_response.tools_used,
                    confidence=therapeutic_response.confidence,
                    emergency_flag=therapeutic_response.emergency_flag
                )
            else:
                response = TherapeuticResponse(
                    content=transcription,
                    response_type=InteractionType.VOICE_THERAPY,
                    modality="audio",
                    tools_used=["transcription_only"],
                    confidence=0.9
                )
            
            # Add interaction to session
            session.add_interaction(
                InteractionType.VOICE_THERAPY,
                transcription,
                "audio"
            )
            
            return response, voice_analysis
            
        except Exception as e:
            error_response = TherapeuticResponse(
                content="I had trouble understanding your voice message. Could you try again or type your message?",
                response_type=InteractionType.VOICE_THERAPY,
                tools_used=["error_handler"],
                confidence=0.0
            )
            
            error_analysis = VoiceAnalysisResult(
                audio_path=request.audio_path,
                transcription="Error occurred during transcription",
                urgency_level=1
            )
            
            return error_response, error_analysis
    
    async def process_multimodal_interaction(self, request: MultimodalRequest) -> TherapeuticResponse:
        """Process combined multimodal interaction"""
        try:
            session = self._get_or_create_session(request.session_id, request.query_type.value)
            
            response_parts = []
            tools_used = []
            highest_confidence = 0.0
            emergency_detected = False
            
            # Process image if provided
            if request.image_path:
                image_request = ImageAnalysisRequest(
                    image_path=request.image_path,
                    query="Analyze this image in the context of the user's overall query",
                    session_id=request.session_id
                )
                image_response, _ = await self.process_image_interaction(image_request)
                response_parts.append(f"Image Analysis: {image_response.content}")
                tools_used.extend(image_response.tools_used)
                highest_confidence = max(highest_confidence, image_response.confidence)
            
            # Process audio if provided
            if request.audio_path:
                audio_request = AudioProcessRequest(
                    audio_path=request.audio_path,
                    session_id=request.session_id
                )
                voice_response, voice_analysis = await self.process_voice_interaction(audio_request)
                response_parts.append(f"Voice Analysis: {voice_response.content}")
                tools_used.extend(voice_response.tools_used)
                highest_confidence = max(highest_confidence, voice_response.confidence)
                emergency_detected = emergency_detected or voice_response.emergency_flag
                
                # Use transcription as text if no text provided
                if not request.text:
                    request.text = voice_analysis.transcription
            
            # Process text (either provided or from audio transcription)
            if request.text:
                text_request = Query(message=request.text, session_id=request.session_id)
                text_response = await self.process_text_interaction(text_request)
                response_parts.append(f"AI Response: {text_response.content}")
                tools_used.extend(text_response.tools_used)
                highest_confidence = max(highest_confidence, text_response.confidence)
                emergency_detected = emergency_detected or text_response.emergency_flag
            
            # Combine all responses
            combined_content = "\\n\\n".join(response_parts) if response_parts else "I didn't receive any input to process."
            
            response = TherapeuticResponse(
                content=combined_content,
                response_type=InteractionType.CONVERSATION,
                modality="multimodal",
                tools_used=list(set(tools_used)),
                confidence=highest_confidence,
                emergency_flag=emergency_detected
            )
            
            # Add multimodal interaction to session
            session.add_interaction(
                InteractionType.CONVERSATION,
                f"Multimodal interaction: {request.text or 'No text'}",
                "multimodal"
            )
            
            return response
            
        except Exception as e:
            error_response = TherapeuticResponse(
                content="I encountered an issue processing your multimodal input. Please try again with a single input type.",
                response_type=InteractionType.CONVERSATION,
                tools_used=["error_handler"],
                confidence=0.0
            )
            return error_response
    
    async def generate_voice_response(self, text: str, use_premium: bool = False) -> str:
        """Generate voice response from text"""
        try:
            if use_premium:
                audio_file = text_to_speech_elevenlabs(text)
            else:
                audio_file = text_to_speech_gtts(text)
            
            return audio_file or ""
            
        except Exception as e:
            print(f"Error generating voice response: {e}")
            return ""
    
    def get_session_history(self, session_id: str) -> Optional[UserSession]:
        """Get session history"""
        return self.conversation_manager.get_session(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear session data"""
        try:
            if session_id in self.chat_history:
                self.chat_history[session_id] = [SystemMessage(content=SYSTEM_PROMPT)]
            
            session = self.conversation_manager.get_session(session_id)
            if session:
                # Create session summary before clearing
                summary = self.conversation_manager.end_session(session_id)
                return True
            return False
        except Exception:
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        from backend.config import OPENAI_API_KEY, GROQ_API_KEY, ELEVENLABS_API_KEY, TWILIO_ACCOUNT_SID
        
        status = {
            "overall_status": "operational",
            "active_sessions": len(self.conversation_manager.active_sessions),
            "configuration": {
                "openai_configured": "✅ Configured" if OPENAI_API_KEY else "❌ Not configured",
                "groq_configured": "✅ Configured" if GROQ_API_KEY else "❌ Not configured",
                "elevenlabs_configured": "✅ Configured" if ELEVENLABS_API_KEY else "❌ Not configured",
                "twilio_configured": "✅ Configured" if TWILIO_ACCOUNT_SID else "❌ Not configured",
            },
            "timestamp": datetime.now().isoformat()
        }
        return status


# Global controller instance
mental_health_controller = MentalHealthController()