"""
🎯 VOSK Caption Generator - THE WORKING SOLUTION
This is exactly how successful Reddit video creators achieve perfect synchronization.

Based on FullyAutomatedRedditVideoMakerBot's proven approach:
1. Extract audio from final video
2. Use VOSK speech recognition for exact word-level timestamps  
3. Generate captions with precise timing from actual audio

NO MORE GUESSING - VOSK measures the real timing!
"""

import os
import sys
import json
import wave
import urllib.request
import zipfile
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    from vosk import Model, KaldiRecognizer, SetLogLevel
except ImportError:
    logging.error("VOSK not installed. Run: pip install vosk")
    sys.exit(1)

from src.core.config import Config

class VoskCaptionGenerator:
    """
    🚀 THE BREAKTHROUGH SOLUTION 🚀
    
    This is the exact approach that successful creators use:
    - Extract audio from completed video
    - Use VOSK for precise word-level speech recognition  
    - Get exact start/end timestamps for each word
    - Generate perfectly synchronized captions
    
    NO MORE PREDICTION - JUST PERFECT MEASUREMENT!
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.model_path = None
        self.font_size = 85  # Smaller for karaoke-style multi-word captions
        self.y_offset = 570  # Position captions higher (avoids YouTube UI)
        
        # Caption styling (mobile optimized)
        self.font_color = (255, 255, 255, 255)  # White
        self.border_size = 15  # Black border for readability
        self.border_color = (0, 0, 0, 255)  # Black
        
    def download_vosk_model(self, model_name: str = "vosk-model-en-us-0.22") -> str:
        """Download VOSK model if not present"""
        model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
        model_path = Path(self.config.working_directory) / "vosk_models" / model_name
        
        if model_path.exists():
            self.logger.info(f"✅ VOSK model already exists: {model_path}")
            return str(model_path)
        
        # Create models directory
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📥 Downloading VOSK model {model_name}...")
        zip_path = model_path.parent / f"{model_name}.zip"
        
        try:
            # Use network resilience for VOSK model download
            try:
                from security.network_resilience import get_network_resilience_manager
                resilience_manager = get_network_resilience_manager()
                
                download_success = resilience_manager.resilient_download(model_url, zip_path)
                if not download_success:
                    raise Exception("Resilient download failed")
                    
            except ImportError:
                # Fallback with socket timeout
                import socket
                original_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(300.0)  # 5 minutes for large model downloads
                try:
                    urllib.request.urlretrieve(model_url, zip_path)
                finally:
                    socket.setdefaulttimeout(original_timeout)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(model_path.parent)
            
            zip_path.unlink()  # Remove zip file
            self.logger.info(f"✅ VOSK model downloaded and extracted: {model_path}")
            return str(model_path)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to download VOSK model: {e}")
            raise
    
    def extract_audio_from_video(self, video_path: str, audio_path: str) -> bool:
        """Extract audio from video for VOSK processing"""
        try:
            if Path(audio_path).exists():
                Path(audio_path).unlink()  # Remove existing file
            
            command = [
                "ffmpeg", "-y",  # Overwrite output
                "-i", video_path,
                "-acodec", "pcm_s16le",  # 16-bit PCM (VOSK requirement)
                "-ac", "1",              # Mono (VOSK requirement) 
                "-ar", "16000",          # 16kHz (VOSK requirement)
                audio_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"❌ FFmpeg failed: {result.stderr}")
                return False
                
            self.logger.info(f"✅ Audio extracted to {audio_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract audio: {e}")
            return False
    
    def transcribe_with_vosk(self, audio_path: str) -> List[Dict]:
        """
        🎯 THE MAGIC HAPPENS HERE 🎯
        
        Use VOSK to get EXACT word-level timestamps from real audio.
        This eliminates all synchronization guesswork!
        """
        try:
            if not self.model_path:
                self.model_path = self.download_vosk_model()
            
            SetLogLevel(0)  # Reduce VOSK logging
            
            # Use secure resource management for wave file
            import sys
            from pathlib import Path
            
            # Add src to path to import security module
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            try:
                from security.robust_resource_manager import safe_wave_open
                
                with safe_wave_open(audio_path, "rb") as wf:
                    if (wf.getnchannels() != 1 or 
                        wf.getsampwidth() != 2 or 
                        wf.getcomptype() != "NONE"):
                        raise ValueError("Audio must be WAV format mono PCM")
                    
                    # Initialize VOSK
                    model = Model(self.model_path)
                    rec = KaldiRecognizer(model, wf.getframerate())
                    rec.SetWords(True)  # 🔥 THIS GIVES WORD-LEVEL TIMING!
                    
                    results = []
                    while True:
                        data = wf.readframes(4000)
                        if len(data) == 0:
                            break
                        if rec.AcceptWaveform(data):
                            part_result = json.loads(rec.Result())
                            if 'result' in part_result:
                                results.extend(part_result['result'])
                    
                    # Get final result
                    final_result = json.loads(rec.FinalResult())
                    if 'result' in final_result:
                        results.extend(final_result['result'])
                        
            except ImportError:
                # Fallback to explicit resource management
                wf = None
                try:
                    wf = wave.open(audio_path, "rb")
                    if (wf.getnchannels() != 1 or 
                        wf.getsampwidth() != 2 or 
                        wf.getcomptype() != "NONE"):
                        raise ValueError("Audio must be WAV format mono PCM")
                    
                    # Initialize VOSK
                    model = Model(self.model_path)
                    rec = KaldiRecognizer(model, wf.getframerate())
                    rec.SetWords(True)  # 🔥 THIS GIVES WORD-LEVEL TIMING!
                    
                    results = []
                    while True:
                        data = wf.readframes(4000)
                        if len(data) == 0:
                            break
                        if rec.AcceptWaveform(data):
                            part_result = json.loads(rec.Result())
                            if 'result' in part_result:
                                results.extend(part_result['result'])
                    
                    # Get final result
                    final_result = json.loads(rec.FinalResult())
                    if 'result' in final_result:
                        results.extend(final_result['result'])
                        
                finally:
                    if wf:
                        try:
                            wf.close()
                            self.logger.debug("🔒 Closed wave file safely")
                        except Exception as e:
                            self.logger.warning(f"⚠️ Failed to close wave file: {e}")
            
            self.logger.info(f"🎯 VOSK transcribed {len(results)} words with exact timing!")
            
            # Log first few words for verification
            if results:
                for i, word in enumerate(results[:5]):
                    self.logger.info(f"Word {i+1}: '{word['word']}' ({word['start']:.2f}s - {word['end']:.2f}s)")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ VOSK transcription failed: {e}")
            return []
    
    def create_text_image(self, text: str, size: tuple, font_path: str) -> np.ndarray:
        """Create text image with border (mobile optimized)"""
        # Increase size to accommodate border
        increased_size = (size[0] + self.border_size * 2, 
                         size[1] + self.border_size * 2 + self.font_size // 2)
        img = Image.new('RGBA', increased_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            font = ImageFont.truetype(font_path, self.font_size)
        except OSError:
            # Fallback to default font
            font = ImageFont.load_default()
            self.font_size = 50  # Adjust for default font
        
        # Calculate text position
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((increased_size[0] - text_width) // 2, 
                   (increased_size[1] - text_height) // 2)
        
        # Draw border (black outline)
        for x_offset in range(-self.border_size, self.border_size + 1):
            for y_offset in range(-self.border_size, self.border_size + 1):
                draw.text((position[0] + x_offset, position[1] + y_offset), 
                         text, font=font, fill=self.border_color)
        
        # Draw main text (white)
        draw.text(position, text, font=font, fill=self.font_color)
        
        return np.array(img)
    
    def create_karaoke_caption_image(self, words_data: List[Dict], highlight_word: str, size: tuple, font_path: str) -> np.ndarray:
        """Create karaoke-style caption with highlighted current word"""
        # Calculate safe area (90% of width to prevent overflow)
        safe_width = int(size[0] * 0.9)
        safe_height = size[1]
        
        # Increase size to accommodate border
        increased_size = (size[0] + self.border_size * 2, 
                         size[1] + self.border_size * 2 + self.font_size // 2)
        img = Image.new('RGBA', increased_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load font with dynamic sizing
        font_size = self.font_size
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            font = ImageFont.load_default()
            font_size = 50
        
        # Create text line from words
        text_parts = [word_data['word'] for word_data in words_data]
        full_text = ' '.join(text_parts)
        
        # Auto-adjust font size to fit within safe area
        while font_size > 30:  # Minimum readable size
            try:
                font = ImageFont.truetype(font_path, font_size)
            except (OSError, TypeError):
                font = ImageFont.load_default()
            
            full_bbox = font.getbbox(full_text)
            full_width = full_bbox[2] - full_bbox[0]
            
            if full_width <= safe_width:
                break
            font_size -= 5
        
        # Calculate text dimensions with final font
        full_bbox = font.getbbox(full_text)
        full_width = full_bbox[2] - full_bbox[0]
        full_height = full_bbox[3] - full_bbox[1]
        
        # Calculate starting position (center the text within safe area)
        start_x = (increased_size[0] - full_width) // 2
        start_y = (increased_size[1] - full_height) // 2
        
        # Draw each word with highlighting
        current_x = start_x
        for word_data in words_data:
            word = word_data['word']
            word_bbox = font.getbbox(word)
            word_width = word_bbox[2] - word_bbox[0]
            
            # Determine colors
            if word == highlight_word:
                # Highlighted word (bright yellow/gold)
                text_color = (255, 215, 0, 255)  # Gold
                outline_color = (0, 0, 0, 255)   # Black outline
            else:
                # Regular word (white)
                text_color = (255, 255, 255, 255)  # White
                outline_color = (0, 0, 0, 255)     # Black outline
            
            # Draw word outline
            for x_offset in range(-self.border_size, self.border_size + 1):
                for y_offset in range(-self.border_size, self.border_size + 1):
                    draw.text((current_x + x_offset, start_y + y_offset), 
                             word, font=font, fill=outline_color)
            
            # Draw word text
            draw.text((current_x, start_y), word, font=font, fill=text_color)
            
            # Move to next word position (add space)
            current_x += word_width + font.getbbox(' ')[2]
        
        return np.array(img)
    
    def group_words_into_phrases(self, word_timings: List[Dict], max_words_per_phrase: int = 3) -> List[Dict]:
        """Group words into readable phrases for better caption display"""
        if not word_timings:
            return []
        
        phrases = []
        current_phrase_words = []
        
        for i, word_data in enumerate(word_timings):
            current_phrase_words.append(word_data)
            
            # Create phrase when we reach max words or natural break
            should_break = (
                len(current_phrase_words) >= max_words_per_phrase or
                i == len(word_timings) - 1 or  # Last word
                word_data['word'].endswith(('.', '!', '?', ','))  # Punctuation break
            )
            
            if should_break:
                if current_phrase_words:
                    phrase = {
                        'words': current_phrase_words.copy(),
                        'start': current_phrase_words[0]['start'],
                        'end': current_phrase_words[-1]['end'],
                        'text': ' '.join([w['word'] for w in current_phrase_words])
                    }
                    phrases.append(phrase)
                    current_phrase_words = []
        
        return phrases
    
    def generate_perfect_captions(self, video_path: str, output_path: str, 
                                 font_path: Optional[str] = None) -> str:
        """
        🏆 GENERATE PERFECTLY SYNCHRONIZED CAPTIONS 🏆
        
        The winning approach:
        1. Extract audio from final video
        2. Use VOSK for exact word timing  
        3. Overlay captions with precise timestamps
        
        Args:
            video_path: Path to the video file
            output_path: Path for the captioned video
            font_path: Path to font file (optional)
            
        Returns:
            Path to captioned video or None if failed
        """
        try:
            # Set up paths
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Video not found: {video_path}")
            
            # Temporary audio file
            temp_audio = Path(self.config.working_directory) / "temp" / "vosk_audio.wav"
            temp_audio.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"🎬 Processing video: {video_path.name}")
            
            # Step 1: Extract audio
            self.logger.info("🎵 Extracting audio for VOSK analysis...")
            if not self.extract_audio_from_video(str(video_path), str(temp_audio)):
                raise Exception("Failed to extract audio")
            
            # Step 2: VOSK transcription with exact timing
            self.logger.info("🔍 Running VOSK speech recognition...")
            word_timings = self.transcribe_with_vosk(str(temp_audio))
            
            if not word_timings:
                raise Exception("VOSK found no words - check audio quality")
            
            # Step 3: Create captioned video with MoviePy
            self.logger.info(f"🎯 Creating captions for {len(word_timings)} words...")
            
            from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
            
            # Load video
            video = VideoFileClip(str(video_path))
            caption_clips = []
            
            # Default font path
            if not font_path:
                font_path = Path(__file__).parent.parent.parent / "working_solution" / "fonts" / "Rubik-Black.ttf"
                if not font_path.exists():
                    # Try system font
                    font_path = "/System/Library/Fonts/Arial.ttf"
            
            # 🎭 NEW: Create karaoke-style captions with phrase grouping
            self.logger.info("🎤 Creating karaoke-style captions with word highlighting...")
            
            # Group words into readable phrases
            phrases = self.group_words_into_phrases(word_timings, max_words_per_phrase=3)
            self.logger.info(f"📝 Created {len(phrases)} caption phrases from {len(word_timings)} words")
            
            # Create caption clips for each phrase with word highlighting
            for phrase in phrases:
                phrase_words = phrase['words']
                phrase_start = phrase['start']
                phrase_end = phrase['end']
                
                # Create highlight clips for each word in the phrase
                for word_data in phrase_words:
                    word = word_data['word']
                    word_start = word_data['start']
                    word_end = word_data['end']
                    word_duration = word_end - word_start
                    
                    if word_duration <= 0:
                        continue
                    
                    # Create karaoke-style image with this word highlighted
                    img_array = self.create_karaoke_caption_image(
                        phrase_words,
                        highlight_word=word,
                        size=(video.w, 120),
                        font_path=str(font_path)
                    )
                    
                    # Create clip with exact word timing for highlighting
                    clip = ImageClip(img_array, duration=word_duration)
                    clip = clip.set_position(('center', video.h - self.y_offset))
                    clip = clip.set_start(word_start)
                    
                    caption_clips.append(clip)
            
            # Compose final video
            self.logger.info("🎬 Compositing final video with perfect sync...")
            final_video = CompositeVideoClip([video] + caption_clips)
            
            # Write output
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            final_video.write_videofile(
                str(output_path),
                fps=24,
                audio_codec='aac',
                codec='libx264'
            )
            
            # Cleanup
            final_video.close()
            video.close()
            if temp_audio.exists():
                temp_audio.unlink()
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            self.logger.info(f"✅ PERFECT SYNC ACHIEVED! Output: {output_path.name} ({file_size_mb:.1f}MB)")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ VOSK caption generation failed: {e}")
            return None

    def initialize(self) -> bool:
        """Initialize VOSK caption generator"""
        try:
            # Download model if needed
            self.model_path = self.download_vosk_model()
            self.logger.info("✅ VOSK Karaoke Caption Generator initialized - READY FOR PERFECT SYNC!")
            return True
        except Exception as e:
            self.logger.error(f"❌ VOSK initialization failed: {e}")
            return False

if __name__ == "__main__":
    # Test the VOSK generator
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    generator = VoskCaptionGenerator()
    if generator.initialize():
        print("🚀 VOSK Caption Generator ready!")
        print("This is the same approach used by successful Reddit video creators.")
    else:
        print("❌ Initialization failed")
