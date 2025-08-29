"""
Video Assembly Manager for Shorts Factory
Orchestrates the complete video assembly workflow using FFmpeg
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import re

from integrations.ffmpeg_video import FFmpegVideoAssembly
from integrations.google_sheets import GoogleSheetsManager
from core.config import config


class VideoAssemblyManager:
    """
    Manages the complete video assembly workflow for Shorts Factory
    Combines audio narration and video clips into final short-form videos
    """
    
    def __init__(self):
        """Initialize Video Assembly Manager"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.ffmpeg_assembly = None
        self.sheets_manager = None
        
        # Working directories
        self.audio_dir = Path(config.working_directory) / "audio"
        self.video_clips_dir = Path(config.working_directory) / "video_clips"
        self.final_videos_dir = Path(config.working_directory) / "final_videos"
        
        self.logger.info("🎬 Video Assembly Manager initialized")
    
    def initialize(self) -> bool:
        """Initialize all required components"""
        try:
            self.logger.info("🔧 Initializing Video Assembly Manager components...")
            
            # Initialize FFmpeg assembly
            self.ffmpeg_assembly = FFmpegVideoAssembly()
            if not self.ffmpeg_assembly.test_ffmpeg_availability():
                self.logger.error("❌ FFmpeg not available")
                return False
            
            # Initialize Google Sheets manager
            self.sheets_manager = GoogleSheetsManager()
            if not self.sheets_manager.initialize():
                self.logger.error("❌ Google Sheets manager initialization failed")
                return False
            
            self.logger.info("✅ Video Assembly Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Video Assembly Manager initialization failed: {e}")
            return False
    
    def find_audio_file_for_content(self, content_id: str) -> Optional[str]:
        """
        Find the audio file for a specific content item
        
        Args:
            content_id: The content ID to find audio for
            
        Returns:
            Path to audio file, or None if not found
        """
        try:
            # Look for audio files matching the content ID pattern
            pattern = f"content_{content_id}_*.mp3"
            
            audio_files = list(self.audio_dir.glob(pattern))
            
            if not audio_files:
                # Try alternative naming patterns
                alt_patterns = [
                    f"content_{content_id.upper()}_*.mp3",
                    f"*_{content_id}_*.mp3",
                    f"{content_id}_*.mp3"
                ]
                
                for alt_pattern in alt_patterns:
                    audio_files = list(self.audio_dir.glob(alt_pattern))
                    if audio_files:
                        break
            
            if not audio_files:
                self.logger.warning(f"⚠️ No audio file found for content ID: {content_id}")
                return None
            
            # Use the most recent file if multiple matches
            audio_file = max(audio_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"🎵 Found audio file: {audio_file.name}")
            
            return str(audio_file)
            
        except Exception as e:
            self.logger.error(f"❌ Error finding audio file for {content_id}: {e}")
            return None
    
    def find_video_clips_for_content(self, content_id: str) -> List[str]:
        """
        Find all video clips for a specific content item
        
        Args:
            content_id: The content ID to find video clips for
            
        Returns:
            List of paths to video clip files
        """
        try:
            # Look for video clips matching the content ID pattern
            pattern = f"content_{content_id}_clip_*.mp4"
            
            video_files = list(self.video_clips_dir.glob(pattern))
            
            if not video_files:
                # Try alternative naming patterns
                alt_patterns = [
                    f"content_{content_id.upper()}_clip_*.mp4",
                    f"*_{content_id}_clip_*.mp4",
                    f"{content_id}_clip_*.mp4"
                ]
                
                for alt_pattern in alt_patterns:
                    video_files = list(self.video_clips_dir.glob(alt_pattern))
                    if video_files:
                        break
            
            if not video_files:
                self.logger.warning(f"⚠️ No video clips found for content ID: {content_id}")
                return []
            
            # Sort by clip number if possible
            def extract_clip_number(filename: str) -> int:
                match = re.search(r'clip_(\d+)', filename)
                return int(match.group(1)) if match else 0
            
            video_files.sort(key=lambda f: extract_clip_number(f.name))
            
            self.logger.info(f"🎬 Found {len(video_files)} video clips for content {content_id}")
            for i, video_file in enumerate(video_files, 1):
                self.logger.debug(f"   Clip {i}: {video_file.name}")
            
            return [str(f) for f in video_files]
            
        except Exception as e:
            self.logger.error(f"❌ Error finding video clips for {content_id}: {e}")
            return []
    
    def generate_output_filename(self, content_id: str, title: str) -> str:
        """
        Generate a suitable filename for the final video
        
        Args:
            content_id: The content ID
            title: The content title
            
        Returns:
            Generated filename for the output video
        """
        try:
            # Clean up title for filename
            clean_title = re.sub(r'[^\w\s-]', '', title)  # Remove special chars
            clean_title = re.sub(r'\s+', '_', clean_title)  # Replace spaces with underscores
            clean_title = clean_title[:50]  # Limit length
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            filename = f"shorts_{content_id}_{clean_title}_{timestamp}.mp4"
            
            self.logger.debug(f"📝 Generated filename: {filename}")
            return filename
            
        except Exception as e:
            # Fallback filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback_filename = f"shorts_{content_id}_{timestamp}.mp4"
            self.logger.warning(f"⚠️ Error generating filename, using fallback: {fallback_filename}")
            return fallback_filename
    
    def save_final_video_path_to_sheet(self, content_id: str, video_path: str) -> bool:
        """
        Save the final assembled video path to Google Sheets
        
        Args:
            content_id: The ID of the content item
            video_path: Path to the final assembled video
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Convert absolute path to relative path from working directory
            video_file = Path(video_path)
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
            
            # Save to Google Sheets - we'll use YOUTUBE_URL column for now
            # (This could be changed to a dedicated FINAL_VIDEO column in the future)
            success = self.sheets_manager.update_content_field(
                content_id,
                'YOUTUBE_URL',  # Using this as final video path for now
                display_path,
                f"Video assembled at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({file_size_mb:.1f}MB)"
            )
            
            if success:
                self.logger.info(f"✅ Final video path saved to Google Sheets for ID {content_id}: {display_path}")
                return True
            else:
                self.logger.error(f"❌ Failed to save final video path to Google Sheets for ID {content_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error saving final video path to Google Sheets: {e}")
            return False
    
    def assemble_video_for_content(self, content_item: Dict[str, Any]) -> bool:
        """
        Assemble the final video for a specific content item
        
        Args:
            content_item: Dictionary containing content information
            
        Returns:
            True if assembly successful, False otherwise
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            if not content_id:
                self.logger.error("❌ Content ID is required for video assembly")
                return False
            
            self.logger.info(f"🎬 Starting video assembly for: {title} (ID: {content_id})")
            
            # Find audio file
            audio_file = self.find_audio_file_for_content(content_id)
            if not audio_file:
                self.logger.error(f"❌ Audio file not found for content ID: {content_id}")
                return False
            
            # Find video clips
            video_clips = self.find_video_clips_for_content(content_id)
            if not video_clips:
                self.logger.error(f"❌ No video clips found for content ID: {content_id}")
                return False
            
            # Generate output filename
            output_filename = self.generate_output_filename(content_id, title)
            
            # Perform video assembly
            self.logger.info(f"🔧 Assembling video with {len(video_clips)} clips and audio narration...")
            
            final_video_path = self.ffmpeg_assembly.assemble_final_video(
                audio_file_path=audio_file,
                video_clips=video_clips,
                output_filename=output_filename
            )
            
            if not final_video_path:
                self.logger.error(f"❌ Video assembly failed for content ID: {content_id}")
                return False
            
            # Validate the output video
            if not self.ffmpeg_assembly.validate_video_output(final_video_path):
                self.logger.warning(f"⚠️ Output video validation failed, but continuing...")
            
            # Save final video path to Google Sheets
            if not self.save_final_video_path_to_sheet(content_id, final_video_path):
                self.logger.warning(f"⚠️ Failed to save video path to sheets, but video was assembled successfully")
            
            self.logger.info(f"🎉 Video assembly completed successfully for: {title}")
            self.logger.info(f"📺 Final video: {final_video_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error assembling video for content: {e}")
            return False
    
    def get_content_ready_for_assembly(self) -> List[Dict[str, Any]]:
        """
        Get all content items that are ready for video assembly
        (Have both audio file and video clips, but no final video yet)
        
        Returns:
            List of content items ready for assembly
        """
        try:
            self.logger.info("🔍 Finding content ready for video assembly...")
            
            # Get all content from Google Sheets
            all_content = self.sheets_manager.get_all_content()
            
            ready_content = []
            
            for content in all_content:
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                audio_file = content.get('audio_file', '')
                video_file = content.get('video_file', '')
                youtube_url = content.get('youtube_url', '')  # Used as final video indicator
                
                # Check if content has audio and video files but no final video
                has_audio = bool(audio_file and audio_file.strip())
                has_video = bool(video_file and video_file.strip())
                has_final_video = bool(youtube_url and youtube_url.strip())
                
                if has_audio and has_video and not has_final_video:
                    self.logger.debug(f"✅ Ready for assembly: {title} (ID: {content_id})")
                    ready_content.append(content)
                else:
                    reasons = []
                    if not has_audio:
                        reasons.append("no audio")
                    if not has_video:
                        reasons.append("no video")
                    if has_final_video:
                        reasons.append("already assembled")
                    
                    self.logger.debug(f"⏭️ Skipping {title} (ID: {content_id}): {', '.join(reasons)}")
            
            self.logger.info(f"🎬 Found {len(ready_content)} content items ready for video assembly")
            return ready_content
            
        except Exception as e:
            self.logger.error(f"❌ Error finding content ready for assembly: {e}")
            return []
    
    def run_video_assembly_cycle(self) -> Dict[str, Any]:
        """
        Run a complete video assembly cycle for all ready content
        
        Returns:
            Dictionary with assembly results and statistics
        """
        try:
            self.logger.info("🎬 Starting video assembly cycle...")
            
            cycle_start_time = datetime.now()
            
            # Find content ready for assembly
            ready_content = self.get_content_ready_for_assembly()
            
            results = {
                'total_ready': len(ready_content),
                'successfully_assembled': 0,
                'failed_assembly': 0,
                'assembled_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0
            }
            
            if not ready_content:
                self.logger.info("📊 No content ready for video assembly")
                return results
            
            # Process each content item
            for content in ready_content:
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                
                try:
                    self.logger.info(f"🎬 Processing: {title} (ID: {content_id})")
                    
                    success = self.assemble_video_for_content(content)
                    
                    if success:
                        results['successfully_assembled'] += 1
                        results['assembled_items'].append({
                            'id': content_id,
                            'title': title
                        })
                        self.logger.info(f"✅ Successfully assembled: {title}")
                    else:
                        results['failed_assembly'] += 1
                        results['failed_items'].append({
                            'id': content_id,
                            'title': title,
                            'error': 'Assembly process failed'
                        })
                        self.logger.error(f"❌ Failed to assemble: {title}")
                        
                except Exception as e:
                    results['failed_assembly'] += 1
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
            self.logger.info("🎉 Video assembly cycle completed!")
            self.logger.info(f"📊 Results: {results['successfully_assembled']}/{results['total_ready']} successful")
            self.logger.info(f"⏱️ Duration: {cycle_duration:.1f} seconds")
            
            if results['failed_assembly'] > 0:
                self.logger.warning(f"⚠️ {results['failed_assembly']} items failed assembly")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in video assembly cycle: {e}")
            return {
                'total_ready': 0,
                'successfully_assembled': 0,
                'failed_assembly': 0,
                'assembled_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0,
                'error': str(e)
            }
