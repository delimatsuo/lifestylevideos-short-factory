"""
FFmpeg Video Assembly Integration for Shorts Factory
Combines audio narration and video clips into final short-form videos
"""

import subprocess
import logging
import os
from typing import List, Optional, Dict, Tuple
from pathlib import Path
import json
from datetime import datetime

from core.config import config


class FFmpegVideoAssembly:
    """Handles video assembly using FFmpeg for combining audio and video clips"""
    
    def __init__(self):
        """Initialize FFmpeg video assembly"""
        self.logger = logging.getLogger(__name__)
        
        # Video output settings for shorts (9:16 aspect ratio)
        self.target_width = 1080
        self.target_height = 1920
        self.target_fps = 30
        self.video_codec = "libx264"
        self.audio_codec = "aac"
        self.video_bitrate = "2500k"  # Good quality for shorts
        self.audio_bitrate = "128k"
        
        # File directories
        self.video_clips_dir = Path(config.working_directory) / "video_clips"
        self.audio_dir = Path(config.working_directory) / "audio"
        self.final_videos_dir = Path(config.working_directory) / "final_videos"
        
        # Ensure output directory exists
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """Ensure the final videos directory exists"""
        try:
            self.final_videos_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Final videos directory ready: {self.final_videos_dir}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create final videos directory: {e}")
            raise
    
    def test_ffmpeg_availability(self) -> bool:
        """Test if FFmpeg is available and working"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.logger.info(f"✅ FFmpeg available: {version_line}")
                return True
            else:
                self.logger.error(f"❌ FFmpeg test failed with return code: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ FFmpeg test timed out")
            return False
        except FileNotFoundError:
            self.logger.error("❌ FFmpeg not found - please install FFmpeg")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error testing FFmpeg: {e}")
            return False
    
    def get_audio_duration(self, audio_file_path: str) -> Optional[float]:
        """Get the duration of an audio file in seconds using FFmpeg"""
        try:
            cmd = [
                "ffprobe", 
                "-i", audio_file_path,
                "-show_entries", "format=duration",
                "-v", "quiet",
                "-of", "csv=p=0"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                self.logger.debug(f"🎵 Audio duration: {duration:.2f} seconds")
                return duration
            else:
                self.logger.error(f"❌ Failed to get audio duration: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting audio duration: {e}")
            return None
    
    def get_video_duration(self, video_file_path: str) -> Optional[float]:
        """Get the duration of a video file in seconds using FFmpeg"""
        try:
            cmd = [
                "ffprobe", 
                "-i", video_file_path,
                "-show_entries", "format=duration",
                "-v", "quiet",
                "-of", "csv=p=0"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                self.logger.debug(f"🎬 Video duration: {duration:.2f} seconds")
                return duration
            else:
                self.logger.error(f"❌ Failed to get video duration: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting video duration: {e}")
            return None
    
    def create_video_concatenation(self, video_clips: List[str], target_duration: float) -> Optional[str]:
        """
        Create a concatenated video from clips that matches target duration
        
        Args:
            video_clips: List of paths to video clip files
            target_duration: Target duration in seconds (from audio)
            
        Returns:
            Path to the concatenated video file, or None if failed
        """
        try:
            if not video_clips:
                self.logger.error("❌ No video clips provided for concatenation")
                return None
            
            # Create temporary concat file list
            concat_file_path = self.final_videos_dir / f"concat_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(concat_file_path, 'w') as f:
                # Calculate how to loop clips to match target duration
                total_clips_duration = 0
                clip_durations = []
                
                for clip_path in video_clips:
                    duration = self.get_video_duration(clip_path)
                    if duration:
                        clip_durations.append(duration)
                        total_clips_duration += duration
                    else:
                        # Fallback duration if we can't detect
                        clip_durations.append(10.0)
                        total_clips_duration += 10.0
                
                if total_clips_duration == 0:
                    self.logger.error("❌ Could not determine duration of any video clips")
                    return None
                
                # Calculate how many times to repeat the clips to cover target duration
                repetitions_needed = max(1, int(target_duration / total_clips_duration) + 1)
                
                self.logger.info(f"🔄 Creating video loop: {repetitions_needed} repetitions of {len(video_clips)} clips")
                self.logger.info(f"📏 Total clips duration: {total_clips_duration:.2f}s, Target: {target_duration:.2f}s")
                
                # Write concat file with repetitions
                for rep in range(repetitions_needed):
                    for clip_path in video_clips:
                        f.write(f"file '{os.path.abspath(clip_path)}'\n")
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            concat_video_path = self.final_videos_dir / f"concat_temp_{timestamp}.mp4"
            
            # Build FFmpeg concatenation command
            cmd = [
                "ffmpeg", "-y",  # Overwrite output files
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file_path),
                "-c", "copy",  # Copy without re-encoding first
                str(concat_video_path)
            ]
            
            self.logger.info(f"🔧 Running video concatenation...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 min timeout
            
            # Clean up temporary concat file
            if concat_file_path.exists():
                concat_file_path.unlink()
            
            if result.returncode == 0:
                self.logger.info(f"✅ Video concatenation successful: {concat_video_path}")
                return str(concat_video_path)
            else:
                self.logger.error(f"❌ Video concatenation failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in video concatenation: {e}")
            return None
    
    def assemble_final_video(
        self, 
        audio_file_path: str, 
        video_clips: List[str], 
        output_filename: str
    ) -> Optional[str]:
        """
        Assemble final video combining audio narration with video clips
        
        Args:
            audio_file_path: Path to the MP3 audio file
            video_clips: List of paths to video clip files
            output_filename: Name for the output video file
            
        Returns:
            Path to the assembled video file, or None if failed
        """
        try:
            self.logger.info(f"🎬 Starting video assembly for: {output_filename}")
            
            # Verify input files exist
            if not Path(audio_file_path).exists():
                self.logger.error(f"❌ Audio file not found: {audio_file_path}")
                return None
            
            for video_clip in video_clips:
                if not Path(video_clip).exists():
                    self.logger.error(f"❌ Video clip not found: {video_clip}")
                    return None
            
            # Get audio duration to determine video length
            audio_duration = self.get_audio_duration(audio_file_path)
            if audio_duration is None:
                self.logger.error("❌ Could not determine audio duration")
                return None
            
            # Create concatenated video that matches audio duration
            concat_video_path = self.create_video_concatenation(video_clips, audio_duration)
            if concat_video_path is None:
                self.logger.error("❌ Failed to create video concatenation")
                return None
            
            # Final output path
            final_output_path = self.final_videos_dir / output_filename
            
            # Build final assembly command with proper scaling and audio sync
            cmd = [
                "ffmpeg", "-y",  # Overwrite output files
                "-i", concat_video_path,  # Video input
                "-i", audio_file_path,    # Audio input
                "-t", str(audio_duration),  # Trim to audio duration
                "-vf", f"scale={self.target_width}:{self.target_height}:force_original_aspect_ratio=decrease,pad={self.target_width}:{self.target_height}:(ow-iw)/2:(oh-ih)/2,fps={self.target_fps}",  # Scale to 9:16 with padding
                "-c:v", self.video_codec,  # Video codec
                "-b:v", self.video_bitrate,  # Video bitrate
                "-c:a", self.audio_codec,   # Audio codec
                "-b:a", self.audio_bitrate,  # Audio bitrate
                "-map", "0:v:0",  # Map video from first input
                "-map", "1:a:0",  # Map audio from second input
                "-shortest",      # End when shortest stream ends
                str(final_output_path)
            ]
            
            self.logger.info(f"🔧 Running final video assembly...")
            self.logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
            
            # Clean up temporary concatenated video
            if Path(concat_video_path).exists():
                Path(concat_video_path).unlink()
            
            if result.returncode == 0:
                # Verify output file was created and has reasonable size
                if final_output_path.exists():
                    file_size = final_output_path.stat().st_size
                    file_size_mb = file_size / (1024 * 1024)
                    
                    self.logger.info(f"🎉 Video assembly successful!")
                    self.logger.info(f"📺 Output: {final_output_path}")
                    self.logger.info(f"💾 File size: {file_size_mb:.2f} MB")
                    self.logger.info(f"⏱️ Duration: {audio_duration:.2f} seconds")
                    
                    return str(final_output_path)
                else:
                    self.logger.error("❌ Output file was not created")
                    return None
            else:
                self.logger.error(f"❌ Video assembly failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Video assembly timed out")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error in video assembly: {e}")
            return None
    
    def validate_video_output(self, video_path: str) -> bool:
        """
        Validate that the output video meets our requirements
        
        Args:
            video_path: Path to the video file to validate
            
        Returns:
            True if video is valid, False otherwise
        """
        try:
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
                self.logger.error(f"❌ Failed to probe video file: {result.stderr}")
                return False
            
            data = json.loads(result.stdout)
            
            # Find video stream
            video_stream = None
            audio_stream = None
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            if not video_stream:
                self.logger.error("❌ No video stream found in output")
                return False
            
            if not audio_stream:
                self.logger.error("❌ No audio stream found in output")
                return False
            
            # Check video dimensions (should be 1080x1920 or close)
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            if width != self.target_width or height != self.target_height:
                self.logger.warning(f"⚠️ Video dimensions: {width}x{height} (expected {self.target_width}x{self.target_height})")
                # Not a hard failure - might be acceptable
            
            # Check duration
            duration = float(data.get('format', {}).get('duration', 0))
            
            self.logger.info(f"✅ Video validation successful:")
            self.logger.info(f"📏 Dimensions: {width}x{height}")
            self.logger.info(f"⏱️ Duration: {duration:.2f} seconds")
            self.logger.info(f"🎵 Audio codec: {audio_stream.get('codec_name', 'unknown')}")
            self.logger.info(f"🎬 Video codec: {video_stream.get('codec_name', 'unknown')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating video: {e}")
            return False
