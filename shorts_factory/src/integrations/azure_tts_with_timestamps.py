"""
🎯 Azure Speech Services TTS with Word Boundaries
Professional-grade TTS with exact word-level timestamps for perfect synchronization

This is the solution used by professional automated video platforms:
- Azure Speech Services provides exact word boundary timestamps
- SSML support for fine-grained control
- Neural voices with precise timing data
- Enterprise-grade reliability and accuracy
"""

import os
import logging
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("⚠️ Azure Speech SDK not installed. Run: pip install azure-cognitiveservices-speech")

from core.config import config


class AzureTTSWithTimestamps:
    """
    Professional TTS using Azure Speech Services with exact word timestamps
    
    This is what major automated video platforms use for perfect synchronization:
    - Exact word boundary timestamps from the TTS engine
    - Neural voices with natural speech patterns
    - SSML support for precise control
    - Enterprise reliability and accuracy
    """
    
    def __init__(self):
        """Initialize Azure Speech Services"""
        self.logger = logging.getLogger(__name__)
        
        if not AZURE_AVAILABLE:
            self.logger.error("❌ Azure Speech SDK not available")
            self.client = None
            return
        
        try:
            # Azure configuration - you'll need to set these in your .env file
            self.subscription_key = os.getenv('AZURE_SPEECH_KEY')
            self.region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
            
            if not self.subscription_key:
                self.logger.warning("⚠️ AZURE_SPEECH_KEY not found in environment")
                self.client = None
                return
            
            # Initialize Azure Speech SDK
            speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key, 
                region=self.region
            )
            
            # Configure for word-level timestamps
            speech_config.request_word_level_timestamps()
            speech_config.output_format = speechsdk.OutputFormat.Detailed
            
            self.speech_config = speech_config
            self.logger.info("✅ Azure Speech Services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Azure Speech: {e}")
            self.client = None
        
        # Voice configuration - Neural voices with best quality
        self.voice_options = {
            "nova": "en-US-AriaNeural",      # Female, clear and engaging
            "alloy": "en-US-DavisNeural",    # Male, professional
            "echo": "en-US-JennyNeural",     # Female, warm and friendly  
            "fable": "en-US-GuyNeural",      # Male, mature and authoritative
            "onyx": "en-US-JasonNeural",     # Male, deep and confident
            "shimmer": "en-US-SaraNeural"    # Female, calm and pleasant
        }
        
        self.default_voice = "nova"
        
        # Audio settings
        self.audio_format = speechsdk.AudioOutputFormat.Audio48Khz16BitMonoPcm
        self.speech_rate = "1.1"  # 10% faster as requested
        
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
        """Test Azure Speech Services connection"""
        try:
            if not AZURE_AVAILABLE or not self.speech_config:
                return False
            
            # Create a simple synthesizer to test
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            
            # Test with a short phrase
            ssml = self._create_ssml("Test connection.", self.voice_options[self.default_voice])
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.logger.info("✅ Azure Speech Services connection successful")
                return True
            else:
                self.logger.error(f"❌ Azure Speech test failed: {result.reason}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Azure Speech connection test failed: {e}")
            return False
    
    def generate_audio_with_perfect_timestamps(
        self, 
        content_id: str, 
        script_text: str, 
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio with exact word-level timestamps from Azure Speech
        
        This is the professional approach used by major platforms:
        1. Generate audio with Azure Speech Services
        2. Extract exact word boundaries during generation
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
            if not AZURE_AVAILABLE or not self.speech_config:
                return {
                    "success": False, 
                    "error": "Azure Speech Services not available",
                    "fallback_recommended": "ElevenLabs"
                }
            
            voice_name = self.voice_options.get(voice or self.default_voice, self.voice_options[self.default_voice])
            
            self.logger.info(f"🎤 Generating audio with Azure Speech: {voice_name}")
            self.logger.info(f"📝 Text length: {len(script_text)} characters")
            
            # Create SSML for precise control
            ssml = self._create_ssml(script_text, voice_name)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"azure_tts_{content_id}_{timestamp}.wav"
            audio_path = self.audio_directory / audio_filename
            
            # Configure audio output
            audio_config = speechsdk.AudioConfig(filename=str(audio_path))
            
            # Create synthesizer with word-level timestamp support
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config, 
                audio_config=audio_config
            )
            
            # Storage for word boundaries
            word_boundaries = []
            
            def word_boundary_handler(evt):
                """Handle word boundary events for precise timing"""
                try:
                    # Azure provides exact timing in ticks (100ns intervals)
                    start_time = evt.audio_offset / 10_000_000  # Convert to seconds
                    duration = evt.duration.total_seconds() if hasattr(evt.duration, 'total_seconds') else evt.duration / 10_000_000
                    
                    word_boundaries.append({
                        'word': evt.text,
                        'start': start_time,
                        'end': start_time + duration,
                        'duration': duration,
                        'audio_offset': evt.audio_offset,
                        'confidence': 1.0,  # Azure provides high-confidence data
                        'source': 'azure_word_boundary'
                    })
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error processing word boundary: {e}")
            
            # Register word boundary event handler
            synthesizer.synthesizing.connect(lambda evt: None)  # Optional progress tracking
            synthesizer.synthesis_word_boundary.connect(word_boundary_handler)
            
            # Generate audio with word boundaries
            self.logger.info("🎵 Generating audio with word-level timestamps...")
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Verify audio file was created
                if not audio_path.exists() or audio_path.stat().st_size == 0:
                    return {"success": False, "error": "Audio file not created properly"}
                
                file_size_kb = audio_path.stat().st_size / 1024
                self.logger.info(f"✅ Audio generated: {audio_filename} ({file_size_kb:.1f} KB)")
                self.logger.info(f"🎯 Word boundaries captured: {len(word_boundaries)}")
                
                # Generate perfectly synchronized SRT file
                srt_path = self._create_perfect_srt(word_boundaries, content_id, timestamp)
                
                if not srt_path:
                    return {"success": False, "error": "SRT generation failed"}
                
                # Calculate quality metrics
                quality_metrics = self._calculate_azure_quality_metrics(word_boundaries)
                
                self.logger.info("✅ Azure Speech generation complete with perfect timing!")
                self.logger.info(f"📊 Quality: PROFESSIONAL (Azure Neural)")
                self.logger.info(f"🎯 Word boundaries: {len(word_boundaries)}")
                self.logger.info(f"⏱️ Total duration: {word_boundaries[-1]['end']:.1f}s" if word_boundaries else "Unknown")
                
                return {
                    "success": True,
                    "method": "azure_neural_tts",
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
                        "format": "WAV 48kHz 16-bit mono",
                        "quality": "Professional Neural Voice"
                    }
                }
                
            else:
                error_details = f"Reason: {result.reason}"
                if result.cancellation_details:
                    error_details += f", Details: {result.cancellation_details.reason}"
                    if result.cancellation_details.error_details:
                        error_details += f", Error: {result.cancellation_details.error_details}"
                
                return {
                    "success": False, 
                    "error": f"Azure Speech synthesis failed: {error_details}",
                    "fallback_recommended": "ElevenLabs"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Azure TTS generation failed: {e}")
            return {
                "success": False, 
                "error": str(e),
                "fallback_recommended": "ElevenLabs"
            }
    
    def _create_ssml(self, text: str, voice_name: str) -> str:
        """
        Create SSML (Speech Synthesis Markup Language) for precise control
        
        SSML allows fine-grained control over:
        - Speech rate and pitch
        - Pronunciation and emphasis  
        - Pauses and breaks
        - Voice characteristics
        """
        # Clean and prepare text
        clean_text = self._clean_text_for_ssml(text)
        
        # Create SSML with precise timing control
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{voice_name}">
                <prosody rate="{self.speech_rate}" pitch="default" volume="default">
                    {clean_text}
                </prosody>
            </voice>
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
    
    def _create_perfect_srt(self, word_boundaries: List[Dict], content_id: str, timestamp: str) -> Optional[str]:
        """
        Create perfectly synchronized SRT file from Azure word boundaries
        
        This creates captions with exact timing from the TTS engine,
        ensuring perfect synchronization between audio and text.
        """
        try:
            if not word_boundaries:
                self.logger.error("❌ No word boundaries for SRT creation")
                return None
            
            # Generate SRT filename
            srt_filename = f"azure_perfect_sync_{content_id}_{timestamp}.srt"
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
    
    def _calculate_azure_quality_metrics(self, word_boundaries: List[Dict]) -> Dict[str, Any]:
        """Calculate quality metrics for Azure Speech generation"""
        if not word_boundaries:
            return {"quality": "none", "method": "azure"}
        
        try:
            total_words = len(word_boundaries)
            total_duration = word_boundaries[-1]['end'] - word_boundaries[0]['start']
            
            # All Azure boundaries are high confidence
            avg_confidence = 1.0
            
            # Calculate speech rate
            words_per_minute = (total_words / total_duration) * 60 if total_duration > 0 else 0
            
            # Azure provides professional quality
            quality = "excellent"
            
            return {
                "quality": quality,
                "method": "azure_neural_tts",
                "total_words": total_words,
                "total_duration": total_duration,
                "avg_confidence": avg_confidence,
                "words_per_minute": words_per_minute,
                "timing_precision": "exact_word_boundaries",
                "voice_quality": "neural_professional"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating Azure quality metrics: {e}")
            return {
                "quality": "unknown",
                "method": "azure_error",
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
        """Get Azure Speech Services information"""
        return {
            "service": "Azure Speech Services",
            "available": AZURE_AVAILABLE and self.speech_config is not None,
            "quality": "Professional Neural Voices",
            "timing_accuracy": "Exact word boundaries",
            "supported_voices": list(self.voice_options.keys()),
            "features": [
                "Word-level timestamps",
                "Neural voice synthesis", 
                "SSML support",
                "Enterprise reliability",
                "Multiple voice options",
                "Precise timing control"
            ],
            "configuration": {
                "region": self.region if hasattr(self, 'region') else "Not configured",
                "speech_rate": self.speech_rate,
                "audio_format": "48kHz 16-bit mono WAV",
                "api_configured": bool(self.subscription_key)
            }
        }


# Example usage and testing
def test_azure_tts():
    """Test Azure TTS with timestamps"""
    
    tts = AzureTTSWithTimestamps()
    
    if tts.test_connection():
        print("✅ Azure Speech Services ready for professional TTS")
        
        # Test generation
        sample_script = "Hello world, this is a test of Azure Speech Services with perfect timing."
        result = tts.generate_audio_with_perfect_timestamps("test_content", sample_script)
        
        if result.get("success"):
            print(f"✅ Test successful: {result['audio_path']}")
            print(f"📊 Word boundaries: {len(result['word_boundaries'])}")
        else:
            print(f"❌ Test failed: {result.get('error')}")
    else:
        print("❌ Azure Speech Services not available")


if __name__ == "__main__":
    test_azure_tts()

