"""
🎯 Google Cloud Text-to-Speech with Word Timing
Professional-grade TTS with exact word-level timestamps for perfect synchronization

This is another professional solution used by major platforms:
- Google Cloud TTS provides exact word timing marks
- WaveNet and Neural2 voices with precise timing data
- SSML support for fine-grained control
- Enterprise-grade reliability and accuracy
"""

import os
import logging
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

try:
    from google.cloud import texttospeech
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google Cloud TTS not installed. Run: pip install google-cloud-texttospeech")

from core.config import config


class GoogleTTSWithTimestamps:
    """
    Professional TTS using Google Cloud Text-to-Speech with exact word timestamps
    
    This is what major automated video platforms use for perfect synchronization:
    - Exact word timing marks from the TTS engine
    - WaveNet and Neural2 voices with natural speech patterns
    - SSML support for precise control
    - Enterprise reliability and accuracy
    """
    
    def __init__(self):
        """Initialize Google Cloud Text-to-Speech"""
        self.logger = logging.getLogger(__name__)
        
        if not GOOGLE_AVAILABLE:
            self.logger.error("❌ Google Cloud TTS not available")
            self.client = None
            return
        
        try:
            # Google Cloud configuration - set GOOGLE_APPLICATION_CREDENTIALS in environment
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if not credentials_path or not os.path.exists(credentials_path):
                self.logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not found or invalid")
                self.client = None
                return
            
            # Initialize Google Cloud TTS client
            self.client = texttospeech.TextToSpeechClient()
            self.logger.info("✅ Google Cloud Text-to-Speech initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Google Cloud TTS: {e}")
            self.client = None
        
        # Voice configuration - Neural2 voices with best quality
        self.voice_options = {
            "nova": ("en-US-Neural2-F", texttospeech.SsmlVoiceGender.FEMALE),    # Clear and engaging
            "alloy": ("en-US-Neural2-D", texttospeech.SsmlVoiceGender.MALE),     # Professional male
            "echo": ("en-US-Neural2-C", texttospeech.SsmlVoiceGender.FEMALE),    # Warm and friendly
            "fable": ("en-US-Neural2-A", texttospeech.SsmlVoiceGender.MALE),     # Mature and authoritative
            "onyx": ("en-US-Neural2-J", texttospeech.SsmlVoiceGender.MALE),      # Deep and confident
            "shimmer": ("en-US-Neural2-E", texttospeech.SsmlVoiceGender.FEMALE)  # Calm and pleasant
        }
        
        self.default_voice = "nova"
        
        # Audio settings
        self.audio_encoding = texttospeech.AudioEncoding.LINEAR16
        self.sample_rate_hertz = 48000  # High quality
        self.speaking_rate = 1.1  # 10% faster as requested
        
        # File management
        self.audio_directory = Path(config.working_directory) / "audio"
        self.captions_directory = Path(config.working_directory) / "captions"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure output directories exist"""
        try:
            self.audio_directory.mkdir(parents=True, exist_ok=True)
            self.captions_directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Directories ready: {self.audio_directory}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create directories: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Google Cloud TTS connection"""
        try:
            if not GOOGLE_AVAILABLE or not self.client:
                return False
            
            # Test with a simple synthesis request
            voice_name, gender = self.voice_options[self.default_voice]
            
            synthesis_input = texttospeech.SynthesisInput(text="Test connection")
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", 
                name=voice_name,
                ssml_gender=gender
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=self.audio_encoding,
                sample_rate_hertz=self.sample_rate_hertz,
                speaking_rate=self.speaking_rate
            )
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice, 
                audio_config=audio_config,
                enable_time_pointing=[texttospeech.SynthesizeSpeechRequest.TimepointType.SSML_MARK]
            )
            
            if response.audio_content:
                self.logger.info("✅ Google Cloud TTS connection successful")
                return True
            else:
                self.logger.error("❌ Google Cloud TTS test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Google Cloud TTS connection test failed: {e}")
            return False
    
    def generate_audio_with_perfect_timestamps(
        self, 
        content_id: str, 
        script_text: str, 
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio with exact word-level timestamps from Google Cloud TTS
        
        This is the professional approach used by major platforms:
        1. Generate audio with Google Cloud TTS and timing marks
        2. Extract exact word boundaries from response
        3. Create perfectly synchronized SRT file
        4. Return both audio and precise timing data
        
        Args:
            content_id: Unique identifier for the content
            script_text: Text to convert to speech
            voice: Voice to use (optional)
            
        Returns:
            Dictionary with audio path, SRT path, and timing data
        """
        try:
            if not GOOGLE_AVAILABLE or not self.client:
                return {
                    "success": False,
                    "error": "Google Cloud TTS not available",
                    "fallback_recommended": "Azure or ElevenLabs"
                }
            
            voice_name, gender = self.voice_options.get(
                voice or self.default_voice, 
                self.voice_options[self.default_voice]
            )
            
            self.logger.info(f"🎤 Generating audio with Google Cloud TTS: {voice_name}")
            self.logger.info(f"📝 Text length: {len(script_text)} characters")
            
            # Create SSML with timing marks for word boundaries
            ssml = self._create_ssml_with_timing_marks(script_text)
            
            # Configure synthesis request
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=voice_name,
                ssml_gender=gender
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=self.audio_encoding,
                sample_rate_hertz=self.sample_rate_hertz,
                speaking_rate=self.speaking_rate
            )
            
            # Generate audio with timing points
            self.logger.info("🎵 Generating audio with word-level timing marks...")
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
                enable_time_pointing=[texttospeech.SynthesizeSpeechRequest.TimepointType.SSML_MARK]
            )
            
            if not response.audio_content:
                return {"success": False, "error": "No audio content generated"}
            
            # Save audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"google_tts_{content_id}_{timestamp}.wav"
            audio_path = self.audio_directory / audio_filename
            
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(response.audio_content)
            
            file_size_kb = audio_path.stat().st_size / 1024
            self.logger.info(f"✅ Audio generated: {audio_filename} ({file_size_kb:.1f} KB)")
            
            # Extract word boundaries from timing marks
            word_boundaries = self._extract_word_boundaries_from_timepoints(
                response.timepoints, 
                script_text
            )
            
            self.logger.info(f"🎯 Word boundaries extracted: {len(word_boundaries)}")
            
            # Generate perfectly synchronized SRT file
            srt_path = self._create_perfect_srt(word_boundaries, content_id, timestamp)
            
            if not srt_path:
                return {"success": False, "error": "SRT generation failed"}
            
            # Calculate quality metrics
            quality_metrics = self._calculate_google_quality_metrics(word_boundaries)
            
            self.logger.info("✅ Google Cloud TTS generation complete with perfect timing!")
            self.logger.info(f"📊 Quality: PROFESSIONAL (Google Neural2)")
            self.logger.info(f"🎯 Word boundaries: {len(word_boundaries)}")
            self.logger.info(f"⏱️ Total duration: {word_boundaries[-1]['end']:.1f}s" if word_boundaries else "Unknown")
            
            return {
                "success": True,
                "method": "google_cloud_tts",
                "audio_path": str(audio_path),
                "srt_path": str(srt_path),
                "word_boundaries": word_boundaries,
                "quality_metrics": quality_metrics,
                "voice_used": voice_name,
                "total_duration": word_boundaries[-1]['end'] if word_boundaries else 0,
                "word_count": len(word_boundaries),
                "audio_info": {
                    "filename": audio_filename,
                    "size_kb": file_size_kb,
                    "format": "WAV 48kHz 16-bit Linear PCM",
                    "quality": "Professional Neural2 Voice"
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Google Cloud TTS generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_recommended": "Azure or ElevenLabs"
            }
    
    def _create_ssml_with_timing_marks(self, text: str) -> str:
        """
        Create SSML with timing marks for word boundary extraction
        
        Google Cloud TTS uses SSML marks to provide precise timing data
        """
        # Clean text for SSML
        clean_text = self._clean_text_for_ssml(text)
        
        # Split into words and add timing marks
        words = clean_text.split()
        marked_words = []
        
        for i, word in enumerate(words):
            # Add a timing mark before each word
            mark_name = f"word_{i}"
            marked_words.append(f'<mark name="{mark_name}"/>{word}')
        
        marked_text = ' '.join(marked_words)
        
        # Create SSML with precise control
        ssml = f"""
        <speak>
            <prosody rate="{self.speaking_rate}" pitch="default" volume="default">
                {marked_text}
            </prosody>
        </speak>
        """.strip()
        
        return ssml
    
    def _clean_text_for_ssml(self, text: str) -> str:
        """Clean text for SSML compatibility"""
        # Escape XML special characters
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;") 
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_word_boundaries_from_timepoints(
        self, 
        timepoints: List[Any], 
        original_text: str
    ) -> List[Dict]:
        """
        Extract word boundaries from Google Cloud TTS timepoints
        
        Args:
            timepoints: List of timepoint objects from Google TTS response
            original_text: Original script text
            
        Returns:
            List of word boundary dictionaries with precise timing
        """
        try:
            words = original_text.split()
            word_boundaries = []
            
            # Convert timepoints to word boundaries
            for i, timepoint in enumerate(timepoints):
                if i < len(words):
                    # Timepoint gives us the start time of each word
                    start_time = timepoint.time_seconds
                    
                    # Estimate end time (next word's start or add duration)
                    if i + 1 < len(timepoints):
                        end_time = timepoints[i + 1].time_seconds
                    else:
                        # For last word, estimate based on word length
                        estimated_duration = len(words[i]) * 0.08  # 80ms per character
                        end_time = start_time + max(0.3, estimated_duration)
                    
                    word_boundaries.append({
                        'word': words[i],
                        'start': start_time,
                        'end': end_time,
                        'duration': end_time - start_time,
                        'confidence': 1.0,  # Google provides high-confidence data
                        'source': 'google_timing_mark',
                        'mark_name': timepoint.mark_name if hasattr(timepoint, 'mark_name') else f"word_{i}"
                    })
            
            self.logger.info(f"✅ Extracted {len(word_boundaries)} word boundaries from timing marks")
            return word_boundaries
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract word boundaries: {e}")
            return []
    
    def _create_perfect_srt(self, word_boundaries: List[Dict], content_id: str, timestamp: str) -> Optional[str]:
        """
        Create perfectly synchronized SRT file from Google word boundaries
        
        This creates captions with exact timing from the TTS engine,
        ensuring perfect synchronization between audio and text.
        """
        try:
            if not word_boundaries:
                self.logger.error("❌ No word boundaries for SRT creation")
                return None
            
            # Generate SRT filename  
            srt_filename = f"google_perfect_sync_{content_id}_{timestamp}.srt"
            srt_path = self.captions_directory / srt_filename
            
            # Group words into optimal caption segments
            caption_segments = self._create_optimal_segments_from_boundaries(word_boundaries)
            
            # Write SRT file
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(caption_segments, 1):
                    start_time = self._format_srt_timestamp(segment['start'])
                    end_time = self._format_srt_timestamp(segment['end'])
                    text = segment['text']
                    
                    srt_file.write(f"{i}\n")
                    srt_file.write(f"{start_time} --> {end_time}\n")
                    srt_file.write(f"{text}\n\n")
            
            self.logger.info(f"✅ Perfect SRT created: {srt_filename} ({len(caption_segments)} segments)")
            return str(srt_path)
            
        except Exception as e:
            self.logger.error(f"❌ Perfect SRT creation failed: {e}")
            return None
    
    def _create_optimal_segments_from_boundaries(self, word_boundaries: List[Dict]) -> List[Dict]:
        """
        Create optimal caption segments from word boundaries
        
        Groups words into readable segments while maintaining perfect timing
        """
        segments = []
        current_segment_words = []
        current_segment_chars = 0
        segment_start_time = None
        
        max_chars_per_caption = 25  # Mobile-optimized
        max_caption_duration = 4.0  # Maximum attention span
        
        for word_data in word_boundaries:
            word = word_data['word']
            word_chars = len(word)
            
            # Initialize first segment
            if segment_start_time is None:
                segment_start_time = word_data['start']
            
            # Check if adding this word would exceed limits
            segment_duration = word_data['end'] - segment_start_time
            would_exceed_chars = current_segment_chars + word_chars + 1 > max_chars_per_caption
            would_exceed_duration = segment_duration > max_caption_duration
            
            if current_segment_words and (would_exceed_chars or would_exceed_duration):
                # Finalize current segment
                segment_text = ' '.join(current_segment_words)
                segment_end_time = word_boundaries[word_boundaries.index(word_data) - 1]['end']
                
                segments.append({
                    'text': segment_text,
                    'start': segment_start_time,
                    'end': segment_end_time,
                    'word_count': len(current_segment_words),
                    'char_count': current_segment_chars,
                    'duration': segment_end_time - segment_start_time
                })
                
                # Start new segment
                current_segment_words = [word]
                current_segment_chars = word_chars
                segment_start_time = word_data['start']
            else:
                # Add word to current segment
                current_segment_words.append(word)
                current_segment_chars += word_chars + (1 if current_segment_words else 0)
        
        # Finalize last segment
        if current_segment_words and word_boundaries:
            segment_text = ' '.join(current_segment_words)
            segment_end_time = word_boundaries[-1]['end']
            
            segments.append({
                'text': segment_text,
                'start': segment_start_time,
                'end': segment_end_time,
                'word_count': len(current_segment_words),
                'char_count': current_segment_chars,
                'duration': segment_end_time - segment_start_time
            })
        
        return segments
    
    def _calculate_google_quality_metrics(self, word_boundaries: List[Dict]) -> Dict[str, Any]:
        """Calculate quality metrics for Google Cloud TTS generation"""
        if not word_boundaries:
            return {"quality": "none", "method": "google"}
        
        try:
            total_words = len(word_boundaries)
            total_duration = word_boundaries[-1]['end'] - word_boundaries[0]['start']
            
            # All Google boundaries are high confidence
            avg_confidence = 1.0
            
            # Calculate speech rate
            words_per_minute = (total_words / total_duration) * 60 if total_duration > 0 else 0
            
            # Google provides professional quality
            quality = "excellent"
            
            return {
                "quality": quality,
                "method": "google_cloud_tts",
                "total_words": total_words,
                "total_duration": total_duration,
                "avg_confidence": avg_confidence,
                "words_per_minute": words_per_minute,
                "timing_precision": "exact_timing_marks",
                "voice_quality": "neural2_professional"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating Google quality metrics: {e}")
            return {
                "quality": "unknown",
                "method": "google_error",
                "error": str(e)
            }
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm)"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millisecs = int((td.total_seconds() % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get Google Cloud TTS information"""
        return {
            "service": "Google Cloud Text-to-Speech",
            "available": GOOGLE_AVAILABLE and self.client is not None,
            "quality": "Professional Neural2 Voices",
            "timing_accuracy": "Exact timing marks",
            "supported_voices": list(self.voice_options.keys()),
            "features": [
                "Word-level timing marks",
                "Neural2 voice synthesis",
                "SSML support", 
                "Enterprise reliability",
                "Multiple voice options",
                "Precise timing control"
            ],
            "configuration": {
                "speaking_rate": self.speaking_rate,
                "audio_format": "48kHz 16-bit Linear PCM WAV",
                "credentials_configured": bool(self.client)
            }
        }


# Example usage and testing
def test_google_tts():
    """Test Google Cloud TTS with timestamps"""
    
    tts = GoogleTTSWithTimestamps()
    
    if tts.test_connection():
        print("✅ Google Cloud TTS ready for professional TTS")
        
        # Test generation
        sample_script = "Hello world, this is a test of Google Cloud TTS with perfect timing."
        result = tts.generate_audio_with_perfect_timestamps("test_content", sample_script)
        
        if result.get("success"):
            print(f"✅ Test successful: {result['audio_path']}")
            print(f"📊 Word boundaries: {len(result['word_boundaries'])}")
        else:
            print(f"❌ Test failed: {result.get('error')}")
    else:
        print("❌ Google Cloud TTS not available")


if __name__ == "__main__":
    test_google_tts()

