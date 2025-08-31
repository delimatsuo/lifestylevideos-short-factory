"""
🎯 SIMPLE VOSK CAPTION GENERATOR - EXACT COPY OF WORKING SOLUTION
Based on FullyAutomatedRedditVideoMakerBot's proven approach.

NO FANCY FEATURES - JUST WHAT WORKS:
- Extract audio from final video
- VOSK word-level timing
- Simple word-by-word captions (no karaoke)
- Exact same positioning and sizing as working solution
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
from typing import List, Dict, Optional

try:
    from vosk import Model, KaldiRecognizer, SetLogLevel
except ImportError:
    logging.error("VOSK not installed. Run: pip install vosk")
    sys.exit(1)

from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.core.config import Config

class SimpleVoskGenerator:
    """
    Simple VOSK caption generator - exact replica of working solution
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.model = None
        self.model_path = None
        
        # EXACT SETTINGS FROM WORKING SOLUTION
        self.font_size = 110  # Same as working solution
        self.y_offset = 570   # Same as working solution (moving subtitles higher up)
        self.border_size = 15 # Same as working solution
        self.font_color = (255, 255, 255, 255)  # White
        self.border_color = (0, 0, 0, 255)      # Black border
        
    def download_vosk_model(self, model_name="vosk-model-en-us-0.22"):
        """Download VOSK model if not present - exact copy from working solution"""
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
            self.logger.info("✅ Simple VOSK Generator initialized - EXACT WORKING SOLUTION!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ VOSK initialization failed: {e}")
            return False
    
    def extract_audio(self, video_path: str, audio_path: str) -> bool:
        """Extract audio from video - exact copy from working solution"""
        if os.path.exists(audio_path):
            self.logger.info(f"File '{audio_path}' already exists. Overwriting...")
            os.remove(audio_path)
        
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-acodec", "pcm_s16le",  # EXACT SAME AS WORKING SOLUTION
            "-ac", "1",              # EXACT SAME AS WORKING SOLUTION
            "-ar", "16000",          # EXACT SAME AS WORKING SOLUTION  
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
        """Transcribe audio with VOSK - exact copy from working solution"""
        if not self.model:
            self.logger.error("❌ VOSK model not initialized")
            return []
        
        try:
            wf = wave.open(audio_path, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                self.logger.error("❌ Audio file must be WAV format mono PCM")
                return []
            
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
            
            # Extract word timings - EXACT SAME AS WORKING SOLUTION
            words = []
            for r in results:
                if 'result' in r:
                    words.extend(r['result'])
            
            self.logger.info(f"🎯 VOSK transcribed {len(words)} words with exact timing!")
            return words
            
        except Exception as e:
            self.logger.error(f"❌ VOSK transcription failed: {e}")
            return []
    
    def create_text_image(self, text: str, size: tuple, font_path: str) -> np.ndarray:
        """Create text image - exact copy from working solution"""
        # EXACT SAME PARAMETERS AS WORKING SOLUTION
        increased_size = (size[0] + self.border_size * 2, 
                         size[1] + self.border_size * 2 + self.font_size // 2)
        img = Image.new('RGBA', increased_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load font - EXACT SAME AS WORKING SOLUTION
        try:
            font = ImageFont.truetype(font_path, self.font_size)
        except (OSError, TypeError):
            font = ImageFont.load_default()
            self.font_size = 50  # Fallback size
        
        # Calculate text position - EXACT SAME AS WORKING SOLUTION
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((increased_size[0] - text_width) // 2, 
                   (increased_size[1] - text_height) // 2)
        
        # Draw border - EXACT SAME AS WORKING SOLUTION  
        for x_offset in range(-self.border_size, self.border_size + 1):
            for y_offset in range(-self.border_size, self.border_size + 1):
                draw.text((position[0] + x_offset, position[1] + y_offset), 
                         text, font=font, fill=self.border_color)
        
        # Draw main text - EXACT SAME AS WORKING SOLUTION
        draw.text(position, text, font=font, fill=self.font_color)
        
        return np.array(img)
    
    def create_caption_clips(self, word_timings: List[Dict], video_width: int, 
                           video_height: int, font_path: str) -> List:
        """Create caption clips - exact copy from working solution"""
        caption_clips = []
        
        # EXACT SAME LOOP AS WORKING SOLUTION - ONE WORD AT A TIME
        for word in word_timings:
            if 'word' not in word or 'start' not in word or 'end' not in word:
                continue
                
            duration = word['end'] - word['start']
            if duration <= 0:
                continue
            
            # Create text image - EXACT SAME PARAMETERS AS WORKING SOLUTION
            img_array = self.create_text_image(
                word['word'], 
                (video_width, 120),  # EXACT SAME SIZE
                font_path
            )
            
            # Create clip - EXACT SAME AS WORKING SOLUTION
            clip = ImageClip(img_array, duration=duration)
            
            # Position clip - EXACT SAME AS WORKING SOLUTION
            clip = clip.set_position(('center', video_height - self.y_offset))
            clip = clip.set_start(word['start'])
            
            caption_clips.append(clip)
        
        self.logger.info(f"✅ Created {len(caption_clips)} simple caption clips")
        return caption_clips
    
    def generate_simple_captions(self, video_path: str, output_path: str) -> Optional[str]:
        """Generate simple captions - exact replica of working solution approach"""
        try:
            if not self.model:
                self.logger.error("❌ VOSK not initialized")
                return None
            
            # Create temporary audio file
            temp_dir = Path(self.config.working_directory) / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_audio = temp_dir / "simple_vosk_audio.wav"
            
            self.logger.info(f"🎬 Processing video with SIMPLE approach: {Path(video_path).name}")
            
            # Step 1: Extract audio - EXACT SAME AS WORKING SOLUTION
            if not self.extract_audio(video_path, str(temp_audio)):
                return None
            
            # Step 2: Transcribe with VOSK - EXACT SAME AS WORKING SOLUTION
            word_timings = self.transcribe_audio(str(temp_audio))
            if not word_timings:
                self.logger.error("❌ No words transcribed")
                return None
            
            self.logger.info(f"📊 First 5 words: {[w.get('word', '') for w in word_timings[:5]]}")
            
            # Step 3: Create video with captions - EXACT SAME AS WORKING SOLUTION
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
            
            # Create caption clips - EXACT SAME AS WORKING SOLUTION
            caption_clips = self.create_caption_clips(
                word_timings, 
                video.w, 
                video.h, 
                font_path
            )
            
            # Overlay captions on video - EXACT SAME AS WORKING SOLUTION
            final_video = CompositeVideoClip([video] + caption_clips)
            
            # Write output video - EXACT SAME AS WORKING SOLUTION
            self.logger.info(f"💾 Writing captioned video...")
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
            
            self.logger.info(f"✅ SIMPLE CAPTIONS COMPLETE: {Path(output_path).name}")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ Simple caption generation failed: {e}")
            return None

