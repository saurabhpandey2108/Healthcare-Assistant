"""
API Models for SAFESPACE AI AGENT

This module contains all Pydantic models used for API requests and responses.
Following MVC architecture, these models define the data structure for the API layer.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class SessionTypeEnum(str, Enum):
    """Types of conversation sessions"""
    GENERAL = "general"
    EMERGENCY = "emergency"
    THERAPY = "therapy"
    ANALYSIS = "analysis"


class ModalityEnum(str, Enum):
    """Types of input modalities"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"


class Query(BaseModel):
    """Basic text query model"""
    message: str = Field(..., description="User's text message", min_length=1)
    session_id: str = Field(default="default", description="Session identifier")
    modality: ModalityEnum = Field(default=ModalityEnum.TEXT, description="Input modality type")


class FileUpload(BaseModel):
    """File upload model for RAG documents"""
    file_path: str = Field(..., description="Path to uploaded file")
    file_type: Optional[str] = Field(None, description="Type of file (pdf, txt, web)")


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis"""
    image_path: str = Field(..., description="Path to uploaded image")
    query: Optional[str] = Field(
        default="Please analyze this image for mental health insights",
        description="Analysis query for the image"
    )
    session_id: str = Field(default="default", description="Session identifier")
    analysis_type: Optional[str] = Field(
        default="general",
        description="Type of analysis: general, emotional, therapeutic"
    )


class AudioProcessRequest(BaseModel):
    """Request model for audio processing"""
    audio_path: str = Field(..., description="Path to uploaded audio file")
    session_id: str = Field(default="default", description="Session identifier")
    transcription_only: bool = Field(
        default=False,
        description="If True, only return transcription without AI response"
    )


class VoiceGenerationRequest(BaseModel):
    """Request model for voice generation"""
    text: str = Field(..., description="Text to convert to speech", min_length=1)
    use_premium_voice: bool = Field(default=False, description="Use ElevenLabs premium voice")
    voice_id: Optional[str] = Field(
        default="pNInz6obpgDQGcFmaJgB",
        description="ElevenLabs voice ID for premium voices"
    )
    language: str = Field(default="en", description="Language code for voice synthesis")


class MultimodalRequest(BaseModel):
    """Request model for multimodal input processing"""
    text: Optional[str] = Field(None, description="Text input")
    image_path: Optional[str] = Field(None, description="Path to image file")
    audio_path: Optional[str] = Field(None, description="Path to audio file")
    session_id: str = Field(default="default", description="Session identifier")
    query_type: SessionTypeEnum = Field(
        default=SessionTypeEnum.GENERAL,
        description="Type of query session"
    )
    priority: int = Field(default=1, description="Priority level (1-5, 5 being highest)")


class EmergencyRequest(BaseModel):
    """Emergency assistance request model"""
    message: str = Field(..., description="Emergency message or context")
    location: Optional[str] = Field(None, description="User's location if available")
    session_id: str = Field(..., description="Session identifier")
    severity: int = Field(default=5, description="Emergency severity (1-5)")


# Response Models

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(default=True, description="Whether the request was successful")
    message: str = Field(..., description="Response message or content")
    session_id: str = Field(..., description="Session identifier")
    timestamp: Optional[str] = Field(None, description="Response timestamp")


class ChatResponse(BaseResponse):
    """Response model for chat interactions"""
    response: str = Field(..., description="AI assistant response")
    tool_called: str = Field(default="none", description="Name of tool used to generate response")
    modality: ModalityEnum = Field(default=ModalityEnum.TEXT, description="Response modality")
    confidence: Optional[float] = Field(None, description="Response confidence score")


class ImageAnalysisResponse(BaseResponse):
    """Response model for image analysis"""
    analysis: str = Field(..., description="Image analysis result")
    query: str = Field(..., description="Original analysis query")
    tool_used: str = Field(default="analyze_uploaded_image", description="Tool used for analysis")
    insights: Optional[Dict[str, Any]] = Field(None, description="Structured insights from analysis")


class AudioProcessResponse(BaseResponse):
    """Response model for audio processing"""
    transcription: str = Field(..., description="Audio transcription")
    response: Optional[str] = Field(None, description="AI response to transcribed content")
    tool_called: Optional[str] = Field(None, description="Tool used for processing")
    audio_info: Optional[Dict[str, Any]] = Field(None, description="Audio file information")


class VoiceGenerationResponse(BaseResponse):
    """Response model for voice generation"""
    audio_file: str = Field(..., description="Path to generated audio file")
    text: str = Field(..., description="Original text")
    premium_voice_used: bool = Field(..., description="Whether premium voice was used")
    audio_duration: Optional[float] = Field(None, description="Audio duration in seconds")


class MultimodalResponse(BaseResponse):
    """Response model for multimodal processing"""
    response: str = Field(..., description="Combined response from all modalities")
    tools_used: List[str] = Field(default_factory=list, description="List of tools used")
    modality_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from each modality"
    )
    multimodal: bool = Field(default=True, description="Indicates multimodal processing")


class SessionHistoryResponse(BaseResponse):
    """Response model for session history"""
    messages: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of conversation messages"
    )
    message_count: int = Field(default=0, description="Total number of messages")
    session_type: SessionTypeEnum = Field(
        default=SessionTypeEnum.GENERAL,
        description="Type of session"
    )


class HealthStatus(BaseModel):
    """Health check status model"""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class SystemStatusResponse(BaseModel):
    """System status response model"""
    overall_status: str = Field(..., description="Overall system status")
    services: List[HealthStatus] = Field(..., description="Individual service statuses")
    configuration: Dict[str, str] = Field(..., description="Configuration status")
    timestamp: str = Field(..., description="Status check timestamp")


# Configuration Models

class APIConfiguration(BaseModel):
    """API configuration model"""
    openai_configured: bool = Field(..., description="OpenAI API configuration status")
    groq_configured: bool = Field(..., description="GROQ API configuration status")
    elevenlabs_configured: bool = Field(..., description="ElevenLabs API configuration status")
    twilio_configured: bool = Field(..., description="Twilio API configuration status")


class AudioConfiguration(BaseModel):
    """Audio processing configuration"""
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    chunk_size: int = Field(default=1024, description="Audio processing chunk size")
    format: str = Field(default="wav", description="Default audio format")
    max_duration: int = Field(default=30, description="Maximum recording duration in seconds")


class ImageConfiguration(BaseModel):
    """Image processing configuration"""
    max_width: int = Field(default=1024, description="Maximum image width")
    max_height: int = Field(default=1024, description="Maximum image height")
    supported_formats: List[str] = Field(
        default=["jpg", "jpeg", "png", "bmp", "gif"],
        description="Supported image formats"
    )
    max_file_size: int = Field(default=10485760, description="Maximum file size in bytes (10MB)")


# Error Models

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always False for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    session_id: Optional[str] = Field(None, description="Session identifier if available")