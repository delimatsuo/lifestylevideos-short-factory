"""
Reddit API integration for trending story extraction
Pulls engaging stories from specified subreddits for content ideas
"""

import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
import time

from core.config import config


class RedditContentExtractor:
    """Extracts trending content from Reddit for video ideas"""
    
    def __init__(self):
        """Initialize Reddit API client"""
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self._setup_session()
        
        # Target subreddits for content extraction
        self.target_subreddits = {
            'career': [
                'careerguidance',
                'careeradvice', 
                'jobs',
                'ITCareerQuestions',
                'cscareerquestions',
                'resumes'
            ],
            'self_help': [
                'getmotivated',
                'selfimprovement',
                'decidingtobebetter',
                'productivity',
                'getdisciplined',
                'motivation'
            ],
            'stories': [
                'tifu',  # Today I F***ed Up
                'AmItheAsshole',
                'relationship_advice',
                'LifeProTips',
                'YouShouldKnow',
                'todayilearned'
            ]
        }
        
        # Story filtering criteria
        self.min_score = 100  # Minimum upvotes
        self.max_age_hours = 24  # Stories from last 24 hours
        
    def _setup_session(self) -> None:
        """Setup Reddit API session with proper headers"""
        try:
            self.session.headers.update({
                'User-Agent': config.reddit_user_agent,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            
            # Set up basic authentication if provided
            if hasattr(config, 'reddit_client_id') and hasattr(config, 'reddit_client_secret'):
                try:
                    self._authenticate()
                except Exception as e:
                    self.logger.warning(f"Reddit authentication failed, using public API: {e}")
            
            self.logger.info("Reddit API session configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Reddit session: {e}")
            raise
    
    def _authenticate(self) -> None:
        """Authenticate with Reddit API for higher rate limits"""
        auth_url = "https://www.reddit.com/api/v1/access_token"
        
        auth_data = {
            'grant_type': 'client_credentials'
        }
        
        auth_response = requests.post(
            auth_url,
            data=auth_data,
            auth=(config.reddit_client_id, config.reddit_client_secret),
            headers={'User-Agent': config.reddit_user_agent}
        )
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
                self.logger.info("✅ Reddit API authenticated successfully")
            else:
                raise Exception("No access token received")
        else:
            raise Exception(f"Authentication failed: {auth_response.status_code}")
    
    def extract_trending_stories(self, max_stories: int = 10) -> List[Dict[str, str]]:
        """
        Extract trending stories from Reddit
        
        Args:
            max_stories: Maximum number of stories to extract
            
        Returns:
            List of story dictionaries with title, content, and metadata
        """
        try:
            self.logger.info(f"Extracting {max_stories} trending stories from Reddit...")
            
            all_stories = []
            stories_per_category = max(1, max_stories // 3)  # Distribute across categories
            
            for category, subreddits in self.target_subreddits.items():
                category_stories = self._extract_from_subreddits(
                    subreddits, 
                    stories_per_category,
                    category
                )
                all_stories.extend(category_stories)
            
            # Limit to requested number and sort by score
            all_stories.sort(key=lambda x: int(x.get('score', 0)), reverse=True)
            all_stories = all_stories[:max_stories]
            
            self.logger.info(f"Successfully extracted {len(all_stories)} trending stories")
            return all_stories
            
        except Exception as e:
            self.logger.error(f"Failed to extract trending stories: {e}")
            return []
    
    def _extract_from_subreddits(self, subreddits: List[str], count: int, category: str) -> List[Dict[str, str]]:
        """Extract stories from a list of subreddits"""
        stories = []
        
        for subreddit in subreddits:
            try:
                # Get hot posts from subreddit
                subreddit_stories = self._get_subreddit_posts(subreddit, count)
                
                # Process and filter stories
                for story_data in subreddit_stories:
                    processed_story = self._process_story(story_data, category, subreddit)
                    if processed_story:
                        stories.append(processed_story)
                
                # Add small delay to be respectful to Reddit's servers
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.warning(f"Failed to extract from r/{subreddit}: {e}")
                continue
        
        return stories
    
    def _get_subreddit_posts(self, subreddit: str, limit: int = 5) -> List[Dict]:
        """Get hot posts from a specific subreddit"""
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        params = {
            'limit': limit * 2,  # Get more to filter better
            't': 'day'  # Posts from today
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            # Extract post data
            post_data = []
            for post in posts:
                if post.get('kind') == 't3':  # Link post
                    post_data.append(post.get('data', {}))
            
            return post_data
            
        except Exception as e:
            self.logger.error(f"Failed to get posts from r/{subreddit}: {e}")
            return []
    
    def _process_story(self, story_data: Dict, category: str, subreddit: str) -> Optional[Dict[str, str]]:
        """Process and validate a Reddit story"""
        try:
            # Extract key information
            title = story_data.get('title', '').strip()
            score = story_data.get('score', 0)
            selftext = story_data.get('selftext', '').strip()
            url = story_data.get('url', '')
            created_utc = story_data.get('created_utc', 0)
            
            # Filter criteria
            if not title or len(title) < 10:
                return None
                
            if score < self.min_score:
                return None
            
            # Check if story is recent enough
            story_age_hours = (time.time() - created_utc) / 3600
            if story_age_hours > self.max_age_hours:
                return None
            
            # Create processed story
            processed_title = self._create_video_friendly_title(title, category)
            
            story = {
                'title': processed_title,
                'original_title': title,
                'category': category,
                'subreddit': subreddit,
                'score': str(score),
                'source': 'Reddit',
                'story_preview': selftext[:200] + '...' if len(selftext) > 200 else selftext,
                'reddit_url': f"https://reddit.com{story_data.get('permalink', '')}",
                'extracted_at': datetime.now().isoformat()
            }
            
            self.logger.debug(f"Processed story from r/{subreddit}: {processed_title}")
            return story
            
        except Exception as e:
            self.logger.warning(f"Failed to process story: {e}")
            return None
    
    def _create_video_friendly_title(self, original_title: str, category: str) -> str:
        """Convert Reddit title to video-friendly format"""
        
        # Clean up common Reddit prefixes
        prefixes_to_remove = [
            'TIFU by',
            'AITA for',
            'AITA if',
            'LPT:',
            'YSK:',
            'TIL:',
            '[Serious]',
            'UPDATE:',
            'WIBTA'
        ]
        
        title = original_title
        for prefix in prefixes_to_remove:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
                break
        
        # Create engaging YouTube format based on category
        if category == 'stories':
            if 'TIFU' in original_title:
                title = f"I Made a HUGE Mistake: {title}"
            elif 'AITA' in original_title:
                title = f"Am I Wrong For This? {title}"
            elif 'relationship' in original_title.lower():
                title = f"Relationship Drama: {title}"
            else:
                title = f"True Story: {title}"
        
        elif category == 'career':
            title = f"Career Advice: {title}"
        
        elif category == 'self_help':
            title = f"Life Lesson: {title}"
        
        # Ensure title isn't too long for YouTube
        if len(title) > 80:
            title = title[:77] + '...'
        
        return title
    
    def test_connection(self) -> bool:
        """Test Reddit API connection"""
        try:
            self.logger.info("Testing Reddit API connection...")
            
            # Test with a simple subreddit request
            test_url = "https://www.reddit.com/r/python/hot.json"
            params = {'limit': 1}
            
            response = self.session.get(test_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    self.logger.info("✅ Reddit API connection successful")
                    return True
                else:
                    self.logger.error("❌ Reddit API returned invalid data")
                    return False
            else:
                self.logger.error(f"❌ Reddit API connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Reddit API connection failed: {e}")
            return False
    
    def get_api_usage_info(self) -> Dict[str, str]:
        """Get information about Reddit API usage and limits"""
        return {
            'provider': 'Reddit',
            'rate_limit': '60 requests/minute (public) / 600/minute (authenticated)',
            'features': 'Trending posts, story extraction, community content',
            'cost': 'Free',
            'authentication': 'Optional (increases rate limits)'
        }
