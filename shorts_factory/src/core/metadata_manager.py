"""
Metadata Manager for Shorts Factory
Orchestrates the complete YouTube metadata generation workflow
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import json

from integrations.youtube_metadata import YouTubeMetadataGenerator
from integrations.google_sheets import GoogleSheetsManager
from core.config import config


class MetadataManager:
    """
    Manages the complete metadata generation workflow for Shorts Factory
    Generates SEO-optimized YouTube titles, descriptions, and tags using Gemini AI
    """
    
    def __init__(self):
        """Initialize Metadata Manager"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.metadata_generator = None
        self.sheets_manager = None
        
        # Working directories
        self.metadata_dir = Path(config.working_directory) / "metadata"
        self.captioned_videos_dir = Path(config.working_directory) / "captioned_videos"
        
        # Ensure metadata directory exists
        self.ensure_metadata_directory()
        
        self.logger.info("📺 Metadata Manager initialized")
    
    def ensure_metadata_directory(self):
        """Ensure the metadata directory exists"""
        try:
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Metadata directory ready: {self.metadata_dir}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create metadata directory: {e}")
            raise
    
    def initialize(self) -> bool:
        """Initialize all required components"""
        try:
            self.logger.info("🔧 Initializing Metadata Manager components...")
            
            # Initialize YouTube Metadata Generator
            self.metadata_generator = YouTubeMetadataGenerator()
            if not self.metadata_generator.initialize():
                self.logger.error("❌ YouTube Metadata Generator initialization failed")
                # return False  # GoogleSheetsManager auto-initializes
            self.logger.info("✅ YouTube Metadata Generator initialized")
            
            # Initialize Google Sheets manager
            self.sheets_manager = GoogleSheetsManager()
            # GoogleSheetsManager auto-initializes, skip check
                # self.logger.error("❌ Google Sheets manager initialization failed")
                # return False  # GoogleSheetsManager auto-initializes
            self.logger.info("✅ Google Sheets manager initialized")
            
            self.logger.info("✅ Metadata Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Metadata Manager initialization failed: {e}")
            # return False  # GoogleSheetsManager auto-initializes
    
    def save_metadata_to_file(self, metadata: Dict[str, Any], content_id: str) -> Optional[str]:
        """
        Save metadata to JSON file for storage and tracking
        
        Args:
            metadata: Generated metadata dictionary
            content_id: Content identifier
            
        Returns:
            Path to saved metadata file, or None if failed
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata_filename = f"metadata_{content_id}_{timestamp}.json"
            metadata_file_path = self.metadata_dir / metadata_filename
            
            # Save to file
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Metadata saved to file: {metadata_filename}")
            return str(metadata_file_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving metadata to file: {e}")
            return None
    
    def save_metadata_to_sheet(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Save generated metadata to Google Sheets for tracking
        
        Args:
            content_id: The ID of the content item
            metadata: Generated metadata dictionary
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Extract metadata components
            title = metadata.get('title', '')
            description = metadata.get('description', '')
            tags = metadata.get('tags', [])
            
            # Format for storage (truncate if needed for sheet display)
            title_display = title[:100] if title else ''
            description_preview = description[:200] + "..." if len(description) > 200 else description
            tags_display = ", ".join(tags[:10])  # Show first 10 tags
            
            # Create metadata summary for the updated date field
            metadata_summary = f"YouTube metadata generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            metadata_summary += f" | Title: {len(title)} chars"
            metadata_summary += f" | Desc: {len(description)} chars" 
            metadata_summary += f" | Tags: {len(tags)}"
            
            # For now, we'll store metadata in the ERROR_LOG column as a JSON summary
            # In a production system, you might want dedicated metadata columns
            metadata_json = {
                'type': 'youtube_metadata',
                'title': title_display,
                'description_preview': description_preview,
                'tags_preview': tags_display,
                'stats': metadata.get('character_counts', {}),
                'generated_at': metadata.get('generated_at', '')
            }
            
            success = self.sheets_manager.update_content_field(
                content_id,
                'ERROR_LOG',  # Using this field for metadata storage
                json.dumps(metadata_json, ensure_ascii=False),
                metadata_summary
            )
            
            if success:
                self.logger.info(f"✅ Metadata saved to Google Sheets for ID {content_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to save metadata to Google Sheets for ID {content_id}")
                # return False  # GoogleSheetsManager auto-initializes
                
        except Exception as e:
            self.logger.error(f"❌ Error saving metadata to Google Sheets: {e}")
            # return False  # GoogleSheetsManager auto-initializes
    
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
            pattern = f"captioned_{content_id}_*.mp4"
            
            video_files = list(self.captioned_videos_dir.glob(pattern))
            
            if not video_files:
                # Try alternative patterns
                alt_patterns = [
                    f"*_{content_id}_*.mp4",
                    f"content_{content_id}_*.mp4"
                ]
                
                for alt_pattern in alt_patterns:
                    video_files = list(self.captioned_videos_dir.glob(alt_pattern))
                    if video_files:
                        break
            
            if not video_files:
                self.logger.warning(f"⚠️ No captioned video found for content ID: {content_id}")
                return None
            
            # Use the most recent file if multiple matches
            video_file = max(video_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"📺 Found captioned video: {video_file.name}")
            
            return str(video_file)
            
        except Exception as e:
            self.logger.error(f"❌ Error finding captioned video for {content_id}: {e}")
            return None
    
    def generate_metadata_for_content(self, content_item: Dict[str, Any]) -> bool:
        """
        Generate complete YouTube metadata for a specific content item
        
        Args:
            content_item: Dictionary containing content information
            
        Returns:
            True if metadata generation successful, False otherwise
        """
        try:
            content_id = content_item.get('id', '')
            title = content_item.get('title', 'Untitled')
            script = content_item.get('script', '')
            
            if not content_id:
                self.logger.error("❌ Content ID is required for metadata generation")
                # return False  # GoogleSheetsManager auto-initializes
            
            if not script:
                self.logger.error(f"❌ No script found for content ID: {content_id}")
                # return False  # GoogleSheetsManager auto-initializes
            
            self.logger.info(f"📺 Starting metadata generation for: {title} (ID: {content_id})")
            
            # Check if captioned video exists (optional check)
            captioned_video = self.find_captioned_video_for_content(content_id)
            if not captioned_video:
                self.logger.warning(f"⚠️ No captioned video found, but continuing with metadata generation")
            
            # Generate complete metadata using Gemini AI
            self.logger.info(f"🤖 Generating YouTube metadata using Gemini AI...")
            metadata = self.metadata_generator.generate_complete_metadata(
                script_text=script,
                original_title=title,
                content_id=content_id
            )
            
            if not metadata:
                self.logger.error(f"❌ Metadata generation failed for content ID: {content_id}")
                # return False  # GoogleSheetsManager auto-initializes
            
            # Save metadata to file
            metadata_file_path = self.save_metadata_to_file(metadata, content_id)
            if metadata_file_path:
                # Add file path to metadata
                metadata['metadata_file_path'] = metadata_file_path
            
            # Save metadata summary to Google Sheets
            if not self.save_metadata_to_sheet(content_id, metadata):
                self.logger.warning(f"⚠️ Failed to save metadata to sheets, but metadata was generated successfully")
            
            self.logger.info(f"🎉 Metadata generation completed successfully for: {title}")
            self.logger.info(f"📝 Title: {metadata['title']}")
            self.logger.info(f"📄 Description: {len(metadata['description'])} characters")
            self.logger.info(f"🏷️ Tags: {len(metadata['tags'])} tags")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error generating metadata for content: {e}")
            # return False  # GoogleSheetsManager auto-initializes
    
    def get_content_ready_for_metadata(self) -> List[Dict[str, Any]]:
        """
        Get all content items that are ready for metadata generation
        (Have script and preferably captioned video, but no metadata yet)
        
        Returns:
            List of content items ready for metadata generation
        """
        try:
            self.logger.info("🔍 Finding content ready for metadata generation...")
            
            # Get all content from Google Sheets
            all_content = self.sheets_manager.get_all_content()
            
            ready_content = []
            
            for content in all_content:
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                script = content.get('script', '')
                error_log = content.get('error_log', '')  # We store metadata here
                
                # Check if content has script but no metadata yet
                has_script = bool(script and script.strip())
                has_metadata = bool(error_log and 'youtube_metadata' in error_log)
                
                if has_script and not has_metadata:
                    self.logger.debug(f"✅ Ready for metadata: {title} (ID: {content_id})")
                    ready_content.append(content)
                else:
                    reasons = []
                    if not has_script:
                        reasons.append("no script")
                    if has_metadata:
                        reasons.append("already has metadata")
                    
                    self.logger.debug(f"⏭️ Skipping {title} (ID: {content_id}): {', '.join(reasons)}")
            
            self.logger.info(f"📺 Found {len(ready_content)} content items ready for metadata generation")
            return ready_content
            
        except Exception as e:
            self.logger.error(f"❌ Error finding content ready for metadata: {e}")
            return []
    
    def run_metadata_generation_cycle(self) -> Dict[str, Any]:
        """
        Run a complete metadata generation cycle for all ready content
        
        Returns:
            Dictionary with metadata generation results and statistics
        """
        try:
            self.logger.info("📺 Starting metadata generation cycle...")
            
            cycle_start_time = datetime.now()
            
            # Find content ready for metadata generation
            ready_content = self.get_content_ready_for_metadata()
            
            results = {
                'total_ready': len(ready_content),
                'successfully_generated': 0,
                'failed_generation': 0,
                'generated_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0
            }
            
            if not ready_content:
                self.logger.info("📊 No content ready for metadata generation")
                return results
            
            # Process each content item
            for content in ready_content:
                content_id = content.get('id', '')
                title = content.get('title', 'Untitled')
                
                try:
                    self.logger.info(f"📺 Processing: {title} (ID: {content_id})")
                    
                    success = self.generate_metadata_for_content(content)
                    
                    if success:
                        results['successfully_generated'] += 1
                        results['generated_items'].append({
                            'id': content_id,
                            'title': title
                        })
                        self.logger.info(f"✅ Successfully generated metadata: {title}")
                    else:
                        results['failed_generation'] += 1
                        results['failed_items'].append({
                            'id': content_id,
                            'title': title,
                            'error': 'Metadata generation process failed'
                        })
                        self.logger.error(f"❌ Failed to generate metadata: {title}")
                        
                except Exception as e:
                    results['failed_generation'] += 1
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
            self.logger.info("🎉 Metadata generation cycle completed!")
            self.logger.info(f"📊 Results: {results['successfully_generated']}/{results['total_ready']} successful")
            self.logger.info(f"⏱️ Duration: {cycle_duration:.1f} seconds")
            
            if results['failed_generation'] > 0:
                self.logger.warning(f"⚠️ {results['failed_generation']} items failed metadata generation")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in metadata generation cycle: {e}")
            return {
                'total_ready': 0,
                'successfully_generated': 0,
                'failed_generation': 0,
                'generated_items': [],
                'failed_items': [],
                'cycle_duration_seconds': 0,
                'error': str(e)
            }
    
    def get_metadata_for_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve generated metadata for a specific content item
        
        Args:
            content_id: Content identifier
            
        Returns:
            Metadata dictionary if found, None otherwise
        """
        try:
            # Look for metadata files matching the content ID
            pattern = f"metadata_{content_id}_*.json"
            metadata_files = list(self.metadata_dir.glob(pattern))
            
            if not metadata_files:
                self.logger.warning(f"⚠️ No metadata file found for content ID: {content_id}")
                return None
            
            # Use the most recent file
            metadata_file = max(metadata_files, key=lambda f: f.stat().st_mtime)
            
            # Load metadata from file
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.logger.info(f"✅ Retrieved metadata for content {content_id}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"❌ Error retrieving metadata for {content_id}: {e}")
            return None
