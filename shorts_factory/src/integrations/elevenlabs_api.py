"""
ElevenLabs Text-to-Speech Integration for Shorts Factory
Converts generated scripts into natural-sounding MP3 audio files
"""

import requests
import logging
from typing import Optional, Dict, List
from pathlib import Path
import json
from datetime import datetime
import os

from security.secure_config import config


class ElevenLabsTextToSpeech:
    """Handles text-to-speech conversion using ElevenLabs API"""
    
    def __init__(self):
        """Initialize ElevenLabs TTS client"""
        self.logger = logging.getLogger(__name__)
        self.api_key = config.elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Voice configuration
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - natural, versatile
        self.voice_settings = {
            "stability": 0.75,      # Balance between stability and variability
            "similarity_boost": 0.75,  # How similar to the original voice
            "style": 0.20,          # Style exaggeration (subtle)
            "use_speaker_boost": True,  # Enhance speaker clarity
            "speaking_rate": 1.1    # 10% faster speech for better engagement
        }
        
        # Audio settings
        self.model_id = "eleven_multilingual_v2"  # High quality multilingual model
        self.output_format = "mp3_44100_128"  # High quality MP3
        
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
    
    def get_available_voices(self) -> List[Dict]:
        """
        Get list of available voices from ElevenLabs
        
        Returns:
            List of voice dictionaries with id, name, and properties
        """
        try:
            self.logger.info("🎤 Fetching available voices from ElevenLabs...")
            
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }
            
            response = requests.get(
                f"{self.base_url}/voices",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                voices_data = response.json()
                voices = voices_data.get('voices', [])
                
                self.logger.info(f"✅ Found {len(voices)} available voices")
                
                # Return simplified voice info
                return [
                    {
                        'id': voice['voice_id'],
                        'name': voice['name'],
                        'category': voice.get('category', 'Unknown'),
                        'description': voice.get('description', ''),
                        'preview_url': voice.get('preview_url', '')
                    }
                    for voice in voices
                ]
            else:
                self.logger.error(f"❌ Failed to fetch voices: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error fetching voices: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test ElevenLabs API connection and authentication"""
        try:
            self.logger.info("🧪 Testing ElevenLabs API connection...")
            
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }
            
            # Test with user info endpoint (lightweight)
            response = requests.get(
                f"{self.base_url}/user",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                self.logger.info(f"✅ ElevenLabs API connection successful")
                self.logger.info(f"📊 Character quota: {user_info.get('subscription', {}).get('character_count', 'Unknown')}")
                return True
            elif response.status_code == 401:
                self.logger.error("❌ ElevenLabs API authentication failed - check API key")
                return False
            else:
                self.logger.error(f"❌ ElevenLabs API connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ ElevenLabs API connection test failed: {e}")
            return False
    
    def preprocess_text_for_tts(self, text: str) -> str:
        """
        Preprocess text for natural TTS narration
        
        Args:
            text: Raw script text
            
        Returns:
            Processed text optimized for natural speech
        """
        import re
        
        # Remove extra whitespace
        processed = ' '.join(text.split())
        
        # Fix common punctuation issues that cause weird pauses
        processed = re.sub(r'\s*\*\s*', ' ', processed)  # Remove asterisks
        processed = re.sub(r'\s*-\s*', ' - ', processed)  # Normalize dashes
        processed = re.sub(r'\s*&\s*', ' and ', processed)  # Replace & with 'and'
        processed = re.sub(r'\s*\+\s*', ' plus ', processed)  # Replace + with 'plus'
        
        # Fix sentence endings for natural flow
        processed = re.sub(r'[.]{2,}', '.', processed)  # Multiple periods to single
        processed = re.sub(r'[!]{2,}', '!', processed)  # Multiple exclamations to single
        processed = re.sub(r'[?]{2,}', '?', processed)  # Multiple questions to single
        
        # Ensure proper spacing after punctuation
        processed = re.sub(r'([.!?])\s*', r'\1 ', processed)
        processed = re.sub(r'([,:;])\s*', r'\1 ', processed)
        
        # Remove parenthetical content that might cause pauses
        processed = re.sub(r'\([^)]*\)', '', processed)
        processed = re.sub(r'\[[^\]]*\]', '', processed)
        
        # Clean up multiple spaces
        processed = re.sub(r'\s{2,}', ' ', processed)
        
        # Remove leading/trailing whitespace
        processed = processed.strip()
        
        self.logger.debug(f"🎙️ Preprocessed text: {processed[:100]}...")
        return processed
    
    def generate_audio_from_text(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        filename_prefix: str = "audio"
    ) -> Optional[str]:
        """
        Generate audio from text using ElevenLabs TTS
        
        Args:
            text: The script text to convert to audio
            voice_id: Voice ID to use (defaults to Rachel)
            filename_prefix: Prefix for the generated audio file
            
        Returns:
            Path to the generated audio file or None if failed
        """
        try:
            if not text or not text.strip():
                self.logger.error("❌ No text provided for audio generation")
                return None
            
            # FIXED: Preprocess text for natural narration
            processed_text = self.preprocess_text_for_tts(text)
            
            if not processed_text:
                self.logger.error("❌ Text preprocessing resulted in empty text")
                return None
            
            voice_id = voice_id or self.default_voice_id
            
            self.logger.info(f"🎙️ Generating audio from text ({len(processed_text)} chars processed, {len(text)} chars original)...")
            self.logger.info(f"🎤 Using voice ID: {voice_id}")
            
            # Prepare API request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": processed_text,  # FIXED: Use preprocessed text
                "model_id": self.model_id,
                "voice_settings": self.voice_settings,
                "output_format": self.output_format
            }
            
            # Make API request
            self.logger.debug(f"📡 Making TTS request to: {url}")
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=60  # Longer timeout for audio generation
            )
            
            if response.status_code == 200:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename_prefix}_{timestamp}.mp3"
                audio_path = self.audio_directory / filename
                
                # Save audio file
                with open(audio_path, 'wb') as audio_file:
                    audio_file.write(response.content)
                
                # Verify file was created and has reasonable size
                if audio_path.exists() and audio_path.stat().st_size > 1000:  # At least 1KB
                    file_size_kb = audio_path.stat().st_size / 1024
                    self.logger.info(f"✅ Audio generated successfully: {filename} ({file_size_kb:.1f} KB)")
                    return str(audio_path)
                else:
                    self.logger.error(f"❌ Generated audio file is invalid or too small")
                    return None
                    
            elif response.status_code == 400:
                error_detail = response.json().get('detail', 'Bad request')
                self.logger.error(f"❌ Audio generation failed - Bad request: {error_detail}")
                return None
            elif response.status_code == 401:
                self.logger.error("❌ Audio generation failed - Authentication error")
                return None
            elif response.status_code == 429:
                self.logger.error("❌ Audio generation failed - Rate limit exceeded")
                return None
            else:
                self.logger.error(f"❌ Audio generation failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error generating audio: {e}")
            return None
    
    def generate_audio_for_content(
        self, 
        content_id: str, 
        script_text: str,
        voice_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate audio for a specific content item
        
        Args:
            content_id: Unique identifier for the content
            script_text: The script to convert to audio
            voice_id: Voice to use (optional)
            
        Returns:
            Path to generated audio file or None if failed
        """
        try:
            if not content_id or not script_text:
                self.logger.error("❌ Content ID and script text are required")
                return None
            
            self.logger.info(f"🎬 Generating audio for content ID: {content_id}")
            
            # Create filename with content ID
            filename_prefix = f"content_{content_id}"
            
            # Generate audio
            audio_path = self.generate_audio_from_text(
                text=script_text,
                voice_id=voice_id,
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
    
    def get_audio_info(self, audio_path: str) -> Dict[str, any]:
        """Get information about a generated audio file"""
        try:
            path = Path(audio_path)
            if not path.exists():
                return {'error': 'File not found'}
            
            stat = path.stat()
            return {
                'filename': path.name,
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 1),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': True
            }
            
        except Exception as e:
            return {'error': str(e), 'exists': False}
    
    def get_generation_stats(self) -> Dict[str, any]:
        """Get statistics about audio generation capabilities and usage"""
        try:
            audio_files = list(self.audio_directory.glob("*.mp3"))
            total_size = sum(f.stat().st_size for f in audio_files if f.exists())
            
            return {
                'audio_directory': str(self.audio_directory),
                'total_audio_files': len(audio_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'default_voice_id': self.default_voice_id,
                'model_id': self.model_id,
                'output_format': self.output_format,
                'voice_settings': self.voice_settings,
                'api_endpoint': f"{self.base_url}/text-to-speech",
                'status': 'operational' if self.api_key else 'needs_api_key'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
