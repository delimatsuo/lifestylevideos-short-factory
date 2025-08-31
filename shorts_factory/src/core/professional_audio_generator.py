"""
🎯 Professional Audio Generator - Enterprise TTS with Perfect Synchronization
Uses professional cloud services that provide exact word-level timestamps

This replaces the problematic estimation-based approach with proven enterprise solutions:
1. Azure Speech Services - Word boundary events
2. Google Cloud TTS - SSML timing marks  
3. ElevenLabs - Fallback with improved estimation

The key difference: We get EXACT timing data from the TTS engines themselves,
not post-processing estimates that cause synchronization issues.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.config import config


class ProfessionalAudioGenerator:
    """
    Professional audio generation using enterprise TTS services with exact timestamps
    
    This solves the synchronization problem by using TTS services that provide
    exact word-level timing data during generation, not estimation afterward.
    
    Priority order:
    1. Azure Speech Services (word boundary events)
    2. Google Cloud TTS (SSML timing marks)  
    3. ElevenLabs (fallback with improved timing)
    """
    
    def __init__(self):
        """Initialize professional audio generator"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("🎵 Initializing Professional Audio Generator...")
        
        # TTS service instances
        self.azure_tts = None
        self.google_tts = None
        self.elevenlabs_tts = None
        
        # Service availability flags
        self.azure_available = False
        self.google_available = False
        self.elevenlabs_available = False
        
        self.logger.info("✅ Professional Audio Generator initialized")
    
    def initialize(self) -> bool:
        """
        Initialize TTS services in priority order
        
        Returns True if at least one professional service is available
        """
        try:
            self.logger.info("🔧 Initializing professional TTS services...")
            
            # Try Azure Speech Services first (best timing accuracy)
            try:
                from integrations.azure_tts_with_timestamps import AzureTTSWithTimestamps
                self.azure_tts = AzureTTSWithTimestamps()
                
                if self.azure_tts.test_connection():
                    self.azure_available = True
                    self.logger.info("✅ Azure Speech Services ready (PRIORITY 1)")
                else:
                    self.logger.warning("⚠️ Azure Speech Services unavailable")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Azure Speech Services failed: {e}")
            
            # Try Google Cloud TTS second (excellent timing accuracy)
            try:
                from integrations.google_tts_with_timestamps import GoogleTTSWithTimestamps
                self.google_tts = GoogleTTSWithTimestamps()
                
                if self.google_tts.test_connection():
                    self.google_available = True
                    self.logger.info("✅ Google Cloud TTS ready (PRIORITY 2)")
                else:
                    self.logger.warning("⚠️ Google Cloud TTS unavailable")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Google Cloud TTS failed: {e}")
            
            # ElevenLabs as fallback (improved timing estimation)
            try:
                from integrations.elevenlabs_api import ElevenLabsTextToSpeech
                self.elevenlabs_tts = ElevenLabsTextToSpeech()
                
                if self.elevenlabs_tts.test_connection():
                    self.elevenlabs_available = True
                    self.logger.info("✅ ElevenLabs TTS ready (FALLBACK)")
                else:
                    self.logger.warning("⚠️ ElevenLabs TTS unavailable")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ ElevenLabs TTS failed: {e}")
            
            # Check if any service is available
            services_available = self.azure_available or self.google_available or self.elevenlabs_available
            
            if services_available:
                self.logger.info("🎉 Professional Audio Generator initialization complete!")
                self._log_service_status()
                return True
            else:
                self.logger.error("❌ No TTS services available")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Professional Audio Generator initialization failed: {e}")
            return False
    
    def generate_professional_audio_with_perfect_sync(
        self, 
        content_item: Dict[str, str], 
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio with perfect synchronization using professional TTS services
        
        Uses the best available service with exact timing data:
        1. Azure Speech Services (word boundary events)
        2. Google Cloud TTS (SSML timing marks)
        3. ElevenLabs (improved estimation fallback)
        
        Args:
            content_item: Dictionary containing content details (id, script, title)
            voice: Voice to use for generation
            
        Returns:
            Dictionary with audio path, SRT path, and exact timing data
        """
        try:
            content_id = content_item.get('id', '').strip()
            script_text = content_item.get('script', '').strip()
            title = content_item.get('title', 'Untitled')
            
            if not content_id:
                return {"success": False, "error": "No content ID provided"}
            
            if not script_text:
                return {"success": False, "error": "No script text provided"}
            
            self.logger.info(f"🎵 Generating professional audio for: {title}")
            self.logger.info(f"📝 Script length: {len(script_text)} characters")
            
            # Try services in priority order
            
            # Priority 1: Azure Speech Services (best timing accuracy)
            if self.azure_available:
                self.logger.info("🥇 Using Azure Speech Services (EXACT word boundaries)")
                result = self.azure_tts.generate_audio_with_perfect_timestamps(
                    content_id, script_text, voice
                )
                
                if result.get("success"):
                    self.logger.info("✅ Azure Speech Services generation successful!")
                    return self._format_professional_result(result, "azure")
                else:
                    self.logger.warning(f"⚠️ Azure failed: {result.get('error')}")
            
            # Priority 2: Google Cloud TTS (excellent timing accuracy)
            if self.google_available:
                self.logger.info("🥈 Using Google Cloud TTS (EXACT timing marks)")
                result = self.google_tts.generate_audio_with_perfect_timestamps(
                    content_id, script_text, voice
                )
                
                if result.get("success"):
                    self.logger.info("✅ Google Cloud TTS generation successful!")
                    return self._format_professional_result(result, "google")
                else:
                    self.logger.warning(f"⚠️ Google TTS failed: {result.get('error')}")
            
            # Fallback: ElevenLabs with improved timing
            if self.elevenlabs_available:
                self.logger.info("🥉 Using ElevenLabs TTS (FALLBACK with improved timing)")
                result = self._generate_with_elevenlabs_improved(content_id, script_text, title, voice)
                
                if result.get("success"):
                    self.logger.info("✅ ElevenLabs generation successful!")
                    return self._format_professional_result(result, "elevenlabs")
                else:
                    self.logger.error(f"❌ ElevenLabs failed: {result.get('error')}")
            
            # All services failed
            return {
                "success": False,
                "error": "All TTS services failed",
                "services_tried": [
                    "Azure Speech Services" if self.azure_available else "Azure (unavailable)",
                    "Google Cloud TTS" if self.google_available else "Google (unavailable)",
                    "ElevenLabs" if self.elevenlabs_available else "ElevenLabs (unavailable)"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Professional audio generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_with_elevenlabs_improved(
        self, 
        content_id: str, 
        script_text: str, 
        title: str, 
        voice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate audio with ElevenLabs using improved timing estimation
        
        This is the fallback when professional services aren't available
        """
        try:
            # Generate audio with ElevenLabs
            audio_path = self.elevenlabs_tts.generate_audio_for_content(
                content_id=content_id,
                script_text=script_text,
                voice_id=voice
            )
            
            if not audio_path:
                return {"success": False, "error": "ElevenLabs audio generation failed"}
            
            # Get audio info
            audio_info = self.elevenlabs_tts.get_audio_info(audio_path)
            
            # Create improved SRT with better timing estimation
            srt_path = self._create_improved_srt_for_elevenlabs(
                script_text, content_id, audio_info.get('duration_seconds', 60)
            )
            
            if not srt_path:
                return {"success": False, "error": "Improved SRT generation failed"}
            
            return {
                "success": True,
                "method": "elevenlabs_improved",
                "audio_path": audio_path,
                "srt_path": srt_path,
                "audio_info": audio_info,
                "quality": "good_fallback",
                "timing_method": "improved_estimation"
            }
            
        except Exception as e:
            self.logger.error(f"❌ ElevenLabs improved generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_improved_srt_for_elevenlabs(
        self, 
        script_text: str, 
        content_id: str, 
        total_duration: float
    ) -> Optional[str]:
        """
        Create improved SRT file for ElevenLabs with better timing estimation
        
        Uses more sophisticated timing algorithms than the basic approach
        """
        try:
            from integrations.caption_generator import SRTCaptionGenerator
            
            caption_gen = SRTCaptionGenerator()
            
            # Use improved timing parameters
            caption_gen.max_chars_per_line = 25  # Mobile optimized
            caption_gen.min_caption_duration = 1.0  # Longer minimum
            caption_gen.max_caption_duration = 3.5  # Shorter maximum
            caption_gen.caption_padding = 0.1  # Reduce padding
            
            return caption_gen.generate_srt_file(script_text, total_duration, content_id)
            
        except Exception as e:
            self.logger.error(f"❌ Improved SRT creation failed: {e}")
            return None
    
    def _format_professional_result(self, result: Dict[str, Any], service: str) -> Dict[str, Any]:
        """Format result from professional TTS services for consistency"""
        try:
            formatted_result = {
                "success": True,
                "service_used": service,
                "method": result.get("method", f"{service}_professional"),
                "audio_path": result["audio_path"],
                "srt_path": result["srt_path"],
                "word_boundaries": result.get("word_boundaries", []),
                "audio_info": result.get("audio_info", {}),
                "quality_metrics": result.get("quality_metrics", {}),
                "voice_used": result.get("voice_used", "unknown"),
                "total_duration": result.get("total_duration", 0),
                "word_count": result.get("word_count", 0),
                "timing_precision": "exact" if service in ["azure", "google"] else "estimated"
            }
            
            # Add service-specific metadata
            if service == "azure":
                formatted_result["timing_source"] = "Azure word boundary events"
                formatted_result["quality"] = "PROFESSIONAL (Azure Neural)"
            elif service == "google":
                formatted_result["timing_source"] = "Google Cloud SSML timing marks"
                formatted_result["quality"] = "PROFESSIONAL (Google Neural2)"
            else:
                formatted_result["timing_source"] = "ElevenLabs improved estimation"
                formatted_result["quality"] = "GOOD (ElevenLabs fallback)"
            
            return formatted_result
            
        except Exception as e:
            self.logger.error(f"❌ Error formatting professional result: {e}")
            return result  # Return original result if formatting fails
    
    def _log_service_status(self):
        """Log the status of all TTS services"""
        self.logger.info("📊 TTS Services Status:")
        self.logger.info(f"   🥇 Azure Speech Services: {'✅ Available' if self.azure_available else '❌ Unavailable'}")
        self.logger.info(f"   🥈 Google Cloud TTS: {'✅ Available' if self.google_available else '❌ Unavailable'}")
        self.logger.info(f"   🥉 ElevenLabs TTS: {'✅ Available' if self.elevenlabs_available else '❌ Unavailable'}")
        
        # Recommend best available service
        if self.azure_available:
            self.logger.info("🏆 BEST: Azure Speech Services (exact word boundaries)")
        elif self.google_available:
            self.logger.info("🏆 BEST: Google Cloud TTS (exact timing marks)")
        elif self.elevenlabs_available:
            self.logger.info("🏆 FALLBACK: ElevenLabs (improved estimation)")
    
    def get_professional_service_info(self) -> Dict[str, Any]:
        """Get information about available professional services"""
        services_info = {
            "initialized": True,
            "azure_available": self.azure_available,
            "google_available": self.google_available,
            "elevenlabs_available": self.elevenlabs_available,
            "best_service": None,
            "timing_precision": None
        }
        
        # Determine best available service
        if self.azure_available:
            services_info["best_service"] = "Azure Speech Services"
            services_info["timing_precision"] = "EXACT (word boundary events)"
        elif self.google_available:
            services_info["best_service"] = "Google Cloud TTS"
            services_info["timing_precision"] = "EXACT (SSML timing marks)"
        elif self.elevenlabs_available:
            services_info["best_service"] = "ElevenLabs"
            services_info["timing_precision"] = "IMPROVED (estimation)"
        else:
            services_info["best_service"] = "None"
            services_info["timing_precision"] = "NONE"
        
        # Add individual service info if available
        if self.azure_tts:
            services_info["azure_info"] = self.azure_tts.get_service_info()
        if self.google_tts:
            services_info["google_info"] = self.google_tts.get_service_info()
        if self.elevenlabs_tts:
            services_info["elevenlabs_info"] = self.elevenlabs_tts.get_service_info()
        
        return services_info
    
    def estimate_cost(self, text: str, service: Optional[str] = None) -> Dict[str, Any]:
        """Estimate cost for generating audio with the best available service"""
        try:
            char_count = len(text)
            
            # Cost estimates (approximate)
            costs = {
                "azure": {
                    "per_char": 0.00004,  # $16 per 1M chars
                    "service": "Azure Speech Services"
                },
                "google": {
                    "per_char": 0.000016,  # $16 per 1M chars
                    "service": "Google Cloud TTS"
                },
                "elevenlabs": {
                    "per_char": 0.00003,  # Variable based on plan
                    "service": "ElevenLabs"
                }
            }
            
            # Use best available service for estimation
            if service:
                target_service = service
            elif self.azure_available:
                target_service = "azure"
            elif self.google_available:
                target_service = "google"
            elif self.elevenlabs_available:
                target_service = "elevenlabs"
            else:
                return {"error": "No services available for cost estimation"}
            
            cost_info = costs.get(target_service, costs["elevenlabs"])
            estimated_cost = char_count * cost_info["per_char"]
            
            return {
                "service": cost_info["service"],
                "character_count": char_count,
                "estimated_cost_usd": estimated_cost,
                "cost_per_character": cost_info["per_char"],
                "currency": "USD"
            }
            
        except Exception as e:
            return {"error": f"Cost estimation failed: {e}"}


# Example usage and testing
def test_professional_audio_generator():
    """Test the professional audio generator"""
    
    generator = ProfessionalAudioGenerator()
    
    if generator.initialize():
        print("✅ Professional Audio Generator ready")
        
        # Test generation
        sample_content = {
            "id": "test_professional",
            "script": "This is a professional test of exact timing synchronization with enterprise TTS services.",
            "title": "Professional TTS Test"
        }
        
        result = generator.generate_professional_audio_with_perfect_sync(sample_content)
        
        if result.get("success"):
            print(f"✅ Professional generation successful!")
            print(f"🎤 Service used: {result.get('service_used')}")
            print(f"📊 Quality: {result.get('quality')}")
            print(f"🎯 Timing precision: {result.get('timing_precision')}")
        else:
            print(f"❌ Professional generation failed: {result.get('error')}")
    else:
        print("❌ Professional Audio Generator initialization failed")


if __name__ == "__main__":
    test_professional_audio_generator()
