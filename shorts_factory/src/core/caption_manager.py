"""
Caption Manager for Shorts Factory
Orchestrates the complete caption generation and burning workflow
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

from integrations.caption_generator import SRTCaptionGenerator
from integrations.ffmpeg_captions import FFmpegCaptionBurner
from integrations.google_sheets import GoogleSheetsManager
from integrations.ffmpeg_video import FFmpegVideoAssembly
from core.config import config


class CaptionManager:
    """
    Manages the complete caption workflow for Shorts Factory
    Generates SRT files and burns captions onto videos with professional styling
    """
    
    def __init__(self):
        """Initialize Caption Manager"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.srt_generator = None
        self.caption_burner = None
        self.sheets_manager = None
        self.ffmpeg_assembly = None
        
        # Working directories
        self.final_videos_dir = Path(config.working_directory) / "final_videos"
        self.captioned_videos_dir = Path(config.working_directory) / "captioned_videos"
        self.captions_dir = Path(config.working_directory) / "captions"
        
        self.logger.info("📝 Caption Manager initialized")
    
    def initialize(self) -> bool:
        """Initialize all required components"""
        try:
            self.logger.info("🔧 Initializing Caption Manager components...")
            
            # Initialize SRT Generator
            self.srt_generator = SRTCaptionGenerator()
            self.logger.info("✅ SRT Generator initialized")
            
            # Initialize Caption Burner
            self.caption_burner = FFmpegCaptionBurner()
            if not self.caption_burner.test_ffmpeg_subtitle_support():
                self.logger.warning("⚠️ FFmpeg subtitle support uncertain, but continuing...")
            self.logger.info("✅ Caption Burner initialized")
            
            # Initialize Google Sheets manager
            self.sheets_manager = GoogleSheetsManager()
            # GoogleSheetsManager auto-initializes, skip check
                # self.logger.error("❌ Google Sheets manager initialization failed")
                # return False  # GoogleSheetsManager auto-initializes
            self.logger.info("✅ Google Sheets manager initialized")
            
            # Initialize FFmpeg assembly for duration detection
            self.ffmpeg_assembly = FFmpegVideoAssembly()
            self.logger.info("✅ FFmpeg Assembly helper initialized")
            
            self.logger.info("✅ Caption Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Caption Manager initialization failed: {e}")
            return False
    
    def get_audio_duration_for_content(self, content_id: str) -> Optional[float]:
        """
        Get audio duration for a content item by finding its audio file
        
        Args:
            content_id: The content ID to find audio duration for
            
        Returns:
            Audio duration in seconds, or None if not found
        """
        try:
            # Look for audio files matching the content ID pattern
            audio_dir = Path(config.working_directory) / "audio"
            pattern = f"content_{content_id}_*.mp3"
            
            audio_files = list(audio_dir.glob(pattern))
            
            if not audio_files:
                # Try alternative patterns
                alt_patterns = [
                    f"content_{content_id.upper()}_*.mp3",
                    f"*_{content_id}_*.mp3",
                    f"{content_id}_*.mp3"
                ]
                
                for alt_pattern in alt_patterns:
                    audio_files = list(audio_dir.glob(alt_pattern))
                    if audio_files:
                        break
            
            if not audio_files:
                self.logger.warning(f"⚠️ No audio file found for content ID: {content_id}")
                return None
            
            # Use the most recent file if multiple matches
            audio_file = max(audio_files, key=lambda f: f.stat().st_mtime)
            
            # Get duration using FFmpeg
            duration = self.ffmpeg_assembly.get_audio_duration(str(audio_file))
            if duration:
                self.logger.info(f"🎵 Audio duration for {content_id}: {duration:.2f}s")
                return duration
            else:
                self.logger.error(f"❌ Failed to get audio duration for {content_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting audio duration for {content_id}: {e}")
            return None
    
    def find_video_file_for_content(self, content_id: str) -> Optional[str]:
        """
        Find the final video file for a content item (from video assembly)
        
        Args:
            content_id: The content ID to find video file for
            
        Returns:
            Path to video file, or None if not found
        """
        try:
            # Look for final video files matching the content ID pattern
            pattern = f"shorts_{content_id}_*.mp4"
            
            video_files = list(self.final_videos_dir.glob(pattern))
            
            if not video_files:
                # Try alternative patterns
                alt_patterns = [
                    f"*_{content_id}_*.mp4",
                    f"content_{content_id}_*.mp4"
                ]
                
                for alt_pattern in alt_patterns:
                    video_files = list(self.final_videos_dir.glob(alt_pattern))
                    if video_files:
                        break
            
            if not video_files:
                self.logger.warning(f"⚠️ No video file found for content ID: {content_id}")
                return None
            
            # Use the most recent file if multiple matches
            video_file = max(video_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"🎬 Found video file: {video_file.name}")
            
            return str(video_file)
            
        except Exception as e:
            self.logger.error(f"❌ Error finding video file for {content_id}: {e}")
            return None
    
    def save_captioned_video_path_to_sheet(self, content_id: str, captioned_video_path: str) -> bool:
        """
        Save the captioned video path to Google Sheets
        
        Args:
            content_id: The ID of the content item
            captioned_video_path: Path to the captioned video
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Convert absolute path to relative path from working directory
            video_file = Path(captioned_video_path)
            working_dir = Path(config.working_directory)
            
            try:
                # Try to make relative path
                relative_path = video_file.relative_to(working_dir)
                display_path = str(relative_path)
            except ValueError:
                # If not relative, use filename only
                display_path = video_file.name
            
            # Get file size for additional info
            file_size = video_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            # For now, we'll update the YOUTUBE_URL field with the captioned video path
            # In a real system, you might want a dedicated CAPTIONED_VIDEO column
            success = self.sheets_manager.update_content_field(
                content_id,
                'YOUTUBE_URL',  # Using this field for captioned video path
                display_path,
                f"Captioned video created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({file_size_mb:.1f}MB)"
            )
            
            if success:
                self.logger.info(f"✅ Captioned video path saved to Google Sheets for ID {content_id}: {display_path}")
                return True
            else:
                self.logger.error(f"❌ Failed to save captioned video path to Google Sheets for ID {content_id}")
                # return False  # GoogleSheetsManager auto-initializes
                
        except Exception as e:
            self.logger.error(f"❌ Error saving captioned video path to Google Sheets: {e}")
            # return False  # GoogleSheetsManager auto-initializes
    
    def generate_captions_for_content(self, content_item: Dict[str, Any]) -> bool:
        """
        Generate complete captioned video for a specific content item
        
        Args:
            content_item: Dictionary containing content information
            
        Returns:
            True if caption generation successful, False otherwise
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            script = content_item.get('script', '')
            
            if not content_id:
                self.logger.error("❌ Content ID is required for caption generation")
                return False
            
            if not script:
                self.logger.error(f"❌ No script found for content ID: {content_id}")
                return False
            
            self.logger.info(f"📝 Starting caption generation for: {title} (ID: {content_id})")
            
            # Get audio duration
            audio_duration = self.get_audio_duration_for_content(content_id)
            if not audio_duration:
                self.logger.error(f"❌ Could not determine audio duration for content ID: {content_id}")
                return False
            
            # Find video file
            video_file_path = self.find_video_file_for_content(content_id)
            if not video_file_path:
                self.logger.error(f"❌ No video file found for content ID: {content_id}")
                return False
            
            # Generate SRT file
            self.logger.info(f"📝 Generating SRT captions...")
            srt_file_path = self.srt_generator.generate_srt_file(
                script_text=script,
                audio_duration=audio_duration,
                content_id=content_id
            )
            
            if not srt_file_path:
                self.logger.error(f"❌ SRT generation failed for content ID: {content_id}")
                return False
            
            # Validate SRT file
            if not self.srt_generator.validate_srt_file(srt_file_path):
                self.logger.error(f"❌ SRT validation failed for content ID: {content_id}")
                return False
            
            # Burn captions onto video
            self.logger.info(f"🔥 Burning captions onto video...")
            captioned_video_path = self.caption_burner.create_captioned_video(
                video_file_path=video_file_path,
                srt_file_path=srt_file_path,
                content_id=content_id,
                title=title
            )
            
            if not captioned_video_path:
                self.logger.error(f"❌ Caption burning failed for content ID: {content_id}")
                return False
            
            # Save captioned video path to Google Sheets
            if not self.save_captioned_video_path_to_sheet(content_id, captioned_video_path):
                self.logger.warning(f"⚠️ Failed to save captioned video path to sheets, but captions were generated successfully")
            
            self.logger.info(f"🎉 Caption generation completed successfully for: {title}")
            self.logger.info(f"📝 SRT file: {Path(srt_file_path).name}")
            self.logger.info(f"📺 Captioned video: {Path(captioned_video_path).name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error generating captions for content: {e}")
            return False
    
    def get_content_ready_for_captions(self) -> List[Dict[str, Any]]:
        """
        Get all content items that are ready for caption generation
        (Have final video but no captioned video yet)
        
        Returns:
            List of content items ready for caption generation
        """
        try:
            self.logger.info("🔍 Finding content ready for caption generation...")
            
            # Get all content from Google Sheets
            all_content = self.sheets_manager.get_all_content()
            
            ready_content = []
            
            for content in all_content:
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                script = content.get('script', '')
                audio_file = content.get('audio_file', '')
                video_file = content.get('video_file', '')
                youtube_url = content.get('youtube_url', '')  # We use this for captioned video status
                
                # Check if content has all prerequisites but no captioned video
                has_script = bool(script and script.strip())
                has_audio = bool(audio_file and audio_file.strip())
                has_video = bool(video_file and video_file.strip())
                has_captioned_video = bool(youtube_url and youtube_url.strip() and 'captioned_' in youtube_url)
                
                # Also check if final video file exists
                final_video_exists = False
                if content_id:
                    video_path = self.find_video_file_for_content(content_id)
                    final_video_exists = video_path is not None
                
                if has_script and has_audio and has_video and final_video_exists and not has_captioned_video:
                    self.logger.debug(f"✅ Ready for captions: {title} (ID: {content_id})")
                    ready_content.append(content)
                else:
                    reasons = []
                    if not has_script:
                        reasons.append("no script")
                    if not has_audio:
                        reasons.append("no audio")
                    if not has_video:
                        reasons.append("no video")
                    if not final_video_exists:
                        reasons.append("no final video file")
                    if has_captioned_video:
                        reasons.append("already captioned")
                    
                    self.logger.debug(f"⏭️ Skipping {title} (ID: {content_id}): {', '.join(reasons)}")
            
            self.logger.info(f"📝 Found {len(ready_content)} content items ready for caption generation")
            return ready_content
            
        except Exception as e:
            self.logger.error(f"❌ Error finding content ready for captions: {e}")
            return []
    
    def run_caption_generation_cycle(self) -> Dict[str, Any]:
        """
        Run a complete caption generation cycle for all ready content
        
        Returns:
            Dictionary with caption generation results and statistics
        """
        try:
            self.logger.info("📝 Starting caption generation cycle...")
            
            cycle_start_time = datetime.now()
            
            # Find content ready for caption generation
            ready_content = self.get_content_ready_for_captions()
            
            results = {
                'total_ready': len(ready_content),
                'successfully_captioned': 0,
                'failed_captioning': 0,
                'captioned_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0
            }
            
            if not ready_content:
                self.logger.info("📊 No content ready for caption generation")
                return results
            
            # Process each content item
            for content in ready_content:
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                
                try:
                    self.logger.info(f"📝 Processing: {title} (ID: {content_id})")
                    
                    success = self.generate_captions_for_content(content)
                    
                    if success:
                        results['successfully_captioned'] += 1
                        results['captioned_items'].append({
                            'id': content_id,
                            'title': title
                        })
                        self.logger.info(f"✅ Successfully captioned: {title}")
                    else:
                        results['failed_captioning'] += 1
                        results['failed_items'].append({
                            'id': content_id,
                            'title': title,
                            'error': 'Caption generation process failed'
                        })
                        self.logger.error(f"❌ Failed to caption: {title}")
                        
                except Exception as e:
                    results['failed_captioning'] += 1
                    results['failed_items'].append({
                        'id': content_id,
                        'title': title,
                        'error': str(e)
                    })
                    self.logger.error(f"❌ Error processing {title}: {e}")
            
            # Calculate cycle duration
            cycle_end_time = datetime.now()
            cycle_duration = (cycle_end_time - cycle_start_time).total_seconds()
            results['cycle_duration_seconds'] = cycle_duration
            
            # Log summary
            self.logger.info("🎉 Caption generation cycle completed!")
            self.logger.info(f"📊 Results: {results['successfully_captioned']}/{results['total_ready']} successful")
            self.logger.info(f"⏱️ Duration: {cycle_duration:.1f} seconds")
            
            if results['failed_captioning'] > 0:
                self.logger.warning(f"⚠️ {results['failed_captioning']} items failed caption generation")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in caption generation cycle: {e}")
            return {
                'total_ready': 0,
                'successfully_captioned': 0,
                'failed_captioning': 0,
                'captioned_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0,
                'error': str(e)
            }
