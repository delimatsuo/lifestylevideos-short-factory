"""
Caption Generation Integration for Shorts Factory
Creates synchronized SRT subtitle files from script text and audio timing
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import math

from core.config import config


class SRTCaptionGenerator:
    """Handles SRT subtitle file generation and synchronization"""
    
    def __init__(self):
        """Initialize SRT caption generator"""
        self.logger = logging.getLogger(__name__)
        
        # Caption settings - FIXED for better mobile readability and sync
        self.max_chars_per_line = 35  # FIXED: Shorter lines for mobile (was 40)
        self.max_lines_per_caption = 2  # Maximum lines per caption
        self.min_caption_duration = 0.8  # FIXED: Shorter minimum (was 1.0) for better sync
        self.max_caption_duration = 3.5  # FIXED: Shorter maximum (was 4.0) for better pacing
        self.caption_padding = 0.05  # FIXED: Less padding (was 0.1) for tighter sync
        
        # Working directory
        self.captions_dir = Path(config.working_directory) / "captions"
        self.ensure_captions_directory()
        
        self.logger.info("📝 SRT Caption Generator initialized")
    
    def ensure_captions_directory(self):
        """Ensure the captions directory exists"""
        try:
            self.captions_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Captions directory ready: {self.captions_dir}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create captions directory: {e}")
            raise
    
    def clean_script_text(self, script_text: str) -> str:
        """
        Clean script text for caption generation
        
        Args:
            script_text: Raw script text
            
        Returns:
            Cleaned script text suitable for captions
        """
        try:
            # Remove extra whitespace and normalize
            cleaned = ' '.join(script_text.split())
            
            # Remove or replace problematic characters
            cleaned = cleaned.replace('"', '"').replace('"', '"')  # Smart quotes
            cleaned = cleaned.replace(''', "'").replace(''', "'")  # Smart apostrophes
            cleaned = re.sub(r'[^\w\s\.\,\!\?\-\'\"\(\):;]', '', cleaned)  # Keep basic punctuation
            
            # Normalize punctuation spacing
            cleaned = re.sub(r'\s+([,.!?;:])', r'\1', cleaned)  # Remove space before punctuation
            cleaned = re.sub(r'([.!?])\s*', r'\1 ', cleaned)  # Ensure space after sentence endings
            
            self.logger.debug(f"📝 Cleaned script: {cleaned[:100]}...")
            return cleaned.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning script text: {e}")
            return script_text
    
    def split_text_into_segments(self, text: str) -> List[str]:
        """
        Split text into caption segments based on natural breaks
        
        Args:
            text: Cleaned script text
            
        Returns:
            List of text segments for captions
        """
        try:
            # First, split by sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            segments = []
            
            for sentence in sentences:
                # If sentence is short enough, use as-is
                if len(sentence) <= self.max_chars_per_line:
                    segments.append(sentence)
                    continue
                
                # Split longer sentences at natural breaks
                # Try to split at commas, conjunctions, or phrases
                words = sentence.split()
                current_segment = ""
                
                for word in words:
                    # Check if adding this word would exceed the limit
                    test_segment = current_segment + (" " if current_segment else "") + word
                    
                    if len(test_segment) <= self.max_chars_per_line:
                        current_segment = test_segment
                    else:
                        # Start new segment
                        if current_segment:
                            segments.append(current_segment.strip())
                        current_segment = word
                
                # Add remaining text
                if current_segment:
                    segments.append(current_segment.strip())
            
            # Remove empty segments
            segments = [seg for seg in segments if seg.strip()]
            
            self.logger.info(f"📝 Split text into {len(segments)} caption segments")
            return segments
            
        except Exception as e:
            self.logger.error(f"❌ Error splitting text into segments: {e}")
            # Fallback: simple word-based splitting
            words = text.split()
            segments = []
            current_segment = ""
            
            for word in words:
                test_segment = current_segment + (" " if current_segment else "") + word
                if len(test_segment) <= self.max_chars_per_line:
                    current_segment = test_segment
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = word
            
            if current_segment:
                segments.append(current_segment)
            
            return segments
    
    def calculate_caption_timing(self, segments: List[str], audio_duration: float) -> List[Tuple[float, float, str]]:
        """
        Calculate start and end times for each caption segment
        
        Args:
            segments: List of text segments
            audio_duration: Total audio duration in seconds
            
        Returns:
            List of (start_time, end_time, text) tuples
        """
        try:
            if not segments:
                return []
            
            # Calculate available time (excluding padding)
            total_padding_time = (len(segments) - 1) * self.caption_padding
            available_time = audio_duration - total_padding_time
            
            # Calculate base duration per segment based on text length
            total_chars = sum(len(seg) for seg in segments)
            caption_timings = []
            
            current_time = 0.0
            
            for i, segment in enumerate(segments):
                # Calculate duration based on text length AND estimated reading speed
                # Estimate reading time: ~150 words per minute for comfortable reading
                words_in_segment = len(segment.split())
                estimated_reading_time = (words_in_segment / 150) * 60  # Convert to seconds
                
                # Use combination of text proportion and reading time
                char_ratio = len(segment) / total_chars if total_chars > 0 else 1.0 / len(segments)
                proportion_time = available_time * char_ratio
                
                # Take the longer of the two for better readability
                base_duration = max(estimated_reading_time, proportion_time)
                
                # Apply min/max constraints
                duration = max(self.min_caption_duration, 
                              min(self.max_caption_duration, base_duration))
                
                start_time = current_time
                end_time = start_time + duration
                
                # Ensure we don't exceed total audio duration
                if end_time > audio_duration:
                    end_time = audio_duration
                    duration = end_time - start_time
                
                caption_timings.append((start_time, end_time, segment))
                
                # Move to next caption start time (with padding)
                current_time = end_time + self.caption_padding
                
                self.logger.debug(f"📝 Caption {i+1}: {start_time:.2f}-{end_time:.2f}s ({duration:.2f}s) - {segment[:30]}...")
            
            # Adjust timing if we have leftover time
            if caption_timings and current_time - self.caption_padding < audio_duration:
                remaining_time = audio_duration - (current_time - self.caption_padding)
                # Distribute remaining time proportionally
                for i, (start, end, text) in enumerate(caption_timings):
                    if i == len(caption_timings) - 1:  # Last caption gets the remaining time
                        caption_timings[i] = (start, end + remaining_time, text)
                        break
            
            self.logger.info(f"📝 Generated timing for {len(caption_timings)} captions over {audio_duration:.2f}s")
            return caption_timings
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating caption timing: {e}")
            return []
    
    def format_srt_timestamp(self, seconds: float) -> str:
        """
        Format seconds to SRT timestamp format (HH:MM:SS,mmm)
        
        Args:
            seconds: Time in seconds
            
        Returns:
            SRT formatted timestamp
        """
        try:
            total_seconds = int(seconds)
            milliseconds = int((seconds - total_seconds) * 1000)
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            secs = total_seconds % 60
            
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
            
        except Exception as e:
            self.logger.error(f"❌ Error formatting timestamp: {e}")
            return "00:00:00,000"
    
    def generate_srt_content(self, caption_timings: List[Tuple[float, float, str]]) -> str:
        """
        Generate SRT file content from caption timings
        
        Args:
            caption_timings: List of (start_time, end_time, text) tuples
            
        Returns:
            SRT file content as string
        """
        try:
            srt_content = ""
            
            for i, (start_time, end_time, text) in enumerate(caption_timings, 1):
                # Caption number
                srt_content += f"{i}\n"
                
                # Timestamp line
                start_timestamp = self.format_srt_timestamp(start_time)
                end_timestamp = self.format_srt_timestamp(end_time)
                srt_content += f"{start_timestamp} --> {end_timestamp}\n"
                
                # Caption text (break into lines if needed)
                lines = self.break_text_into_lines(text)
                for line in lines:
                    srt_content += f"{line}\n"
                
                # Empty line separator
                srt_content += "\n"
            
            self.logger.debug(f"📝 Generated SRT content: {len(srt_content)} characters")
            return srt_content
            
        except Exception as e:
            self.logger.error(f"❌ Error generating SRT content: {e}")
            return ""
    
    def break_text_into_lines(self, text: str) -> List[str]:
        """
        Break text into multiple lines if needed for better readability
        
        Args:
            text: Caption text
            
        Returns:
            List of text lines
        """
        try:
            if len(text) <= self.max_chars_per_line:
                return [text]
            
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                
                if len(test_line) <= self.max_chars_per_line:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                    
                    # Prevent too many lines
                    if len(lines) >= self.max_lines_per_caption - 1:
                        break
            
            if current_line:
                lines.append(current_line)
            
            return lines[:self.max_lines_per_caption]
            
        except Exception as e:
            self.logger.error(f"❌ Error breaking text into lines: {e}")
            return [text]
    
    def generate_srt_file(
        self, 
        script_text: str, 
        audio_duration: float, 
        content_id: str
    ) -> Optional[str]:
        """
        Generate complete SRT file from script text and audio duration
        
        Args:
            script_text: The video script text
            audio_duration: Duration of audio narration in seconds
            content_id: Unique identifier for the content
            
        Returns:
            Path to generated SRT file, or None if failed
        """
        try:
            self.logger.info(f"📝 Generating SRT file for content {content_id}")
            
            # Clean and prepare script text
            cleaned_text = self.clean_script_text(script_text)
            if not cleaned_text:
                self.logger.error("❌ No text available for caption generation")
                return None
            
            # Split into segments
            segments = self.split_text_into_segments(cleaned_text)
            if not segments:
                self.logger.error("❌ Failed to split text into segments")
                return None
            
            # Calculate timing
            caption_timings = self.calculate_caption_timing(segments, audio_duration)
            if not caption_timings:
                self.logger.error("❌ Failed to calculate caption timing")
                return None
            
            # Generate SRT content
            srt_content = self.generate_srt_content(caption_timings)
            if not srt_content:
                self.logger.error("❌ Failed to generate SRT content")
                return None
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            srt_filename = f"captions_{content_id}_{timestamp}.srt"
            srt_file_path = self.captions_dir / srt_filename
            
            with open(srt_file_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            self.logger.info(f"✅ SRT file generated: {srt_file_path}")
            self.logger.info(f"📊 Caption stats: {len(caption_timings)} segments over {audio_duration:.2f}s")
            
            return str(srt_file_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating SRT file: {e}")
            return None
    
    def validate_srt_file(self, srt_file_path: str) -> bool:
        """
        Validate that an SRT file is properly formatted
        
        Args:
            srt_file_path: Path to SRT file
            
        Returns:
            True if SRT file is valid, False otherwise
        """
        try:
            if not Path(srt_file_path).exists():
                self.logger.error(f"❌ SRT file not found: {srt_file_path}")
                return False
            
            with open(srt_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                self.logger.error("❌ SRT file is empty")
                return False
            
            # Basic format validation
            blocks = content.split('\n\n')
            caption_count = 0
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:  # Number, timestamp, text (minimum)
                    # Check caption number
                    if lines[0].isdigit():
                        # Check timestamp format
                        if ' --> ' in lines[1]:
                            caption_count += 1
            
            if caption_count > 0:
                self.logger.info(f"✅ SRT file validation passed: {caption_count} captions found")
                return True
            else:
                self.logger.error("❌ SRT file validation failed: no valid captions found")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Error validating SRT file: {e}")
            return False
