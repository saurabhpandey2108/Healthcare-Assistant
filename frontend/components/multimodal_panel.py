"""
Multimodal Panel Component for SAFESPACE AI AGENT Streamlit Interface

This module provides the multimodal interaction panel for image and audio processing.
"""

import streamlit as st
import requests
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional
import tempfile
import base64

if TYPE_CHECKING:
    from frontend.components.session_manager import SessionManager

from frontend.utils.config import (
    ENDPOINTS, SUPPORTED_IMAGE_FORMATS, SUPPORTED_AUDIO_FORMATS,
    MAX_IMAGE_SIZE_MB, MAX_AUDIO_SIZE_MB, IMAGE_ANALYSIS_TYPES,
    VOICE_OPTIONS, ERROR_MESSAGES
)
from frontend.utils.styling import create_alert
from frontend.components.audio_recorder import simple_audio_interface, audio_recorder_widget


def render_multimodal_panel(session_manager: 'SessionManager'):
    """Render the complete multimodal interaction panel"""
    
    st.markdown('<div class="multimodal-container">', unsafe_allow_html=True)
    
    st.header("🎭 Multimodal Interactions")
    st.markdown("Upload images or audio for AI analysis and insights")
    
    # Tabs for different modalities
    tab1, tab2, tab3 = st.tabs(["📷 Images", "🎤 Audio", "🔊 Voice"])
    
    with tab1:
        render_image_upload_panel(session_manager)
    
    with tab2:
        render_audio_upload_panel(session_manager)
    
    with tab3:
        render_voice_generation_panel(session_manager)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_image_upload_panel(session_manager: 'SessionManager'):
    """Render image upload and analysis panel"""
    
    st.subheader("📷 Image Analysis")
    st.markdown("Upload images for emotional and therapeutic analysis")
    
    # Image upload
    uploaded_files = st.file_uploader(
        "Choose image files",
        type=SUPPORTED_IMAGE_FORMATS,
        accept_multiple_files=True,
        key="image_uploader",
        help=f"Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            process_uploaded_image(uploaded_file, session_manager)
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Analysis Type",
        options=[item["type"] for item in IMAGE_ANALYSIS_TYPES],
        format_func=lambda x: next(item["name"] for item in IMAGE_ANALYSIS_TYPES if item["type"] == x),
        key="analysis_type"
    )
    
    # Custom analysis query
    custom_query = st.text_area(
        "Custom Analysis Query (Optional)",
        placeholder="e.g., 'What emotions do you see in this artwork?'",
        key="custom_image_query"
    )
    
    # Analysis settings
    with st.expander("⚙️ Analysis Settings"):
        include_therapeutic_insights = st.checkbox("Include Therapeutic Insights", value=True)
        include_color_analysis = st.checkbox("Include Color Psychology", value=True)
        include_composition = st.checkbox("Analyze Composition", value=False)
    
    # Show uploaded images
    if st.session_state.get('uploaded_images'):
        st.markdown("**Recently Uploaded Images:**")
        
        for filename, image_data in st.session_state.uploaded_images.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.image(image_data['path'], caption=filename, width=200)
            
            with col2:
                if st.button(f"Analyze", key=f"analyze_{filename}"):
                    analyze_image(image_data['path'], analysis_type, custom_query, session_manager)
                
                if st.button(f"Remove", key=f"remove_{filename}"):
                    remove_uploaded_image(filename)


def process_uploaded_image(uploaded_file, session_manager: 'SessionManager'):
    """Process and save uploaded image"""
    
    # Check file size
    if uploaded_file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        st.error(f"File size exceeds {MAX_IMAGE_SIZE_MB}MB limit")
        return
    
    try:
        # Save to uploads directory
        upload_dir = Path("uploads/images")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store in session state
        if 'uploaded_images' not in st.session_state:
            st.session_state.uploaded_images = {}
        
        st.session_state.uploaded_images[uploaded_file.name] = {
            'path': str(file_path),
            'size': uploaded_file.size,
            'type': uploaded_file.type
        }
        
        st.success(f"✅ {uploaded_file.name} uploaded successfully!")
        
        # Auto-analyze if it's the first image
        if len(st.session_state.uploaded_images) == 1:
            st.info("💡 Click 'Analyze' to get AI insights about your image")
        
    except Exception as e:
        st.error(f"Error uploading image: {str(e)}")


def analyze_image(image_path: str, analysis_type: str, custom_query: str, session_manager: 'SessionManager'):
    """Analyze uploaded image using AI"""
    
    try:
        with st.spinner("🔍 Analyzing image..."):
            # Prepare analysis query
            if custom_query.strip():
                query = custom_query
            else:
                type_info = next(item for item in IMAGE_ANALYSIS_TYPES if item["type"] == analysis_type)
                query = f"Please provide {type_info['description'].lower()} for this image"
            
            # Make API request
            response = requests.post(
                ENDPOINTS['analyze_image'],
                json={
                    "image_path": image_path,
                    "query": query,
                    "session_id": st.session_state.active_chat_id,
                    "analysis_type": analysis_type
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('analysis', 'No analysis available')
                
                # Add to chat history
                session_manager.add_message(
                    "user",
                    f"[Image Analysis Request] {query}",
                    {"type": "image_analysis", "image_path": image_path}
                )
                
                session_manager.add_message(
                    "assistant",
                    f"🖼️ **Image Analysis Results:**\n\n{analysis}",
                    {
                        "tool_called": "analyze_uploaded_image",
                        "analysis_type": analysis_type,
                        "image_path": image_path
                    }
                )
                
                st.success("✅ Image analysis completed! Check the chat for results.")
                st.rerun()
                
            else:
                st.error(f"Analysis failed: {response.status_code}")
                
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")


def remove_uploaded_image(filename: str):
    """Remove uploaded image from session"""
    if filename in st.session_state.uploaded_images:
        # Try to delete file
        try:
            file_path = st.session_state.uploaded_images[filename]['path']
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        # Remove from session state
        del st.session_state.uploaded_images[filename]
        st.success(f"Removed {filename}")
        st.rerun()


def render_audio_upload_panel(session_manager: 'SessionManager'):
    """Render audio upload and processing panel"""
    
    st.subheader("🎤 Audio Processing")
    st.markdown("Record or upload audio files for transcription and analysis")
    
    # Use the enhanced audio interface
    uploaded_audio = simple_audio_interface()
    
    if uploaded_audio:
        # Process the uploaded audio
        process_uploaded_audio(uploaded_audio, session_manager)
    
    # Alternative: Use the advanced audio recorder widget
    st.markdown("---")
    st.markdown("**Advanced Recording Options:**")
    
    recorded_audio = audio_recorder_widget()
    if recorded_audio:
        process_uploaded_audio(recorded_audio, session_manager)
    
    # Processing options
    with st.expander("⚙️ Audio Processing Options"):
        transcription_only = st.checkbox("Transcription Only", value=False)
        include_emotion_analysis = st.checkbox("Include Emotional Analysis", value=True)
        include_urgency_detection = st.checkbox("Detect Urgency Level", value=True)
    
    # Show uploaded audio files
    if st.session_state.get('uploaded_audio'):
        st.markdown("**Recently Uploaded Audio:**")
        
        for filename, audio_data in st.session_state.uploaded_audio.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.audio(audio_data['path'])
                st.caption(f"📁 {filename} ({audio_data['size']/1024:.1f} KB)")
            
            with col2:
                if st.button(f"Process", key=f"process_{filename}"):
                    process_audio_file(audio_data['path'], transcription_only, session_manager)
                
                if st.button(f"Delete", key=f"delete_{filename}"):
                    remove_uploaded_audio(filename)


def process_uploaded_audio(uploaded_file, session_manager: 'SessionManager'):
    """Process and save uploaded audio file"""
    
    # Check file size
    if uploaded_file.size > MAX_AUDIO_SIZE_MB * 1024 * 1024:
        st.error(f"File size exceeds {MAX_AUDIO_SIZE_MB}MB limit")
        return
    
    try:
        # Save to uploads directory
        upload_dir = Path("uploads/audio")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store in session state
        if 'uploaded_audio' not in st.session_state:
            st.session_state.uploaded_audio = {}
        
        st.session_state.uploaded_audio[uploaded_file.name] = {
            'path': str(file_path),
            'size': uploaded_file.size,
            'type': uploaded_file.type
        }
        
        st.success(f"✅ {uploaded_file.name} uploaded successfully!")
        
    except Exception as e:
        st.error(f"Error uploading audio: {str(e)}")


def process_audio_file(audio_path: str, transcription_only: bool, session_manager: 'SessionManager'):
    """Process audio file for transcription and analysis"""
    
    try:
        with st.spinner("🎧 Processing audio..."):
            # Make API request
            response = requests.post(
                ENDPOINTS['process_audio'],
                json={
                    "audio_path": audio_path,
                    "session_id": st.session_state.active_chat_id,
                    "transcription_only": transcription_only
                },
                timeout=60  # Audio processing can take longer
            )
            
            if response.status_code == 200:
                result = response.json()
                transcription = result.get('transcription', 'No transcription available')
                ai_response = result.get('response')
                
                # Add to chat history
                session_manager.add_message(
                    "user",
                    f"[Audio Message] {transcription}",
                    {"type": "audio_transcription", "audio_path": audio_path}
                )
                
                if ai_response and not transcription_only:
                    session_manager.add_message(
                        "assistant",
                        ai_response,
                        {
                            "tool_called": "process_voice_message",
                            "transcription": transcription,
                            "audio_path": audio_path
                        }
                    )
                
                st.success("✅ Audio processing completed! Check the chat for results.")
                st.rerun()
                
            else:
                st.error(f"Audio processing failed: {response.status_code}")
                
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")


def remove_uploaded_audio(filename: str):
    """Remove uploaded audio from session"""
    if filename in st.session_state.uploaded_audio:
        # Try to delete file
        try:
            file_path = st.session_state.uploaded_audio[filename]['path']
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        # Remove from session state
        del st.session_state.uploaded_audio[filename]
        st.success(f"Removed {filename}")
        st.rerun()


def render_voice_generation_panel(session_manager: 'SessionManager'):
    """Render voice generation panel"""
    
    st.subheader("🔊 Voice Generation")
    st.markdown("Convert text to speech with AI voices")
    
    # Text input for voice generation
    text_to_speak = st.text_area(
        "Text to Convert to Speech",
        placeholder="Enter the text you want to convert to speech...",
        key="voice_text",
        height=100
    )
    
    # Voice options
    col1, col2 = st.columns(2)
    
    with col1:
        use_premium = st.checkbox("Use Premium Voice", value=False, key="use_premium_voice")
    
    with col2:
        if use_premium:
            voice_id = st.selectbox(
                "Voice Selection",
                options=list(VOICE_OPTIONS["ElevenLabs"]["voices"].keys()),
                format_func=lambda x: VOICE_OPTIONS["ElevenLabs"]["voices"][x],
                key="selected_voice"
            )
        else:
            st.info("Using Google Text-to-Speech (Free)")
    
    # Voice settings
    with st.expander("⚙️ Voice Settings"):
        language = st.selectbox("Language", ["en", "es", "fr", "de", "it"], key="voice_language")
        if use_premium:
            st.info("Premium voices provide better quality and emotional expression")
        else:
            st.info("Free voices are suitable for basic text-to-speech needs")
    
    # Generate voice button
    if st.button("🎤 Generate Voice", disabled=not text_to_speak.strip()):
        generate_voice_from_text(text_to_speak, use_premium, session_manager)
    
    # Show generated audio files
    if st.session_state.get('generated_audio'):
        st.markdown("**Generated Audio Files:**")
        
        for filename, audio_info in st.session_state.generated_audio.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.audio(audio_info['path'])
                st.caption(f"🎵 {filename}")
                st.text(f"Text: {audio_info['text'][:50]}...")
            
            with col2:
                # Download button
                with open(audio_info['path'], 'rb') as audio_file:
                    st.download_button(
                        "💾 Download",
                        audio_file.read(),
                        file_name=filename,
                        mime="audio/mpeg",
                        key=f"download_{filename}"
                    )


def generate_voice_from_text(text: str, use_premium: bool, session_manager: 'SessionManager'):
    """Generate voice from text using AI"""
    
    try:
        with st.spinner("🎵 Generating voice..."):
            # Prepare request
            request_data = {
                "text": text,
                "use_premium_voice": use_premium,
                "language": st.session_state.get('voice_language', 'en')
            }
            
            if use_premium:
                request_data["voice_id"] = st.session_state.get('selected_voice')
            
            # Make API request
            response = requests.post(
                ENDPOINTS['generate_voice'],
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                audio_file = result.get('audio_file')
                
                if audio_file and os.path.exists(audio_file):
                    # Store in session state
                    if 'generated_audio' not in st.session_state:
                        st.session_state.generated_audio = {}
                    
                    filename = os.path.basename(audio_file)
                    st.session_state.generated_audio[filename] = {
                        'path': audio_file,
                        'text': text,
                        'premium': use_premium
                    }
                    
                    # Add to chat history
                    session_manager.add_message(
                        "user",
                        f"[Voice Generation Request] {text[:50]}...",
                        {"type": "voice_generation", "text": text}
                    )
                    
                    session_manager.add_message(
                        "assistant",
                        f"🔊 **Voice Generated Successfully!**\n\nYour text has been converted to speech.",
                        {
                            "tool_called": "generate_voice_response",
                            "audio_file": audio_file,
                            "premium_used": use_premium
                        }
                    )
                    
                    st.success("✅ Voice generated successfully!")
                    st.rerun()
                    
                else:
                    st.error("Voice generation completed but file not found")
                    
            else:
                st.error(f"Voice generation failed: {response.status_code}")
                
    except Exception as e:
        st.error(f"Error generating voice: {str(e)}")