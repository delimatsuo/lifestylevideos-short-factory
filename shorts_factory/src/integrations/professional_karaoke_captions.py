"""
🎤 PROFESSIONAL KARAOKE CAPTIONS - YOUTUBE SHORTS STANDARD
Exactly how successful creators do it: 2 lines + word highlighting

Based on analysis of viral YouTube Shorts creators:
- 2 lines of text (6-8 words per line)  
- Current word highlighted in gold/yellow
- Other words in white
- Text stays on screen longer (not rapid single words)
- Bottom third positioning (avoids YouTube UI)
"""

import os
import sys
import json
import wave
import urllib.request
import zipfile
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    from vosk import Model, KaldiRecognizer, SetLogLevel
except ImportError:
    logging.error("VOSK not installed. Run: pip install vosk")
    sys.exit(1)

from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.config import Config

class ProfessionalKaraokeGenerator:
    """
    Professional 2-line karaoke captions exactly like successful YouTube Shorts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.model = None
        self.model_path = None
        
        # PROFESSIONAL YOUTUBE SHORTS SETTINGS (FIXED FOR NO CUTOFF)
        self.font_size = 65   # Smaller to prevent cutoff
        self.line_height = 75  # Tighter spacing
        self.y_offset = 350   # Higher from bottom (more clearance from YouTube UI)
        self.border_size = 2  # Thinner border (less visual clutter)
        self.font_color = (255, 255, 255, 255)  # White
        self.highlight_color = (255, 215, 0, 255)  # Gold/Yellow highlight
        self.border_color = (0, 0, 0, 255)      # Black border
        
        # Caption timing settings for 2-line format (CONSERVATIVE FOR NO CUTOFF)
        self.words_per_line = 5  # Fewer words per line to prevent cutoff  
        self.min_display_time = 2.5  # Longer display time for better readability
        self.max_display_time = 4.5  # More time to read multiple words
        
    def download_vosk_model(self, model_name="vosk-model-en-us-0.22"):
        """Download VOSK model if not present"""
        model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
        model_path = Path(self.config.working_directory) / "vosk_models" / model_name
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not model_path.exists():
            self.logger.info(f"📥 Downloading VOSK model {model_name}...")
            try:
                zip_path, _ = urllib.request.urlretrieve(model_url)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(model_path.parent)
                os.remove(zip_path)
                self.logger.info("✅ VOSK model downloaded and extracted")
            except Exception as e:
                self.logger.error(f"❌ Failed to download VOSK model: {e}")
                return None
        
        return str(model_path)
    
    def initialize(self) -> bool:
        """Initialize VOSK model"""
        try:
            self.model_path = self.download_vosk_model()
            if not self.model_path:
                return False
            
            SetLogLevel(0)  # Reduce VOSK logging
            self.model = Model(self.model_path)
            self.logger.info("✅ Professional Karaoke Generator initialized - 2-LINE FORMAT!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ VOSK initialization failed: {e}")
            return False
    
    def extract_audio(self, video_path: str, audio_path: str) -> bool:
        """Extract audio from video for VOSK processing"""
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",
            audio_path
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
            self.logger.info(f"✅ Audio extracted to {audio_path}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Audio extraction failed: {e}")
            return False
    
    def transcribe_audio(self, audio_path: str) -> List[Dict]:
        """Transcribe audio with VOSK - get word-level timing"""
        if not self.model:
            self.logger.error("❌ VOSK model not initialized")
            return []
        
        # Use secure resource management for wave file
        import sys
        from pathlib import Path
        
        # Add src to path to import security module  
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        try:
            from security.robust_resource_manager import safe_wave_open
            
            with safe_wave_open(audio_path, "rb") as wf:
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    self.logger.error("❌ Audio file must be WAV format mono PCM")
                    return []
                    
                # Process audio with automatic wave file cleanup
                return self._process_audio_with_vosk(wf, script)
                
        except ImportError:
            # Fallback to explicit resource management
            wf = None
            try:
                wf = wave.open(audio_path, "rb")
                if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                    self.logger.error("❌ Audio file must be WAV format mono PCM")
                    return []
                    
                return self._process_audio_with_vosk(wf, script)
                
            finally:
                if wf:
                    try:
                        wf.close()
                        self.logger.debug("🔒 Closed wave file safely")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to close wave file: {e}")
        
    def _process_audio_with_vosk(self, wf, script: str) -> List[dict]:
        """Process audio file with VOSK for word-level timestamps"""
        try:
            
            rec = KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)  # Enable word-level timing
            
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    part_result = json.loads(rec.Result())
                    results.append(part_result)
            
            part_result = json.loads(rec.FinalResult())
            results.append(part_result)
            
            # Extract word timings
            words = []
            for r in results:
                if 'result' in r:
                    words.extend(r['result'])
            
            self.logger.info(f"🎯 VOSK transcribed {len(words)} words with exact timing!")
            return words
            
        except Exception as e:
            self.logger.error(f"❌ VOSK transcription failed: {e}")
            return []
    
    def group_words_into_two_lines(self, word_timings: List[Dict]) -> List[Dict]:
        """
        Group words into 2-line caption blocks like professional YouTube Shorts
        Each block contains ~14 words (7 per line) and stays on screen 2-4 seconds
        """
        if not word_timings:
            return []
        
        caption_blocks = []
        current_block_words = []
        block_start_time = 0
        
        for i, word_data in enumerate(word_timings):
            if not current_block_words:
                block_start_time = word_data.get('start', 0)
            
            current_block_words.append(word_data)
            
            # Create block when we have enough words or reached end
            should_create_block = (
                len(current_block_words) >= (self.words_per_line * 2) or  # 14 words (2 lines × 7 words)
                i == len(word_timings) - 1 or  # Last word
                (len(current_block_words) >= self.words_per_line and 
                 word_data['word'].endswith(('.', '!', '?')))  # Natural sentence break
            )
            
            if should_create_block and current_block_words:
                block_end_time = current_block_words[-1].get('end', block_start_time + self.min_display_time)
                block_duration = max(block_end_time - block_start_time, self.min_display_time)
                block_duration = min(block_duration, self.max_display_time)
                
                # Split words into 2 lines
                words_line1 = current_block_words[:self.words_per_line]
                words_line2 = current_block_words[self.words_per_line:] if len(current_block_words) > self.words_per_line else []
                
                caption_blocks.append({
                    'start_time': block_start_time,
                    'end_time': block_start_time + block_duration,
                    'duration': block_duration,
                    'line1_words': words_line1,
                    'line2_words': words_line2,
                    'all_words': current_block_words
                })
                
                current_block_words = []
        
        self.logger.info(f"📝 Created {len(caption_blocks)} professional 2-line caption blocks")
        return caption_blocks
    
    def create_two_line_karaoke_image(self, caption_block: Dict, current_word: str, 
                                    size: tuple, font_path: str) -> np.ndarray:
        """
        Create 2-line karaoke caption image with word highlighting
        Line 1: First ~7 words
        Line 2: Next ~7 words  
        Current word highlighted in gold, others in white
        """
        # Calculate image size with padding
        img_width = size[0]
        img_height = self.line_height * 2 + self.border_size * 4  # Space for 2 lines
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            font = ImageFont.truetype(font_path, self.font_size)
        except (OSError, TypeError):
            font = ImageFont.load_default()
            self.font_size = 50
        
        # Render Line 1
        if caption_block['line1_words']:
            line1_text = ' '.join([w['word'] for w in caption_block['line1_words']])
            line1_y = self.border_size
            self._draw_line_with_highlight(
                draw, font, line1_text, caption_block['line1_words'], 
                current_word, img_width, line1_y
            )
        
        # Render Line 2  
        if caption_block['line2_words']:
            line2_text = ' '.join([w['word'] for w in caption_block['line2_words']])
            line2_y = self.border_size + self.line_height
            self._draw_line_with_highlight(
                draw, font, line2_text, caption_block['line2_words'], 
                current_word, img_width, line2_y
            )
        
        return np.array(img)
    
    def _draw_line_with_highlight(self, draw, font, line_text: str, words_data: List[Dict], 
                                current_word: str, img_width: int, y_position: int):
        """Draw a single line with word-by-word highlighting"""
        
        # Calculate total line width and ensure it fits safely
        line_bbox = font.getbbox(line_text)
        line_width = line_bbox[2] - line_bbox[0]
        
        # Safe area: leave 10% margin on each side (80% of screen width)
        safe_width = img_width * 0.80
        margin = img_width * 0.10
        
        # If line is too wide, adjust font size down until it fits
        original_font_size = self.font_size
        while line_width > safe_width and self.font_size > 30:
            self.font_size -= 2
            try:
                font = ImageFont.truetype(font.path, self.font_size)
            except:
                font = ImageFont.load_default()
            line_bbox = font.getbbox(line_text)
            line_width = line_bbox[2] - line_bbox[0]
        
        # Center within safe area
        start_x = margin + (safe_width - line_width) // 2
        
        current_x = start_x
        
        for word_data in words_data:
            word = word_data['word']
            word_bbox = font.getbbox(word)
            word_width = word_bbox[2] - word_bbox[0]
            
            # Choose color: gold for current word, white for others
            if word == current_word:
                text_color = self.highlight_color
            else:
                text_color = self.font_color
            
            # Draw border (black outline)
            for x_offset in range(-self.border_size, self.border_size + 1):
                for y_offset in range(-self.border_size, self.border_size + 1):
                    draw.text((current_x + x_offset, y_position + y_offset), 
                             word, font=font, fill=self.border_color)
            
            # Draw main text
            draw.text((current_x, y_position), word, font=font, fill=text_color)
            
            # Move to next word position (add space)
            current_x += word_width + font.getbbox(' ')[2]
    
    def generate_professional_karaoke_captions(self, video_path: str, output_path: str) -> Optional[str]:
        """Generate professional 2-line karaoke captions like successful YouTube Shorts"""
        try:
            if not self.model:
                self.logger.error("❌ VOSK not initialized")
                return None
            
            # Create temporary audio file
            temp_dir = Path(self.config.working_directory) / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_audio = temp_dir / "professional_karaoke_audio.wav"
            
            self.logger.info(f"🎬 Creating PROFESSIONAL 2-line karaoke captions: {Path(video_path).name}")
            
            # Step 1: Extract audio from final video
            if not self.extract_audio(video_path, str(temp_audio)):
                return None
            
            # Step 2: Transcribe with VOSK for exact word timing
            word_timings = self.transcribe_audio(str(temp_audio))
            if not word_timings:
                self.logger.error("❌ No words transcribed")
                return None
            
            self.logger.info(f"📊 Words transcribed: {len(word_timings)}")
            
            # Step 3: Group into 2-line caption blocks
            caption_blocks = self.group_words_into_two_lines(word_timings)
            if not caption_blocks:
                self.logger.error("❌ No caption blocks created")
                return None
            
            # Step 4: Create video with 2-line karaoke captions
            video = VideoFileClip(video_path)
            
            # Find font path
            font_paths = [
                str(Path(__file__).parent.parent.parent / "working_solution" / "fonts" / "Rubik-Black.ttf"),
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/arial.ttf"
            ]
            
            font_path = None
            for fp in font_paths:
                if Path(fp).exists():
                    font_path = fp
                    break
            
            if not font_path:
                self.logger.error("❌ No font found")
                return None
            
            self.logger.info(f"🔤 Using font: {Path(font_path).name}")
            self.logger.info(f"🎭 Creating {len(caption_blocks)} professional 2-line karaoke blocks...")
            
            caption_clips = []
            
            # Create caption clips for each block with word highlighting
            for block_idx, block in enumerate(caption_blocks):
                # For each word in the block, create a clip with that word highlighted
                for word_data in block['all_words']:
                    word = word_data['word']
                    word_start = word_data['start']
                    word_end = word_data['end'] 
                    word_duration = word_end - word_start
                    
                    if word_duration <= 0:
                        continue
                    
                    # Create 2-line image with this word highlighted
                    img_array = self.create_two_line_karaoke_image(
                        block,
                        current_word=word,
                        size=(video.w, self.line_height * 2 + 50),
                        font_path=font_path
                    )
                    
                    # Create clip with exact word timing for highlighting
                    clip = ImageClip(img_array, duration=word_duration)
                    clip = clip.set_position(('center', video.h - self.y_offset))
                    clip = clip.set_start(word_start)
                    
                    caption_clips.append(clip)
            
            # Compose final video
            self.logger.info(f"🎬 Compositing video with {len(caption_clips)} professional karaoke clips...")
            final_video = CompositeVideoClip([video] + caption_clips)
            
            # Write output video
            self.logger.info(f"💾 Writing professional karaoke video...")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Clean up
            try:
                temp_audio.unlink()
                video.close()
                final_video.close()
            except:
                pass
            
            self.logger.info(f"✅ PROFESSIONAL 2-LINE KARAOKE COMPLETE: {Path(output_path).name}")
            self.logger.info(f"🎯 Format: 2 lines × {self.words_per_line} words with gold highlighting")
            self.logger.info(f"📺 Style: Exactly like successful YouTube Shorts creators!")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ Professional karaoke generation failed: {e}")
            return None
