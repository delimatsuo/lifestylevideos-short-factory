"""
YouTube Metadata Generation Integration for Shorts Factory
Uses Google Gemini API to generate optimized YouTube titles, descriptions, and tags
"""

import logging
from typing import Dict, List, Optional, Any
import json
import re
from datetime import datetime

from integrations.gemini_api import GeminiContentGenerator
from core.config import config


class YouTubeMetadataGenerator:
    """Handles YouTube metadata generation using Gemini AI"""
    
    def __init__(self):
        """Initialize YouTube metadata generator"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini API
        self.gemini_generator = None
        
        # YouTube optimization parameters
        self.max_title_length = 100  # YouTube title limit
        self.max_description_length = 5000  # YouTube description limit
        self.max_tags_count = 15  # Recommended tags count for optimal performance
        self.max_tag_length = 30  # Individual tag length limit
        
        # Content categories for better targeting
        self.lifestyle_categories = [
            "lifestyle", "productivity", "morning routine", "habits", "wellness", 
            "motivation", "personal development", "life tips", "success", "mindset",
            "health", "fitness", "self-care", "inspiration", "transformation"
        ]
        
        self.logger.info("📺 YouTube Metadata Generator initialized")
    
    def initialize(self) -> bool:
        """Initialize Gemini API connection"""
        try:
            self.logger.info("🔧 Initializing Gemini API for metadata generation...")
            
            # Initialize Gemini content generator
            self.gemini_generator = GeminiContentGenerator()
            if not self.gemini_generator.initialize():
                self.logger.error("❌ Gemini API initialization failed")
                return False
            
            self.logger.info("✅ YouTube Metadata Generator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ YouTube Metadata Generator initialization failed: {e}")
            return False
    
    def generate_optimized_title(self, script_text: str, original_title: str = "") -> Optional[str]:
        """
        Generate SEO-optimized YouTube title using Gemini API
        
        Args:
            script_text: The video script content
            original_title: Original content title for reference
            
        Returns:
            Optimized YouTube title, or None if generation fails
        """
        try:
            self.logger.info("📝 Generating optimized YouTube title...")
            
            # Build comprehensive title generation prompt
            title_prompt = f"""
            Create an engaging, SEO-optimized YouTube title for a lifestyle/productivity short video.
            
            SCRIPT CONTENT:
            {script_text}
            
            ORIGINAL TITLE: {original_title}
            
            REQUIREMENTS:
            - Maximum {self.max_title_length} characters
            - High click-through rate potential
            - Include relevant keywords for YouTube algorithm
            - Emotional hooks (curiosity, benefit, urgency)
            - Suitable for lifestyle/productivity niche
            - Format for YouTube Shorts (vertical videos)
            
            STYLE GUIDELINES:
            - Use numbers when relevant (5 Tips, 3 Habits, etc.)
            - Include power words (Amazing, Simple, Proven, Secret, etc.)
            - Create curiosity without clickbait
            - Target audience: young professionals, lifestyle enthusiasts
            
            EXAMPLES OF GOOD TITLES:
            - "5 Morning Habits That Will Change Your Life"
            - "The Simple Productivity Trick Everyone Should Know" 
            - "Why Successful People Do This Every Day"
            - "Transform Your Mornings With These 3 Steps"
            
            Generate ONLY the title text, nothing else.
            """
            
            # Generate title using Gemini
            generated_title = self.gemini_generator.generate_text(title_prompt)
            
            if not generated_title:
                self.logger.error("❌ Title generation failed - empty response")
                return None
            
            # Clean and validate title
            cleaned_title = self._clean_and_validate_title(generated_title)
            
            if cleaned_title:
                self.logger.info(f"✅ Generated optimized title: {cleaned_title}")
                return cleaned_title
            else:
                self.logger.error("❌ Title validation failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error generating title: {e}")
            return None
    
    def generate_detailed_description(self, script_text: str, title: str, original_title: str = "") -> Optional[str]:
        """
        Generate detailed YouTube description using Gemini API
        
        Args:
            script_text: The video script content
            title: Generated YouTube title
            original_title: Original content title for reference
            
        Returns:
            Detailed YouTube description, or None if generation fails
        """
        try:
            self.logger.info("📝 Generating detailed YouTube description...")
            
            # Build comprehensive description generation prompt
            description_prompt = f"""
            Create a compelling, SEO-optimized YouTube description for this lifestyle/productivity short video.
            
            VIDEO TITLE: {title}
            ORIGINAL TITLE: {original_title}
            
            SCRIPT CONTENT:
            {script_text}
            
            REQUIREMENTS:
            - Maximum {self.max_description_length} characters
            - SEO optimized with relevant keywords
            - Engaging hook in first 125 characters (mobile preview)
            - Include value proposition and key takeaways
            - Call-to-action for engagement
            - Professional but conversational tone
            
            STRUCTURE:
            1. Hook: Compelling opening that expands on the title
            2. Value: What viewers will learn/gain from this video
            3. Key Points: Brief summary of main takeaways (if applicable)
            4. Engagement: Subscribe/like/comment call-to-action
            5. Community: Invite viewers to share their experience
            
            STYLE GUIDELINES:
            - Use emojis strategically for visual appeal
            - Include relevant hashtags at the end
            - Write for lifestyle/productivity audience
            - Focus on transformation and improvement
            - Keep paragraphs short for mobile readability
            
            EXAMPLE FORMAT:
            Transform your daily routine with these simple yet powerful strategies! ✨
            
            In this video, you'll discover [key benefit] that successful people use every day. These proven methods will help you [specific outcome] in just [time frame].
            
            What you'll learn:
            • [Key point 1]
            • [Key point 2]
            • [Key point 3]
            
            Ready to level up your life? Hit that subscribe button for more productivity tips and life-changing content! 🚀
            
            What's your biggest productivity challenge? Let me know in the comments below! 👇
            
            #Productivity #LifestyleTips #MorningRoutine #Success #Motivation
            
            Generate the complete description following this structure.
            """
            
            # Generate description using Gemini
            generated_description = self.gemini_generator.generate_text(description_prompt)
            
            if not generated_description:
                self.logger.error("❌ Description generation failed - empty response")
                return None
            
            # Clean and validate description
            cleaned_description = self._clean_and_validate_description(generated_description)
            
            if cleaned_description:
                self.logger.info(f"✅ Generated description: {len(cleaned_description)} characters")
                self.logger.debug(f"Description preview: {cleaned_description[:150]}...")
                return cleaned_description
            else:
                self.logger.error("❌ Description validation failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error generating description: {e}")
            return None
    
    def generate_relevant_tags(self, script_text: str, title: str) -> List[str]:
        """
        Generate relevant SEO tags using Gemini API
        
        Args:
            script_text: The video script content
            title: YouTube title
            
        Returns:
            List of relevant tags
        """
        try:
            self.logger.info("📝 Generating relevant SEO tags...")
            
            # Build tags generation prompt
            tags_prompt = f"""
            Generate SEO-optimized tags for this YouTube lifestyle/productivity short video.
            
            VIDEO TITLE: {title}
            
            SCRIPT CONTENT:
            {script_text}
            
            REQUIREMENTS:
            - Generate exactly {self.max_tags_count} tags
            - Each tag maximum {self.max_tag_length} characters
            - Focus on lifestyle, productivity, and personal development
            - Include both broad and specific keywords
            - Mix of single words and short phrases
            - Target YouTube algorithm for discovery
            
            TAG CATEGORIES TO INCLUDE:
            - Main topic keywords
            - Audience-focused terms (productivity, lifestyle, success)
            - Action-oriented words (tips, habits, routine, motivation)
            - Outcome-focused terms (transformation, improvement, growth)
            - Platform-specific terms (shorts, quick tips)
            
            EXAMPLE TAGS:
            productivity, morning routine, life tips, success habits, motivation, lifestyle, personal development, productivity tips, daily habits, life transformation, success mindset, wellness, self improvement, lifestyle tips, productivity hacks
            
            Generate ONLY the tags separated by commas, nothing else.
            Format: tag1, tag2, tag3, etc.
            """
            
            # Generate tags using Gemini
            generated_tags_text = self.gemini_generator.generate_text(tags_prompt)
            
            if not generated_tags_text:
                self.logger.error("❌ Tags generation failed - empty response")
                return []
            
            # Parse and validate tags
            tags = self._parse_and_validate_tags(generated_tags_text)
            
            if tags:
                self.logger.info(f"✅ Generated {len(tags)} relevant tags")
                self.logger.debug(f"Tags: {', '.join(tags)}")
                return tags
            else:
                self.logger.warning("⚠️ Tag parsing failed, using fallback tags")
                return self._get_fallback_tags()
                
        except Exception as e:
            self.logger.error(f"❌ Error generating tags: {e}")
            return self._get_fallback_tags()
    
    def _clean_and_validate_title(self, title: str) -> Optional[str]:
        """Clean and validate generated title"""
        try:
            # Remove quotes and extra whitespace
            cleaned = title.strip().strip('"\'').strip()
            
            # Remove any prefixes like "Title:" or similar
            cleaned = re.sub(r'^(Title:|Generated Title:|YouTube Title:)\s*', '', cleaned, flags=re.IGNORECASE)
            
            # Ensure it's not too long
            if len(cleaned) > self.max_title_length:
                # Try to truncate at word boundary
                words = cleaned.split()
                truncated = ""
                for word in words:
                    if len(truncated + " " + word) <= self.max_title_length:
                        truncated = (truncated + " " + word).strip()
                    else:
                        break
                cleaned = truncated
            
            # Validate minimum length and content
            if len(cleaned) < 10:
                self.logger.error("❌ Title too short")
                return None
            
            # Check for inappropriate content (basic check)
            inappropriate_words = ['clickbait', 'fake', 'scam', 'lie', 'hate']
            if any(word.lower() in cleaned.lower() for word in inappropriate_words):
                self.logger.error("❌ Title contains inappropriate content")
                return None
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning title: {e}")
            return None
    
    def _clean_and_validate_description(self, description: str) -> Optional[str]:
        """Clean and validate generated description"""
        try:
            # Remove extra whitespace and normalize
            cleaned = description.strip()
            
            # Ensure it's not too long
            if len(cleaned) > self.max_description_length:
                cleaned = cleaned[:self.max_description_length-3] + "..."
            
            # Validate minimum length
            if len(cleaned) < 50:
                self.logger.error("❌ Description too short")
                return None
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning description: {e}")
            return None
    
    def _parse_and_validate_tags(self, tags_text: str) -> List[str]:
        """Parse and validate generated tags"""
        try:
            # Split by commas and clean
            raw_tags = [tag.strip().strip('"\'') for tag in tags_text.split(',')]
            
            valid_tags = []
            for tag in raw_tags:
                # Clean tag
                cleaned_tag = re.sub(r'[^\w\s-]', '', tag).strip()
                
                # Validate tag
                if (len(cleaned_tag) >= 2 and 
                    len(cleaned_tag) <= self.max_tag_length and 
                    cleaned_tag.lower() not in [t.lower() for t in valid_tags]):
                    valid_tags.append(cleaned_tag.lower())
                
                # Stop if we have enough tags
                if len(valid_tags) >= self.max_tags_count:
                    break
            
            return valid_tags[:self.max_tags_count]
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing tags: {e}")
            return []
    
    def _get_fallback_tags(self) -> List[str]:
        """Get fallback tags if generation fails"""
        return [
            "productivity", "lifestyle", "motivation", "success", "tips",
            "personal development", "habits", "routine", "wellness", "mindset",
            "life tips", "productivity tips", "success habits", "lifestyle tips", "shorts"
        ]
    
    def generate_complete_metadata(
        self, 
        script_text: str, 
        original_title: str = "",
        content_id: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Generate complete YouTube metadata package
        
        Args:
            script_text: The video script content
            original_title: Original content title
            content_id: Content identifier for tracking
            
        Returns:
            Dictionary with title, description, and tags, or None if failed
        """
        try:
            self.logger.info(f"📺 Generating complete YouTube metadata for content {content_id}")
            
            # Generate optimized title
            title = self.generate_optimized_title(script_text, original_title)
            if not title:
                self.logger.error("❌ Failed to generate title")
                return None
            
            # Generate detailed description
            description = self.generate_detailed_description(script_text, title, original_title)
            if not description:
                self.logger.error("❌ Failed to generate description")
                return None
            
            # Generate relevant tags
            tags = self.generate_relevant_tags(script_text, title)
            if not tags:
                self.logger.warning("⚠️ Failed to generate tags, using fallback")
                tags = self._get_fallback_tags()
            
            # Build metadata package
            metadata = {
                'title': title,
                'description': description,
                'tags': tags,
                'generated_at': datetime.now().isoformat(),
                'content_id': content_id,
                'original_title': original_title,
                'character_counts': {
                    'title': len(title),
                    'description': len(description),
                    'tags_count': len(tags)
                }
            }
            
            self.logger.info("🎉 Complete YouTube metadata generated successfully!")
            self.logger.info(f"📊 Title: {len(title)} chars, Description: {len(description)} chars, Tags: {len(tags)}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"❌ Error generating complete metadata: {e}")
            return None
