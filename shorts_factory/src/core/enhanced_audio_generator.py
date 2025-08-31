"""
Enhanced Audio Generator for Shorts Factory
Combines OpenAI TTS with Whisper alignment for perfect synchronization
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime

from integrations.openai_tts import OpenAITextToSpeech
from integrations.whisper_alignment import WhisperAlignment
from core.config import config


class EnhancedAudioGenerator:
    """
    Enhanced audio generation with perfect caption synchronization
    
    Features:
    - OpenAI TTS for natural speech (replacing ElevenLabs)
    - Whisper forced alignment for perfect timing
    - Word-level timestamp accuracy
    - Eliminates caption-audio drift
    """
    
    def __init__(self):
        """Initialize enhanced audio generator"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.openai_tts = None
        self.whisper_alignment = None
        
        # Configuration
        self.default_voice = "nova"  # Engaging female voice
        self.voice_options = {
            "nova": "Young female, engaging for viral content",
            "alloy": "Neutral, professional",
            "echo": "Male, warm and friendly",
            "fable": "British accent, sophisticated", 
            "onyx": "Deep male, authoritative",
            "shimmer": "Soft female, calming"
        }
        
        self.logger.info("🎵 Enhanced Audio Generator initialized")
    
    def initialize(self) -> bool:
        """Initialize all audio generation components"""
        try:
            self.logger.info("🔧 Initializing Enhanced Audio Generator components...")
            
            # Try OpenAI TTS first
            try:
                self.openai_tts = OpenAITextToSpeech()
                if self.openai_tts.test_connection():
                    self.logger.info("✅ OpenAI TTS initialized")
                    
                    # Initialize Whisper alignment  
                    self.whisper_alignment = WhisperAlignment()
                    self.logger.info("✅ Whisper alignment initialized")
                    
                    self.logger.info("✅ Enhanced Audio Generator initialized successfully")
                    return True
                else:
                    raise Exception("OpenAI TTS test failed")
                    
            except Exception as openai_error:
                self.logger.warning(f"⚠️ OpenAI TTS unavailable: {openai_error}")
                self.logger.info("🔄 Falling back to ElevenLabs TTS...")
                
                # Fallback to ElevenLabs
                try:
                    from integrations.elevenlabs_api import ElevenLabsTextToSpeech
                    self.elevenlabs_tts = ElevenLabsTextToSpeech()
                    if self.elevenlabs_tts.test_connection():
                        self.logger.info("✅ ElevenLabs TTS fallback initialized")
                        self.logger.warning("⚠️ Using legacy timing estimation (no Whisper alignment)")
                        return True
                    else:
                        raise Exception("ElevenLabs TTS test failed")
                        
                except Exception as elevenlabs_error:
                    self.logger.error(f"❌ ElevenLabs fallback failed: {elevenlabs_error}")
                    return False
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced Audio Generator initialization failed: {e}")
            return False
    
    def generate_audio_with_perfect_sync(
        self, 
        content_item: Dict[str, str], 
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio with perfect caption synchronization
        
        Args:
            content_item: Dictionary containing content details (id, script, etc.)
            voice: Voice to use for generation
            
        Returns:
            Dictionary with audio path, alignment data, and SRT path
        """
        try:
            content_id = content_item.get('id', '').strip()
            script_text = content_item.get('script', '').strip()
            title = content_item.get('title', 'Untitled')
            
            if not content_id:
                self.logger.error("❌ No content ID provided")
                return {"success": False, "error": "No content ID"}
            
            if not script_text:
                self.logger.error(f"❌ No script found for content ID {content_id}")
                return {"success": False, "error": "No script text"}
            
            voice = voice or self.default_voice
            
            self.logger.info(f"🎵 Generating perfectly synced audio for: {title}")
            self.logger.info(f"🎤 Using voice: {voice} ({self.voice_options.get(voice, 'Unknown')})")
            
            # Check which TTS system is available and working
            openai_available = (hasattr(self, 'openai_tts') and self.openai_tts and 
                              hasattr(self.openai_tts, 'client') and self.openai_tts.client)
            elevenlabs_available = hasattr(self, 'elevenlabs_tts') and self.elevenlabs_tts
            
            if openai_available:
                # Use OpenAI TTS with Whisper alignment
                self.logger.info("🎯 Using OpenAI TTS with Whisper alignment (perfect sync)")
                return self._generate_with_openai_and_whisper(content_id, script_text, title, voice)
            elif elevenlabs_available:
                # Use ElevenLabs TTS with legacy timing
                self.logger.info("🔄 Using ElevenLabs TTS with timing estimation (fallback)")
                return self._generate_with_elevenlabs_fallback(content_id, script_text, title)
            else:
                return {"success": False, "error": "No TTS service available"}
            
        except Exception as e:
            self.logger.error(f"❌ Error generating synced audio: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_with_openai_and_whisper(self, content_id: str, script_text: str, title: str, voice: str) -> Dict[str, Any]:
        """Generate audio with OpenAI TTS and Whisper alignment (perfect sync)"""
        try:
            # Step 1: Generate audio using OpenAI TTS
            self.logger.info("🎙️ Step 1: Generating natural speech audio...")
            
            # Check if OpenAI TTS is actually working
            if not self.openai_tts or not hasattr(self.openai_tts, 'client') or not self.openai_tts.client:
                raise Exception("OpenAI TTS client not properly initialized")
            
            audio_path = self.openai_tts.generate_audio_for_content(
                content_id=content_id,
                script_text=script_text,
                voice=voice
            )
            
            if not audio_path:
                return {"success": False, "error": "OpenAI TTS generation failed"}
            
            # Get audio info
            audio_info = self.openai_tts.get_audio_info(audio_path)
            self.logger.info(f"✅ Audio generated: {audio_info.get('filename')} ({audio_info.get('size_kb', 0):.1f} KB)")
            
            # Step 2: Get enhanced alignment using superior algorithm
            self.logger.info("🎯 Step 2: Creating enhanced caption alignment...")
            from integrations.enhanced_whisper_alignment import EnhancedWhisperAlignment
            
            enhanced_alignment = EnhancedWhisperAlignment()
            aligned_words = enhanced_alignment.get_enhanced_word_alignment(audio_path, script_text)
            
            if not aligned_words:
                return {"success": False, "error": "Enhanced alignment failed"}
            
            # Step 3: Generate optimally segmented SRT file
            self.logger.info("📝 Step 3: Generating enhanced SRT with optimal segmentation...")
            srt_path = enhanced_alignment.generate_enhanced_srt(aligned_words, content_id)
            
            if not srt_path:
                return {"success": False, "error": "Enhanced SRT generation failed"}
            
            # Step 4: Calculate quality metrics from enhanced alignment
            quality_metrics = self._calculate_enhanced_quality_metrics(aligned_words)
            
            self.logger.info(f"✅ Enhanced synchronization complete!")
            self.logger.info(f"📊 Alignment quality: {quality_metrics['quality'].upper()}")
            self.logger.info(f"🎯 Words: {quality_metrics['total_words']}")
            self.logger.info(f"⏱️ Total duration: {quality_metrics['total_duration']:.1f}s")
            self.logger.info(f"🎤 Method: Enhanced Whisper with word-level precision")
            
            # Calculate total duration from aligned words
            total_duration = aligned_words[-1]['end'] if aligned_words else 0
            
            return {
                "success": True,
                "audio_path": audio_path,
                "srt_path": srt_path,
                "aligned_segments": aligned_words,  # Using word-level alignment
                "audio_info": audio_info,
                "quality_metrics": quality_metrics,
                "total_duration": total_duration,
                "segment_count": len(aligned_words),
                "voice_used": voice,
                "method": "enhanced_openai_whisper"
            }
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI+Whisper generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_with_elevenlabs_fallback(self, content_id: str, script_text: str, title: str) -> Dict[str, Any]:
        """Generate audio with ElevenLabs and create basic SRT (fallback)"""
        try:
            self.logger.info("🎙️ Generating audio with ElevenLabs (fallback)...")
            
            # Generate audio using ElevenLabs
            audio_path = self.elevenlabs_tts.generate_audio_for_content(
                content_id=content_id,
                script_text=script_text
            )
            
            if not audio_path:
                return {"success": False, "error": "ElevenLabs TTS generation failed"}
            
            # Get audio info
            audio_info = self.elevenlabs_tts.get_audio_info(audio_path)
            self.logger.info(f"✅ Audio generated: {audio_info.get('filename')} ({audio_info.get('size_kb', 0):.1f} KB)")
            
            # Create basic SRT with timing estimation (legacy method)
            self.logger.info("📝 Creating basic SRT with timing estimation...")
            srt_path = self._create_basic_srt(content_id, script_text, audio_info.get('duration', 60))
            
            if not srt_path:
                return {"success": False, "error": "Basic SRT generation failed"}
            
            self.logger.info("✅ ElevenLabs fallback generation complete!")
            self.logger.warning("⚠️ Using basic timing estimation (less accurate than Whisper)")
            
            return {
                "success": True,
                "audio_path": audio_path,
                "srt_path": srt_path,
                "aligned_segments": [],  # No Whisper segments
                "audio_info": audio_info,
                "quality_metrics": {"quality": "basic", "method": "timing_estimation"},
                "total_duration": audio_info.get('duration', 60),
                "segment_count": 0,
                "voice_used": "rachel",  # ElevenLabs default
                "method": "elevenlabs_basic"
            }
            
        except Exception as e:
            self.logger.error(f"❌ ElevenLabs fallback generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_basic_srt(self, content_id: str, script_text: str, duration: float) -> Optional[str]:
        """Create basic SRT file with timing estimation (fallback method)"""
        try:
            from integrations.caption_generator import SRTCaptionGenerator
            
            srt_generator = SRTCaptionGenerator()
            
            # Use the legacy caption generator to create basic SRT
            srt_path = srt_generator.generate_srt_file(
                script_text=script_text,
                audio_duration=duration,
                content_id=content_id
            )
            
            return srt_path
            
        except Exception as e:
            self.logger.error(f"❌ Basic SRT generation failed: {e}")
            return None
    
    def generate_audio_for_content(self, content_item: Dict[str, str]) -> Optional[str]:
        """
        Legacy method for compatibility with existing code
        Generates audio and returns path (without alignment data)
        """
        try:
            result = self.generate_audio_with_perfect_sync(content_item)
            
            if result.get("success"):
                return result.get("audio_path")
            else:
                self.logger.error(f"❌ Audio generation failed: {result.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in legacy audio generation: {e}")
            return None
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get available voice options with descriptions"""
        return self.voice_options.copy()
    
    def estimate_generation_cost(self, script_text: str) -> Dict[str, Any]:
        """
        Estimate cost for audio generation
        
        Args:
            script_text: Text to be converted
            
        Returns:
            Cost estimation details
        """
        try:
            char_count = len(script_text)
            
            # OpenAI TTS cost: $15.00 per 1M characters
            tts_cost = self.openai_tts.get_estimated_cost(script_text)
            
            # Whisper cost: $0.006 per minute (estimated)
            # Estimate ~150 words per minute, ~5 chars per word = ~750 chars per minute
            estimated_minutes = char_count / 750
            whisper_cost = estimated_minutes * 0.006
            
            total_cost = tts_cost + whisper_cost
            
            return {
                "character_count": char_count,
                "estimated_duration_minutes": estimated_minutes,
                "tts_cost": tts_cost,
                "whisper_cost": whisper_cost,
                "total_cost": total_cost,
                "cost_breakdown": {
                    "openai_tts": f"${tts_cost:.4f}",
                    "whisper_alignment": f"${whisper_cost:.4f}",
                    "total": f"${total_cost:.4f}"
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error estimating cost: {e}")
            return {"error": str(e)}
    
    def cleanup_temp_files(self, content_id: str):
        """Clean up temporary files for a content item"""
        try:
            audio_dir = Path(config.working_directory) / "audio"
            captions_dir = Path(config.working_directory) / "captions"
            
            # Find and remove temporary files
            for directory in [audio_dir, captions_dir]:
                if directory.exists():
                    temp_files = list(directory.glob(f"*{content_id}*temp*"))
                    for temp_file in temp_files:
                        temp_file.unlink()
                        self.logger.debug(f"🗑️ Cleaned up: {temp_file.name}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error cleaning up temp files: {e}")
    
    def _calculate_enhanced_quality_metrics(self, aligned_words: List[Dict]) -> Dict[str, Any]:
        """
        Calculate quality metrics for enhanced word alignment
        
        Args:
            aligned_words: List of aligned word dictionaries
            
        Returns:
            Quality metrics dictionary
        """
        if not aligned_words:
            return {
                "quality": "poor",
                "total_words": 0,
                "total_duration": 0.0,
                "avg_confidence": 0.0,
                "timing_method": "none"
            }
        
        try:
            total_words = len(aligned_words)
            total_duration = aligned_words[-1]['end'] - aligned_words[0]['start']
            
            # Calculate average confidence
            confidences = [word.get('confidence', 1.0) for word in aligned_words]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Analyze timing sources
            source_counts = {}
            for word in aligned_words:
                source = word.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            # Determine overall quality based on confidence and source distribution
            whisper_ratio = (source_counts.get('whisper_match', 0) + 
                           source_counts.get('whisper_lookahead', 0)) / total_words
            
            if whisper_ratio > 0.8 and avg_confidence > 0.8:
                quality = "excellent"
            elif whisper_ratio > 0.6 and avg_confidence > 0.6:
                quality = "good"
            elif whisper_ratio > 0.4 and avg_confidence > 0.5:
                quality = "fair"
            else:
                quality = "poor"
            
            # Calculate words per second
            words_per_second = total_words / total_duration if total_duration > 0 else 0
            
            return {
                "quality": quality,
                "total_words": total_words,
                "total_duration": total_duration,
                "avg_confidence": avg_confidence,
                "words_per_second": words_per_second,
                "whisper_ratio": whisper_ratio,
                "source_distribution": source_counts,
                "timing_method": "enhanced_whisper"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating quality metrics: {e}")
            return {
                "quality": "unknown",
                "total_words": len(aligned_words),
                "total_duration": 0.0,
                "avg_confidence": 0.0,
                "timing_method": "error"
            }
