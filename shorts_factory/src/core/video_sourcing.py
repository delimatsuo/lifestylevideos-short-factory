"""
Video Sourcing Module for Shorts Factory
Orchestrates stock video sourcing using Pexels API and Google Sheets integration
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

from integrations.pexels_api import PexelsVideoSourcing
from integrations.google_sheets import GoogleSheetsManager
from security.secure_config import config


class VideoSourcingManager:
    """Orchestrates video sourcing workflow for content with scripts and audio"""
    
    def __init__(self):
        """Initialize the video sourcing manager"""
        self.logger = logging.getLogger(__name__)
        self.pexels = None
        self.sheets_manager = None
        
        # Video sourcing settings
        self.default_video_count = 3  # Number of video clips per content
        self.video_quality = "medium"
        self.orientation = "portrait"  # For shorts
        
    def initialize(self) -> bool:
        """Initialize video sourcing components"""
        try:
            self.logger.info("🎥 Initializing Video Sourcing Manager...")
            
            # Initialize Pexels API
            self.pexels = PexelsVideoSourcing()
            if not self.pexels.test_connection():
                raise Exception("Pexels API connection failed")
            
            # Initialize Google Sheets
            self.sheets_manager = GoogleSheetsManager()
            if not self.sheets_manager.test_connection():
                raise Exception("Google Sheets connection failed")
            
            self.logger.info("✅ Video Sourcing Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Video Sourcing Manager: {e}")
            return False
    
    def source_videos_for_content(self, content_item: Dict[str, str]) -> List[str]:
        """
        Source video clips for a single content item
        
        Args:
            content_item: Dictionary containing content details (id, title, script, etc.)
            
        Returns:
            List of paths to downloaded video files
        """
        try:
            content_id = content_item.get('id', '').strip()
            title = content_item.get('title', '').strip()
            script = content_item.get('script', '').strip()
            
            if not content_id:
                self.logger.warning("⚠️ No content ID provided")
                return []
            
            if not title:
                self.logger.warning(f"⚠️ No title found for content ID {content_id}")
                return []
            
            self.logger.info(f"🎥 Sourcing videos for: {title} (ID: {content_id})")
            
            # Source videos using Pexels
            video_paths = self.pexels.source_videos_for_content(
                content_id=content_id,
                title=title,
                script=script,
                num_videos=self.default_video_count
            )
            
            if video_paths:
                self.logger.info(f"✅ Sourced {len(video_paths)} videos for: {title}")
                
                # Log video details
                for i, path in enumerate(video_paths, 1):
                    video_file = Path(path)
                    if video_file.exists():
                        size_mb = video_file.stat().st_size / (1024 * 1024)
                        self.logger.info(f"   📹 Video {i}: {video_file.name} ({size_mb:.1f} MB)")
                
                return video_paths
            else:
                self.logger.warning(f"⚠️ No videos sourced for: {title}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error sourcing videos: {e}")
            return []
    
    def save_video_paths_to_sheet(self, content_id: str, video_paths: List[str]) -> bool:
        """
        Save video file paths to Google Sheets
        
        Args:
            content_id: The ID of the content item
            video_paths: List of paths to video files
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            if not video_paths:
                self.logger.warning(f"⚠️ No video paths to save for content {content_id}")
                return True  # Not an error, just no videos
            
            # Convert absolute paths to relative paths from working directory
            working_dir = Path(config.working_directory)
            relative_paths = []
            
            for video_path in video_paths:
                video_file = Path(video_path)
                
                try:
                    # Try to make relative path
                    relative_path = video_file.relative_to(working_dir)
                    relative_paths.append(str(relative_path))
                except ValueError:
                    # If not relative, use filename only
                    relative_paths.append(video_file.name)
            
            # Create a formatted string of video paths
            video_paths_str = " | ".join(relative_paths)  # Separate with |
            
            # Save to Google Sheets VIDEO_FILE column
            success = self.sheets_manager.update_content_field(
                content_id,
                'VIDEO_FILE',
                video_paths_str,
                f"Videos sourced at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({len(video_paths)} clips)"
            )
            
            if success:
                self.logger.info(f"✅ Video paths saved to Google Sheets for ID {content_id}")
                self.logger.info(f"   📋 Paths: {video_paths_str}")
                return True
            else:
                self.logger.error(f"❌ Failed to save video paths to Google Sheets for ID {content_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error saving video paths to Google Sheets: {e}")
            return False
    
    def source_and_save_videos(self, content_item: Dict[str, str]) -> bool:
        """
        Complete workflow: source videos and save paths to Google Sheets
        
        Args:
            content_item: Dictionary containing content details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            # Source the videos
            video_paths = self.source_videos_for_content(content_item)
            
            if not video_paths:
                # Log warning but don't fail - some content might not have good video matches
                self.logger.warning(f"⚠️ No videos sourced for: {title}")
                
                # Save empty result to Google Sheets to track attempt
                success = self.sheets_manager.update_content_field(
                    content_id,
                    'VIDEO_FILE',
                    "No suitable videos found",
                    f"Video search attempted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                return success  # Return success even with no videos
            
            # Save paths to Google Sheets
            if self.save_video_paths_to_sheet(content_id, video_paths):
                self.logger.info(f"🎉 Complete video sourcing successful for: {title}")
                return True
            else:
                self.logger.error(f"❌ Failed to save video info for: {title}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in complete video sourcing workflow: {e}")
            return False
    
    def batch_source_videos(self, content_items: List[Dict[str, str]]) -> Dict[str, bool]:
        """
        Source videos for multiple content items
        
        Args:
            content_items: List of content item dictionaries with scripts
            
        Returns:
            Dictionary mapping content_id to success status
        """
        results = {}
        
        self.logger.info(f"🎥 Starting batch video sourcing for {len(content_items)} items")
        
        for content_item in content_items:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            try:
                success = self.source_and_save_videos(content_item)
                results[content_id] = success
                
                if success:
                    self.logger.info(f"✅ [{len(results)}/{len(content_items)}] Success: {title}")
                else:
                    self.logger.error(f"❌ [{len(results)}/{len(content_items)}] Failed: {title}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing {title}: {e}")
                results[content_id] = False
        
        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"📊 Batch video sourcing complete: {successful}/{len(content_items)} successful")
        
        return results
    
    def get_content_ready_for_videos(self) -> List[Dict[str, str]]:
        """
        Get content items that have scripts and audio but need video clips
        
        Returns:
            List of content items ready for video sourcing
        """
        try:
            self.logger.info("📋 Fetching content ready for video sourcing...")
            
            # Get all content from spreadsheet
            all_content = self.sheets_manager.get_all_content()
            
            ready_for_videos = []
            for content_item in all_content:
                script = content_item.get('script', '').strip()
                audio_file = content_item.get('audio_file', '').strip()
                video_file = content_item.get('video_file', '').strip()
                status = content_item.get('status', '').strip()
                
                # Check if has script and audio but no videos, and status allows processing
                if (script and 
                    audio_file and 
                    not video_file and 
                    status.lower() in ['approved', 'in progress', 'completed']):
                    ready_for_videos.append(content_item)
            
            self.logger.info(f"📊 Found {len(ready_for_videos)} items ready for video sourcing")
            return ready_for_videos
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching content for video sourcing: {e}")
            return []
    
    def cleanup_old_videos(self, days_old: int = 7) -> int:
        """Clean up old video files to manage storage"""
        if self.pexels:
            return self.pexels.cleanup_old_videos(days_old)
        return 0
    
    def get_video_sourcing_stats(self) -> Dict[str, any]:
        """Get statistics about video sourcing capabilities"""
        stats = {
            'default_video_count': self.default_video_count,
            'video_quality': self.video_quality,
            'orientation': self.orientation,
            'pexels_available': self.pexels is not None,
            'sheets_available': self.sheets_manager is not None,
            'status': 'operational' if (self.pexels and self.sheets_manager) else 'needs_initialization'
        }
        
        # Add Pexels-specific stats if available
        if self.pexels:
            pexels_stats = self.pexels.get_video_sourcing_stats()
            stats.update({
                'video_directory': pexels_stats.get('video_directory'),
                'total_video_files': pexels_stats.get('total_video_files', 0),
                'total_size_mb': pexels_stats.get('total_size_mb', 0),
                'pexels_status': pexels_stats.get('status', 'unknown')
            })
        
        return stats
