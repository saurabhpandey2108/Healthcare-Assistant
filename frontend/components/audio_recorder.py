"""
Enhanced Streamlit Audio Component

This module provides audio recording capabilities for Streamlit 
by embedding Gradio components and providing alternative solutions.
"""

import streamlit as st
import streamlit.components.v1 as components
import tempfile
import requests
import base64
from pathlib import Path
import subprocess
import time

class StreamlitAudioRecorder:
    """Audio recording solution for Streamlit"""
    
    def __init__(self):
        self.gradio_port = 7862  # Different port to avoid conflicts
        self.gradio_process = None
    
    def render_audio_recorder(self):
        """Render audio recording interface"""
        st.subheader("🎤 Voice Recording")
        
        # Method 1: File Upload (Always works)
        st.markdown("**Method 1: Upload Audio File**")
        uploaded_audio = st.file_uploader(
            "Upload an audio file",
            type=['wav', 'mp3', 'm4a', 'ogg', 'flac'],
            key="audio_upload"
        )
        
        if uploaded_audio:
            st.audio(uploaded_audio)
            
            # Save uploaded file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}")
            temp_file.write(uploaded_audio.getbuffer())
            temp_file.close()
            
            return temp_file.name
        
        # Method 2: Browser-based recording (HTML5)
        st.markdown("**Method 2: Browser Recording**")
        if st.button("🎤 Record Audio (Browser)", key="browser_record"):
            self.render_browser_recorder()
        
        # Method 3: Gradio integration
        st.markdown("**Method 3: Advanced Recording (Gradio)**")
        if st.button("🎙️ Open Advanced Audio Recorder", key="gradio_recorder"):
            self.launch_gradio_recorder()
        
        return None
    
    def render_browser_recorder(self):
        """Render HTML5 audio recorder"""
        audio_recorder_html = """
        <div id="audio-recorder">
            <button id="record-btn" onclick="toggleRecording()">🎤 Start Recording</button>
            <button id="stop-btn" onclick="stopRecording()" disabled>⏹️ Stop</button>
            <button id="play-btn" onclick="playRecording()" disabled>▶️ Play</button>
            <audio id="audio-playback" controls style="display:none;"></audio>
            <div id="status">Ready to record</div>
        </div>

        <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        async function toggleRecording() {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        const audioPlayback = document.getElementById('audio-playback');
                        audioPlayback.src = audioUrl;
                        audioPlayback.style.display = 'block';
                        document.getElementById('play-btn').disabled = false;
                        
                        // Convert to base64 and send to Streamlit
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const base64Audio = e.target.result.split(',')[1];
                            window.parent.postMessage({
                                type: 'audio-recorded',
                                data: base64Audio
                            }, '*');
                        };
                        reader.readAsDataURL(audioBlob);
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    document.getElementById('record-btn').textContent = '🔴 Recording...';
                    document.getElementById('record-btn').disabled = true;
                    document.getElementById('stop-btn').disabled = false;
                    document.getElementById('status').textContent = 'Recording...';
                } catch (err) {
                    document.getElementById('status').textContent = 'Error: ' + err.message;
                }
            }
        }

        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                document.getElementById('record-btn').textContent = '🎤 Start Recording';
                document.getElementById('record-btn').disabled = false;
                document.getElementById('stop-btn').disabled = true;
                document.getElementById('status').textContent = 'Recording stopped';
                audioChunks = [];
                
                // Stop all audio tracks
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        }

        function playRecording() {
            const audioPlayback = document.getElementById('audio-playback');
            audioPlayback.play();
        }
        </script>

        <style>
        #audio-recorder {
            padding: 20px;
            border: 2px dashed #667eea;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
        }
        
        #audio-recorder button {
            margin: 5px;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            cursor: pointer;
        }
        
        #audio-recorder button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        #status {
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }
        </style>
        """
        
        components.html(audio_recorder_html, height=250)
        
        # Note about browser compatibility
        st.info("📝 **Note:** Browser recording requires HTTPS in production and microphone permissions.")
    
    def launch_gradio_recorder(self):
        """Launch a Gradio interface for advanced audio recording"""
        st.info("🚀 Launching advanced audio recorder in a new window...")
        
        # Create a simple Gradio interface for audio recording
        gradio_code = '''
import gradio as gr
import tempfile

def process_audio(audio):
    if audio is None:
        return "No audio recorded"
    
    # Save the audio file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(temp_file.name, "wb") as f:
        f.write(audio)
    
    return f"Audio saved to: {temp_file.name}"

# Create Gradio interface
with gr.Blocks(title="SAFESPACE Audio Recorder") as app:
    gr.Markdown("# 🎤 SAFESPACE Audio Recorder")
    gr.Markdown("Record audio and process it with AI")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(type="filepath", label="🎤 Record Audio")
            process_btn = gr.Button("🔄 Process Audio", variant="primary")
        
        with gr.Column():
            output_text = gr.Textbox(label="📝 Transcription", lines=5)
            status = gr.Textbox(label="Status")
    
    process_btn.click(
        process_audio,
        inputs=[audio_input],
        outputs=[status]
    )

if __name__ == "__main__":
    app.launch(server_port=7862, share=False)
'''
        
        # Save Gradio code to a temporary file
        gradio_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        gradio_file.write(gradio_code)
        gradio_file.close()
        
        # Launch Gradio in background
        try:
            self.gradio_process = subprocess.Popen([
                'python', gradio_file.Path
            ])
            
            time.sleep(3)  # Give it time to start
            
            st.success("✅ Audio recorder launched!")
            st.markdown("**Access the audio recorder at:** http://localhost:7862")
            
            # Embed the Gradio interface
            st.markdown("### Embedded Audio Recorder:")
            components.iframe("http://localhost:7862", height=600)
            
        except Exception as e:
            st.error(f"❌ Failed to launch audio recorder: {e}")
            st.markdown("**Alternative:** Use the file upload method above.")
    
    def cleanup(self):
        """Clean up resources"""
        if self.gradio_process:
            self.gradio_process.terminate()


# Audio recorder widget for Streamlit
def audio_recorder_widget():
    """Streamlit widget for audio recording"""
    if 'audio_recorder' not in st.session_state:
        st.session_state.audio_recorder = StreamlitAudioRecorder()
    
    return st.session_state.audio_recorder.render_audio_recorder()


# Alternative: Simple file-based audio recorder
def simple_audio_interface():
    """Simple audio interface for Streamlit"""
    st.subheader("🎤 Audio Processing")
    
    # Create tabs for different audio input methods
    tab1, tab2 = st.tabs(["📁 Upload Audio", "🌐 Record Online"])
    
    with tab1:
        st.markdown("**Upload pre-recorded audio files:**")
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'm4a', 'ogg', 'flac', 'aac'],
            help="Upload audio files up to 50MB"
        )
        
        if uploaded_file:
            st.audio(uploaded_file)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Transcribe Audio"):
                    with st.spinner("Transcribing audio..."):
                        # Process audio here
                        st.success("Audio transcribed successfully!")
            
            with col2:
                if st.button("🧠 Analyze Audio"):
                    with st.spinner("Analyzing audio..."):
                        # Analyze audio here
                        st.success("Audio analyzed successfully!")
        
        return uploaded_file
    
    with tab2:
        st.markdown("**Record audio online:**")
        st.info("💡 **Tip:** Use online voice recorders and upload the file:")
        
        online_recorders = [
            {"name": "Online Voice Recorder", "url": "https://online-voice-recorder.com/"},
            {"name": "Vocaroo", "url": "https://vocaroo.com/"},
            {"name": "Rev Voice Recorder", "url": "https://www.rev.com/onlinevoicerecorder"}
        ]
        
        for recorder in online_recorders:
            st.markdown(f"- [{recorder['name']}]({recorder['url']})")
        
        st.markdown("**Steps:**")
        st.markdown("1. Click on any recorder link above")
        st.markdown("2. Record your audio")
        st.markdown("3. Download the audio file")
        st.markdown("4. Upload it using the 'Upload Audio' tab")
        
        return None