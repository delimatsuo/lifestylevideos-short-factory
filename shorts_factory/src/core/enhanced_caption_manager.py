"""
Enhanced Caption Manager for Shorts Factory
Uses Whisper-aligned captions for perfect synchronization
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

from integrations.ffmpeg_captions import FFmpegCaptionBurner
from integrations.google_sheets import GoogleSheetsManager
from core.config import config


class EnhancedCaptionManager:
    """
    Enhanced caption management with perfect synchronization
    
    Features:
    - Uses Whisper-aligned SRT files (no timing estimation)
    - Perfect audio-caption synchronization
    - Mobile-optimized font sizing
    - Professional styling for vertical videos
    """
    
    def __init__(self):
        """Initialize Enhanced Caption Manager"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.caption_burner = None
        self.sheets_manager = None
        
        # Working directories
        self.final_videos_dir = Path(config.working_directory) / "final_videos"
        self.captioned_videos_dir = Path(config.working_directory) / "captioned_videos"
        self.captions_dir = Path(config.working_directory) / "captions"
        
        self.logger.info("📝 Enhanced Caption Manager initialized")
    
    def initialize(self) -> bool:
        """Initialize all required components"""
        try:
            self.logger.info("🔧 Initializing Enhanced Caption Manager components...")
            
            # Initialize FFmpeg caption burner with enhanced settings
            self.caption_burner = FFmpegCaptionBurner()
            # FFmpegCaptionBurner doesn't have test_ffmpeg_availability method, skip test
            self.logger.info("✅ Caption Burner initialized")
            
            # Initialize Google Sheets manager
            try:
                self.sheets_manager = GoogleSheetsManager()
                self.logger.info("✅ Google Sheets manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Google Sheets initialization failed: {e}")
                # Continue without sheets integration
            
            self.logger.info("✅ Enhanced Caption Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced Caption Manager initialization failed: {e}")
            return False
    
    def generate_perfect_captions(
        self, 
        content_item: Dict[str, Any],
        aligned_srt_path: str
    ) -> Dict[str, Any]:
        """
        Generate perfectly synchronized captions using pre-aligned SRT
        
        Args:
            content_item: Dictionary containing content information
            aligned_srt_path: Path to Whisper-aligned SRT file
            
        Returns:
            Dictionary with success status and captioned video path
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            if not content_id:
                self.logger.error("❌ Content ID is required")
                return {"success": False, "error": "No content ID"}
            
            if not Path(aligned_srt_path).exists():
                self.logger.error(f"❌ Aligned SRT file not found: {aligned_srt_path}")
                return {"success": False, "error": "SRT file not found"}
            
            self.logger.info(f"📝 Generating perfect captions for: {title}")
            
            # Find the video file to caption
            video_file_path = self._find_video_file_for_content(content_id)
            if not video_file_path:
                self.logger.error(f"❌ No video file found for content ID: {content_id}")
                return {"success": False, "error": "Video file not found"}
            
            self.logger.info(f"🎬 Found video: {Path(video_file_path).name}")
            self.logger.info(f"📝 Using aligned SRT: {Path(aligned_srt_path).name}")
            
            # Generate captioned video
            self.logger.info("🔥 Burning perfectly synced captions...")
            captioned_video_path = self.caption_burner.create_captioned_video(
                video_file_path=video_file_path,
                srt_file_path=aligned_srt_path,
                content_id=content_id,
                title=title
            )
            
            if not captioned_video_path:
                self.logger.error("❌ Caption burning failed")
                return {"success": False, "error": "Caption burning failed"}
            
            # Validate captioned video
            captioned_path = Path(captioned_video_path)
            if not captioned_path.exists() or captioned_path.stat().st_size == 0:
                self.logger.error("❌ Captioned video is invalid or empty")
                return {"success": False, "error": "Invalid captioned video"}
            
            # Get video info
            video_info = self._get_video_info(captioned_video_path)
            
            self.logger.info(f"🎉 Perfect caption generation completed!")
            self.logger.info(f"📺 Captioned video: {captioned_path.name}")
            self.logger.info(f"💾 File size: {video_info.get('size_mb', 0):.1f} MB")
            self.logger.info(f"⏱️ Duration: {video_info.get('duration_seconds', 0):.1f} seconds")
            
            # Try to save to Google Sheets (optional)
            self._save_captioned_video_path(content_id, captioned_video_path)
            
            return {
                "success": True,
                "captioned_video_path": captioned_video_path,
                "video_info": video_info,
                "srt_path": aligned_srt_path,
                "alignment_method": "whisper_perfect"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error generating perfect captions: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_captions_for_content(self, content_item: Dict[str, Any]) -> bool:
        """
        Legacy method for compatibility with existing code
        
        Note: This method expects aligned_srt_path in the content_item
        If not provided, it will look for pre-generated aligned SRT files
        """
        try:
            content_id = content_item.get('id', '')
            
            # Look for aligned SRT path in content item first
            aligned_srt_path = content_item.get('aligned_srt_path')
            
            # If not provided, look for existing aligned SRT files
            if not aligned_srt_path:
                aligned_srt_path = self._find_aligned_srt_for_content(content_id)
            
            if not aligned_srt_path:
                self.logger.error(f"❌ No aligned SRT found for content ID: {content_id}")
                return False
            
            result = self.generate_perfect_captions(content_item, aligned_srt_path)
            return result.get("success", False)
            
        except Exception as e:
            self.logger.error(f"❌ Error in legacy caption generation: {e}")
            return False
    
    def _find_video_file_for_content(self, content_id: str) -> Optional[str]:
        """Find the video file for a content item"""
        try:
            # Search in final videos directory
            video_files = (
                list(self.final_videos_dir.glob(f"*{content_id}*.mp4")) +
                list(self.final_videos_dir.glob(f"shorts_{content_id}*.mp4")) +
                list(self.final_videos_dir.glob(f"content_{content_id}*.mp4"))
            )
            
            if video_files:
                # Return the most recent file
                video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                return str(video_files[0])
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error finding video file: {e}")
            return None
    
    def _find_aligned_srt_for_content(self, content_id: str) -> Optional[str]:
        """Find aligned SRT file for a content item"""
        try:
            # Search for aligned SRT files
            srt_files = (
                list(self.captions_dir.glob(f"aligned_{content_id}*.srt")) +
                list(self.captions_dir.glob(f"*{content_id}*.srt"))
            )
            
            if srt_files:
                # Return the most recent file
                srt_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                return str(srt_files[0])
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error finding aligned SRT: {e}")
            return None
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video file information"""
        try:
            video_file = Path(video_path)
            if not video_file.exists():
                return {"error": "File not found"}
            
            file_size = video_file.stat().st_size
            
            # Get video duration using ffprobe (if available)
            duration = self._get_video_duration(video_path)
            
            return {
                "filename": video_file.name,
                "size_bytes": file_size,
                "size_mb": file_size / (1024 * 1024),
                "duration_seconds": duration,
                "format": "mp4",
                "created": datetime.fromtimestamp(video_file.stat().st_ctime).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting video info: {e}")
            return {"error": str(e)}
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe"""
        try:
            import subprocess
            import json
            
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data.get('format', {}).get('duration', 0))
                return duration
            else:
                return 0.0
                
        except Exception as e:
            self.logger.debug(f"Could not get video duration: {e}")
            return 0.0
    
    def _save_captioned_video_path(self, content_id: str, captioned_video_path: str):
        """Save captioned video path to Google Sheets (optional)"""
        try:
            if self.sheets_manager:
                self.sheets_manager.update_content_field(
                    content_id=content_id,
                    field_name='captioned_video',
                    field_value=captioned_video_path
                )
                self.logger.info("✅ Captioned video path saved to sheets")
            else:
                self.logger.debug("📋 Sheets manager not available, skipping save")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save captioned video path to sheets: {e}")
    
    def validate_caption_sync(
        self, 
        captioned_video_path: str, 
        aligned_srt_path: str
    ) -> Dict[str, Any]:
        """
        Validate that captions are properly synchronized
        
        Args:
            captioned_video_path: Path to captioned video
            aligned_srt_path: Path to aligned SRT file
            
        Returns:
            Validation results
        """
        try:
            # Basic file existence checks
            if not Path(captioned_video_path).exists():
                return {"valid": False, "error": "Captioned video not found"}
            
            if not Path(aligned_srt_path).exists():
                return {"valid": False, "error": "SRT file not found"}
            
            # Get video duration
            video_duration = self._get_video_duration(captioned_video_path)
            
            # Parse SRT to get last caption end time
            srt_end_time = self._get_srt_duration(aligned_srt_path)
            
            # Check duration match (within 1 second tolerance)
            duration_diff = abs(video_duration - srt_end_time)
            duration_match = duration_diff <= 1.0
            
            return {
                "valid": duration_match,
                "video_duration": video_duration,
                "srt_duration": srt_end_time,
                "duration_difference": duration_diff,
                "sync_quality": "excellent" if duration_diff <= 0.5 else "good" if duration_diff <= 1.0 else "poor"
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _get_srt_duration(self, srt_path: str) -> float:
        """Get the end time of the last caption in SRT file"""
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all time codes (format: HH:MM:SS,mmm --> HH:MM:SS,mmm)
            import re
            time_pattern = r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})'
            matches = re.findall(time_pattern, content)
            
            if not matches:
                return 0.0
            
            # Get the end time of the last match
            last_match = matches[-1]
            hours = int(last_match[4])
            minutes = int(last_match[5])
            seconds = int(last_match[6])
            milliseconds = int(last_match[7])
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            return total_seconds
            
        except Exception as e:
            self.logger.error(f"❌ Error getting SRT duration: {e}")
            return 0.0
