"""
Google Gemini API integration for content ideation
Generates creative ideas for Career/Self-Help/Management topics
"""

import logging
import random
from typing import List, Dict, Optional
import google.generativeai as genai
from datetime import datetime

from security.secure_config import config


class GeminiContentGenerator:
    """Generates content ideas using Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini API client"""
        self.logger = logging.getLogger(__name__)
        self._configure_gemini()
        
        # Content categories and prompts
        self.content_categories = {
            "Career": [
                "career advancement strategies",
                "workplace productivity tips", 
                "professional networking advice",
                "job interview preparation",
                "salary negotiation tactics",
                "leadership development",
                "workplace communication skills"
            ],
            "Self-Help": [
                "personal development habits",
                "motivation and mindset tips",
                "time management strategies", 
                "stress management techniques",
                "goal-setting frameworks",
                "confidence building exercises",
                "work-life balance tips"
            ],
            "Management": [
                "team leadership strategies",
                "employee motivation techniques",
                "project management tips",
                "delegation best practices",
                "conflict resolution skills",
                "performance management",
                "organizational culture building"
            ]
        }
    
    def _configure_gemini(self) -> None:
        """Configure Gemini API client"""
        try:
            genai.configure(api_key=config.google_gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.logger.info("Gemini API configured successfully")
        except Exception as e:
            self.logger.error(f"Failed to configure Gemini API: {e}")
            raise
    
    def generate_content_ideas(self, num_ideas: int = 15) -> List[Dict[str, str]]:
        """
        Generate content ideas for YouTube Shorts
        
        Args:
            num_ideas: Number of ideas to generate (default: 15)
            
        Returns:
            List of content idea dictionaries with title and category
        """
        try:
            self.logger.info(f"Generating {num_ideas} content ideas with Gemini...")
            
            ideas = []
            ideas_per_category = max(1, num_ideas // 3)  # Distribute across 3 categories
            
            for category, topics in self.content_categories.items():
                category_ideas = self._generate_category_ideas(
                    category, 
                    topics, 
                    ideas_per_category
                )
                ideas.extend(category_ideas)
            
            # If we need more ideas to reach the target, generate extras
            while len(ideas) < num_ideas:
                category = random.choice(list(self.content_categories.keys()))
                topics = self.content_categories[category]
                extra_ideas = self._generate_category_ideas(category, topics, 1)
                ideas.extend(extra_ideas)
            
            # Limit to requested number
            ideas = ideas[:num_ideas]
            
            self.logger.info(f"Successfully generated {len(ideas)} content ideas")
            return ideas
            
        except Exception as e:
            self.logger.error(f"Failed to generate content ideas: {e}")
            return []
    
    def _generate_category_ideas(self, category: str, topics: List[str], count: int) -> List[Dict[str, str]]:
        """Generate ideas for a specific category"""
        ideas = []
        
        for i in range(count):
            try:
                # Select a random topic for variety
                topic = random.choice(topics)
                
                # Create dynamic prompt for Gemini
                prompt = self._create_content_prompt(category, topic)
                
                # Generate content with Gemini
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    # Parse the response to extract title
                    title = self._extract_title_from_response(response.text, category)
                    
                    if title:
                        ideas.append({
                            'title': title,
                            'category': category,
                            'topic': topic,
                            'source': 'Gemini',
                            'generated_at': datetime.now().isoformat()
                        })
                        self.logger.debug(f"Generated {category} idea: {title}")
                
            except Exception as e:
                self.logger.warning(f"Failed to generate idea for {category}/{topic}: {e}")
                continue
        
        return ideas
    
    def _create_content_prompt(self, category: str, topic: str) -> str:
        """Create a targeted prompt for content generation"""
        
        base_prompt = f"""Generate a compelling title for a YouTube Short about {topic} in the {category} category.

Requirements:
- Title should be 8-15 words
- Must be engaging and clickable  
- Use numbers when possible (e.g., "5 Ways to...")
- Focus on actionable advice
- Target audience: young professionals aged 22-35
- Format for 60-second vertical video content

Examples of good titles:
- "5 Career Mistakes That Keep You From Getting Promoted"
- "The 2-Minute Confidence Trick That Changed My Life"
- "Why 90% of Managers Fail (And How to Be Different)"

Generate ONE compelling title only:"""

        return base_prompt
    
    def _extract_title_from_response(self, response_text: str, category: str) -> Optional[str]:
        """Extract and clean the title from Gemini's response"""
        try:
            # Clean up the response text
            title = response_text.strip()
            
            # Remove quotes if present
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            elif title.startswith("'") and title.endswith("'"):
                title = title[1:-1]
            
            # Remove any prefixes like "Title:" or numbering
            prefixes_to_remove = [
                'Title:', 'title:', 'TITLE:',
                '1.', '2.', '3.', '4.', '5.',
                '-', '•', '*'
            ]
            
            for prefix in prefixes_to_remove:
                if title.startswith(prefix):
                    title = title[len(prefix):].strip()
            
            # Take only the first line if multiple lines
            title = title.split('\n')[0].strip()
            
            # Validate title length (reasonable for YouTube)
            if 5 <= len(title) <= 100 and len(title.split()) >= 3:
                return title
            else:
                self.logger.warning(f"Generated title too short/long: {title}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract title from response: {e}")
            return None
    
    def generate_text(self, prompt: str) -> Optional[str]:
        """
        Generate text content using Gemini API with a custom prompt
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Generated text or None if generation fails
        """
        try:
            if not self.model:
                self.logger.error("Gemini model not initialized")
                return None
            
            self.logger.debug(f"Generating text with prompt: {prompt[:100]}...")
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                generated_text = response.text.strip()
                self.logger.debug(f"Generated text: {generated_text[:100]}...")
                return generated_text
            else:
                self.logger.error("No text generated by Gemini API")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating text: {e}")
            return None
    
    def generate_ideas(self, prompt: str, num_ideas: int = 1) -> List[str]:
        """
        Generate multiple ideas/text responses using Gemini API
        
        Args:
            prompt: The prompt to send to Gemini
            num_ideas: Number of ideas to generate (default: 1)
            
        Returns:
            List of generated texts
        """
        try:
            ideas = []
            
            for i in range(num_ideas):
                idea = self.generate_text(prompt)
                if idea:
                    ideas.append(idea)
                else:
                    self.logger.warning(f"Failed to generate idea {i+1}/{num_ideas}")
            
            self.logger.info(f"Generated {len(ideas)}/{num_ideas} ideas")
            return ideas
            
        except Exception as e:
            self.logger.error(f"Error generating ideas: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test the Gemini API connection"""
        try:
            self.logger.info("Testing Gemini API connection...")
            
            # Simple test prompt
            test_prompt = "Generate a short professional tip for career success."
            response = self.model.generate_content(test_prompt)
            
            if response and response.text:
                self.logger.info("✅ Gemini API connection successful")
                self.logger.debug(f"Test response: {response.text[:100]}...")
                return True
            else:
                self.logger.error("❌ Gemini API returned empty response")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Gemini API connection failed: {e}")
            return False
    
    def get_api_usage_info(self) -> Dict[str, str]:
        """Get information about API usage and limits"""
        return {
            'provider': 'Google Gemini',
            'model': 'gemini-2.5-flash',
            'rate_limit': '60 requests/minute',
            'features': 'Content generation, creative writing',
            'cost_estimate': 'Free tier: 15 requests/minute'
        }
