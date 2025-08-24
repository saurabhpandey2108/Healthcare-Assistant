"""
Business Models for SAFESPACE AI AGENT

This module contains business logic models and data structures
used throughout the application for mental health assistance.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class MentalHealthCondition(str, Enum):
    """Common mental health conditions the AI can help with"""
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    PANIC = "panic"
    PTSD = "ptsd"
    GENERAL = "general"
    EMERGENCY = "emergency"


class EmotionalState(str, Enum):
    """Emotional states that can be detected"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    CALM = "calm"
    EXCITED = "excited"
    DEPRESSED = "depressed"
    STRESSED = "stressed"
    NEUTRAL = "neutral"


class InteractionType(str, Enum):
    """Types of therapeutic interactions"""
    CONVERSATION = "conversation"
    CRISIS_INTERVENTION = "crisis_intervention"
    BREATHING_EXERCISE = "breathing_exercise"
    MINDFULNESS = "mindfulness"
    ART_THERAPY = "art_therapy"
    VOICE_THERAPY = "voice_therapy"
    RESOURCE_PROVISION = "resource_provision"


@dataclass
class UserSession:
    """Represents a user's therapy session"""
    session_id: str
    user_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    session_type: str = "general"
    emotional_state: Optional[EmotionalState] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    multimodal_interactions: List[Dict[str, Any]] = field(default_factory=list)
    risk_level: int = 1  # 1-5 scale, 5 being highest risk
    
    def add_interaction(self, interaction_type: InteractionType, content: str, modality: str = "text"):
        """Add an interaction to the session"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type.value,
            "content": content,
            "modality": modality
        }
        self.conversation_history.append(interaction)
        self.last_activity = datetime.now()
    
    def update_emotional_state(self, state: EmotionalState):
        """Update the user's emotional state"""
        self.emotional_state = state
        self.last_activity = datetime.now()


@dataclass
class ImageAnalysisResult:
    """Result of image analysis for therapeutic insights"""
    image_path: str
    analysis_text: str
    emotional_indicators: List[str] = field(default_factory=list)
    color_psychology: Dict[str, str] = field(default_factory=dict)
    therapeutic_insights: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VoiceAnalysisResult:
    """Result of voice analysis for emotional assessment"""
    audio_path: str
    transcription: str
    emotional_tone: Optional[EmotionalState] = None
    stress_indicators: List[str] = field(default_factory=list)
    speech_patterns: Dict[str, Any] = field(default_factory=dict)
    therapeutic_response: str = ""
    urgency_level: int = 1  # 1-5 scale
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TherapeuticResponse:
    """A therapeutic response from the AI"""
    content: str
    response_type: InteractionType
    modality: str = "text"  # text, audio, visual
    tools_used: List[str] = field(default_factory=list)
    confidence: float = 0.0
    follow_up_suggestions: List[str] = field(default_factory=list)
    emergency_flag: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyAssessment:
    """Assessment for emergency situations"""
    session_id: str
    risk_level: int  # 1-5 scale, 5 being immediate danger
    indicators: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    emergency_contacts: List[str] = field(default_factory=list)
    immediate_response: str = ""
    requires_human_intervention: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MentalHealthResource:
    """Mental health resource information"""
    name: str
    type: str  # hotline, website, app, local_service
    description: str
    contact_info: str
    availability: str = "24/7"
    location: Optional[str] = None
    specialization: List[MentalHealthCondition] = field(default_factory=list)


@dataclass
class TherapistRecommendation:
    """Therapist or mental health professional recommendation"""
    name: str
    specialization: List[str]
    location: str
    contact_info: str
    availability: str
    rating: Optional[float] = None
    distance: Optional[float] = None  # in miles/km
    insurance_accepted: List[str] = field(default_factory=list)


@dataclass
class BreathingExercise:
    """Breathing exercise configuration"""
    name: str
    description: str
    inhale_duration: int = 4
    hold_duration: int = 4
    exhale_duration: int = 4
    pause_duration: int = 4
    repetitions: int = 5
    instructions: List[str] = field(default_factory=list)


@dataclass
class DailyAffirmation:
    """Daily affirmation data"""
    text: str
    category: str = "general"
    mood_target: List[EmotionalState] = field(default_factory=list)
    source: str = "internal"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SessionSummary:
    """Summary of a therapy session"""
    session_id: str
    duration: float  # in minutes
    interaction_count: int
    modalities_used: List[str]
    emotional_journey: List[EmotionalState]
    tools_utilized: List[str]
    key_insights: List[str]
    recommendations: List[str]
    follow_up_needed: bool = False
    overall_mood_improvement: float = 0.0  # -1 to 1 scale
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationManager:
    """Manages conversation state and context"""
    
    def __init__(self):
        self.active_sessions: Dict[str, UserSession] = {}
        self.session_summaries: Dict[str, SessionSummary] = {}
    
    def create_session(self, session_id: str, session_type: str = "general") -> UserSession:
        """Create a new user session"""
        session = UserSession(
            session_id=session_id,
            session_type=session_type
        )
        self.active_sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get an existing session"""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> Optional[SessionSummary]:
        """End a session and create summary"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        # Create session summary
        summary = SessionSummary(
            session_id=session_id,
            duration=(datetime.now() - session.start_time).total_seconds() / 60,
            interaction_count=len(session.conversation_history),
            modalities_used=list(set(
                interaction.get("modality", "text") 
                for interaction in session.conversation_history
            )),
            emotional_journey=[],  # Would be populated based on conversation analysis
            tools_utilized=list(set(
                interaction.get("tool_used", "") 
                for interaction in session.conversation_history 
                if interaction.get("tool_used")
            )),
            key_insights=[],  # Would be generated based on conversation analysis
            recommendations=[]  # Would be generated based on session analysis
        )
        
        self.session_summaries[session_id] = summary
        del self.active_sessions[session_id]
        return summary


class RiskAssessment:
    """Risk assessment utilities"""
    
    @staticmethod
    def assess_text_risk(text: str) -> int:
        """Assess risk level based on text content"""
        # High-risk keywords and phrases
        high_risk_keywords = [
            "suicide", "kill myself", "end it all", "want to die",
            "hurt myself", "self harm", "no point", "can't go on"
        ]
        
        medium_risk_keywords = [
            "hopeless", "worthless", "give up", "can't cope",
            "everything is wrong", "no one cares", "alone"
        ]
        
        text_lower = text.lower()
        
        # Check for high-risk indicators
        for keyword in high_risk_keywords:
            if keyword in text_lower:
                return 5  # Immediate attention needed
        
        # Check for medium-risk indicators
        for keyword in medium_risk_keywords:
            if keyword in text_lower:
                return 3  # Elevated concern
        
        return 1  # Low risk
    
    @staticmethod
    def assess_voice_risk(voice_analysis: VoiceAnalysisResult) -> int:
        """Assess risk level based on voice analysis"""
        risk_level = 1
        
        # Check transcription content
        text_risk = RiskAssessment.assess_text_risk(voice_analysis.transcription)
        risk_level = max(risk_level, text_risk)
        
        # Additional voice-based indicators could be added here
        # such as speech rate, tone analysis, etc.
        
        return risk_level


# Global conversation manager instance
conversation_manager = ConversationManager()