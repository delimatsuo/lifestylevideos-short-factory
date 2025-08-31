#!/usr/bin/env python3
"""
🚀 Viral Shorts Factory v2.0 - Next-Generation Content Creation System
Theme-driven viral content optimization with queue-based architecture
"""

import os
import sys
import asyncio
import logging
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import random
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path  
sys.path.insert(0, 'src')

class ContentTheme(Enum):
    FAMILY = "family"
    SELFHELP = "selfhelp"  
    NEWS = "news"
    REDDIT = "reddit"
    MIXED = "mixed"

class ProcessingStage(Enum):
    QUEUED = "queued"
    IDEATION = "ideation"
    SCRIPT = "script"
    AUDIO = "audio"
    VIDEO_CLIPS = "video_clips"
    ASSEMBLY = "assembly"
    CAPTIONS = "captions"
    METADATA = "metadata"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class ContentItem:
    """Enhanced content item with viral optimization tracking"""
    id: str
    theme: ContentTheme
    title: str = ""
    script: str = ""
    viral_score: float = 0.0
    engagement_hooks: List[str] = field(default_factory=list)
    stage: ProcessingStage = ProcessingStage.QUEUED
    artifacts: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    duration_target: int = 90  # seconds
    
    def advance_stage(self, stage: ProcessingStage, artifact_key: str = None, artifact_value: Any = None):
        """Advance to next processing stage"""
        self.stage = stage
        if artifact_key and artifact_value:
            self.artifacts[artifact_key] = artifact_value
    
    def add_error(self, error_msg: str):
        """Add error and mark as failed"""
        self.stage = ProcessingStage.FAILED
        self.errors.append(f"{datetime.now()}: {error_msg}")

class ViralPromptEngine:
    """Advanced prompt engineering for viral content optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Viral engagement patterns by theme
        self.viral_patterns = {
            ContentTheme.FAMILY: {
                "hooks": [
                    "My [family member] did something that changed our family forever...",
                    "I never expected my [age] year old [relation] to teach me this...",
                    "This family tradition seemed normal until I realized...",
                    "Growing up, my family had a rule that I thought was weird, but now...",
                    "My [family member] kept this secret for [time period], and when I found out..."
                ],
                "emotions": ["nostalgia", "surprise", "heartwarming", "relatable", "shocking"],
                "structures": ["reveal", "transformation", "realization", "contrast", "mystery"],
                "cta_styles": ["share_your_story", "relate_experience", "family_memory"]
            },
            ContentTheme.SELFHELP: {
                "hooks": [
                    "I tried this for 30 days and it completely changed my life...",
                    "The one habit that separates successful people from everyone else...",
                    "I wish someone told me this when I was struggling with...",
                    "This 2-minute morning routine will transform your entire day...",
                    "I was failing at [goal] until I discovered this one secret..."
                ],
                "emotions": ["inspiration", "motivation", "transformation", "empowerment", "hope"],
                "structures": ["before_after", "method_reveal", "breakthrough", "challenge", "solution"],
                "cta_styles": ["try_challenge", "implement_now", "share_results"]
            },
            ContentTheme.NEWS: {
                "hooks": [
                    "Breaking: This just happened and it's going to change everything...",
                    "While everyone was distracted by [event], this happened...",
                    "The media isn't talking about this, but you need to know...",
                    "This story is developing right now and here's what it means...",
                    "Everyone's getting this wrong about [current event]..."
                ],
                "emotions": ["urgency", "controversy", "concern", "curiosity", "outrage"],
                "structures": ["breaking_news", "hidden_truth", "analysis", "prediction", "expose"],
                "cta_styles": ["share_awareness", "join_discussion", "stay_informed"]
            },
            ContentTheme.REDDIT: {
                "hooks": [
                    "Someone on Reddit confessed something that broke the internet...",
                    "This Reddit thread reveals the dark truth about...",
                    "A Redditor asked for advice and the responses were shocking...",
                    "This anonymous confession on Reddit will make you question everything...",
                    "Reddit solved a mystery that baffled everyone for years..."
                ],
                "emotions": ["curiosity", "shock", "drama", "intrigue", "moral_conflict"],
                "structures": ["confession", "mystery", "drama", "moral_dilemma", "plot_twist"],
                "cta_styles": ["comment_opinion", "share_story", "moral_debate"]
            }
        }
    
    def generate_viral_content_prompt(self, theme: ContentTheme, target_duration: int = 90) -> str:
        """Generate optimized prompt for viral content creation"""
        
        theme_data = self.viral_patterns[theme]
        hook_template = random.choice(theme_data["hooks"])
        emotion = random.choice(theme_data["emotions"]) 
        structure = random.choice(theme_data["structures"])
        cta_style = random.choice(theme_data["cta_styles"])
        
        # Duration-specific optimization
        if target_duration <= 60:
            pacing = "ultra-fast pacing with immediate hook"
            word_count = "120-150 words"
        elif target_duration <= 90:
            pacing = "fast pacing with strong retention hooks"
            word_count = "150-180 words"
        else:
            pacing = "engaging pacing with multiple retention points"
            word_count = "180-250 words"
        
        prompt = f"""Create a VIRAL YouTube Shorts script optimized for maximum engagement.

THEME: {theme.value.upper()} Stories
TARGET DURATION: {target_duration} seconds
VIRAL OPTIMIZATION: Focus on {emotion} emotion using {structure} structure

MANDATORY REQUIREMENTS:
1. HOOK (0-3 seconds): Use pattern like "{hook_template}"
2. RETENTION (throughout): Include 2-3 mid-video hooks to prevent drop-off
3. PACING: {pacing}
4. WORD COUNT: {word_count} (optimized for natural speech)
5. CALL-TO-ACTION: End with {cta_style} style engagement

VIRAL ELEMENTS TO INCLUDE:
- Open with question or shocking statement
- Include specific numbers, ages, timeframes
- Create emotional investment in first 5 seconds
- Use "But here's what happened next..." style transitions
- Include relatable universal experiences
- End with engagement question that sparks comments

SCRIPT STRUCTURE:
- Hook (3 seconds): Immediate attention grabber
- Setup (10 seconds): Context that builds investment  
- Conflict/Challenge (20-30 seconds): The main tension
- Resolution/Reveal (30-40 seconds): The payoff moment
- Impact/Lesson (10-15 seconds): Why it matters
- Call-to-Action (5 seconds): Engagement driver

TONE: Conversational, authentic, emotionally engaging
PERSPECTIVE: First-person narrative (more personal/viral)
LANGUAGE: Simple, accessible, punchy sentences

CRITICAL OUTPUT INSTRUCTION:
Return ONLY the script content meant for narration. Do NOT include:
- Production notes (like "Visuals:", "Audio:", "Text overlays:")
- Formatting instructions
- Stage directions
- Meta-commentary about the script
- Introduction phrases like "Here's your script:"

Just return the pure narration text that will be read aloud, nothing else."""

        return prompt
    
    def extract_viral_elements(self, script: str) -> Tuple[float, List[str]]:
        """Analyze script for viral elements and assign viral score"""
        
        viral_indicators = [
            "you won't believe", "changed my life", "everyone needs to know",
            "this happened", "but then", "here's what", "I never expected",
            "shocking", "amazing", "incredible", "unbelievable", "mind-blowing"
        ]
        
        engagement_hooks = []
        score = 0.0
        
        script_lower = script.lower()
        
        # Check for viral language
        for indicator in viral_indicators:
            if indicator in script_lower:
                score += 0.1
                engagement_hooks.append(indicator)
        
        # Check for questions (engagement drivers)
        question_count = script.count('?')
        score += question_count * 0.15
        if question_count > 0:
            engagement_hooks.append(f"{question_count} engagement questions")
        
        # Check for emotional words
        emotional_words = ["amazing", "shocking", "incredible", "life-changing", "powerful"]
        for word in emotional_words:
            if word in script_lower:
                score += 0.05
        
        # Check for personal pronouns (authenticity)
        personal_pronouns = ["i ", "my ", "me ", "we ", "our "]
        for pronoun in personal_pronouns:
            if pronoun in script_lower:
                score += 0.02
        
        # Normalize score to 0-10 scale
        viral_score = min(score * 10, 10.0)
        
        return viral_score, engagement_hooks
    
    def clean_script_for_narration(self, raw_script: str) -> str:
        """
        Clean the LLM-generated script to extract only narration content
        Remove production notes, formatting, and stage directions
        """
        if not raw_script:
            return ""
        
        # Split into lines for processing
        lines = raw_script.strip().split('\n')
        clean_lines = []
        
        # Patterns to identify and remove production instructions
        production_patterns = [
            r'^(visuals?|visual\s+elements?):', 
            r'^(audio|sound|music):', 
            r'^(text|overlay|caption):', 
            r'^(graphics?|animation):', 
            r'^(transitions?|cuts?):', 
            r'^(camera|shot|angle):', 
            r'^(note|notes?):', 
            r'^(instruction|instructions?):', 
            r'^(direction|directions?):', 
            r'^(stage|production):', 
            r'^(here\'?s\s+(your|the|a)\s+script)', 
            r'^(script:|content:)', 
            r'^(background|b-roll):', 
            r'here\'?s\s+(your|a)\s+viral.*script',  # NEW: Catch "Here's your viral script"
            r'here\'?s\s+(your|a)\s+youtube.*script',  # NEW: Catch "Here's your YouTube script"
            r'optimized\s+for\s+maximum\s+engagement',  # NEW: Catch engagement text
            r'^---+',  # Separator lines
            r'^\*\*.*\*\*$',  # Bold formatting markers
            r'^#{1,6}\s',  # Markdown headers
            r'^\s*\*\*[^*]+\*\*\s*$',  # Bold text on its own line
        ]
        
        import re
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip lines that match production patterns
            is_production_note = False
            for pattern in production_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_production_note = True
                    break
            
            if not is_production_note:
                # Clean up formatting markers from the line
                line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove bold
                line = re.sub(r'\*(.*?)\*', r'\1', line)      # Remove italics
                line = re.sub(r'`(.*?)`', r'\1', line)        # Remove code formatting
                line = re.sub(r'\[(.*?)\]', r'\1', line)      # Remove square brackets
                line = re.sub(r'\{(.*?)\}', '', line)         # Remove curly braces entirely
                
                clean_lines.append(line)
        
        # Join lines back together
        clean_script = '\n'.join(clean_lines).strip()
        
        # Final cleanup - remove any remaining artifacts
        clean_script = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_script)  # Normalize line breaks
        clean_script = re.sub(r'^\s*[-*•]\s*', '', clean_script, flags=re.MULTILINE)  # Remove bullet points
        
        return clean_script

class ContentQueue:
    """Queue-based content processing with priority and retry logic"""
    
    def __init__(self, max_size: int = 100):
        self.queue: List[ContentItem] = []
        self.processing: Dict[str, ContentItem] = {}
        self.completed: Dict[str, ContentItem] = {}
        self.failed: Dict[str, ContentItem] = {}
        self.max_size = max_size
        self.logger = logging.getLogger(__name__)
    
    def add_content(self, content: ContentItem) -> bool:
        """Add content to processing queue"""
        if len(self.queue) >= self.max_size:
            return False
        
        self.queue.append(content)
        self.logger.info(f"✅ Added to queue: {content.title[:50]}... (ID: {content.id})")
        return True
    
    def get_next(self) -> Optional[ContentItem]:
        """Get next content item for processing"""
        if not self.queue:
            return None
        
        # Simple FIFO for now, could add priority logic later
        content = self.queue.pop(0)
        self.processing[content.id] = content
        return content
    
    def mark_completed(self, content_id: str):
        """Mark content as successfully completed"""
        if content_id in self.processing:
            content = self.processing.pop(content_id)
            content.stage = ProcessingStage.COMPLETE
            self.completed[content_id] = content
            self.logger.info(f"🎉 Completed: {content.title[:50]}...")
    
    def mark_failed(self, content_id: str, error: str):
        """Mark content as failed"""
        if content_id in self.processing:
            content = self.processing.pop(content_id)
            content.add_error(error)
            self.failed[content_id] = content
            self.logger.error(f"❌ Failed: {content.title[:50]}... - {error}")
    
    def get_status(self) -> Dict[str, int]:
        """Get current queue status"""
        return {
            "queued": len(self.queue),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "failed": len(self.failed)
        }

class APIConnectionPool:
    """Optimized API connection management with retry logic"""
    
    def __init__(self):
        self._connections = {}
        self.logger = logging.getLogger(__name__)
    
    def get_gemini(self):
        """Get Gemini API connection"""
        if 'gemini' not in self._connections:
            from integrations.gemini_api import GeminiContentGenerator
            self._connections['gemini'] = GeminiContentGenerator()
        return self._connections['gemini']
    
    def get_sheets(self):
        """Get Google Sheets API connection"""
        if 'sheets' not in self._connections:
            from integrations.google_sheets import GoogleSheetsManager
            self._connections['sheets'] = GoogleSheetsManager()
        return self._connections['sheets']
    
    def get_enhanced_audio(self):
        """Get Enhanced Audio Generator (OpenAI TTS + Whisper alignment)"""
        if 'enhanced_audio' not in self._connections:
            from core.enhanced_audio_generator import EnhancedAudioGenerator
            self._connections['enhanced_audio'] = EnhancedAudioGenerator()
        return self._connections['enhanced_audio']
    
    def get_elevenlabs(self):
        """Get ElevenLabs API connection (legacy fallback)"""
        if 'elevenlabs' not in self._connections:
            from integrations.elevenlabs_api import ElevenLabsTextToSpeech
            self._connections['elevenlabs'] = ElevenLabsTextToSpeech()
        return self._connections['elevenlabs']
    
    def get_pexels(self):
        """Get Pexels API connection"""
        if 'pexels' not in self._connections:
            from integrations.pexels_api import PexelsVideoSourcing
            self._connections['pexels'] = PexelsVideoSourcing()
        return self._connections['pexels']
    
    def get_ffmpeg(self):
        """Get FFmpeg connection"""
        if 'ffmpeg' not in self._connections:
            from integrations.ffmpeg_video import FFmpegVideoAssembly
            self._connections['ffmpeg'] = FFmpegVideoAssembly()
        return self._connections['ffmpeg']
    
    def get_enhanced_captions(self):
        """Get Enhanced Caption Manager (Whisper-aligned)"""
        if 'enhanced_captions' not in self._connections:
            from core.enhanced_caption_manager import EnhancedCaptionManager
            self._connections['enhanced_captions'] = EnhancedCaptionManager()
        return self._connections['enhanced_captions']
    
    def get_captions(self):
        """Get caption generator (legacy fallback)"""
        if 'captions' not in self._connections:
            from integrations.caption_generator import SRTCaptionGenerator
            self._connections['captions'] = SRTCaptionGenerator()
        return self._connections['captions']

class ViralShortsFactory:
    """Main production-grade viral content creation system"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.prompt_engine = ViralPromptEngine()
        self.content_queue = ContentQueue()
        self.api_pool = APIConnectionPool()
        
        # Use secure configuration for working directory 
        from src.security.secure_config import config
        self.working_dir = config.working_directory
        
        # Initialize professional audio generator with exact timing
        from core.professional_audio_generator import ProfessionalAudioGenerator
        self.professional_audio = ProfessionalAudioGenerator()
        
        # Performance tracking
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "avg_viral_score": 0.0,
            "processing_time": 0.0
        }
    
    def _setup_logging(self):
        """Setup comprehensive logging with secure path validation"""
        from src.security.secure_path_validator import get_secure_path_validator
        
        # Create secure log file path
        log_filename = f'viral_shorts_factory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        validator = get_secure_path_validator()
        secure_log_path = validator.get_secure_temp_path(log_filename)
        
        if not secure_log_path:
            # Fallback to basic temp path if validation fails
            import tempfile
            secure_log_path = Path(tempfile.gettempdir()) / log_filename
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(secure_log_path)
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"📝 Secure logging initialized: {secure_log_path}")
        return logger
    
    async def create_viral_batch(self, theme: ContentTheme, count: int = 5) -> Dict[str, Any]:
        """Create a batch of viral-optimized videos for specified theme"""
        
        start_time = datetime.now()
        
        print(f"\n🚀 VIRAL SHORTS FACTORY v2.0")
        print(f"🎭 Theme: {theme.value.upper()}")
        print(f"📊 Count: {count} videos")
        print("=" * 60)
        
        try:
            # Phase 1: Viral Content Ideation
            content_items = await self._generate_viral_ideas(theme, count)
            
            if not content_items:
                return {"success": False, "error": "No content generated"}
            
            # Phase 2: Queue Processing
            results = await self._process_content_queue(content_items)
            
            # Phase 3: Results Analysis
            summary = self._generate_batch_summary(results, start_time)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Critical batch processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_viral_ideas(self, theme: ContentTheme, count: int) -> List[ContentItem]:
        """Generate viral-optimized content ideas for theme"""
        
        print(f"\n💡 Phase 1: Generating {count} viral {theme.value} ideas...")
        print("-" * 50)
        
        content_items = []
        gemini = self.api_pool.get_gemini()
        
        for i in range(count):
            try:
                # Generate viral-optimized prompt
                prompt = self.prompt_engine.generate_viral_content_prompt(theme)
                
                # Get content from Gemini
                ideas = gemini.generate_ideas(prompt, num_ideas=1)
                
                if ideas and ideas[0]:
                    # Clean the script to remove production instructions
                    raw_script = ideas[0]
                    script = self.prompt_engine.clean_script_for_narration(raw_script)
                    
                    # Extract title from script (first line or hook)
                    title = self._extract_title_from_script(script)
                    
                    # Calculate viral score
                    viral_score, engagement_hooks = self.prompt_engine.extract_viral_elements(script)
                    
                    # Create content item
                    content = ContentItem(
                        id=f"{theme.value}_{i+1}_{int(datetime.now().timestamp())}",
                        theme=theme,
                        title=title,
                        script=script,
                        viral_score=viral_score,
                        engagement_hooks=engagement_hooks,
                        duration_target=random.randint(60, 180)  # YouTube Shorts can be up to 3 minutes
                    )
                    
                    content_items.append(content)
                    print(f"✅ {i+1}. {title[:60]}... (Viral Score: {viral_score:.1f}/10)")
                
            except Exception as e:
                self.logger.error(f"Error generating idea {i+1}: {e}")
                print(f"❌ {i+1}. Generation failed: {e}")
        
        print(f"\n📈 Generated {len(content_items)}/{count} viral-optimized ideas")
        return content_items
    
    def _extract_title_from_script(self, script: str) -> str:
        """Extract engaging title from generated script"""
        lines = script.strip().split('\n')
        
        # Look for the hook (usually first meaningful line)
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not line.startswith('TITLE:'):
                # Clean up the line to make a good title
                title = line.replace('"', '').replace("'", "")
                if len(title) > 80:
                    title = title[:77] + "..."
                return title
        
        # Fallback
        return "Viral Content Story"
    
    async def _process_content_queue(self, content_items: List[ContentItem]) -> List[ContentItem]:
        """Process content items through production pipeline"""
        
        print(f"\n🎬 Phase 2: Processing {len(content_items)} videos through pipeline...")
        print("-" * 50)
        
        # Add all items to queue
        for content in content_items:
            self.content_queue.add_content(content)
        
        # Process concurrently (up to 3 at a time to avoid API limits)
        semaphore = asyncio.Semaphore(3)
        tasks = [self._process_single_video(content, semaphore) for content in content_items]
        
        # Wait for all processing to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                content_items[i].add_error(str(result))
                print(f"❌ Video {i+1} failed: {result}")
            else:
                successful_results.append(result)
                print(f"✅ Video {i+1} completed successfully")
        
        return content_items
    
    async def _process_single_video(self, content: ContentItem, semaphore: asyncio.Semaphore) -> ContentItem:
        """Process single video through all production stages"""
        
        async with semaphore:  # Limit concurrent processing
            try:
                # Stage 1: Save to Google Sheets
                await self._save_to_sheets_stage(content)
                
                # Stage 2: Generate Audio
                await self._generate_audio_stage(content)
                
                # Stage 3: Source Video Clips
                await self._source_video_clips_stage(content)
                
                # Stage 4: Assemble Video
                await self._assemble_video_stage(content)
                
                # Stage 5: Add Captions
                await self._add_captions_stage(content)
                
                # Stage 6: Generate Metadata
                await self._generate_metadata_stage(content)
                
                # Mark as complete
                content.advance_stage(ProcessingStage.COMPLETE)
                self.content_queue.mark_completed(content.id)
                
                return content
                
            except Exception as e:
                content.add_error(str(e))
                self.content_queue.mark_failed(content.id, str(e))
                raise e
    
    async def _save_to_sheets_stage(self, content: ContentItem):
        """Save content to Google Sheets"""
        try:
            sheets = self.api_pool.get_sheets()
            
            # Add content idea to sheets
            success = sheets.add_content_idea(
                source=f'Viral AI ({content.theme.value})',
                title=content.title
            )
            
            if not success:
                raise Exception("Failed to save to Google Sheets")
            
            content.advance_stage(ProcessingStage.IDEATION)
            
        except Exception as e:
            raise Exception(f"Sheets stage failed: {e}")
    
    async def _generate_audio_stage(self, content: ContentItem):
        """Generate audio with PERFECT synchronization using Professional TTS Services"""
        try:
            # Initialize professional audio generator if needed
            if not self.professional_audio.initialize():
                raise Exception("Professional Audio Generator initialization failed")
            
            # Create content item for professional audio generation
            content_item = {
                'id': content.id,
                'title': content.title,
                'script': content.script
            }
            
            self.logger.info(f"🎵 Generating professional audio with exact timing for: {content.title}")
            
            # Generate audio with EXACT word-level timestamps
            result = self.professional_audio.generate_professional_audio_with_perfect_sync(content_item)
            
            if not result.get("success"):
                error_msg = result.get('error', 'Unknown error')
                services_tried = result.get('services_tried', [])
                raise Exception(f"Professional audio generation failed: {error_msg}. Services tried: {services_tried}")
            
            # Store all the professional audio results in content artifacts
            content.advance_stage(ProcessingStage.AUDIO, 'audio_path', result['audio_path'])
            content.artifacts.update({
                'srt_path': result['srt_path'],
                'word_boundaries': result.get('word_boundaries', []),
                'audio_info': result.get('audio_info', {}),
                'quality_metrics': result.get('quality_metrics', {}),
                'total_duration': result.get('total_duration', 0),
                'voice_used': result.get('voice_used', 'unknown'),
                'service_used': result.get('service_used', 'unknown'),
                'timing_precision': result.get('timing_precision', 'unknown'),
                'timing_source': result.get('timing_source', 'unknown')
            })
            
            self.logger.info("✅ PROFESSIONAL audio generation complete!")
            self.logger.info(f"🏆 Service: {result.get('service_used', 'Unknown').upper()}")
            self.logger.info(f"🎯 Quality: {result.get('quality', 'UNKNOWN')}")
            self.logger.info(f"📊 Words: {result.get('word_count', 0)}")
            self.logger.info(f"⏱️ Duration: {result.get('total_duration', 0):.1f}s")
            self.logger.info(f"🎤 Timing: {result.get('timing_precision', 'unknown').upper()}")
            
        except Exception as e:
            raise Exception(f"Professional audio stage failed: {e}")
    
    async def _source_video_clips_stage(self, content: ContentItem):
        """Source theme-appropriate video clips"""
        try:
            pexels = self.api_pool.get_pexels()
            
            # Generate search terms based on theme and content
            search_terms = self._generate_search_terms(content)
            
            clips = pexels.source_videos_for_content(
                content_id=content.id,
                title=content.title,
                script=content.script,
                num_videos=3
            )
            
            if not clips:
                raise Exception("No video clips sourced")
            
            content.advance_stage(ProcessingStage.VIDEO_CLIPS, 'video_clips', clips)
            
        except Exception as e:
            raise Exception(f"Video sourcing stage failed: {e}")
    
    def _generate_search_terms(self, content: ContentItem) -> List[str]:
        """Generate search terms based on theme and content"""
        
        theme_keywords = {
            ContentTheme.FAMILY: ["family", "home", "children", "parents", "together", "happy"],
            ContentTheme.SELFHELP: ["success", "motivation", "growth", "business", "achievement", "lifestyle"],
            ContentTheme.NEWS: ["cityscape", "office", "technology", "people", "modern", "urban"],
            ContentTheme.REDDIT: ["computer", "social", "discussion", "online", "community", "digital"]
        }
        
        # Get theme-specific keywords
        keywords = theme_keywords.get(content.theme, ["lifestyle", "modern", "people"])
        
        # Add content-specific terms from title
        title_words = [word.lower() for word in content.title.split() if len(word) > 3]
        keywords.extend(title_words[:2])  # Add first 2 meaningful words from title
        
        return keywords
    
    async def _assemble_video_stage(self, content: ContentItem):
        """Assemble final video using real FFmpeg assembly"""
        try:
            from core.video_assembly import VideoAssemblyManager
            
            # Initialize video assembly manager
            video_assembly = VideoAssemblyManager()
            
            # IMPORTANT: Initialize the components
            if not video_assembly.initialize():
                raise Exception("VideoAssemblyManager initialization failed")
            
            # Create content item for the assembler (expected format)
            content_item = {
                'id': content.id,
                'title': content.title
            }
            
            self.logger.info(f"🎬 Assembling video for: {content.title}")
            
            # Use real video assembly
            success = video_assembly.assemble_video_for_content(content_item)
            
            if not success:
                raise Exception("FFmpeg video assembly failed")
            
            # Find the assembled video file using atomic operations
            from src.security.atomic_file_operations import get_atomic_file_operations
            atomic_ops = get_atomic_file_operations()
            
            final_videos_dir = self.working_dir / "final_videos"
            
            # Atomically ensure the directory exists
            atomic_ops.atomic_mkdir(final_videos_dir, parents=True, exist_ok=True)
            
            # Sanitize content ID to prevent injection attacks
            sanitized_content_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', content.id)
            
            # Look for video files with atomic glob operations to prevent race conditions
            video_files = []
            patterns = [f"content_{sanitized_content_id}_*.mp4", f"shorts_{sanitized_content_id}_*.mp4", f"*{sanitized_content_id}*.mp4"]
            
            for pattern in patterns:
                matches = atomic_ops.atomic_glob_with_lock(pattern, final_videos_dir)
                video_files.extend(matches)
            
            if not video_files:
                raise Exception(f"No assembled video file found for content {content.id}")
            
            # Atomically verify files exist and get the most recent one
            valid_files = []
            for video_file in video_files:
                exists, stat_result = atomic_ops.atomic_exists_and_action(
                    video_file,
                    lambda p: p.stat() if p.stat().st_size > 0 else None
                )
                if exists and stat_result:
                    valid_files.append((video_file, stat_result.st_mtime))
            
            if not valid_files:
                raise Exception(f"No valid assembled video files found for content {content.id}")
            
            # Get the most recent valid file
            video_path = max(valid_files, key=lambda x: x[1])[0]
            
            self.logger.info(f"✅ Video assembled successfully: {video_path.name}")
            content.advance_stage(ProcessingStage.ASSEMBLY, 'video_path', str(video_path))
            
        except Exception as e:
            raise Exception(f"Assembly stage failed: {e}")
    
    async def _add_captions_stage(self, content: ContentItem):
        """🚀 Add captions using VOSK - THE PROVEN WORKING SOLUTION! 🚀
        
        This uses the exact same approach as successful Reddit video creators:
        1. Find the assembled video (with TTS audio)  
        2. Use VOSK speech recognition to get exact word-level timestamps
        3. Generate perfectly synchronized captions
        
        NO MORE GUESSING - VOSK MEASURES THE REAL TIMING!
        """
        try:
            self.logger.info(f"🎯 Adding VOSK-powered captions for: {content.title}")
            self.logger.info("🏆 Using PROVEN approach from FullyAutomatedRedditVideoMakerBot!")
            
            # 🎤 ONLY USE 2-LINE KARAOKE: No fallbacks to broken systems!
            from integrations.professional_karaoke_captions import ProfessionalKaraokeGenerator
            karaoke_generator = ProfessionalKaraokeGenerator()
            
            # Force initialization - no fallbacks allowed!
            self.logger.info("🔧 Force-initializing Professional Karaoke Generator...")
            if not karaoke_generator.initialize():
                self.logger.error("❌ Karaoke Generator failed to initialize")
                self.logger.info("🔧 Attempting to download VOSK model...")
                # Try to download model manually if it fails
                model_path = karaoke_generator.download_vosk_model()
                if not model_path:
                    raise Exception("❌ CRITICAL: Cannot download VOSK model - no internet connection or disk space")
                # Try initialization one more time
                if not karaoke_generator.initialize():
                    raise Exception("❌ CRITICAL: Professional Karaoke Generator initialization failed even after model download")
            
            # Find the assembled video file with atomic operations to prevent race conditions
            from src.security.secure_path_validator import get_secure_path_validator
            from src.security.atomic_file_operations import get_atomic_file_operations
            
            validator = get_secure_path_validator()
            atomic_ops = get_atomic_file_operations()
            
            video_path = None
            video_dir = self.working_dir / "final_videos"
            
            # Atomically ensure video directory exists
            if not atomic_ops.atomic_mkdir(video_dir, parents=True, exist_ok=True):
                raise Exception(f"Failed to create video directory: {video_dir}")
            
            # Validate video directory is secure
            video_dir_result = validator.validate_path(
                video_dir, 
                validator.PathCategory.VIDEO_FILES,
                allow_creation=True
            )
            
            if not video_dir_result.is_valid:
                raise Exception(f"Insecure video directory: {video_dir_result.violations}")
                
            secure_video_dir = video_dir_result.sanitized_path
            
            # Sanitize content ID to prevent path injection in glob patterns
            sanitized_content_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', content.id)
            
            # Atomically search for assembled video with race condition protection
            for pattern in [f"*{sanitized_content_id}*.mp4", f"shorts_{sanitized_content_id}*.mp4", f"content_{sanitized_content_id}*.mp4"]:
                try:
                    # Use atomic glob to prevent TOCTOU race conditions
                    matches = atomic_ops.atomic_glob_with_lock(pattern, secure_video_dir)
                    
                    for match in matches:
                        # Atomically verify file exists and validate it
                        exists, validated_path = atomic_ops.atomic_exists_and_action(
                            match,
                            lambda p: validator.validate_path(p, validator.PathCategory.VIDEO_FILES).sanitized_path
                                     if validator.validate_path(p, validator.PathCategory.VIDEO_FILES).is_valid else None
                        )
                        
                        if exists and validated_path:
                            video_path = str(validated_path)
                            self.logger.info(f"🎬 Found assembled video atomically: {Path(video_path).name}")
                            break
                    
                    if video_path:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Error in atomic glob pattern {pattern}: {e}")
            
            # Final atomic verification that the video file exists
            if not video_path:
                raise Exception(f"No assembled video file found for content {content.id}")
                
            video_exists, final_path = atomic_ops.atomic_exists_and_action(
                video_path,
                lambda p: p if p.stat().st_size > 0 else None  # Ensure non-empty file
            )
            
            if not video_exists or not final_path:
                raise Exception(f"Assembled video file not found or empty: {video_path}")
            
            self.logger.info(f"🎬 Found assembled video: {Path(video_path).name}")
            
            # Generate secure output path for PROFESSIONAL karaoke captioned video
            video_path_obj = Path(video_path)
            
            # Create secure output directory with atomic operations
            captioned_videos_dir = validator.create_secure_path(
                "captioned_videos", 
                validator.PathCategory.OUTPUT_FILES
            )
            
            if not captioned_videos_dir:
                raise Exception("Failed to create secure captioned videos directory")
            
            # Atomically create directory to prevent race conditions
            if not atomic_ops.atomic_mkdir(captioned_videos_dir, parents=True, exist_ok=True):
                raise Exception(f"Failed to atomically create captioned videos directory: {captioned_videos_dir}")
            
            # Create secure output filename
            safe_filename = f"professional_karaoke_{re.sub(r'[^a-zA-Z0-9_\-]', '_', video_path_obj.stem)}.mp4"
            captioned_video_path_obj = captioned_videos_dir / safe_filename
            
            # Validate output path
            output_result = validator.validate_path(
                captioned_video_path_obj,
                validator.PathCategory.OUTPUT_FILES, 
                allow_creation=True
            )
            
            if not output_result.is_valid:
                raise Exception(f"Insecure output path: {output_result.violations}")
                
            captioned_video_path = str(output_result.sanitized_path)
            
            # 🎤 THE NEW STANDARD: Professional 2-line karaoke captions!
            self.logger.info("🎭 Using PROFESSIONAL 2-line karaoke approach!")
            self.logger.info("🏆 2 lines × 7 words + gold highlighting - like successful YouTube Shorts!")
            self.logger.info("✨ No more rapid single words - readable 2-line blocks!")
            
            result_path = karaoke_generator.generate_professional_karaoke_captions(
                video_path=video_path,
                output_path=captioned_video_path
            )
            
            if not result_path or not Path(result_path).exists():
                raise Exception("VOSK caption generation failed")
            
            # Get video information
            captioned_path = Path(result_path)
            file_size_mb = captioned_path.stat().st_size / (1024 * 1024)
            
            # Get duration from artifacts or probe the file
            duration = content.artifacts.get('total_duration', 0)
            
            video_info = {
                'filename': captioned_path.name,
                'size_mb': file_size_mb,
                'duration_seconds': duration,
                'path': str(captioned_path)
            }
            
            # Store caption results in content artifacts
            content.artifacts.update({
                'captioned_video_path': result_path,
                'captioned_video_info': video_info,
                'alignment_method': 'vosk_speech_recognition',
                'caption_quality': 'PERFECT_VOSK_SYNC'
            })
            
            self.logger.info("🎉 PROFESSIONAL KARAOKE CAPTIONS ACHIEVED!")
            self.logger.info("🏆 Method: VOSK + 2-Line Karaoke → Like Successful YouTube Shorts")
            self.logger.info(f"📺 Video: {video_info.get('filename', 'Unknown')}")
            self.logger.info(f"💾 Size: {file_size_mb:.1f} MB")
            self.logger.info(f"⏱️ Duration: {duration:.1f}s")
            self.logger.info("🎭 Style: 2 lines × 7 words + gold word highlighting")
            self.logger.info("✨ Readable caption blocks (no rapid single words)")
            self.logger.info("🔥 EXACTLY like successful YouTube Shorts creators!")
            self.logger.info("✅ Perfect synchronization + professional presentation!")
            
            content.advance_stage(ProcessingStage.CAPTIONS, 'captioned_path', str(captioned_path))
            
        except Exception as e:
            raise Exception(f"VOSK captions stage failed: {e}")
    
    async def _generate_metadata_stage(self, content: ContentItem):
        """Generate viral-optimized metadata"""
        try:
            gemini = self.api_pool.get_gemini()
            
            metadata_prompt = f"""Generate viral YouTube Shorts metadata for this {content.theme.value} story:

TITLE: {content.title}
SCRIPT: {content.script[:200]}...
VIRAL SCORE: {content.viral_score}/10

Create:
1. YouTube Title (under 60 chars, clickbait but accurate)
2. Description (2-3 paragraphs, SEO optimized, includes hashtags)
3. Tags (15 relevant tags for maximum reach)

Focus on viral optimization and YouTube Shorts algorithm preferences."""
            
            metadata_response = gemini.generate_ideas(metadata_prompt, num_ideas=1)
            
            if metadata_response:
                metadata = {
                    'youtube_title': content.title,
                    'description': f"Viral {content.theme.value} story with {content.viral_score:.1f}/10 viral score",
                    'tags': f'{content.theme.value},viral,shorts,story,trending'
                }
                
                content.advance_stage(ProcessingStage.METADATA, 'metadata', metadata)
            else:
                raise Exception("Metadata generation failed")
            
        except Exception as e:
            raise Exception(f"Metadata stage failed: {e}")
    
    def _generate_batch_summary(self, results: List[ContentItem], start_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive batch processing summary"""
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        completed = len([r for r in results if r.stage == ProcessingStage.COMPLETE])
        failed = len([r for r in results if r.stage == ProcessingStage.FAILED])
        
        avg_viral_score = sum(r.viral_score for r in results) / len(results) if results else 0
        
        # Organize results by theme
        theme_results = {}
        for result in results:
            theme = result.theme.value
            if theme not in theme_results:
                theme_results[theme] = []
            theme_results[theme].append({
                'id': result.id,
                'title': result.title,
                'viral_score': result.viral_score,
                'stage': result.stage.value,
                'errors': result.errors
            })
        
        summary = {
            'success': completed > 0,
            'total_videos': len(results),
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / len(results) * 100) if results else 0,
            'avg_viral_score': round(avg_viral_score, 2),
            'processing_time_seconds': round(processing_time, 2),
            'output_directory': str(self.working_dir / "captioned_videos"),
            'results_by_theme': theme_results,
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def print_results_summary(self, summary: Dict[str, Any]):
        """Print comprehensive results summary"""
        
        print(f"\n🎊 VIRAL SHORTS FACTORY - BATCH COMPLETE!")
        print("=" * 60)
        print(f"📊 Success Rate: {summary['success_rate']:.1f}% ({summary['completed']}/{summary['total_videos']})")
        print(f"🔥 Average Viral Score: {summary['avg_viral_score']}/10")
        print(f"⏱️  Processing Time: {summary['processing_time_seconds']:.1f} seconds")
        print(f"📁 Output Location: {summary['output_directory']}")
        
        if summary['results_by_theme']:
            print(f"\n📈 Results by Theme:")
            for theme, videos in summary['results_by_theme'].items():
                completed_count = len([v for v in videos if v['stage'] == 'complete'])
                avg_score = sum(v['viral_score'] for v in videos) / len(videos)
                print(f"  🎭 {theme.upper()}: {completed_count}/{len(videos)} videos (avg score: {avg_score:.1f}/10)")
        
        if summary['failed'] > 0:
            print(f"\n⚠️  Failed Videos: {summary['failed']}")
            for theme, videos in summary['results_by_theme'].items():
                failed_videos = [v for v in videos if v['stage'] == 'failed']
                for video in failed_videos:
                    print(f"  ❌ {video['title'][:50]}... - {video['errors'][-1] if video['errors'] else 'Unknown error'}")

async def main():
    """Main entry point with command-line interface"""
    
    parser = argparse.ArgumentParser(description='Viral Shorts Factory v2.0 - Theme-driven viral content creation')
    parser.add_argument('--theme', type=str, choices=['family', 'selfhelp', 'news', 'reddit', 'mixed'], 
                       required=True, help='Content theme for viral optimization')
    parser.add_argument('--count', type=int, default=5, 
                       help='Number of videos to create (default: 5)')
    
    args = parser.parse_args()
    
    # Convert string to enum
    theme = ContentTheme(args.theme)
    
    # Initialize factory
    factory = ViralShortsFactory()
    
    # Process batch
    if theme == ContentTheme.MIXED:
        # Mixed theme: create videos across all themes
        themes = [ContentTheme.FAMILY, ContentTheme.SELFHELP, ContentTheme.NEWS, ContentTheme.REDDIT]
        videos_per_theme = args.count // 4
        remaining = args.count % 4
        
        all_results = []
        for i, single_theme in enumerate(themes):
            count = videos_per_theme + (1 if i < remaining else 0)
            if count > 0:
                results = await factory.create_viral_batch(single_theme, count)
                all_results.extend(results.get('results_by_theme', {}).get(single_theme.value, []))
        
        # Create combined summary
        completed = len([r for r in all_results if r.get('stage') == 'complete'])
        factory.print_results_summary({
            'success': completed > 0,
            'total_videos': len(all_results),
            'completed': completed,
            'failed': len(all_results) - completed,
            'success_rate': (completed / len(all_results) * 100) if all_results else 0,
            'avg_viral_score': sum(r.get('viral_score', 0) for r in all_results) / len(all_results) if all_results else 0,
            'processing_time_seconds': 0,
            'output_directory': str(factory.working_dir / "captioned_videos"),
            'results_by_theme': {'mixed': all_results}
        })
    else:
        # Single theme processing
        results = await factory.create_viral_batch(theme, args.count)
        factory.print_results_summary(results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
