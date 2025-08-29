"""
YouTube API Integration for Shorts Factory
Handles OAuth 2.0 authentication and video uploads using YouTube Data API v3
"""

import logging
import os
import pickle
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from core.config import config


class YouTubeAPIManager:
    """
    Manages YouTube Data API v3 integration for automated video uploads
    Handles OAuth 2.0 authentication and video publishing
    """
    
    def __init__(self):
        """Initialize YouTube API Manager"""
        self.logger = logging.getLogger(__name__)
        
        # YouTube API configuration
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.api_service_name = 'youtube'
        self.api_version = 'v3'
        
        # File paths for credentials
        self.credentials_dir = Path(config.working_directory) / "credentials"
        self.client_secrets_file = self.credentials_dir / "client_secret.json"
        self.token_file = self.credentials_dir / "youtube_token.pickle"
        
        # YouTube service client
        self.youtube_service = None
        self.credentials = None
        
        # Upload configurations
        self.max_retries = 3
        self.retriable_exceptions = (HttpError,)
        self.retriable_status_codes = [500, 502, 503, 504]
        
        # Video upload settings
        self.default_privacy_status = 'public'  # Options: 'private', 'unlisted', 'public'
        self.default_category_id = '22'  # People & Blogs category
        
        # Ensure credentials directory exists
        self.ensure_credentials_directory()
        
        self.logger.info("📺 YouTube API Manager initialized")
    
    def ensure_credentials_directory(self):
        """Ensure the credentials directory exists"""
        try:
            self.credentials_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"📁 Credentials directory ready: {self.credentials_dir}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create credentials directory: {e}")
            raise
    
    def initialize(self) -> bool:
        """Initialize YouTube API service with OAuth 2.0 authentication"""
        try:
            self.logger.info("🔧 Initializing YouTube API service...")
            
            # Check if client secrets file exists
            if not self.client_secrets_file.exists():
                self.logger.error(f"❌ Client secrets file not found: {self.client_secrets_file}")
                self.logger.info("📝 Please download client_secret.json from Google Cloud Console")
                self.logger.info("   1. Go to https://console.cloud.google.com/")
                self.logger.info("   2. Select your project")
                self.logger.info("   3. Go to APIs & Services > Credentials")
                self.logger.info("   4. Create OAuth 2.0 Client ID (Desktop application)")
                self.logger.info(f"   5. Download and save as {self.client_secrets_file}")
                return False
            
            # Load or create credentials
            self.credentials = self._get_authenticated_credentials()
            
            if not self.credentials:
                self.logger.error("❌ Failed to obtain YouTube API credentials")
                return False
            
            # Build YouTube service
            self.youtube_service = build(
                self.api_service_name,
                self.api_version,
                credentials=self.credentials
            )
            
            # Test the connection
            if not self._test_api_connection():
                self.logger.error("❌ YouTube API connection test failed")
                return False
            
            self.logger.info("✅ YouTube API service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ YouTube API initialization failed: {e}")
            return False
    
    def _get_authenticated_credentials(self) -> Optional[Credentials]:
        """Get authenticated credentials using OAuth 2.0 flow"""
        try:
            credentials = None
            
            # Load existing token if available
            if self.token_file.exists():
                self.logger.debug("📄 Loading existing credentials...")
                try:
                    with open(self.token_file, 'rb') as token:
                        credentials = pickle.load(token)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to load existing credentials: {e}")
            
            # If there are no valid credentials available, run the OAuth flow
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    self.logger.info("🔄 Refreshing expired credentials...")
                    try:
                        credentials.refresh(Request())
                        self.logger.info("✅ Credentials refreshed successfully")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to refresh credentials: {e}")
                        credentials = None
                
                # Run OAuth flow if needed
                if not credentials:
                    self.logger.info("🔐 Starting OAuth 2.0 authentication flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file,
                        self.scopes
                    )
                    
                    # Use local server for OAuth flow
                    credentials = flow.run_local_server(port=0)
                    self.logger.info("✅ OAuth authentication completed")
                
                # Save credentials for future use
                try:
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(credentials, token)
                    self.logger.info(f"✅ Credentials saved to {self.token_file}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to save credentials: {e}")
            
            return credentials
            
        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            return None
    
    def _test_api_connection(self) -> bool:
        """Test the YouTube API connection"""
        try:
            # Test by getting channel information
            request = self.youtube_service.channels().list(
                part="snippet,contentDetails,statistics",
                mine=True
            )
            response = request.execute()
            
            if 'items' in response and len(response['items']) > 0:
                channel = response['items'][0]
                channel_name = channel['snippet']['title']
                self.logger.info(f"✅ Connected to YouTube channel: {channel_name}")
                return True
            else:
                self.logger.error("❌ No YouTube channel found for authenticated account")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ API connection test failed: {e}")
            return False
    
    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the authenticated YouTube channel"""
        try:
            if not self.youtube_service:
                self.logger.error("❌ YouTube service not initialized")
                return None
            
            request = self.youtube_service.channels().list(
                part="snippet,contentDetails,statistics,brandingSettings",
                mine=True
            )
            response = request.execute()
            
            if 'items' in response and len(response['items']) > 0:
                return response['items'][0]
            else:
                self.logger.error("❌ No channel information found")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get channel info: {e}")
            return None
    
    def upload_video(
        self,
        video_file_path: str,
        title: str,
        description: str,
        tags: List[str],
        privacy_status: str = None,
        category_id: str = None,
        thumbnail_path: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Upload a video to YouTube with metadata
        
        Args:
            video_file_path: Path to the video file to upload
            title: Video title
            description: Video description
            tags: List of video tags
            privacy_status: Privacy setting ('private', 'unlisted', 'public')
            category_id: YouTube category ID
            thumbnail_path: Optional path to custom thumbnail
            
        Returns:
            Dictionary with upload results, or None if failed
        """
        try:
            if not self.youtube_service:
                self.logger.error("❌ YouTube service not initialized")
                return None
            
            # Validate video file
            video_path = Path(video_file_path)
            if not video_path.exists():
                self.logger.error(f"❌ Video file not found: {video_file_path}")
                return None
            
            self.logger.info(f"📺 Starting YouTube upload: {title}")
            
            # Set default values
            if privacy_status is None:
                privacy_status = self.default_privacy_status
            if category_id is None:
                category_id = self.default_category_id
            
            # Prepare video metadata
            video_metadata = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id,
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False,
                    'publishAt': None  # Publish immediately
                },
                'recordingDetails': {
                    'recordingDate': datetime.now().isoformat() + 'Z'
                }
            }
            
            # Create media upload object
            media = MediaFileUpload(
                video_file_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            # Create upload request
            upload_request = self.youtube_service.videos().insert(
                part=','.join(video_metadata.keys()),
                body=video_metadata,
                media_body=media
            )
            
            # Execute upload with retry logic
            upload_response = self._execute_upload_with_retry(upload_request)
            
            if not upload_response:
                self.logger.error("❌ Video upload failed")
                return None
            
            video_id = upload_response.get('id')
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            self.logger.info(f"✅ Video uploaded successfully!")
            self.logger.info(f"📺 Video ID: {video_id}")
            self.logger.info(f"🔗 Video URL: {video_url}")
            
            # Upload custom thumbnail if provided
            if thumbnail_path and Path(thumbnail_path).exists():
                self._upload_thumbnail(video_id, thumbnail_path)
            
            # Return upload results
            return {
                'video_id': video_id,
                'video_url': video_url,
                'title': title,
                'privacy_status': privacy_status,
                'upload_response': upload_response,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Video upload failed: {e}")
            return None
    
    def _execute_upload_with_retry(self, upload_request) -> Optional[Dict[str, Any]]:
        """Execute upload request with retry logic for resilient uploads"""
        try:
            response = None
            retry_count = 0
            
            while response is None and retry_count < self.max_retries:
                try:
                    self.logger.info(f"📤 Uploading video (attempt {retry_count + 1}/{self.max_retries})...")
                    
                    status, response = upload_request.next_chunk()
                    
                    if response is not None:
                        if 'id' in response:
                            self.logger.info("✅ Upload completed successfully")
                            return response
                        else:
                            self.logger.error(f"❌ Upload failed with response: {response}")
                            return None
                    elif status:
                        progress = int(status.progress() * 100)
                        self.logger.info(f"📤 Upload progress: {progress}%")
                
                except HttpError as e:
                    if e.resp.status in self.retriable_status_codes:
                        self.logger.warning(f"⚠️ Retriable error {e.resp.status}: {e}")
                        retry_count += 1
                        if retry_count >= self.max_retries:
                            self.logger.error("❌ Maximum retries exceeded")
                            return None
                    else:
                        self.logger.error(f"❌ Non-retriable HTTP error: {e}")
                        return None
                
                except Exception as e:
                    if retry_count < self.max_retries:
                        self.logger.warning(f"⚠️ Upload error, retrying: {e}")
                        retry_count += 1
                    else:
                        self.logger.error(f"❌ Upload failed after {self.max_retries} retries: {e}")
                        return None
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Upload execution failed: {e}")
            return None
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload custom thumbnail for a video"""
        try:
            self.logger.info(f"🖼️ Uploading custom thumbnail...")
            
            thumbnail_media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            
            request = self.youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=thumbnail_media
            )
            
            response = request.execute()
            
            if response:
                self.logger.info("✅ Custom thumbnail uploaded successfully")
                return True
            else:
                self.logger.error("❌ Thumbnail upload failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Thumbnail upload error: {e}")
            return False
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an uploaded video"""
        try:
            if not self.youtube_service:
                self.logger.error("❌ YouTube service not initialized")
                return None
            
            request = self.youtube_service.videos().list(
                part="snippet,status,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if 'items' in response and len(response['items']) > 0:
                return response['items'][0]
            else:
                self.logger.error(f"❌ Video not found: {video_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get video info: {e}")
            return None
    
    def update_video_metadata(
        self,
        video_id: str,
        title: str = None,
        description: str = None,
        tags: List[str] = None,
        privacy_status: str = None
    ) -> bool:
        """Update metadata for an existing video"""
        try:
            if not self.youtube_service:
                self.logger.error("❌ YouTube service not initialized")
                return False
            
            # Get current video info
            current_info = self.get_video_info(video_id)
            if not current_info:
                return False
            
            # Prepare update data
            update_data = {
                'id': video_id,
                'snippet': current_info['snippet']
            }
            
            # Update fields if provided
            if title:
                update_data['snippet']['title'] = title
            if description:
                update_data['snippet']['description'] = description
            if tags:
                update_data['snippet']['tags'] = tags
            
            if privacy_status:
                update_data['status'] = current_info.get('status', {})
                update_data['status']['privacyStatus'] = privacy_status
            
            # Execute update
            request = self.youtube_service.videos().update(
                part=','.join(update_data.keys()) if 'status' in update_data else 'snippet',
                body=update_data
            )
            
            response = request.execute()
            
            if response:
                self.logger.info(f"✅ Video metadata updated: {video_id}")
                return True
            else:
                self.logger.error("❌ Video metadata update failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Video metadata update error: {e}")
            return False
    
    def delete_video(self, video_id: str) -> bool:
        """Delete a video from YouTube"""
        try:
            if not self.youtube_service:
                self.logger.error("❌ YouTube service not initialized")
                return False
            
            request = self.youtube_service.videos().delete(id=video_id)
            response = request.execute()
            
            self.logger.info(f"✅ Video deleted: {video_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Video deletion failed: {e}")
            return False
    
    def list_channel_videos(self, max_results: int = 25) -> List[Dict[str, Any]]:
        """List recent videos from the authenticated channel"""
        try:
            if not self.youtube_service:
                self.logger.error("❌ YouTube service not initialized")
                return []
            
            # Get channel's upload playlist
            channel_info = self.get_channel_info()
            if not channel_info:
                return []
            
            upload_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from upload playlist
            request = self.youtube_service.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=upload_playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_info = {
                    'video_id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails'].get('default', {}).get('url', '')
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list channel videos: {e}")
            return []
