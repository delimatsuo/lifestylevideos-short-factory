"""
YouTube Distribution Manager for Shorts Factory
Orchestrates automated YouTube video uploads with metadata integration
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json

from integrations.youtube_api import YouTubeAPIManager
from integrations.google_sheets import GoogleSheetsManager
from core.metadata_manager import MetadataManager
from core.config import config


class YouTubeDistributionManager:
    """
    Manages complete YouTube distribution workflow for Shorts Factory
    Handles video uploads, metadata integration, and status tracking
    """
    
    def __init__(self):
        """Initialize YouTube Distribution Manager"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.youtube_api = None
        self.sheets_manager = None
        self.metadata_manager = None
        
        # Working directories
        self.captioned_videos_dir = Path(config.working_directory) / "captioned_videos"
        self.metadata_dir = Path(config.working_directory) / "metadata"
        self.distribution_logs_dir = Path(config.working_directory) / "logs" / "distribution"
        
        # Distribution settings
        self.default_privacy_status = 'public'  # Options: 'private', 'unlisted', 'public'
        self.default_category_id = '22'  # People & Blogs category
        self.max_concurrent_uploads = 3  # Rate limiting for YouTube API
        
        # Ensure distribution logs directory exists
        self.ensure_distribution_logs_directory()
        
        self.logger.info("📺 YouTube Distribution Manager initialized")
    
    def ensure_distribution_logs_directory(self):
        """Ensure the distribution logs directory exists"""
        try:
            self.distribution_logs_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"📁 Distribution logs directory ready: {self.distribution_logs_dir}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create distribution logs directory: {e}")
            raise
    
    def initialize(self) -> bool:
        """Initialize all required components for YouTube distribution"""
        try:
            self.logger.info("🔧 Initializing YouTube Distribution Manager components...")
            
            # Create YouTube API Manager but don't authenticate yet (defer OAuth)
            self.youtube_api = YouTubeAPIManager()
            self.logger.info("✅ YouTube API Manager created (authentication deferred)")
            
            # Initialize Google Sheets manager
            self.sheets_manager = GoogleSheetsManager()
            self.logger.info("✅ Google Sheets manager initialized")
            
            # Initialize Metadata Manager
            self.metadata_manager = MetadataManager()
            self.logger.info("✅ Metadata Manager initialized")
            
            self.logger.info("✅ YouTube Distribution Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ YouTube Distribution Manager initialization failed: {e}")
            return False
    
    def find_captioned_video_for_content(self, content_id: str) -> Optional[str]:
        """
        Find the captioned video file for a content item
        
        Args:
            content_id: The content ID to find captioned video for
            
        Returns:
            Path to captioned video file, or None if not found
        """
        try:
            # Look for captioned video files matching the content ID pattern
            patterns = [
                f"captioned_{content_id}_*.mp4",
                f"*_{content_id}_captioned*.mp4",
                f"content_{content_id}_*.mp4"
            ]
            
            for pattern in patterns:
                video_files = list(self.captioned_videos_dir.glob(pattern))
                if video_files:
                    # Use the most recent file if multiple matches
                    video_file = max(video_files, key=lambda f: f.stat().st_mtime)
                    self.logger.info(f"📺 Found captioned video: {video_file.name}")
                    return str(video_file)
            
            self.logger.warning(f"⚠️ No captioned video found for content ID: {content_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error finding captioned video for {content_id}: {e}")
            return None
    
    def get_metadata_for_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve generated metadata for a content item
        
        Args:
            content_id: Content identifier
            
        Returns:
            Metadata dictionary if found, None otherwise
        """
        try:
            # Use metadata manager to get stored metadata
            metadata = self.metadata_manager.get_metadata_for_content(content_id)
            
            if metadata:
                self.logger.info(f"✅ Retrieved metadata for content {content_id}")
                return metadata
            else:
                self.logger.warning(f"⚠️ No metadata found for content ID: {content_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error retrieving metadata for {content_id}: {e}")
            return None
    
    def log_distribution_event(
        self, 
        content_id: str, 
        event_type: str, 
        details: Dict[str, Any]
    ) -> None:
        """Log distribution events for tracking and debugging"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'content_id': content_id,
                'event_type': event_type,
                'details': details
            }
            
            # Log to file
            log_file = self.distribution_logs_dir / f"distribution_{datetime.now().strftime('%Y%m%d')}.jsonl"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            self.logger.debug(f"📝 Distribution event logged: {event_type} for {content_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log distribution event: {e}")
    
    def update_sheets_with_youtube_url(
        self, 
        content_id: str, 
        youtube_url: str, 
        upload_details: Dict[str, Any]
    ) -> bool:
        """
        Update Google Sheets with YouTube URL and completion status
        
        Args:
            content_id: The content ID
            youtube_url: The YouTube video URL
            upload_details: Details about the upload
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Prepare status update
            completion_message = f"COMPLETE - Video published to YouTube at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Create YouTube info summary
            youtube_info = {
                'youtube_url': youtube_url,
                'video_id': upload_details.get('video_id', ''),
                'uploaded_at': upload_details.get('uploaded_at', ''),
                'privacy_status': upload_details.get('privacy_status', 'public'),
                'title': upload_details.get('title', ''),
                'distribution_complete': True
            }
            
            # Update Google Sheets with YouTube URL (using a suitable column)
            # We'll use the ERROR_LOG column to store YouTube info as JSON
            success = self.sheets_manager.update_content_field(
                content_id,
                'ERROR_LOG',  # Using this field for YouTube URL storage
                json.dumps(youtube_info, ensure_ascii=False),
                completion_message
            )
            
            if success:
                self.logger.info(f"✅ Google Sheets updated with YouTube URL for ID {content_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to update Google Sheets for ID {content_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error updating Google Sheets with YouTube URL: {e}")
            return False
    
    def upload_video_to_youtube(self, content_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Upload a complete video to YouTube with metadata
        
        Args:
            content_item: Dictionary containing content information
            
        Returns:
            Upload results dictionary, or None if failed
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            
            if not content_id:
                self.logger.error("❌ Content ID is required for YouTube upload")
                return None
            
            self.logger.info(f"📺 Starting YouTube upload for: {title} (ID: {content_id})")
            
            # Find captioned video file
            video_file_path = self.find_captioned_video_for_content(content_id)
            if not video_file_path:
                self.logger.error(f"❌ No captioned video found for content ID: {content_id}")
                return None
            
            # Get metadata for upload
            metadata = self.get_metadata_for_content(content_id)
            if not metadata:
                self.logger.warning(f"⚠️ No metadata found for {content_id}, using defaults")
                # Use basic metadata from content item
                metadata = {
                    'title': title,
                    'description': f"Check out this amazing content: {title}",
                    'tags': ['lifestyle', 'productivity', 'tips', 'motivation', 'success']
                }
            
            # Extract metadata components
            youtube_title = metadata.get('title', title)
            youtube_description = metadata.get('description', f"Amazing content: {title}")
            youtube_tags = metadata.get('tags', ['lifestyle', 'productivity'])
            
            # Log upload start
            self.log_distribution_event(content_id, 'upload_started', {
                'video_file': Path(video_file_path).name,
                'title': youtube_title,
                'tags_count': len(youtube_tags)
            })
            
            # Upload video to YouTube
            self.logger.info(f"⬆️ Uploading to YouTube...")
            upload_result = self.youtube_api.upload_video(
                video_file_path=video_file_path,
                title=youtube_title,
                description=youtube_description,
                tags=youtube_tags,
                privacy_status=self.default_privacy_status,
                category_id=self.default_category_id
            )
            
            if not upload_result:
                self.logger.error(f"❌ YouTube upload failed for content ID: {content_id}")
                
                # Log upload failure
                self.log_distribution_event(content_id, 'upload_failed', {
                    'error': 'YouTube API upload returned None',
                    'video_file': Path(video_file_path).name
                })
                
                return None
            
            # Log successful upload
            self.log_distribution_event(content_id, 'upload_successful', {
                'video_id': upload_result.get('video_id', ''),
                'video_url': upload_result.get('video_url', ''),
                'privacy_status': upload_result.get('privacy_status', '')
            })
            
            # Update Google Sheets with YouTube URL
            youtube_url = upload_result.get('video_url', '')
            if youtube_url:
                self.update_sheets_with_youtube_url(content_id, youtube_url, upload_result)
            
            self.logger.info(f"🎉 YouTube upload completed successfully for: {title}")
            self.logger.info(f"🔗 YouTube URL: {youtube_url}")
            
            return upload_result
            
        except Exception as e:
            self.logger.error(f"❌ YouTube upload error for content {content_id}: {e}")
            
            # Log upload error
            self.log_distribution_event(content_id, 'upload_error', {
                'error': str(e),
                'content_id': content_id
            })
            
            return None
    
    def get_content_ready_for_distribution(self) -> List[Dict[str, Any]]:
        """
        Get all content items that are ready for YouTube distribution
        (Have captioned video and metadata, but no YouTube URL yet)
        
        Returns:
            List of content items ready for distribution
        """
        try:
            self.logger.info("🔍 Finding content ready for YouTube distribution...")
            
            # Get all content from Google Sheets
            all_content = self.sheets_manager.get_all_content()
            
            ready_content = []
            
            for content in all_content:
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                error_log = content.get('error_log', '')  # We store both metadata and YouTube info here
                
                # Check if content has metadata but no YouTube URL yet
                has_metadata = bool(error_log and ('youtube_metadata' in error_log or 'metadata' in error_log))
                has_youtube_url = bool(error_log and 'youtube_url' in error_log and 'distribution_complete' in error_log)
                has_captioned_video = bool(self.find_captioned_video_for_content(content_id))
                
                if has_metadata and has_captioned_video and not has_youtube_url:
                    self.logger.debug(f"✅ Ready for distribution: {title} (ID: {content_id})")
                    ready_content.append(content)
                else:
                    reasons = []
                    if not has_metadata:
                        reasons.append("no metadata")
                    if not has_captioned_video:
                        reasons.append("no captioned video")
                    if has_youtube_url:
                        reasons.append("already distributed")
                    
                    self.logger.debug(f"⏭️ Skipping {title} (ID: {content_id}): {', '.join(reasons)}")
            
            self.logger.info(f"📺 Found {len(ready_content)} content items ready for YouTube distribution")
            return ready_content
            
        except Exception as e:
            self.logger.error(f"❌ Error finding content ready for distribution: {e}")
            return []
    
    def run_distribution_cycle(self) -> Dict[str, Any]:
        """
        Run a complete YouTube distribution cycle for all ready content
        
        Returns:
            Dictionary with distribution results and statistics
        """
        try:
            self.logger.info("📺 Starting YouTube distribution cycle...")
            
            cycle_start_time = datetime.now()
            
            # Find content ready for distribution
            ready_content = self.get_content_ready_for_distribution()
            
            results = {
                'total_ready': len(ready_content),
                'successfully_uploaded': 0,
                'failed_uploads': 0,
                'uploaded_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0
            }
            
            if not ready_content:
                self.logger.info("📊 No content ready for YouTube distribution")
                return results
            
            # Limit concurrent uploads to avoid rate limits
            process_count = min(len(ready_content), self.max_concurrent_uploads)
            self.logger.info(f"📺 Processing {process_count} items for YouTube upload")
            
            # Process each content item
            for i, content in enumerate(ready_content[:process_count]):
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                
                try:
                    self.logger.info(f"📺 Processing ({i+1}/{process_count}): {title} (ID: {content_id})")
                    
                    upload_result = self.upload_video_to_youtube(content)
                    
                    if upload_result:
                        results['successfully_uploaded'] += 1
                        results['uploaded_items'].append({
                            'id': content_id,
                            'title': title,
                            'youtube_url': upload_result.get('video_url', ''),
                            'video_id': upload_result.get('video_id', '')
                        })
                        self.logger.info(f"✅ Successfully uploaded: {title}")
                    else:
                        results['failed_uploads'] += 1
                        results['failed_items'].append({
                            'id': content_id,
                            'title': title,
                            'error': 'Upload process failed'
                        })
                        self.logger.error(f"❌ Failed to upload: {title}")
                        
                except Exception as e:
                    results['failed_uploads'] += 1
                    results['failed_items'].append({
                        'id': content_id,
                        'title': title,
                        'error': str(e)
                    })
                    self.logger.error(f"❌ Error processing {title}: {e}")
            
            # Calculate cycle duration
            cycle_end_time = datetime.now()
            cycle_duration = (cycle_end_time - cycle_start_time).total_seconds()
            results['cycle_duration_seconds'] = cycle_duration
            
            # Log summary
            self.logger.info("🎉 YouTube distribution cycle completed!")
            self.logger.info(f"📊 Results: {results['successfully_uploaded']}/{results['total_ready']} successful uploads")
            self.logger.info(f"⏱️ Duration: {cycle_duration:.1f} seconds")
            
            if results['failed_uploads'] > 0:
                self.logger.warning(f"⚠️ {results['failed_uploads']} uploads failed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in YouTube distribution cycle: {e}")
            return {
                'total_ready': 0,
                'successfully_uploaded': 0,
                'failed_uploads': 0,
                'uploaded_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0,
                'error': str(e)
            }
    
    def get_channel_statistics(self) -> Optional[Dict[str, Any]]:
        """Get statistics about the YouTube channel"""
        try:
            if not self.youtube_api:
                self.logger.error("❌ YouTube API not initialized")
                return None
            
            channel_info = self.youtube_api.get_channel_info()
            if not channel_info:
                return None
            
            stats = channel_info.get('statistics', {})
            
            return {
                'channel_name': channel_info['snippet']['title'],
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'channel_id': channel_info['id']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get channel statistics: {e}")
            return None
    
    def list_recent_uploads(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """List recent video uploads from the channel"""
        try:
            if not self.youtube_api:
                self.logger.error("❌ YouTube API not initialized")
                return []
            
            return self.youtube_api.list_channel_videos(max_results)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list recent uploads: {e}")
            return []
