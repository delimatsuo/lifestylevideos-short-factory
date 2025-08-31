"""
Whisper Forced Alignment for Shorts Factory
Perfect caption synchronization using OpenAI Whisper word-level timestamps
"""

import openai
import logging
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile

from security.secure_config import config


class WhisperAlignment:
    """
    Whisper-based forced alignment for perfect caption synchronization
    Provides word-level timestamps from actual audio for precise caption timing
    """
    
    def __init__(self):
        """Initialize Whisper alignment"""
        self.logger = logging.getLogger(__name__)
        try:
            # Initialize OpenAI client with network resilience timeouts
            try:
                from security.network_resilience import get_timeout_for_operation
                connect_timeout, read_timeout = get_timeout_for_operation('ai_generation')
                
                # OpenAI client with timeout configuration for Whisper
                self.client = openai.OpenAI(
                    api_key=config.openai_api_key,
                    timeout=connect_timeout + read_timeout,  # Total timeout for transcription
                    max_retries=2  # Built-in retry mechanism
                )
            except ImportError:
                # Fallback with basic timeout
                self.client = openai.OpenAI(
                    api_key=config.openai_api_key,
                    timeout=180.0,  # 3 minutes for AI transcription
                    max_retries=2
                )
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OpenAI client for Whisper: {e}")
            self.client = None
        
        # Whisper settings
        self.model = "whisper-1"
        self.response_format = "verbose_json"  # Get detailed timing info
        self.timestamp_granularities = ["word"]  # Word-level timestamps
        
        self.logger.info("🎯 Whisper Alignment initialized")
    
    def get_word_level_timestamps(self, audio_file_path: str) -> Optional[List[Dict]]:
        """
        Get word-level timestamps from audio using Whisper
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            List of word timing dictionaries or None if failed
        """
        try:
            if not self.client:
                self.logger.error("❌ OpenAI client not initialized for Whisper")
                return None
                
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                self.logger.error(f"❌ Audio file not found: {audio_file_path}")
                return None
            
            self.logger.info(f"🎯 Getting word-level timestamps from: {audio_path.name}")
            
            # Open and transcribe audio with word timestamps
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format=self.response_format,
                    timestamp_granularities=self.timestamp_granularities
                )
            
            # Extract word-level timing data
            if hasattr(transcript, 'words') and transcript.words:
                word_timings = []
                
                for word_data in transcript.words:
                    word_timings.append({
                        'word': word_data.word,
                        'start': word_data.start,
                        'end': word_data.end
                    })
                
                self.logger.info(f"✅ Extracted {len(word_timings)} word timestamps")
                return word_timings
            
            else:
                self.logger.error("❌ No word-level timestamps in Whisper response")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get word timestamps: {e}")
            return None
    
    def align_script_to_audio(
        self, 
        script_text: str, 
        audio_file_path: str
    ) -> Optional[List[Dict]]:
        """
        Align script text to audio timestamps using Whisper
        
        Args:
            script_text: Original script text
            audio_file_path: Path to generated audio
            
        Returns:
            List of aligned caption segments with precise timing
        """
        try:
            # Get word-level timestamps from audio
            word_timings = self.get_word_level_timestamps(audio_file_path)
            
            if not word_timings:
                self.logger.error("❌ No word timings available for alignment")
                return None
            
            # Clean and split script text
            script_words = self._clean_and_split_text(script_text)
            
            # Align script words to audio timestamps
            aligned_segments = self._create_aligned_segments(script_words, word_timings)
            
            self.logger.info(f"✅ Created {len(aligned_segments)} aligned caption segments")
            return aligned_segments
            
        except Exception as e:
            self.logger.error(f"❌ Failed to align script to audio: {e}")
            return None
    
    def _clean_and_split_text(self, text: str) -> List[str]:
        """Clean text and split into words for alignment"""
        import re
        
        # Basic cleaning
        cleaned = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', text)  # Keep basic punctuation
        cleaned = ' '.join(cleaned.split())  # Normalize whitespace
        
        # Split into words (keeping punctuation attached)
        words = cleaned.split()
        
        return words
    
    def _create_aligned_segments(
        self, 
        script_words: List[str], 
        word_timings: List[Dict]
    ) -> List[Dict]:
        """
        Create caption segments from aligned words
        Optimal segment length: 3-8 words for mobile readability
        """
        segments = []
        current_segment_words = []
        segment_start_time = None
        
        # Parameters for segment creation
        min_words_per_segment = 3
        max_words_per_segment = 8
        max_segment_duration = 4.0  # Maximum 4 seconds per segment
        
        i = 0
        for timing_data in word_timings:
            if i >= len(script_words):
                break
                
            word = timing_data['word'].strip()
            start_time = timing_data['start']
            end_time = timing_data['end']
            
            # Start new segment
            if not current_segment_words:
                segment_start_time = start_time
            
            current_segment_words.append(word)
            
            # Check if we should end current segment
            should_end_segment = (
                len(current_segment_words) >= max_words_per_segment or  # Max words reached
                (end_time - segment_start_time) >= max_segment_duration or  # Max duration reached
                self._is_natural_break_point(word) and len(current_segment_words) >= min_words_per_segment  # Natural break
            )
            
            if should_end_segment:
                # Create segment
                segment_text = ' '.join(current_segment_words)
                
                segments.append({
                    'text': segment_text,
                    'start': segment_start_time,
                    'end': end_time,
                    'duration': end_time - segment_start_time,
                    'word_count': len(current_segment_words)
                })
                
                # Reset for next segment
                current_segment_words = []
                segment_start_time = None
            
            i += 1
        
        # Handle remaining words
        if current_segment_words and segment_start_time is not None:
            # Use last timing for end time
            last_end_time = word_timings[-1]['end'] if word_timings else segment_start_time + 2.0
            
            segment_text = ' '.join(current_segment_words)
            segments.append({
                'text': segment_text,
                'start': segment_start_time,
                'end': last_end_time,
                'duration': last_end_time - segment_start_time,
                'word_count': len(current_segment_words)
            })
        
        return segments
    
    def _is_natural_break_point(self, word: str) -> bool:
        """Check if word represents a natural break point for captions"""
        # Words that naturally end sentences or clauses
        break_indicators = ['.', '!', '?', ',', ';', ':', '--']
        
        return any(indicator in word for indicator in break_indicators)
    
    def generate_srt_from_alignment(
        self, 
        aligned_segments: List[Dict], 
        content_id: str
    ) -> Optional[str]:
        """
        Generate SRT file from aligned segments
        
        Args:
            aligned_segments: List of aligned caption segments
            content_id: Content identifier for filename
            
        Returns:
            Path to generated SRT file
        """
        try:
            if not aligned_segments:
                self.logger.error("❌ No aligned segments provided")
                return None
            
            # Create SRT content
            srt_content = []
            
            for i, segment in enumerate(aligned_segments, 1):
                start_time = self._seconds_to_srt_time(segment['start'])
                end_time = self._seconds_to_srt_time(segment['end'])
                text = segment['text']
                
                # SRT format
                srt_content.extend([
                    str(i),
                    f"{start_time} --> {end_time}",
                    text,
                    ""  # Empty line between segments
                ])
            
            # Write SRT file
            captions_dir = Path(config.working_directory) / "captions"
            captions_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            srt_filename = f"aligned_{content_id}_{timestamp}.srt"
            srt_path = captions_dir / srt_filename
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_content))
            
            self.logger.info(f"✅ Generated aligned SRT file: {srt_filename}")
            self.logger.info(f"📊 Segments: {len(aligned_segments)}")
            
            return str(srt_path)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate SRT from alignment: {e}")
            return None
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def validate_alignment_quality(self, aligned_segments: List[Dict]) -> Dict:
        """
        Validate the quality of alignment
        
        Returns:
            Quality metrics and recommendations
        """
        if not aligned_segments:
            return {"quality": "poor", "reason": "No segments"}
        
        total_duration = sum(seg['duration'] for seg in aligned_segments)
        avg_duration = total_duration / len(aligned_segments)
        avg_words = sum(seg['word_count'] for seg in aligned_segments) / len(aligned_segments)
        
        # Quality criteria
        quality_score = 0
        issues = []
        
        # Check average segment duration (1.5-3.5 seconds is ideal)
        if 1.5 <= avg_duration <= 3.5:
            quality_score += 25
        else:
            issues.append(f"Average duration {avg_duration:.1f}s not optimal (1.5-3.5s)")
        
        # Check average words per segment (3-7 is ideal)
        if 3 <= avg_words <= 7:
            quality_score += 25
        else:
            issues.append(f"Average {avg_words:.1f} words per segment not optimal (3-7)")
        
        # Check for segments that are too short or too long
        short_segments = [s for s in aligned_segments if s['duration'] < 0.8]
        long_segments = [s for s in aligned_segments if s['duration'] > 5.0]
        
        if len(short_segments) < len(aligned_segments) * 0.1:  # Less than 10% short
            quality_score += 25
        else:
            issues.append(f"{len(short_segments)} segments too short (<0.8s)")
            
        if len(long_segments) < len(aligned_segments) * 0.1:  # Less than 10% long
            quality_score += 25
        else:
            issues.append(f"{len(long_segments)} segments too long (>5.0s)")
        
        # Determine quality level
        if quality_score >= 75:
            quality = "excellent"
        elif quality_score >= 50:
            quality = "good"
        elif quality_score >= 25:
            quality = "fair"
        else:
            quality = "poor"
        
        return {
            "quality": quality,
            "score": quality_score,
            "total_segments": len(aligned_segments),
            "avg_duration": avg_duration,
            "avg_words": avg_words,
            "issues": issues
        }
