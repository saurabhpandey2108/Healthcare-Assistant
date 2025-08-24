"""
Audio Processing Module for SAFESPACE AI AGENT

This module handles all audio-related functionality including:
- Audio recording from microphone
- Audio file format conversion
- Speech-to-text transcription
- Text-to-speech synthesis
- Audio playback utilities
"""

import os
import tempfile
import threading
import time
from typing import Optional, Tuple
import wave
import pyaudio
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import ffmpeg
from groq import Groq
from gtts import gTTS
import pygame

# ElevenLabs import with error handling
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings
except ImportError:
    try:
        from elevenlabs import Voice, VoiceSettings, generate, save
    except ImportError:
        # Fallback if ElevenLabs is not available
        Voice = None
        VoiceSettings = None
        generate = None
        save = None
        ElevenLabs = None

from backend.config import (
    GROQ_API_KEY,
    ELEVENLABS_API_KEY,
    OPENAI_API_KEY,
    AUDIO_SAMPLE_RATE,
    AUDIO_CHUNK_SIZE,
    AUDIO_FORMAT
)


class AudioProcessor:
    """
    Comprehensive audio processing class for handling all audio operations
    in the SAFESPACE AI AGENT system.
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        except ImportError:
            self.openai_client = None
            
        self.sample_rate = AUDIO_SAMPLE_RATE
        self.chunk_size = AUDIO_CHUNK_SIZE
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Initialize PyAudio
        self.audio_interface = pyaudio.PyAudio()
        
    def __del__(self):
        """Clean up audio resources."""
        if hasattr(self, 'audio_interface'):
            self.audio_interface.terminate()
    
    def record_audio(self, duration: float = 5.0, filename: Optional[str] = None) -> str:
        """
        Record audio from the default microphone.
        
        Args:
            duration: Recording duration in seconds
            filename: Output filename (if None, creates temp file)
            
        Returns:
            Path to the recorded audio file
        """
        if filename is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            filename = temp_file.name
            temp_file.close()
        
        try:
            # Open audio stream
            stream = self.audio_interface.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print(f"Recording audio for {duration} seconds...")
            frames = []
            
            # Record audio
            for _ in range(int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size)
                frames.append(data)
            
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            
            # Save recording to file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio_interface.get_sample_size(self.audio_format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            print(f"Audio recorded successfully: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
    
    def convert_audio_format(self, input_file: str, output_format: str = "wav") -> str:
        """
        Convert audio file to specified format using ffmpeg.
        
        Args:
            input_file: Path to input audio file
            output_format: Target format (wav, mp3, flac, etc.)
            
        Returns:
            Path to converted audio file
        """
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False)
            output_file = temp_file.name
            temp_file.close()
            
            # Use ffmpeg to convert audio
            (
                ffmpeg
                .input(input_file)
                .output(output_file, ar=self.sample_rate, ac=self.channels)
                .overwrite_output()
                .run(quiet=True)
            )
            
            return output_file
            
        except Exception as e:
            print(f"Error converting audio format: {e}")
            return input_file  # Return original file if conversion fails
    
    def transcribe_with_groq(self, audio_file: str) -> str:
        """
        Transcribe audio file using available AI services (OpenAI Whisper first, then GROQ as fallback).
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        # Try OpenAI Whisper first (preferred for accuracy)
        if self.openai_client and OPENAI_API_KEY:
            try:
                with open(audio_file, "rb") as file:
                    transcription = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=file,
                        language="en"  # Can be made configurable
                    )
                return transcription.text.strip()
            except Exception as e:
                print(f"OpenAI Whisper failed, trying GROQ: {e}")
        
        # Fallback to GROQ Whisper
        if self.groq_client:
            try:
                with open(audio_file, "rb") as file:
                    transcription = self.groq_client.audio.transcriptions.create(
                        file=(audio_file, file.read()),
                        model="whisper-large-v3",
                        language="en"  # Can be made configurable
                    )
                return transcription.text.strip()
            except Exception as e:
                print(f"Error with GROQ transcription: {e}")
        
        # Final fallback to speech_recognition
        return self._transcribe_with_speech_recognition(audio_file)
    
    def _transcribe_with_speech_recognition(self, audio_file: str) -> str:
        """
        Fallback transcription using speech_recognition library.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text.strip()
                
        except sr.UnknownValueError:
            return "I couldn't understand the audio. Please speak clearly and try again."
        except sr.RequestError as e:
            return f"Could not request results from speech recognition service: {e}"
        except Exception as e:
            return f"Error during transcription: {e}"
    
    def text_to_speech_gtts(self, text: str, language: str = 'en', slow: bool = False) -> str:
        """
        Convert text to speech using Google Text-to-Speech.
        
        Args:
            text: Text to convert
            language: Language code
            slow: Whether to speak slowly
            
        Returns:
            Path to generated audio file
        """
        try:
            tts = gTTS(text=text, lang=language, slow=slow)
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            tts.save(temp_file.name)
            return temp_file.name
            
        except Exception as e:
            print(f"Error with gTTS: {e}")
            return None
    
    def text_to_speech_elevenlabs(self, text: str, voice_id: str = "pNInz6obpgDQGcFmaJgB") -> str:
        """
        Convert text to speech using ElevenLabs API.
        
        Args:
            text: Text to convert
            voice_id: ElevenLabs voice ID (default is a warm, empathetic voice)
            
        Returns:
            Path to generated audio file
        """
        if not ELEVENLABS_API_KEY:
            return self.text_to_speech_gtts(text)
        
        try:
            # Try newer ElevenLabs client
            if ElevenLabs:
                client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                audio = client.generate(
                    text=text,
                    voice=voice_id,
                    model="eleven_monolingual_v1"
                )
            # Fallback to older API if available
            elif generate and Voice and VoiceSettings:
                audio = generate(
                    text=text,
                    voice=Voice(
                        voice_id=voice_id,
                        settings=VoiceSettings(
                            stability=0.71,
                            similarity_boost=0.5,
                            style=0.0,
                            use_speaker_boost=True
                        )
                    ),
                    api_key=ELEVENLABS_API_KEY
                )
            else:
                # ElevenLabs not available, use gTTS
                return self.text_to_speech_gtts(text)
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            
            # Save audio to file
            if hasattr(audio, 'content'):
                # For newer API
                with open(temp_file.name, 'wb') as f:
                    f.write(audio.content)
            elif save and callable(save):
                # For older API
                save(audio, temp_file.name)
            else:
                # Direct bytes
                with open(temp_file.name, 'wb') as f:
                    f.write(audio)
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error with ElevenLabs: {e}")
            return self.text_to_speech_gtts(text)  # Fallback to gTTS
    
    def play_audio(self, audio_file: str) -> bool:
        """
        Play audio file using pygame.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            return True
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
    
    def record_and_transcribe(self, duration: float = 5.0) -> Tuple[str, str]:
        """
        Record audio and transcribe it in one operation.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Tuple of (audio_file_path, transcribed_text)
        """
        audio_file = self.record_audio(duration)
        if audio_file:
            transcribed_text = self.transcribe_with_groq(audio_file)
            return audio_file, transcribed_text
        return None, "Recording failed"
    
    def get_audio_info(self, audio_file: str) -> dict:
        """
        Get information about an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with audio file information
        """
        try:
            audio = AudioSegment.from_file(audio_file)
            return {
                "duration": len(audio) / 1000,  # Duration in seconds
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "format": audio_file.split('.')[-1],
                "file_size": os.path.getsize(audio_file)
            }
        except Exception as e:
            return {"error": f"Could not analyze audio file: {e}"}


# Global audio processor instance
audio_processor = AudioProcessor()