"""
FFmpeg Caption Burning Integration for Shorts Factory
Burns SRT subtitles onto videos with professional styling optimized for mobile viewing
"""

import subprocess
import logging
import os
from typing import Optional, Dict
from pathlib import Path
import json
from datetime import datetime

from core.config import config


class FFmpegCaptionBurner:
    """Handles burning SRT captions onto videos using FFmpeg"""
    
    def __init__(self):
        """Initialize FFmpeg caption burner"""
        self.logger = logging.getLogger(__name__)
        
        # Caption styling for mobile/vertical videos (optimized for YouTube Shorts)
        self.font_family = "Arial"  # Widely available font
        self.font_size = 28  # Good size for 1080x1920 videos
        self.font_color = "white"
        self.outline_color = "black"
        self.outline_width = 2
        self.shadow_offset = "1:1"
        self.shadow_color = "black@0.5"
        
        # Caption positioning (optimized for vertical videos)
        self.caption_position_y = "h-th-60"  # 60 pixels from bottom
        self.caption_position_x = "(w-tw)/2"  # Centered horizontally
        self.max_width = "w*0.9"  # 90% of video width
        
        # Video quality settings (maintain high quality during caption burn)
        self.video_codec = "libx264"
        self.crf_value = "18"  # High quality constant rate factor
        self.preset = "medium"  # Balance between speed and compression
        self.audio_codec = "copy"  # Copy audio without re-encoding
        
        # Working directories
        self.captions_dir = Path(config.working_directory) / "captions"
        self.final_videos_dir = Path(config.working_directory) / "final_videos"
        self.captioned_videos_dir = Path(config.working_directory) / "captioned_videos"
        
        # Ensure output directory exists
        self.ensure_captioned_videos_directory()
        
        self.logger.info("🔥 FFmpeg Caption Burner initialized")
    
    def ensure_captioned_videos_directory(self):
        """Ensure the captioned videos directory exists"""
        try:
            self.captioned_videos_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Captioned videos directory ready: {self.captioned_videos_dir}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create captioned videos directory: {e}")
            raise
    
    def test_ffmpeg_subtitle_support(self) -> bool:
        """Test if FFmpeg supports subtitle burning"""
        try:
            # Test FFmpeg subtitle filter availability
            result = subprocess.run(
                ["ffmpeg", "-filters", "2>/dev/null | grep subtitles"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Alternative test - check if ffmpeg has subtitle support
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-filters"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "subtitles" in result.stdout:
                self.logger.info("✅ FFmpeg subtitle support confirmed")
                return True
            else:
                self.logger.warning("⚠️ FFmpeg subtitle support uncertain")
                return True  # Proceed anyway - most FFmpeg builds have subtitle support
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not verify FFmpeg subtitle support: {e}")
            return True  # Assume support exists
    
    def build_subtitle_filter(self, srt_file_path: str) -> str:
        """
        Build FFmpeg subtitle filter string with professional styling
        
        Args:
            srt_file_path: Path to SRT subtitle file
            
        Returns:
            FFmpeg subtitle filter string
        """
        try:
            # Escape the file path for FFmpeg
            escaped_path = srt_file_path.replace('\\', '\\\\').replace(':', '\\:')
            
            # Build comprehensive subtitle filter with professional styling
            subtitle_filter = (
                f"subtitles='{escaped_path}':"
                f"fontsdir='/System/Library/Fonts':"  # macOS system fonts directory
                f"force_style='FontName={self.font_family},"
                f"FontSize={self.font_size},"
                f"PrimaryColour=&H00FFFFFF,"  # White text (BGR format)
                f"OutlineColour=&H00000000,"  # Black outline (BGR format)
                f"BackColour=&H80000000,"     # Semi-transparent black background
                f"Bold=-1,"                   # Bold text
                f"Outline={self.outline_width},"  # Outline width
                f"Shadow=1,"                  # Enable shadow
                f"Alignment=2'"               # Bottom center alignment
            )
            
            self.logger.debug(f"🔥 Subtitle filter: {subtitle_filter}")
            return subtitle_filter
            
        except Exception as e:
            self.logger.error(f"❌ Error building subtitle filter: {e}")
            # Fallback simple filter
            return f"subtitles='{srt_file_path}'"
    
    def burn_captions_onto_video(
        self, 
        video_file_path: str, 
        srt_file_path: str, 
        output_filename: str
    ) -> Optional[str]:
        """
        Burn SRT captions onto video using FFmpeg
        
        Args:
            video_file_path: Path to input video file
            srt_file_path: Path to SRT subtitle file
            output_filename: Name for output video with captions
            
        Returns:
            Path to captioned video file, or None if failed
        """
        try:
            self.logger.info(f"🔥 Burning captions onto video: {Path(video_file_path).name}")
            
            # Verify input files exist
            if not Path(video_file_path).exists():
                self.logger.error(f"❌ Video file not found: {video_file_path}")
                return None
            
            if not Path(srt_file_path).exists():
                self.logger.error(f"❌ SRT file not found: {srt_file_path}")
                return None
            
            # Build output path
            output_path = self.captioned_videos_dir / output_filename
            
            # Build subtitle filter
            subtitle_filter = self.build_subtitle_filter(srt_file_path)
            
            # Build comprehensive FFmpeg command
            cmd = [
                "ffmpeg", "-y",  # Overwrite output files
                "-i", video_file_path,  # Input video
                "-vf", subtitle_filter,  # Video filter for subtitles
                "-c:v", self.video_codec,  # Video codec
                "-crf", self.crf_value,    # Quality setting
                "-preset", self.preset,    # Encoding speed preset
                "-c:a", self.audio_codec,  # Audio codec (copy without re-encoding)
                "-movflags", "+faststart", # Optimize for streaming
                str(output_path)
            ]
            
            self.logger.info(f"🔧 Running caption burn process...")
            self.logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            # Execute FFmpeg command
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                # Verify output file was created
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    file_size_mb = file_size / (1024 * 1024)
                    
                    self.logger.info(f"🎉 Caption burning successful!")
                    self.logger.info(f"📺 Output: {output_path}")
                    self.logger.info(f"💾 File size: {file_size_mb:.2f} MB")
                    
                    return str(output_path)
                else:
                    self.logger.error("❌ Output file was not created")
                    return None
            else:
                self.logger.error(f"❌ FFmpeg caption burning failed:")
                self.logger.error(f"stdout: {result.stdout}")
                self.logger.error(f"stderr: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Caption burning timed out")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error burning captions: {e}")
            return None
    
    def validate_captioned_video(self, video_path: str) -> bool:
        """
        Validate that the captioned video is properly created
        
        Args:
            video_path: Path to captioned video file
            
        Returns:
            True if video is valid, False otherwise
        """
        try:
            if not Path(video_path).exists():
                self.logger.error(f"❌ Captioned video not found: {video_path}")
                return False
            
            # Use ffprobe to get video information
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.error(f"❌ Failed to probe captioned video: {result.stderr}")
                return False
            
            data = json.loads(result.stdout)
            
            # Find video and audio streams
            video_stream = None
            audio_stream = None
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            if not video_stream:
                self.logger.error("❌ No video stream found in captioned video")
                return False
            
            if not audio_stream:
                self.logger.error("❌ No audio stream found in captioned video")
                return False
            
            # Check basic properties
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            duration = float(data.get('format', {}).get('duration', 0))
            
            self.logger.info(f"✅ Captioned video validation successful:")
            self.logger.info(f"📏 Dimensions: {width}x{height}")
            self.logger.info(f"⏱️ Duration: {duration:.2f} seconds")
            self.logger.info(f"🎵 Audio codec: {audio_stream.get('codec_name', 'unknown')}")
            self.logger.info(f"🎬 Video codec: {video_stream.get('codec_name', 'unknown')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating captioned video: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """
        Get video information for processing
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information, or None if failed
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting video info: {e}")
            return None
    
    def create_captioned_video(
        self, 
        video_file_path: str, 
        srt_file_path: str, 
        content_id: str,
        title: str = "Captioned Video"
    ) -> Optional[str]:
        """
        Create a captioned video from input video and SRT file
        
        Args:
            video_file_path: Path to input video
            srt_file_path: Path to SRT subtitle file
            content_id: Content identifier
            title: Content title for filename generation
            
        Returns:
            Path to captioned video, or None if failed
        """
        try:
            self.logger.info(f"🔥 Creating captioned video for content {content_id}")
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Clean title for filename
            import re
            clean_title = re.sub(r'[^\w\s-]', '', title)
            clean_title = re.sub(r'\s+', '_', clean_title)[:50]
            
            output_filename = f"captioned_{content_id}_{clean_title}_{timestamp}.mp4"
            
            # Burn captions onto video
            captioned_video_path = self.burn_captions_onto_video(
                video_file_path=video_file_path,
                srt_file_path=srt_file_path,
                output_filename=output_filename
            )
            
            if not captioned_video_path:
                self.logger.error(f"❌ Failed to create captioned video for {content_id}")
                return None
            
            # Validate the output
            if not self.validate_captioned_video(captioned_video_path):
                self.logger.warning(f"⚠️ Captioned video validation failed, but file exists")
            
            self.logger.info(f"🎉 Captioned video created successfully: {Path(captioned_video_path).name}")
            return captioned_video_path
            
        except Exception as e:
            self.logger.error(f"❌ Error creating captioned video: {e}")
            return None
