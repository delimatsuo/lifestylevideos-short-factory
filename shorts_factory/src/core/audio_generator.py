"""
Audio Generation Module for Shorts Factory
Orchestrates script-to-audio conversion using ElevenLabs and Google Sheets integration
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

from integrations.elevenlabs_api import ElevenLabsTextToSpeech
from integrations.google_sheets import GoogleSheetsManager
from core.config import config


class AudioGenerator:
    """Orchestrates audio generation workflow for approved content with scripts"""
    
    def __init__(self):
        """Initialize the audio generator"""
        self.logger = logging.getLogger(__name__)
        self.elevenlabs = None
        self.sheets_manager = None
        
        # Audio generation settings
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - natural, versatile
        self.audio_quality = "high"
        self.supported_formats = ["mp3"]
    
    def initialize(self) -> bool:
        """Initialize audio generation components"""
        try:
            self.logger.info("🎙️ Initializing Audio Generator...")
            
            # Initialize ElevenLabs TTS
            self.elevenlabs = ElevenLabsTextToSpeech()
            if not self.elevenlabs.test_connection():
                raise Exception("ElevenLabs API connection failed")
            
            # Initialize Google Sheets
            self.sheets_manager = GoogleSheetsManager()
            if not self.sheets_manager.test_connection():
                raise Exception("Google Sheets connection failed")
            
            self.logger.info("✅ Audio Generator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Audio Generator: {e}")
            return False
    
    def generate_audio_for_content(self, content_item: Dict[str, str]) -> Optional[str]:
        """
        Generate audio for a single content item with script
        
        Args:
            content_item: Dictionary containing content details (id, script, etc.)
            
        Returns:
            Path to generated audio file or None if generation fails
        """
        try:
            content_id = content_item.get('id', '').strip()
            script_text = content_item.get('script', '').strip()
            title = content_item.get('title', 'Untitled')
            
            if not content_id:
                self.logger.warning("⚠️ No content ID provided")
                return None
            
            if not script_text:
                self.logger.warning(f"⚠️ No script found for content ID {content_id}")
                return None
            
            self.logger.info(f"🎙️ Generating audio for: {title} (ID: {content_id})")
            
            # Prepare script for TTS (basic cleanup)
            processed_script = self._prepare_script_for_tts(script_text)
            
            # Generate audio using ElevenLabs
            audio_path = self.elevenlabs.generate_audio_for_content(
                content_id=content_id,
                script_text=processed_script,
                voice_id=self.default_voice_id
            )
            
            if audio_path:
                # Get audio file info
                audio_info = self.elevenlabs.get_audio_info(audio_path)
                self.logger.info(f"✅ Audio generated ({audio_info.get('size_kb', 0)} KB): {title}")
                
                return audio_path
            else:
                self.logger.error(f"❌ Failed to generate audio for: {title}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error generating audio: {e}")
            return None
    
    def _prepare_script_for_tts(self, script_text: str) -> str:
        """
        Prepare script text for optimal TTS conversion
        
        Args:
            script_text: Raw script text
            
        Returns:
            Processed script optimized for speech synthesis
        """
        try:
            # Basic script preparation for TTS
            processed = script_text.strip()
            
            # Add natural pauses for better pacing
            processed = processed.replace('. ', '. ')  # Ensure space after periods
            processed = processed.replace('! ', '! ')  # Ensure space after exclamations  
            processed = processed.replace('? ', '? ')  # Ensure space after questions
            
            # Add slight pause indicators for better flow
            processed = processed.replace(':', ': ')   # Pause after colons
            processed = processed.replace(';', '; ')   # Pause after semicolons
            
            # Clean up any double spaces
            while '  ' in processed:
                processed = processed.replace('  ', ' ')
            
            return processed.strip()
            
        except Exception as e:
            self.logger.warning(f"⚠️ Script preparation failed, using original: {e}")
            return script_text.strip()
    
    def save_audio_path_to_sheet(self, content_id: str, audio_path: str) -> bool:
        """
        Save generated audio file path to Google Sheets
        
        Args:
            content_id: The ID of the content item
            audio_path: Path to the generated audio file
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Convert absolute path to relative path from working directory
            audio_file = Path(audio_path)
            working_dir = Path(config.working_directory)
            
            try:
                # Try to make relative path
                relative_path = audio_file.relative_to(working_dir)
                display_path = str(relative_path)
            except ValueError:
                # If not relative, use filename only
                display_path = audio_file.name
            
            # Save to Google Sheets AUDIO_FILE column
            success = self.sheets_manager.update_content_field(
                content_id,
                'AUDIO_FILE',
                display_path,
                f"Audio generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            if success:
                self.logger.info(f"✅ Audio path saved to Google Sheets for ID {content_id}: {display_path}")
                return True
            else:
                self.logger.error(f"❌ Failed to save audio path to Google Sheets for ID {content_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error saving audio path to Google Sheets: {e}")
            return False
    
    def generate_and_save_audio(self, content_item: Dict[str, str]) -> bool:
        """
        Complete workflow: generate audio and save path to Google Sheets
        
        Args:
            content_item: Dictionary containing content details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            # Generate the audio
            audio_path = self.generate_audio_for_content(content_item)
            
            if not audio_path:
                return False
            
            # Save path to Google Sheets
            if self.save_audio_path_to_sheet(content_id, audio_path):
                self.logger.info(f"🎉 Complete audio generation successful for: {title}")
                return True
            else:
                self.logger.error(f"❌ Failed to save audio info for: {title}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in complete audio generation workflow: {e}")
            return False
    
    def batch_generate_audio(self, content_items: List[Dict[str, str]]) -> Dict[str, bool]:
        """
        Generate audio for multiple content items
        
        Args:
            content_items: List of content item dictionaries with scripts
            
        Returns:
            Dictionary mapping content_id to success status
        """
        results = {}
        
        self.logger.info(f"🎙️ Starting batch audio generation for {len(content_items)} items")
        
        for content_item in content_items:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            try:
                success = self.generate_and_save_audio(content_item)
                results[content_id] = success
                
                if success:
                    self.logger.info(f"✅ [{len(results)}/{len(content_items)}] Success: {title}")
                else:
                    self.logger.error(f"❌ [{len(results)}/{len(content_items)}] Failed: {title}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing {title}: {e}")
                results[content_id] = False
        
        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"📊 Batch audio generation complete: {successful}/{len(content_items)} successful")
        
        return results
    
    def get_content_with_scripts(self) -> List[Dict[str, str]]:
        """
        Get content items that have scripts but no audio files yet
        
        Returns:
            List of content items ready for audio generation
        """
        try:
            self.logger.info("📋 Fetching content with scripts for audio generation...")
            
            # Get all content from spreadsheet
            all_content = self.sheets_manager.get_all_content()
            
            ready_for_audio = []
            for content_item in all_content:
                script = content_item.get('script', '').strip()
                audio_file = content_item.get('audio_file', '').strip()
                status = content_item.get('status', '').strip()
                
                # Check if has script but no audio file, and status allows processing
                if (script and 
                    not audio_file and 
                    status.lower() in ['approved', 'in progress', 'script generated']):
                    ready_for_audio.append(content_item)
            
            self.logger.info(f"📊 Found {len(ready_for_audio)} items ready for audio generation")
            return ready_for_audio
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching content for audio generation: {e}")
            return []
    
    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices for audio generation"""
        if self.elevenlabs:
            return self.elevenlabs.get_available_voices()
        else:
            self.logger.warning("⚠️ ElevenLabs not initialized - cannot fetch voices")
            return []
    
    def get_audio_generation_stats(self) -> Dict[str, any]:
        """Get statistics about audio generation capabilities"""
        stats = {
            'default_voice_id': self.default_voice_id,
            'audio_quality': self.audio_quality,
            'supported_formats': self.supported_formats,
            'elevenlabs_available': self.elevenlabs is not None,
            'sheets_available': self.sheets_manager is not None,
            'status': 'operational' if (self.elevenlabs and self.sheets_manager) else 'needs_initialization'
        }
        
        # Add ElevenLabs-specific stats if available
        if self.elevenlabs:
            elevenlabs_stats = self.elevenlabs.get_generation_stats()
            stats.update({
                'audio_directory': elevenlabs_stats.get('audio_directory'),
                'total_audio_files': elevenlabs_stats.get('total_audio_files', 0),
                'total_size_mb': elevenlabs_stats.get('total_size_mb', 0)
            })
        
        return stats
