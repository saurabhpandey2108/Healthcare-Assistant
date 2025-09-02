"""
Gradio Voice Interface for SAFESPACE AI AGENT - MVC Architecture

This module provides the View layer for voice interactions (TTS/STT) in the
healthcare assistant. Focused on speech-to-text and text-to-speech capabilities.
Following proper MVC architecture patterns.
"""

import gradio as gr
import os
import asyncio
from typing import Tuple
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.mental_health_controller import mental_health_controller
from models.api_models import Query, AudioProcessRequest
from backend.config import (
    GROQ_API_KEY,
    ELEVENLABS_API_KEY,
    OPENAI_API_KEY
)


class SafeSpaceGradioUI:
    """
    Gradio-based voice interface for SAFESPACE AI AGENT.
    Focused on TTS/STT capabilities for healthcare consultations.
    This is the View component in the MVC architecture.
    """
    
    def __init__(self):
        self.current_session_id = "default_session"
        
    def process_text_message(self, message: str, session_id: str = None) -> Tuple[str, str]:
        """Process text message through the controller."""
        if not session_id:
            session_id = self.current_session_id
            
        try:
            query = Query(message=message, session_id=session_id)
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def get_response():
                return await mental_health_controller.process_text_interaction(query)
            
            therapeutic_response = loop.run_until_complete(get_response())
            loop.close()
            
            return therapeutic_response.content, therapeutic_response.tools_used[0] if therapeutic_response.tools_used else "none"
            
        except Exception as e:
            error_response = f"I encountered an error processing your message: {str(e)}"
            return error_response, "error"
    
    def process_voice_input(self, audio_file) -> Tuple[str, str]:
        """Process voice input by transcribing and generating response."""
        if audio_file is None:
            return "No audio file provided.", "Please upload an audio file or record your voice."
        
        try:
            request = AudioProcessRequest(
                audio_path=audio_file,
                session_id=self.current_session_id
            )
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def get_response():
                return await mental_health_controller.process_voice_interaction(request)
            
            therapeutic_response, voice_analysis = loop.run_until_complete(get_response())
            loop.close()
            
            return voice_analysis.transcription, therapeutic_response.content
            
        except Exception as e:
            error_msg = f"Error processing voice input: {str(e)}"
            return error_msg, error_msg
    
    def generate_voice_response(self, text: str, use_premium: bool = False) -> str:
        """Generate voice response from text."""
        try:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def get_response():
                return await mental_health_controller.generate_voice_response(text, use_premium)
            
            audio_file = loop.run_until_complete(get_response())
            loop.close()
            
            return audio_file
            
        except Exception as e:
            print(f"Error generating voice response: {e}")
            return None
    
    def create_interface(self):
        """Create and configure the Gradio interface."""
        
        css = """
        .gradio-container {
            max-width: 1200px !important;
            margin: auto !important;
        }
        .chat-message {
            padding: 10px;
            margin: 5px;
            border-radius: 10px;
            background-color: #f0f0f0;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
        }
        .assistant-message {
            background-color: #f3e5f5;
        }
        """
        
        with gr.Blocks(css=css, title="SAFESPACE AI Agent - Voice Interface (TTS/STT)") as interface:
            
            gr.Markdown("""
            # SAFESPACE AI Agent - Voice Interface
            ## Text-to-Speech & Speech-to-Text Healthcare Assistant
            
            This interface focuses on voice interactions for healthcare support:
            - **Voice Chat** - Speak your health concerns and get audio responses
            - **Speech-to-Text** - Convert your spoken queries to text
            - **Text-to-Speech** - Get AI responses in natural voice
            - **Mental Health & General Health** - Support for all healthcare domains
            
            *For comprehensive healthcare tools, image analysis, and document uploads, use the Streamlit interface.*
            
            *Remember: This is a supportive tool, not a replacement for professional medical care.*
            """)
            
            with gr.Tabs():
                
                # Voice Chat Tab
                with gr.TabItem("Voice Chat"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Voice Healthcare Consultation")
                            gr.Markdown("Upload audio files or record your voice for healthcare consultations")
                            
                            audio_input = gr.Audio(
                                type="filepath",
                                label="Upload Audio for Healthcare Consultation"
                            )
                            process_audio_btn = gr.Button("Process Audio", variant="primary")
                        
                        with gr.Column():
                            transcription_output = gr.Textbox(
                                label="Your Healthcare Query (Transcription)",
                                lines=4
                            )
                            voice_response_output = gr.Textbox(
                                label="Healthcare Assistant Response",
                                lines=10
                            )
                            voice_audio_output = gr.Audio(
                                label="Healthcare Assistant Voice Response"
                            )
                            
                            with gr.Row():
                                generate_voice_btn = gr.Button("Generate Voice Response", variant="secondary")
                                premium_voice_checkbox = gr.Checkbox(
                                    label="Use Premium Voice (ElevenLabs)",
                                    value=False
                            )
                
                # Text Chat (for reference/backup)
                with gr.TabItem("Text Chat"):
                    gr.Markdown("### Text Chat Interface")
                    gr.Markdown("*Note: For comprehensive healthcare tools, please use the Streamlit interface*")
                    
                    with gr.Row():
                        with gr.Column(scale=4):
                            chatbot = gr.Chatbot(
                                height=400,
                                label="Healthcare Conversation",
                                show_label=True
                            )
                            msg_input = gr.Textbox(
                                placeholder="Type your healthcare question here...",
                                label="Your Message",
                                lines=2
                            )
                            with gr.Row():
                                send_btn = gr.Button("Send", variant="primary")
                                clear_btn = gr.Button("Clear Chat")
                        
                        with gr.Column(scale=1):
                            gr.Markdown("### Quick Actions")
                            emergency_btn = gr.Button("Emergency Help", variant="stop")
                            gr.Markdown("*Other healthcare tools available in Streamlit interface*")
                
                # Settings Tab
                with gr.TabItem("Settings"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### API Configuration Status")
                            
                            openai_status = gr.Textbox(
                                value="Configured" if OPENAI_API_KEY else "Not configured",
                                label="OpenAI API (Primary for Vision & Audio)",
                                interactive=False
                            )
                            
                            groq_status = gr.Textbox(
                                value="Configured" if GROQ_API_KEY else "Not configured",
                                label="GROQ API (Fallback for Vision & Audio)",
                                interactive=False
                            )
                            
                            elevenlabs_status = gr.Textbox(
                                value="Configured" if ELEVENLABS_API_KEY else "Not configured (using gTTS fallback)",
                                label="ElevenLabs API (Premium Voice)",
                                interactive=False
                            )
                            
                        with gr.Column():
                            gr.Markdown("### Session Management")
                            gr.Markdown("""
                            **What is Session Management?**
                            
                            Session management allows you to:
                            - **Maintain Conversation Context**: Keep track of your ongoing conversation with the AI
                            - **Separate Different Topics**: Use different session IDs for different health concerns
                            - **Privacy Control**: Each session stores its own conversation history
                            - **Multi-User Support**: Different users can have separate sessions
                            
                            **How Session ID Works:**
                            - **Default Session**: "default_session" - Your main conversation
                            - **Custom Sessions**: Create specific sessions like "anxiety_session", "health_checkup", etc.
                            - **Session History**: All messages in a session are remembered for context
                            - **Session Reset**: Clear history and start fresh conversation
                            
                            **Examples:**
                            - mental_health_2024 - For ongoing therapy discussions
                            - physical_symptoms - For tracking physical health concerns
                            - emergency_session - For crisis situations
                            """)
                            
                            session_id_input = gr.Textbox(
                                value="default_session",
                                label="Current Session ID",
                                placeholder="Enter a unique session name"
                            )
                            
                            with gr.Row():
                                reset_session_btn = gr.Button("Reset Current Session", variant="secondary")
                                new_session_btn = gr.Button("Create New Session", variant="primary")
                            
                            gr.Markdown("### Voice Interface Capabilities")
                            gr.Markdown("""
                            **TTS/STT Processing:**
                            - Speech-to-Text: OpenAI Whisper to GROQ Whisper to Google Speech
                            - Voice Synthesis: ElevenLabs to Google TTS
                            - Text Generation: OpenAI GPT-4o
                            
                            **Healthcare Support:**
                            - Mental Health: Therapy, crisis intervention, emotional support
                            - General Health: Voice consultations for any health concerns
                            
                            **Note:** For comprehensive tools (image analysis, document upload, 
                            healthcare provider finder), please use the Streamlit interface.
                            """)
            
            # Event handlers
            def chat_response(message, history):
                if not message.strip():
                    return history, ""
                
                response, tool_used = self.process_text_message(message)
                history.append((message, response))
                return history, ""
            
            def clear_chat():
                mental_health_controller.clear_session(self.current_session_id)
                return []
            
            def emergency_help(history):
                response, _ = self.process_text_message("I need emergency mental health help")
                history.append(("Emergency help request", response))
                return history
            
            def process_uploaded_audio(audio):
                transcription, response = self.process_voice_input(audio)
                return transcription, response
            
            def generate_voice(text, use_premium):
                if not text.strip():
                    return None
                audio_file = self.generate_voice_response(text, use_premium)
                return audio_file
            
            def update_session_id(new_session_id):
                """Update the current session ID"""
                if new_session_id.strip():
                    self.current_session_id = new_session_id.strip()
                    return f"Session updated to: {self.current_session_id}"
                else:
                    return "Please enter a valid session ID"
            
            def reset_session():
                """Reset the current session history"""
                try:
                    mental_health_controller.clear_session(self.current_session_id)
                    return f"Session '{self.current_session_id}' has been reset. Chat history cleared."
                except Exception as e:
                    return f"Error resetting session: {str(e)}"
            
            def create_new_session():
                """Create a new session with timestamp"""
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_session_id = f"session_{timestamp}"
                self.current_session_id = new_session_id
                return new_session_id, f"New session created: {new_session_id}"
            
            # Connect event handlers
            send_btn.click(
                chat_response,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            msg_input.submit(
                chat_response,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input]
            )
            
            clear_btn.click(clear_chat, outputs=[chatbot])
            
            emergency_btn.click(
                emergency_help,
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            process_audio_btn.click(
                process_uploaded_audio,
                inputs=[audio_input],
                outputs=[transcription_output, voice_response_output]
            )
            
            generate_voice_btn.click(
                generate_voice,
                inputs=[voice_response_output, premium_voice_checkbox],
                outputs=[voice_audio_output]
            )
            
            session_id_input.change(
                update_session_id,
                inputs=[session_id_input],
                outputs=[]
            )
            
            reset_session_btn.click(
                reset_session,
                outputs=[]
            )
            
            new_session_btn.click(
                create_new_session,
                outputs=[session_id_input]
            )
        
        return interface
    
    def launch(self, share=False, debug=False, server_port=7860, server_name="localhost"):
        """Launch the Gradio interface with proper localhost configuration."""
        interface = self.create_interface()
        
        print(f"Starting SAFESPACE AI Agent Voice Interface")
        print(f"Server will be available at: http://{server_name}:{server_port}")
        print(f"Debug mode: {debug}")
        print(f"Public sharing: {share}")
        
        interface.launch(
            share=share,
            debug=debug,
            server_port=server_port,
            server_name=server_name,
            show_error=True,
            quiet=False
        )


# Global UI instance
safespace_ui = SafeSpaceGradioUI()


if __name__ == "__main__":
    # Launch the voice interface
    print("SAFESPACE AI Agent - Voice Interface (TTS/STT)")
    print("Starting voice consultation interface...")
    safespace_ui.launch(share=False, debug=True, server_name="localhost")