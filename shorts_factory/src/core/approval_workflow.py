"""
Google Sheets Approval Workflow Monitor
Monitors spreadsheet for status changes and triggers content processing pipeline
"""

import logging
from typing import List, Dict, Optional, Set
from datetime import datetime
import time
import json
from pathlib import Path

from integrations.google_sheets import GoogleSheetsManager
from core.config import config


class ApprovalWorkflowMonitor:
    """Monitors Google Sheets for approval status changes and triggers processing"""
    
    def __init__(self):
        """Initialize the approval workflow monitor"""
        self.logger = logging.getLogger(__name__)
        self.sheets_manager = None
        self._last_known_status = {}  # Track status of each content item
        self._processed_items = set()  # Track items already processed
        
        # Status tracking file
        self.status_file = Path(config.working_directory) / "approval_status.json"
        self._load_status_tracking()
        
        # Status constants
        self.PENDING_STATUS = "Pending Approval"
        self.APPROVED_STATUS = "Approved" 
        self.IN_PROGRESS_STATUS = "In Progress"
        self.COMPLETED_STATUS = "Completed"
        self.FAILED_STATUS = "Failed"
    
    def initialize(self) -> bool:
        """Initialize the workflow monitor with Google Sheets connection"""
        try:
            self.logger.info("🔍 Initializing Approval Workflow Monitor...")
            
            # Initialize Google Sheets manager
            self.sheets_manager = GoogleSheetsManager()
            if not self.sheets_manager.test_connection():
                raise Exception("Google Sheets connection failed")
            
            self.logger.info("✅ Approval Workflow Monitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Approval Workflow Monitor: {e}")
            return False
    
    def scan_for_approvals(self) -> List[Dict[str, str]]:
        """
        Scan Google Sheets for newly approved content items
        
        Returns:
            List of approved content items ready for processing
        """
        try:
            self.logger.info("🔍 Scanning for newly approved content...")
            
            # Get all content from spreadsheet
            all_content = self.sheets_manager.get_all_content()
            if not all_content:
                self.logger.info("No content found in spreadsheet")
                return []
            
            newly_approved = []
            status_changes = 0
            
            for content_item in all_content:
                content_id = content_item.get('id', '')
                current_status = content_item.get('status', '').strip()
                
                if not content_id:
                    continue
                
                # Track status change
                previous_status = self._last_known_status.get(content_id)
                self._last_known_status[content_id] = current_status
                
                # Check for approval status change
                if self._is_newly_approved(content_id, current_status, previous_status):
                    newly_approved.append(content_item)
                    status_changes += 1
                    
                    self.logger.info(f"✅ Newly approved: ID {content_id} - {content_item.get('title', 'Untitled')}")
            
            if status_changes > 0:
                self.logger.info(f"📊 Found {status_changes} newly approved items")
                self._save_status_tracking()
            else:
                self.logger.info("📊 No new approvals found")
            
            return newly_approved
            
        except Exception as e:
            self.logger.error(f"❌ Error scanning for approvals: {e}")
            return []
    
    def _is_newly_approved(self, content_id: str, current_status: str, previous_status: Optional[str]) -> bool:
        """Check if content item was newly approved"""
        
        # Skip if already processed
        if content_id in self._processed_items:
            return False
        
        # Check if status changed to approved
        if current_status == self.APPROVED_STATUS:
            # If we don't have previous status, consider it newly approved
            if previous_status is None:
                return True
            
            # If status changed from pending to approved
            if previous_status == self.PENDING_STATUS:
                return True
        
        return False
    
    def mark_as_processing(self, content_id: str, title: str = "") -> bool:
        """Mark a content item as being processed"""
        try:
            # Update status in Google Sheets
            success = self.sheets_manager.update_content_status(
                content_id, 
                self.IN_PROGRESS_STATUS,
                f"Processing started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            if success:
                # Add to processed items set
                self._processed_items.add(content_id)
                self._save_status_tracking()
                
                self.logger.info(f"✅ Marked ID {content_id} as processing: {title}")
                return True
            else:
                self.logger.warning(f"⚠️ Failed to mark ID {content_id} as processing")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error marking content as processing: {e}")
            return False
    
    def mark_as_completed(self, content_id: str, result_info: Dict[str, str] = None) -> bool:
        """Mark a content item as completed with optional result information"""
        try:
            # Prepare update info
            status_note = f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            if result_info:
                # Add result information to the note
                if result_info.get('video_file'):
                    status_note += f" | Video: {result_info['video_file']}"
                if result_info.get('youtube_url'):
                    status_note += f" | YouTube: {result_info['youtube_url']}"
            
            # Update status in Google Sheets
            success = self.sheets_manager.update_content_status(
                content_id,
                self.COMPLETED_STATUS,
                status_note
            )
            
            if success:
                self.logger.info(f"✅ Marked ID {content_id} as completed")
                return True
            else:
                self.logger.warning(f"⚠️ Failed to mark ID {content_id} as completed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error marking content as completed: {e}")
            return False
    
    def mark_as_failed(self, content_id: str, error_message: str) -> bool:
        """Mark a content item as failed with error information"""
        try:
            status_note = f"Failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Error: {error_message}"
            
            # Update status in Google Sheets
            success = self.sheets_manager.update_content_status(
                content_id,
                self.FAILED_STATUS,
                status_note
            )
            
            # Remove from processed items so it can be retried later
            self._processed_items.discard(content_id)
            self._save_status_tracking()
            
            if success:
                self.logger.info(f"✅ Marked ID {content_id} as failed: {error_message}")
                return True
            else:
                self.logger.warning(f"⚠️ Failed to mark ID {content_id} as failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error marking content as failed: {e}")
            return False
    
    def run_approval_monitor_cycle(self) -> Dict[str, any]:
        """
        Run one cycle of the approval monitoring process
        
        Returns:
            Dictionary with monitoring results and statistics
        """
        start_time = time.time()
        
        try:
            self.logger.info("🔄 Starting approval monitoring cycle...")
            
            # Scan for newly approved items
            approved_items = self.scan_for_approvals()
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'newly_approved_count': len(approved_items),
                'approved_items': approved_items,
                'execution_time': round(time.time() - start_time, 2),
                'success': True
            }
            
            if approved_items:
                self.logger.info(f"🎉 Approval monitoring cycle complete: {len(approved_items)} items ready for processing")
            else:
                self.logger.info("📊 Approval monitoring cycle complete: No new approvals")
            
            return results
            
        except Exception as e:
            error_msg = f"Approval monitoring cycle failed: {e}"
            self.logger.error(f"❌ {error_msg}")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'newly_approved_count': 0,
                'approved_items': [],
                'execution_time': round(time.time() - start_time, 2),
                'success': False,
                'error': error_msg
            }
    
    def _load_status_tracking(self):
        """Load status tracking from file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    self._last_known_status = data.get('last_known_status', {})
                    self._processed_items = set(data.get('processed_items', []))
                    
                self.logger.info(f"📂 Loaded status tracking: {len(self._last_known_status)} items")
            else:
                self.logger.info("📂 No existing status tracking found - starting fresh")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load status tracking: {e}")
            # Reset to empty state
            self._last_known_status = {}
            self._processed_items = set()
    
    def _save_status_tracking(self):
        """Save status tracking to file"""
        try:
            # Ensure directory exists
            self.status_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'last_known_status': self._last_known_status,
                'processed_items': list(self._processed_items),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.debug("📂 Status tracking saved")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save status tracking: {e}")
    
    def get_monitoring_status(self) -> Dict[str, any]:
        """Get current monitoring status and statistics"""
        return {
            'tracked_items': len(self._last_known_status),
            'processed_items': len(self._processed_items),
            'status_file': str(self.status_file),
            'status_file_exists': self.status_file.exists(),
            'last_scan': datetime.now().isoformat()
        }
    
    def reset_tracking(self):
        """Reset all status tracking (for testing/debugging)"""
        self.logger.warning("🔄 Resetting all status tracking...")
        self._last_known_status = {}
        self._processed_items = set()
        
        if self.status_file.exists():
            self.status_file.unlink()
            
        self.logger.info("✅ Status tracking reset complete")
