"""
Pexels API Integration for Shorts Factory
Automatically sources and downloads relevant stock video clips based on content topics
"""

import requests
import logging
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime
import os
import re
from urllib.parse import urlparse

from security.secure_config import config


class PexelsVideoSourcing:
    """Handles stock video sourcing and downloading using Pexels API"""
    
    def __init__(self):
        """Initialize Pexels video sourcing client"""
        self.logger = logging.getLogger(__name__)
        self.api_key = config.pexels_api_key
        self.base_url = "https://api.pexels.com/videos"
        
        # API configuration
        self.headers = {
            "Authorization": self.api_key
        }
        
        # Video search parameters
        self.default_per_page = 5  # Number of videos per search
        self.orientation = "portrait"  # For shorts/vertical videos
        self.size = "medium"  # Balance between quality and file size
        self.locale = "en-US"
        
        # Video download settings
        self.video_directory = Path(config.working_directory) / "video_clips"
        self.max_file_size_mb = 50  # Max file size for downloads
        self.supported_formats = ['.mp4', '.mov', '.avi']
        
        # Ensure directory exists
        self.ensure_video_directory()
    
    def ensure_video_directory(self):
        """Ensure the video clips directory exists"""
        try:
            self.video_directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Video directory ready: {self.video_directory}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create video directory: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Pexels API connection and authentication"""
        try:
            self.logger.info("🧪 Testing Pexels API connection...")
            
            # Test with a simple search query
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={
                    'query': 'nature',
                    'per_page': 1,
                    'orientation': self.orientation
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('total_results', 0)
                self.logger.info(f"✅ Pexels API connection successful")
                self.logger.info(f"📊 Test search returned {total_results} results")
                return True
            elif response.status_code == 401:
                self.logger.error("❌ Pexels API authentication failed - check API key")
                return False
            elif response.status_code == 429:
                self.logger.error("❌ Pexels API rate limit exceeded")
                return False
            else:
                self.logger.error(f"❌ Pexels API connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Pexels API connection test failed: {e}")
            return False
    
    def extract_keywords_from_title(self, title: str) -> List[str]:
        """
        Extract meaningful keywords from content title for video search
        
        Args:
            title: Content title/concept
            
        Returns:
            List of extracted keywords
        """
        try:
            if not title or not title.strip():
                return []
            
            # Clean and normalize title
            title = title.strip().lower()
            
            # Remove common words that don't help with video search
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                'of', 'with', 'by', 'about', 'into', 'through', 'during', 'before', 
                'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
                'again', 'further', 'then', 'once', 'will', 'would', 'should', 'could',
                'that', 'this', 'these', 'those', 'your', 'you', 'how', 'what', 'why',
                'when', 'where', 'tips', 'ways', 'steps', 'secrets', 'best', 'top'
            }
            
            # Extract words (remove numbers, special chars)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', title)
            
            # Filter out stop words and short words
            keywords = [word for word in words if word not in stop_words and len(word) >= 3]
            
            # Take most relevant keywords (first 3-5)
            primary_keywords = keywords[:5]
            
            # Add some generic business/lifestyle keywords for context
            content_categories = {
                'productivity', 'business', 'success', 'lifestyle', 'professional',
                'career', 'work', 'office', 'meeting', 'planning', 'strategy',
                'motivation', 'achievement', 'growth', 'leadership', 'management'
            }
            
            # Check if any category keywords appear
            category_matches = [word for word in keywords if word in content_categories]
            if category_matches:
                primary_keywords.extend(category_matches[:2])
            
            # Remove duplicates while preserving order
            seen = set()
            final_keywords = []
            for keyword in primary_keywords:
                if keyword not in seen:
                    seen.add(keyword)
                    final_keywords.append(keyword)
            
            self.logger.info(f"📝 Extracted keywords from '{title[:50]}...': {final_keywords}")
            return final_keywords[:4]  # Limit to 4 keywords
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting keywords from title: {e}")
            return []
    
    def search_videos_by_keywords(
        self, 
        keywords: List[str], 
        per_page: int = None,
        fallback_query: str = "business professional"
    ) -> List[Dict]:
        """
        Search for videos using extracted keywords
        
        Args:
            keywords: List of keywords to search for
            per_page: Number of results per page
            fallback_query: Fallback search if keywords don't work
            
        Returns:
            List of video data dictionaries
        """
        try:
            if not keywords:
                keywords = [fallback_query]
            
            per_page = per_page or self.default_per_page
            
            # Create search query from keywords
            search_query = " ".join(keywords[:3])  # Use top 3 keywords
            
            self.logger.info(f"🔍 Searching Pexels for: '{search_query}'")
            
            params = {
                'query': search_query,
                'per_page': per_page,
                'orientation': self.orientation,
                'size': self.size,
                'locale': self.locale
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get('videos', [])
                total_results = data.get('total_results', 0)
                
                self.logger.info(f"✅ Found {len(videos)} videos from {total_results} total results")
                
                # If no results with keywords, try fallback
                if not videos and search_query != fallback_query:
                    self.logger.info(f"🔄 No results for '{search_query}', trying fallback: '{fallback_query}'")
                    
                    params['query'] = fallback_query
                    fallback_response = requests.get(
                        f"{self.base_url}/search",
                        headers=self.headers,
                        params=params,
                        timeout=15
                    )
                    
                    if fallback_response.status_code == 200:
                        fallback_data = fallback_response.json()
                        videos = fallback_data.get('videos', [])
                        self.logger.info(f"✅ Fallback search found {len(videos)} videos")
                
                return videos
                
            else:
                self.logger.error(f"❌ Pexels search failed: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error searching videos: {e}")
            return []
    
    def download_video(
        self, 
        video_url: str, 
        filename: str,
        max_size_mb: int = None
    ) -> Optional[str]:
        """
        Download a video from URL to local storage
        
        Args:
            video_url: Direct URL to video file
            filename: Desired filename for the video
            max_size_mb: Maximum file size in MB
            
        Returns:
            Path to downloaded video file or None if failed
        """
        try:
            max_size_mb = max_size_mb or self.max_file_size_mb
            max_size_bytes = max_size_mb * 1024 * 1024
            
            self.logger.info(f"📥 Downloading video: {filename}")
            
            # Start download with streaming
            response = requests.get(video_url, stream=True, timeout=30)
            
            if response.status_code != 200:
                self.logger.error(f"❌ Failed to download video: HTTP {response.status_code}")
                return None
            
            # Check content length if available
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > max_size_bytes:
                self.logger.warning(f"⚠️ Video too large ({int(content_length)/1024/1024:.1f}MB), skipping")
                return None
            
            # Download with size tracking
            video_path = self.video_directory / filename
            downloaded_size = 0
            
            with open(video_path, 'wb') as video_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        video_file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Check size limit during download
                        if downloaded_size > max_size_bytes:
                            self.logger.warning(f"⚠️ Video exceeds size limit during download, stopping")
                            video_file.close()
                            video_path.unlink()  # Delete partial file
                            return None
            
            # Verify download
            if video_path.exists() and video_path.stat().st_size > 1000:  # At least 1KB
                file_size_mb = video_path.stat().st_size / (1024 * 1024)
                self.logger.info(f"✅ Video downloaded: {filename} ({file_size_mb:.1f} MB)")
                return str(video_path)
            else:
                self.logger.error(f"❌ Downloaded video is invalid or too small")
                if video_path.exists():
                    video_path.unlink()
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error downloading video: {e}")
            return None
    
    def source_videos_for_content(
        self, 
        content_id: str,
        title: str,
        script: str = "",
        num_videos: int = 3
    ) -> List[str]:
        """
        Complete workflow to source videos for content
        
        Args:
            content_id: Unique identifier for the content
            title: Content title/concept
            script: Content script (optional, for additional keywords)
            num_videos: Number of videos to download
            
        Returns:
            List of paths to downloaded video files
        """
        try:
            self.logger.info(f"🎥 Sourcing {num_videos} videos for content: {title}")
            
            # Extract keywords from title (and script if provided)
            keywords = self.extract_keywords_from_title(title)
            
            # Add keywords from script if available
            if script:
                script_keywords = self.extract_keywords_from_title(script[:200])  # First 200 chars
                keywords.extend([k for k in script_keywords if k not in keywords][:2])  # Add 2 unique ones
            
            # Search for videos
            videos = self.search_videos_by_keywords(keywords, per_page=num_videos * 2)  # Get more than needed
            
            if not videos:
                self.logger.warning(f"⚠️ No videos found for content: {title}")
                return []
            
            downloaded_paths = []
            
            for i, video_data in enumerate(videos[:num_videos]):
                try:
                    # Get the best quality video file URL
                    video_files = video_data.get('video_files', [])
                    if not video_files:
                        continue
                    
                    # Find the best quality file (prefer mp4, medium size)
                    best_file = self._select_best_video_file(video_files)
                    
                    if not best_file:
                        continue
                    
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"content_{content_id}_clip_{i+1}_{timestamp}.mp4"
                    
                    # Download video
                    video_path = self.download_video(best_file['link'], filename)
                    
                    if video_path:
                        downloaded_paths.append(video_path)
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to process video {i+1}: {e}")
                    continue
            
            self.logger.info(f"🎉 Successfully sourced {len(downloaded_paths)} videos for: {title}")
            return downloaded_paths
            
        except Exception as e:
            self.logger.error(f"❌ Error sourcing videos for content: {e}")
            return []
    
    def _select_best_video_file(self, video_files: List[Dict]) -> Optional[Dict]:
        """Select the best quality video file from available options"""
        try:
            # Prefer mp4 format
            mp4_files = [f for f in video_files if f.get('file_type') == 'video/mp4']
            
            # If no mp4, use any available
            candidates = mp4_files if mp4_files else video_files
            
            # Sort by quality preference (medium size, good quality)
            quality_preference = ['sd', 'hd', 'uhd']  # Standard def to ultra HD
            
            for quality in quality_preference:
                for file_data in candidates:
                    file_quality = file_data.get('quality', '') or ''  # Handle None values
                    if quality in file_quality.lower():
                        return file_data
            
            # If no quality match, return first available
            return candidates[0] if candidates else None
            
        except Exception as e:
            self.logger.error(f"❌ Error selecting video file: {e}")
            return None
    
    def get_video_sourcing_stats(self) -> Dict[str, any]:
        """Get statistics about video sourcing capabilities"""
        try:
            video_files = list(self.video_directory.glob("*.mp4"))
            total_size = sum(f.stat().st_size for f in video_files if f.exists())
            
            return {
                'video_directory': str(self.video_directory),
                'total_video_files': len(video_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'orientation': self.orientation,
                'size_preference': self.size,
                'max_file_size_mb': self.max_file_size_mb,
                'supported_formats': self.supported_formats,
                'api_endpoint': f"{self.base_url}/search",
                'status': 'operational' if self.api_key and self.api_key != 'your_pexels_api_key_here' else 'needs_api_key'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def cleanup_old_videos(self, days_old: int = 7) -> int:
        """Clean up video files older than specified days"""
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            cleaned = 0
            for video_file in self.video_directory.glob("*.mp4"):
                if video_file.stat().st_mtime < cutoff_time:
                    video_file.unlink()
                    cleaned += 1
            
            if cleaned > 0:
                self.logger.info(f"🧹 Cleaned up {cleaned} old video files")
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up videos: {e}")
            return 0
