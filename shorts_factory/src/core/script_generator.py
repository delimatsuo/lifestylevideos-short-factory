"""
Automated Script Generation Module for Shorts Factory
Generates 160-word video scripts optimized for short-form content using Gemini API
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
import re

from integrations.gemini_api import GeminiContentGenerator
from integrations.google_sheets import GoogleSheetsManager
from core.config import config


class ScriptGenerator:
    """Generates optimized video scripts for approved content ideas"""
    
    def __init__(self):
        """Initialize the script generator"""
        self.logger = logging.getLogger(__name__)
        self.gemini_generator = None
        self.sheets_manager = None
        
        # Script generation parameters
        self.target_word_count = 160
        self.script_style = "conversational"
        self.platform_optimization = "shorts"
        
    def initialize(self) -> bool:
        """Initialize script generation components"""
        try:
            self.logger.info("🎬 Initializing Script Generator...")
            
            # Initialize Gemini API
            self.gemini_generator = GeminiContentGenerator()
            if not self.gemini_generator.test_connection():
                raise Exception("Gemini API connection failed")
            
            # Initialize Google Sheets
            self.sheets_manager = GoogleSheetsManager()
            if not self.sheets_manager.test_connection():
                raise Exception("Google Sheets connection failed")
            
            self.logger.info("✅ Script Generator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Script Generator: {e}")
            return False
    
    def generate_script_for_content(self, content_item: Dict[str, str]) -> Optional[str]:
        """
        Generate a script for a single content item
        
        Args:
            content_item: Dictionary containing content details (id, title, source, etc.)
            
        Returns:
            Generated script text or None if generation fails
        """
        try:
            title = content_item.get('title', '').strip()
            source = content_item.get('source', '').strip()
            content_id = content_item.get('id', '')
            
            if not title:
                self.logger.warning(f"⚠️ No title provided for content ID {content_id}")
                return None
            
            self.logger.info(f"📝 Generating script for: {title}")
            
            # Create optimized prompt for script generation
            prompt = self._create_script_prompt(title, source)
            
            # Generate script using Gemini
            scripts = self.gemini_generator.generate_ideas(prompt, num_ideas=1)
            
            if not scripts or not scripts[0]:
                self.logger.error(f"❌ Failed to generate script for: {title}")
                return None
            
            # Process and validate the generated script
            script = self._process_generated_script(scripts[0])
            
            # Validate script length
            word_count = len(script.split())
            if word_count < 120 or word_count > 200:
                self.logger.warning(f"⚠️ Script word count ({word_count}) outside optimal range (120-200)")
            
            self.logger.info(f"✅ Generated script ({word_count} words) for: {title}")
            return script
            
        except Exception as e:
            self.logger.error(f"❌ Error generating script: {e}")
            return None
    
    def _create_script_prompt(self, title: str, source: str = "") -> str:
        """Create an optimized prompt for script generation"""
        
        # Base prompt for script generation
        base_prompt = f"""Create a compelling short-form video script for the topic: "{title}"

REQUIREMENTS:
- Target length: 160 words (±20 words acceptable)
- Format: Short-form vertical video (TikTok/YouTube Shorts style)
- Style: Conversational, engaging, direct
- Structure: Hook → Main Content → Call-to-Action
- Tone: Professional but approachable

STRUCTURE GUIDELINES:
1. HOOK (15-20 words): Start with an attention-grabbing statement or question
2. MAIN CONTENT (120-130 words): Deliver the core message with practical value
3. CALL-TO-ACTION (15-20 words): Encourage engagement (like, follow, comment)

CONTENT GUIDELINES:
- Use "you" to speak directly to the viewer
- Include specific, actionable advice
- Break complex ideas into simple points
- Create moments that encourage pausing/rewatching
- End with a question or challenge for comments

"""
        
        # Add source-specific context
        if source.lower() == 'gemini':
            base_prompt += """SOURCE CONTEXT: This is an AI-generated concept, so ensure the content feels authentic and relatable to real human experiences.

"""
        elif source.lower() == 'reddit':
            base_prompt += """SOURCE CONTEXT: This topic came from Reddit discussions, so tap into the authentic, community-driven perspective that made it popular.

"""
        
        # Add final instructions
        base_prompt += """OUTPUT FORMAT:
Provide only the script text without any formatting, titles, or explanations. Write it as natural speech that will be spoken directly to the camera.

SCRIPT:"""
        
        return base_prompt
    
    def _process_generated_script(self, raw_script: str) -> str:
        """Process and clean the generated script"""
        
        # Remove any formatting or labels that might have been included
        script = raw_script.strip()
        
        # Remove common unwanted prefixes
        unwanted_prefixes = [
            "SCRIPT:",
            "Script:",
            "Video Script:",
            "Short Script:",
            "Here's the script:",
            "Generated Script:",
        ]
        
        for prefix in unwanted_prefixes:
            if script.startswith(prefix):
                script = script[len(prefix):].strip()
        
        # Remove quotes if the entire script is wrapped in them
        if script.startswith('"') and script.endswith('"'):
            script = script[1:-1].strip()
        if script.startswith("'") and script.endswith("'"):
            script = script[1:-1].strip()
        
        # Clean up extra whitespace and formatting
        script = re.sub(r'\s+', ' ', script)
        script = script.strip()
        
        # Ensure proper sentence endings
        if script and not script[-1] in '.!?':
            script += '.'
        
        return script
    
    def save_script_to_sheet(self, content_id: str, script: str) -> bool:
        """
        Save generated script to Google Sheets
        
        Args:
            content_id: The ID of the content item
            script: The generated script text
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            success = self.sheets_manager.update_content_field(
                content_id,
                'SCRIPT',
                script,
                f"Script generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            if success:
                self.logger.info(f"✅ Script saved to Google Sheets for ID {content_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to save script to Google Sheets for ID {content_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error saving script to Google Sheets: {e}")
            return False
    
    def generate_and_save_script(self, content_item: Dict[str, str]) -> bool:
        """
        Complete workflow: generate script and save to Google Sheets
        
        Args:
            content_item: Dictionary containing content details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            # Generate the script
            script = self.generate_script_for_content(content_item)
            
            if not script:
                return False
            
            # Save to Google Sheets
            if self.save_script_to_sheet(content_id, script):
                self.logger.info(f"🎬 Complete script generation successful for: {title}")
                return True
            else:
                self.logger.error(f"❌ Failed to save script for: {title}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in complete script generation workflow: {e}")
            return False
    
    def batch_generate_scripts(self, content_items: List[Dict[str, str]]) -> Dict[str, bool]:
        """
        Generate scripts for multiple content items
        
        Args:
            content_items: List of content item dictionaries
            
        Returns:
            Dictionary mapping content_id to success status
        """
        results = {}
        
        self.logger.info(f"📝 Starting batch script generation for {len(content_items)} items")
        
        for content_item in content_items:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            try:
                success = self.generate_and_save_script(content_item)
                results[content_id] = success
                
                if success:
                    self.logger.info(f"✅ [{len(results)}/{len(content_items)}] Success: {title}")
                else:
                    self.logger.error(f"❌ [{len(results)}/{len(content_items)}] Failed: {title}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing {title}: {e}")
                results[content_id] = False
        
        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"📊 Batch script generation complete: {successful}/{len(content_items)} successful")
        
        return results
    
    def get_script_generation_stats(self) -> Dict[str, any]:
        """Get statistics about script generation capabilities"""
        return {
            'target_word_count': self.target_word_count,
            'script_style': self.script_style,
            'platform_optimization': self.platform_optimization,
            'gemini_available': self.gemini_generator is not None,
            'sheets_available': self.sheets_manager is not None,
            'status': 'operational' if (self.gemini_generator and self.sheets_manager) else 'needs_initialization'
        }
