"""
OpenAI Text-to-Speech Integration for Shorts Factory
Superior alternative to ElevenLabs with more natural speech and better pricing
"""

import openai
import logging
from typing import Optional, Dict, List
from pathlib import Path
import json
from datetime import datetime
import os
import re

from core.config import config


class OpenAITextToSpeech:
    """
    OpenAI TTS integration for natural, cost-effective voice generation
    Advantages over ElevenLabs:
    - More natural speech patterns
    - Better punctuation handling
    - Consistent pacing
    - Lower cost ($15/1M characters vs ElevenLabs $11-99/month)
    - No unnatural pauses
    """
    
    def __init__(self):
        """Initialize OpenAI TTS client"""
        self.logger = logging.getLogger(__name__)
        try:
            # Initialize OpenAI client with explicit API key (avoid environment issues)
            self.client = openai.OpenAI(
                api_key=config.openai_api_key
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            self.client = None
        
        # Voice configuration (OpenAI TTS voices)
        self.default_voice = "nova"  # Natural, engaging female voice
        self.available_voices = {
            "nova": "Young female voice, good for engaging content",
            "alloy": "Neutral voice, professional",
            "echo": "Male voice, warm and friendly", 
            "fable": "British accent, sophisticated",
            "onyx": "Deep male voice, authoritative",
            "shimmer": "Soft female voice, calming"
        }
        
        # Audio settings
        self.model = "tts-1-hd"  # High quality model
        self.output_format = "mp3"  # MP3 format
        self.speed = 1.1  # 10% faster for better engagement (0.25 - 4.0)
        
        # File management
        self.audio_directory = Path(config.working_directory) / "audio"
        self.ensure_audio_directory()
    
    def ensure_audio_directory(self):
        """Ensure the audio output directory exists"""
        try:
            self.audio_directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Audio directory ready: {self.audio_directory}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create audio directory: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test connection to OpenAI TTS API"""
        try:
            if not self.client:
                self.logger.error("❌ OpenAI client not initialized")
                return False
                
            # Test with a short phrase
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.default_voice,
                input="Test connection.",
                response_format=self.output_format
            )
            
            self.logger.info("✅ OpenAI TTS connection successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI TTS connection failed: {e}")
            return False
    
    def preprocess_text_for_natural_speech(self, text: str) -> str:
        """
        Minimal preprocessing for natural speech
        OpenAI TTS handles punctuation better than ElevenLabs
        """
        # Basic cleanup only
        processed = ' '.join(text.split())  # Normalize whitespace
        
        # Fix obvious issues without being aggressive
        processed = re.sub(r'([.!?])\s*([a-zA-Z])', r'\1 \2', processed)  # Ensure space after punctuation
        processed = re.sub(r'\s{2,}', ' ', processed)  # Remove multiple spaces
        processed = processed.strip()
        
        self.logger.debug(f"🎙️ Minimal preprocessing: {len(text)} → {len(processed)} chars")
        return processed
    
    def generate_audio_from_text(
        self, 
        text: str, 
        voice: Optional[str] = None,
        filename_prefix: str = "audio"
    ) -> Optional[str]:
        """
        Generate audio from text using OpenAI TTS
        
        Args:
            text: The script text to convert to audio
            voice: Voice to use (defaults to nova)
            filename_prefix: Prefix for the generated audio file
            
        Returns:
            Path to the generated audio file or None if failed
        """
        try:
            if not text or not text.strip():
                self.logger.error("❌ No text provided for audio generation")
                return None
            
            # Preprocess text for natural speech
            processed_text = self.preprocess_text_for_natural_speech(text)
            
            if not processed_text:
                self.logger.error("❌ Text preprocessing resulted in empty text")
                return None
            
            voice = voice or self.default_voice
            
            self.logger.info(f"🎙️ Generating audio with OpenAI TTS...")
            self.logger.info(f"🎤 Voice: {voice} ({self.available_voices.get(voice, 'Unknown')})")
            self.logger.info(f"📝 Text length: {len(processed_text)} characters")
            
            # Generate audio using OpenAI TTS
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=processed_text,
                response_format=self.output_format,
                speed=self.speed
            )
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.mp3"
            output_path = self.audio_directory / filename
            
            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Get file size
            file_size = output_path.stat().st_size
            size_kb = file_size / 1024
            
            self.logger.info(f"✅ Audio generated successfully: {filename} ({size_kb:.1f} KB)")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate audio: {e}")
            return None
    
    def generate_audio_for_content(
        self, 
        content_id: str, 
        script_text: str, 
        voice: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate audio for a content item with specific naming
        
        Args:
            content_id: Unique identifier for the content
            script_text: Script text to convert to audio
            voice: Voice to use for generation
            
        Returns:
            Path to generated audio file or None if failed
        """
        try:
            if not content_id or not script_text:
                self.logger.error("❌ Content ID and script text are required")
                return None
            
            self.logger.info(f"🎬 Generating audio for content ID: {content_id}")
            
            # Create filename with content ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_prefix = f"content_{content_id}_{timestamp}"
            
            # Generate audio
            audio_path = self.generate_audio_from_text(
                text=script_text,
                voice=voice,
                filename_prefix=filename_prefix
            )
            
            if audio_path:
                self.logger.info(f"🎉 Audio generation complete for content {content_id}")
                return audio_path
            else:
                self.logger.error(f"❌ Audio generation failed for content {content_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error generating audio for content {content_id}: {e}")
            return None
    
    def get_audio_info(self, audio_file_path: str) -> Dict:
        """
        Get information about an audio file
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary with audio file information
        """
        try:
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                return {"error": "File not found"}
            
            file_size = audio_path.stat().st_size
            
            return {
                "filename": audio_path.name,
                "size_bytes": file_size,
                "size_kb": file_size / 1024,
                "size_mb": file_size / (1024 * 1024),
                "format": "mp3",
                "created": datetime.fromtimestamp(audio_path.stat().st_ctime).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting audio info: {e}")
            return {"error": str(e)}
    
    def get_estimated_cost(self, text: str) -> float:
        """
        Estimate cost for text-to-speech generation
        OpenAI TTS pricing: $15.00 per 1M characters
        
        Args:
            text: Text to be converted
            
        Returns:
            Estimated cost in USD
        """
        char_count = len(text)
        cost_per_char = 15.00 / 1_000_000  # $15 per million characters
        estimated_cost = char_count * cost_per_char
        
        return estimated_cost
