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
from datetime import datetime

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
    tab1, tab2, tab3, tab4 = st.tabs(["📷 Images", "🎤 Audio", "🔊 Voice", "📊 Manage"])
    
    with tab1:
        render_image_upload_panel(session_manager)
    
    with tab2:
        render_audio_upload_panel(session_manager)
    
    with tab3:
        render_voice_generation_panel(session_manager)
    
    with tab4:
        render_multimodal_management_panel(session_manager)
    
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
    
    # Add option to not save images
    save_images = st.checkbox("Save images to knowledge base", value=True, help="Uncheck to analyze images without saving them permanently")
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            process_uploaded_image(uploaded_file, session_manager, save_to_kb=save_images)
    
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


def process_uploaded_image(uploaded_file, session_manager: 'SessionManager', save_to_kb: bool = True):
    """Process and save uploaded image"""
    
    # Check file size
    if uploaded_file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        st.error(f"File size exceeds {MAX_IMAGE_SIZE_MB}MB limit")
        return
    
    # Check if already exists in persistent storage
    persistent_images = session_manager.get_multimodal_images()
    if uploaded_file.name in persistent_images and save_to_kb:
        st.warning(f"🖼️ {uploaded_file.name} is already saved in your multimodal collection")
        return
    
    try:
        # Save to uploads directory (persistent storage)
        upload_dir = Path("uploads/images")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store in session state for immediate use
        if 'uploaded_images' not in st.session_state:
            st.session_state.uploaded_images = {}
        
        st.session_state.uploaded_images[uploaded_file.name] = {
            'path': str(file_path),
            'size': uploaded_file.size,
            'type': uploaded_file.type,
            'temporary': not save_to_kb
        }
        
        # Only add to persistent session storage if save_to_kb is True
        if save_to_kb:
            session_manager.add_multimodal_image(uploaded_file.name)
            
            # Add to chat history
            session_manager.add_message(
                "system",
                f"🖼️ **Image Added:** {uploaded_file.name} has been saved to your multimodal collection and is ready for analysis.",
                {
                    "type": "image_uploaded",
                    "filename": uploaded_file.name,
                    "file_path": str(file_path),
                    "size": uploaded_file.size
                }
            )
            
            st.success(f"✅ {uploaded_file.name} uploaded and saved permanently!")
        else:
            # Different message for temporary images
            st.success(f"✅ {uploaded_file.name} uploaded for temporary analysis (not saved to knowledge base)")
        
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
            
            # Prepare multipart form data
            if not os.path.exists(image_path):
                st.error(f"Image file not found: {image_path}")
                return
            
            # Read the image file
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': (os.path.basename(image_path), image_file, 'image/jpeg')
                }
                data = {
                    'query': query
                }
                
                # Make API request with multipart form data
                try:
                    response = requests.post(
                        ENDPOINTS['analyze_image'],
                        files=files,
                        data=data,
                        timeout=60  # Increased timeout
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
                                "image_path": image_path,
                                "confidence": result.get('confidence', 0.8),
                                "tools_used": result.get('tools_used', [])
                            }
                        )
                        
                        st.success("✅ Image analysis completed! Check the chat for results.")
                        
                        # Display quick preview of results
                        with st.expander("📊 Analysis Preview", expanded=True):
                            st.markdown(f"**Analysis:** {analysis[:200]}{'...' if len(analysis) > 200 else ''}")
                            
                            if result.get('emotional_indicators'):
                                st.markdown(f"**Emotional Indicators:** {', '.join(result['emotional_indicators'])}")
                            
                            if result.get('confidence'):
                                st.markdown(f"**Confidence:** {result['confidence']:.2%}")
                        
                        st.rerun()
                        
                    elif response.status_code == 422:
                        error_detail = response.json().get('detail', 'Validation error')
                        st.error(f"❌ Request format error: {error_detail}")
                        st.info("💡 Please try uploading the image again or contact support.")
                        
                    else:
                        st.error(f"❌ Analysis failed with status {response.status_code}")
                        try:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"Error details: {error_detail}")
                        except:
                            st.error(f"Response: {response.text[:200]}")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. The server may be busy processing the image. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the backend. Please check if the API server is running.")
                except Exception as e:
                    st.error(f"❌ Error during API request: {str(e)}")
                    st.info("💡 Please try again or contact support if the issue persists.")
                
    except Exception as e:
        st.error(f"❌ Error analyzing image: {str(e)}")
        st.info("💡 Please try again or contact support if the issue persists.")


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
    
    # Check if already exists in persistent storage
    persistent_audio = session_manager.get_multimodal_audio()
    if uploaded_file.name in persistent_audio:
        st.warning(f"🎤 {uploaded_file.name} is already saved in your multimodal collection")
        return
    
    try:
        # Save to uploads directory (persistent storage)
        upload_dir = Path("uploads/audio")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Add to persistent session storage
        session_manager.add_multimodal_audio(uploaded_file.name)
        
        # Store in session state for immediate use
        if 'uploaded_audio' not in st.session_state:
            st.session_state.uploaded_audio = {}
        
        st.session_state.uploaded_audio[uploaded_file.name] = {
            'path': str(file_path),
            'size': uploaded_file.size,
            'type': uploaded_file.type
        }
        
        # Add to chat history
        session_manager.add_message(
            "system",
            f"🎤 **Audio Added:** {uploaded_file.name} has been saved to your multimodal collection and is ready for processing.",
            {
                "type": "audio_uploaded",
                "filename": uploaded_file.name,
                "file_path": str(file_path),
                "size": uploaded_file.size
            }
        )
        
        st.success(f"✅ {uploaded_file.name} uploaded and saved permanently!")
        
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


def render_multimodal_management_panel(session_manager: 'SessionManager'):
    """Render multimodal content management panel"""
    
    st.subheader("📊 Multimodal Management")
    st.markdown("Manage your saved images and audio files across all conversations")
    
    # Sync existing files
    sync_existing_multimodal_files(session_manager)
    
    # Get current multimodal items
    persistent_images = session_manager.get_multimodal_images()
    persistent_audio = session_manager.get_multimodal_audio()
    
    # Statistics overview
    render_multimodal_statistics(persistent_images, persistent_audio)
    
    # Management tabs
    mgmt_tab1, mgmt_tab2 = st.tabs(["🖼️ Image Library", "🎤 Audio Library"])
    
    with mgmt_tab1:
        render_image_library_management(persistent_images, session_manager)
    
    with mgmt_tab2:
        render_audio_library_management(persistent_audio, session_manager)
    
    # Export and cleanup options
    st.markdown("---")
    render_multimodal_actions(session_manager)


def sync_existing_multimodal_files(session_manager: 'SessionManager'):
    """Sync existing multimodal files from uploads directories"""
    
    # Check for existing images
    image_dir = Path("uploads/images")
    if image_dir.exists():
        current_images = session_manager.get_multimodal_images()
        new_images = []
        
        for image_file in image_dir.glob("*"):
            if image_file.is_file() and image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                if image_file.name not in current_images:
                    session_manager.add_multimodal_image(image_file.name)
                    new_images.append(image_file.name)
        
        if new_images:
            with st.info(f"Found {len(new_images)} existing images in your library"):
                for img in new_images:
                    st.write(f"- {img}")
    
    # Check for existing audio
    audio_dir = Path("uploads/audio")
    if audio_dir.exists():
        current_audio = session_manager.get_multimodal_audio()
        new_audio = []
        
        for audio_file in audio_dir.glob("*"):
            if audio_file.is_file() and audio_file.suffix.lower() in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
                if audio_file.name not in current_audio:
                    session_manager.add_multimodal_audio(audio_file.name)
                    new_audio.append(audio_file.name)
        
        if new_audio:
            with st.info(f"Found {len(new_audio)} existing audio files in your library"):
                for audio in new_audio:
                    st.write(f"- {audio}")


def render_multimodal_statistics(persistent_images: set, persistent_audio: set):
    """Render multimodal content statistics"""
    
    with st.expander("📈 Multimodal Statistics", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Images", len(persistent_images))
        
        with col2:
            st.metric("Total Audio Files", len(persistent_audio))
        
        with col3:
            total_items = len(persistent_images) + len(persistent_audio)
            st.metric("Total Multimodal Items", total_items)
        
        # Storage information
        if persistent_images or persistent_audio:
            st.markdown("**Storage Information:**")
            
            # Calculate total storage size
            total_size = 0
            
            # Images
            image_size = 0
            for img in persistent_images:
                img_path = Path("uploads/images") / img
                if img_path.exists():
                    image_size += img_path.stat().st_size
            total_size += image_size
            
            # Audio
            audio_size = 0
            for audio in persistent_audio:
                audio_path = Path("uploads/audio") / audio
                if audio_path.exists():
                    audio_size += audio_path.stat().st_size
            total_size += audio_size
            
            if total_size > 0:
                st.markdown(f"- Total Storage: {total_size / (1024*1024):.1f} MB")
                if image_size > 0:
                    st.markdown(f"- Images: {image_size / (1024*1024):.1f} MB")
                if audio_size > 0:
                    st.markdown(f"- Audio: {audio_size / (1024*1024):.1f} MB")


def render_image_library_management(persistent_images: set, session_manager: 'SessionManager'):
    """Render image library management interface"""
    
    if persistent_images:
        st.markdown(f"**Saved Images ({len(persistent_images)}):**")
        
        # Search functionality
        search_query = st.text_input(
            "🔍 Search Images",
            placeholder="Search by filename...",
            key="image_search"
        )
        
        # Filter images based on search
        filtered_images = [img for img in persistent_images 
                          if search_query.lower() in img.lower()] if search_query else list(persistent_images)
        
        # Display images in grid
        cols_per_row = 3
        for i in range(0, len(filtered_images), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(filtered_images):
                    img_name = filtered_images[i + j]
                    img_path = Path("uploads/images") / img_name
                    
                    with col:
                        if img_path.exists():
                            st.image(str(img_path), caption=img_name, width=150)
                            
                            # Action buttons
                            if st.button(f"🔍 Analyze", key=f"analyze_lib_{img_name}"):
                                analyze_image(str(img_path), "emotional_analysis", "", session_manager)
                            
                            if st.button(f"🗑️ Remove", key=f"remove_lib_{img_name}"):
                                remove_multimodal_image(img_name, session_manager)
                        else:
                            st.warning(f"File not found: {img_name}")
                            if st.button(f"Clean Up", key=f"cleanup_{img_name}"):
                                session_manager.remove_multimodal_image(img_name)
                                st.rerun()
    else:
        st.info("🖼️ No images in your library yet. Upload some images to get started!")


def render_audio_library_management(persistent_audio: set, session_manager: 'SessionManager'):
    """Render audio library management interface"""
    
    if persistent_audio:
        st.markdown(f"**Saved Audio Files ({len(persistent_audio)}):**")
        
        # Search functionality
        search_query = st.text_input(
            "🔍 Search Audio Files",
            placeholder="Search by filename...",
            key="audio_search"
        )
        
        # Filter audio based on search
        filtered_audio = [audio for audio in persistent_audio 
                         if search_query.lower() in audio.lower()] if search_query else list(persistent_audio)
        
        # Display audio files
        for audio_name in filtered_audio:
            audio_path = Path("uploads/audio") / audio_name
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                if audio_path.exists():
                    st.audio(str(audio_path))
                    st.caption(f"🎤 {audio_name}")
                    
                    # File info
                    try:
                        file_size = audio_path.stat().st_size
                        st.text(f"Size: {file_size / 1024:.1f} KB")
                    except:
                        pass
                else:
                    st.warning(f"File not found: {audio_name}")
            
            with col2:
                if audio_path.exists():
                    if st.button(f"🎧 Process", key=f"process_lib_{audio_name}"):
                        process_audio_file(str(audio_path), False, session_manager)
            
            with col3:
                if st.button(f"🗑️ Remove", key=f"remove_aud_{audio_name}"):
                    remove_multimodal_audio(audio_name, session_manager)
                elif not audio_path.exists():
                    if st.button(f"Clean Up", key=f"cleanup_aud_{audio_name}"):
                        session_manager.remove_multimodal_audio(audio_name)
                        st.rerun()
    else:
        st.info("🎤 No audio files in your library yet. Upload some audio to get started!")


def render_multimodal_actions(session_manager: 'SessionManager'):
    """Render multimodal action buttons"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Library", use_container_width=True, help="Re-scan for files and sync library"):
            # Clear current multimodal items and re-sync
            active_chat_id = st.session_state.active_chat_id
            st.session_state.all_chats[active_chat_id]["multimodal_images"] = set()
            st.session_state.all_chats[active_chat_id]["multimodal_audio"] = set()
            sync_existing_multimodal_files(session_manager)
            st.success("Multimodal library refreshed!")
            st.rerun()
    
    with col2:
        if st.button("📤 Export Library Info", use_container_width=True):
            export_multimodal_library(session_manager)
    
    with col3:
        if st.button("🧹 Clean Library", use_container_width=True, help="Remove entries for missing files"):
            clean_multimodal_library(session_manager)


def remove_multimodal_image(image_name: str, session_manager: 'SessionManager'):
    """Remove image from multimodal library"""
    
    try:
        # Remove from session
        session_manager.remove_multimodal_image(image_name)
        
        # Try to delete physical file
        img_path = Path("uploads/images") / image_name
        if img_path.exists():
            img_path.unlink()
        
        # Remove from session state if present
        if 'uploaded_images' in st.session_state and image_name in st.session_state.uploaded_images:
            del st.session_state.uploaded_images[image_name]
        
        # Add removal message to chat
        session_manager.add_message(
            "system",
            f"🗑️ **Image Removed:** {image_name} has been removed from your multimodal library.",
            {"type": "image_removed", "filename": image_name}
        )
        
        st.success(f"✅ Successfully removed {image_name}")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error removing image: {str(e)}")


def remove_multimodal_audio(audio_name: str, session_manager: 'SessionManager'):
    """Remove audio from multimodal library"""
    
    try:
        # Remove from session
        session_manager.remove_multimodal_audio(audio_name)
        
        # Try to delete physical file
        audio_path = Path("uploads/audio") / audio_name
        if audio_path.exists():
            audio_path.unlink()
        
        # Remove from session state if present
        if 'uploaded_audio' in st.session_state and audio_name in st.session_state.uploaded_audio:
            del st.session_state.uploaded_audio[audio_name]
        
        # Add removal message to chat
        session_manager.add_message(
            "system",
            f"🗑️ **Audio Removed:** {audio_name} has been removed from your multimodal library.",
            {"type": "audio_removed", "filename": audio_name}
        )
        
        st.success(f"✅ Successfully removed {audio_name}")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error removing audio: {str(e)}")


def export_multimodal_library(session_manager: 'SessionManager'):
    """Export multimodal library information"""
    
    persistent_images = session_manager.get_multimodal_images()
    persistent_audio = session_manager.get_multimodal_audio()
    active_chat = session_manager.get_active_chat()
    
    # Create export data
    export_data = {
        "chat_title": active_chat.get('title', 'Unknown'),
        "export_timestamp": str(datetime.now()),
        "total_images": len(persistent_images),
        "total_audio": len(persistent_audio),
        "images": list(persistent_images),
        "audio_files": list(persistent_audio)
    }
    
    # Convert to JSON
    import json
    export_json = json.dumps(export_data, indent=2)
    
    # Offer download
    st.download_button(
        label="💾 Download Multimodal Library Export",
        data=export_json,
        file_name=f"multimodal_library_export_{active_chat.get('title', 'chat').replace(' ', '_')}.json",
        mime="application/json"
    )


def clean_multimodal_library(session_manager: 'SessionManager'):
    """Clean up multimodal library by removing entries for missing files"""
    
    persistent_images = session_manager.get_multimodal_images()
    persistent_audio = session_manager.get_multimodal_audio()
    
    # Check images
    missing_images = []
    for img in list(persistent_images):
        img_path = Path("uploads/images") / img
        if not img_path.exists():
            session_manager.remove_multimodal_image(img)
            missing_images.append(img)
    
    # Check audio
    missing_audio = []
    for audio in list(persistent_audio):
        audio_path = Path("uploads/audio") / audio
        if not audio_path.exists():
            session_manager.remove_multimodal_audio(audio)
            missing_audio.append(audio)
    
    # Report results
    total_cleaned = len(missing_images) + len(missing_audio)
    if total_cleaned > 0:
        st.success(f"🧹 Cleaned {total_cleaned} missing file entries from library")
        
        if missing_images:
            st.info(f"Removed {len(missing_images)} missing images")
        if missing_audio:
            st.info(f"Removed {len(missing_audio)} missing audio files")
        
        st.rerun()
    else:
        st.info("✅ Library is already clean - no missing files found")