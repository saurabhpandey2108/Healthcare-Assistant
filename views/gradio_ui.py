"""
Gradio Multimodal UI for SAFESPACE AI AGENT - MVC Architecture

This module provides the View layer for the multimodal mental health assistant,
following proper MVC architecture patterns.
"""

import gradio as gr
import tempfile
import os
import asyncio
from typing import Optional, Tuple, List
import threading
import time

from controllers.mental_health_controller import mental_health_controller
from models.api_models import Query, ImageAnalysisRequest, AudioProcessRequest, VoiceGenerationRequest
from models.business_models import InteractionType
from backend.config import (
    GROQ_API_KEY,
    ELEVENLABS_API_KEY,
    OPENAI_API_KEY,
    SUPPORTED_IMAGE_FORMATS
)


class SafeSpaceGradioUI:
    """
    Gradio-based multimodal user interface for SAFESPACE AI AGENT.
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
    
    def process_image_upload(self, image_file, query: str = None) -> str:
        """Process uploaded image for analysis."""
        if image_file is None:
            return "Please upload an image first."
        
        try:
            if not query:
                query = "Please analyze this image for mental health insights and emotional wellness guidance."
            
            request = ImageAnalysisRequest(
                image_path=image_file,
                query=query,
                session_id=self.current_session_id
            )
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def get_response():
                return await mental_health_controller.process_image_interaction(request)
            
            therapeutic_response, analysis_result = loop.run_until_complete(get_response())
            loop.close()
            
            return therapeutic_response.content
            
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
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
        
        with gr.Blocks(css=css, title="SAFESPACE AI Agent - Multimodal Mental Health Assistant") as interface:
            
            gr.Markdown("""
            # 🌟 SAFESPACE AI Agent
            ## Multimodal Mental Health Assistant
            
            Welcome to your personal AI mental health companion. I can help you through:
            - **Text conversations** for emotional support and guidance
            - **Image analysis** for art therapy and emotional insights  
            - **Voice interactions** for hands-free conversations
            
            *Remember: This is a supportive tool, not a replacement for professional mental health care.*
            """)
            
            with gr.Tabs():
                
                # Text Chat Tab
                with gr.TabItem("💬 Text Chat"):
                    with gr.Row():
                        with gr.Column(scale=3):
                            chatbot = gr.Chatbot(
                                height=400,
                                label="Conversation",
                                show_label=True
                            )
                            msg_input = gr.Textbox(
                                placeholder="Type your message here...",
                                label="Your Message",
                                lines=2
                            )
                            with gr.Row():
                                send_btn = gr.Button("Send", variant="primary")
                                clear_btn = gr.Button("Clear Chat")
                        
                        with gr.Column(scale=1):
                            gr.Markdown("### Quick Actions")
                            affirmation_btn = gr.Button("💝 Daily Affirmation")
                            breathing_btn = gr.Button("🫁 Breathing Exercise")
                            emergency_btn = gr.Button("🚨 Emergency Help", variant="stop")
                
                # Image Analysis Tab
                with gr.TabItem("🖼️ Image Analysis"):
                    with gr.Row():
                        with gr.Column():
                            image_input = gr.Image(
                                type="filepath",
                                label="Upload Image for Analysis"
                            )
                            image_query = gr.Textbox(
                                placeholder="What would you like me to analyze about this image?",
                                label="Analysis Query (Optional)",
                                lines=2
                            )
                            analyze_btn = gr.Button("Analyze Image", variant="primary")
                        
                        with gr.Column():
                            image_output = gr.Textbox(
                                label="Image Analysis",
                                lines=15,
                                show_copy_button=True
                            )
                
                # Voice Interaction Tab
                with gr.TabItem("🎤 Voice Chat"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Upload Audio File")
                            audio_input = gr.Audio(
                                type="filepath",
                                label="Upload Audio File"
                            )
                            process_audio_btn = gr.Button("Process Audio")
                        
                        with gr.Column():
                            transcription_output = gr.Textbox(
                                label="What You Said",
                                lines=3
                            )
                            voice_response_output = gr.Textbox(
                                label="AI Response",
                                lines=8
                            )
                            voice_audio_output = gr.Audio(
                                label="AI Voice Response"
                            )
                            
                            with gr.Row():
                                generate_voice_btn = gr.Button("🔊 Generate Voice Response")
                                premium_voice_checkbox = gr.Checkbox(
                                    label="Use Premium Voice (ElevenLabs)",
                                    value=False
                                )
                
                # Settings Tab
                with gr.TabItem("⚙️ Settings"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Configuration Status")
                            
                            openai_status = gr.Textbox(
                                value="✅ Configured" if OPENAI_API_KEY else "❌ Not configured",
                                label="OpenAI API (Primary for Vision & Audio)",
                                interactive=False
                            )
                            
                            groq_status = gr.Textbox(
                                value="✅ Configured" if GROQ_API_KEY else "❌ Not configured",
                                label="GROQ API (Fallback for Vision & Audio)",
                                interactive=False
                            )
                            
                            elevenlabs_status = gr.Textbox(
                                value="✅ Configured" if ELEVENLABS_API_KEY else "❌ Not configured (using gTTS fallback)",
                                label="ElevenLabs API (Premium Voice)",
                                interactive=False
                            )
                            
                        with gr.Column():
                            gr.Markdown("### Session Management")
                            session_id_input = gr.Textbox(
                                value="default_session",
                                label="Session ID"
                            )
                            reset_session_btn = gr.Button("Reset Session")
                            
                            gr.Markdown("### API Priority")
                            gr.Markdown("""
                            **Image Analysis:** OpenAI GPT-4 Vision → GROQ Llama Vision
                            **Speech Transcription:** OpenAI Whisper → GROQ Whisper → Google Speech
                            **Voice Synthesis:** ElevenLabs → Google TTS
                            **Text Generation:** OpenAI GPT-4o
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
            
            def quick_affirmation(history):
                response, _ = self.process_text_message("Please give me a daily affirmation")
                history.append(("Daily affirmation request", response))
                return history
            
            def quick_breathing(history):
                response, _ = self.process_text_message("I'm feeling anxious, can you guide me through a breathing exercise?")
                history.append(("Breathing exercise request", response))
                return history
            
            def emergency_help(history):
                response, _ = self.process_text_message("I need emergency mental health help")
                history.append(("Emergency help request", response))
                return history
            
            def analyze_image(image, query):
                if image is None:
                    return "Please upload an image first."
                return self.process_image_upload(image, query)
            
            def process_uploaded_audio(audio):
                transcription, response = self.process_voice_input(audio)
                return transcription, response
            
            def generate_voice(text, use_premium):
                if not text.strip():
                    return None
                audio_file = self.generate_voice_response(text, use_premium)
                return audio_file
            
            def update_session_id(new_session_id):
                self.current_session_id = new_session_id
                return f"Session updated to: {new_session_id}"
            
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
            
            affirmation_btn.click(
                quick_affirmation,
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            breathing_btn.click(
                quick_breathing,
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            emergency_btn.click(
                emergency_help,
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            analyze_btn.click(
                analyze_image,
                inputs=[image_input, image_query],
                outputs=[image_output]
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
        
        return interface
    
    def launch(self, share=False, debug=False, server_port=7860):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        interface.launch(
            share=share,
            debug=debug,
            server_port=server_port,
            server_name="0.0.0.0"
        )


# Global UI instance
safespace_ui = SafeSpaceGradioUI()


if __name__ == "__main__":
    # Launch the interface
    safespace_ui.launch(share=False, debug=True)