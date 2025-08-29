"""
Google Sheets integration for Shorts Factory
Manages the content dashboard and workflow tracking
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from core.config import config


class GoogleSheetsManager:
    """Manages Google Sheets API operations for the content dashboard"""
    
    # Dashboard schema column mapping
    COLUMNS = {
        'ID': 'A',
        'SOURCE': 'B', 
        'TITLE_CONCEPT': 'C',
        'STATUS': 'D',
        'SCRIPT': 'E',
        'AUDIO_FILE': 'F',
        'VIDEO_FILE': 'G',
        'YOUTUBE_URL': 'H',
        'ERROR_LOG': 'I',
        'CREATED_DATE': 'J',
        'UPDATED_DATE': 'K'
    }
    
    # Status values
    class Status:
        PENDING_APPROVAL = "Pending Approval"
        APPROVED = "Approved"
        IN_PROGRESS = "In Progress" 
        COMPLETED = "Complete"
        FAILED = "Failed"
    
    def __init__(self):
        """Initialize Google Sheets Manager"""
        self.logger = logging.getLogger(__name__)
        self.service = None
        self.spreadsheet_id = config.google_sheets_spreadsheet_id
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API"""
        try:
            # Try service account authentication first
            credentials_path = Path(config.google_credentials_file)
            
            if credentials_path.exists() and credentials_path.suffix == '.json':
                self.logger.info("Using service account authentication")
                credentials = Credentials.from_service_account_file(
                    config.google_credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                self.logger.info("Using OAuth authentication")
                credentials = self._oauth_authentication()
            
            self.service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Successfully authenticated with Google Sheets API")
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate with Google Sheets API: {e}")
            raise
    
    def _oauth_authentication(self) -> UserCredentials:
        """Handle OAuth authentication flow"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        creds = None
        token_path = Path(__file__).parent.parent.parent / 'config' / 'token.json'
        
        # Load existing credentials
        if token_path.exists():
            creds = UserCredentials.from_authorized_user_file(str(token_path), SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.youtube_client_secrets_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            token_path.parent.mkdir(exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def create_dashboard_headers(self) -> bool:
        """Create or update dashboard headers in the spreadsheet"""
        try:
            headers = [
                'ID', 'Source', 'Title/Concept', 'Status', 'Script', 
                'Audio File', 'Video File', 'YouTube URL', 'Error Log', 
                'Created Date', 'Updated Date'
            ]
            
            # Update headers in row 1
            body = {
                'values': [headers]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range='A1:K1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            self.logger.info(f"Updated {result.get('updatedCells')} header cells")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create dashboard headers: {e}")
            return False
    
    def add_content_idea(self, source: str, title: str, content_type: str = None) -> Optional[int]:
        """Add a new content idea to the dashboard"""
        try:
            # Get next available ID
            next_id = self._get_next_id()
            
            # Prepare row data
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row_data = [
                next_id,
                source,
                title,
                self.Status.PENDING_APPROVAL,
                '',  # Script (empty initially)
                '',  # Audio file 
                '',  # Video file
                '',  # YouTube URL
                '',  # Error log
                current_time,  # Created date
                current_time   # Updated date
            ]
            
            # Add to next available row
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='A:K',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            self.logger.info(f"Added content idea with ID {next_id}: {title}")
            return next_id
            
        except Exception as e:
            self.logger.error(f"Failed to add content idea: {e}")
            return None
    
    def get_approved_content(self) -> List[Dict[str, Any]]:
        """Get all content items with 'Approved' status"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:K'
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            headers = values[0]
            approved_content = []
            
            for i, row in enumerate(values[1:], start=2):  # Start from row 2
                if len(row) >= 4 and row[3] == self.Status.APPROVED:
                    content_item = {
                        'row_number': i,
                        'id': row[0] if len(row) > 0 else '',
                        'source': row[1] if len(row) > 1 else '',
                        'title': row[2] if len(row) > 2 else '',
                        'status': row[3] if len(row) > 3 else '',
                        'script': row[4] if len(row) > 4 else '',
                        'audio_file': row[5] if len(row) > 5 else '',
                        'video_file': row[6] if len(row) > 6 else '',
                        'youtube_url': row[7] if len(row) > 7 else '',
                        'error_log': row[8] if len(row) > 8 else '',
                        'created_date': row[9] if len(row) > 9 else '',
                        'updated_date': row[10] if len(row) > 10 else ''
                    }
                    approved_content.append(content_item)
            
            self.logger.info(f"Found {len(approved_content)} approved content items")
            return approved_content
            
        except Exception as e:
            self.logger.error(f"Failed to get approved content: {e}")
            return []
    
    def update_content_status(self, content_id: str, status: str, **kwargs) -> bool:
        """Update the status and other fields for a content item"""
        try:
            # Find the row with matching ID
            row_number = self._find_row_by_id(content_id)
            if not row_number:
                self.logger.error(f"Content ID {content_id} not found")
                return False
            
            # Prepare updates
            updates = []
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Always update status and updated_date
            updates.append({
                'range': f'D{row_number}',
                'values': [[status]]
            })
            updates.append({
                'range': f'K{row_number}', 
                'values': [[current_time]]
            })
            
            # Update additional fields if provided
            if 'script' in kwargs:
                updates.append({
                    'range': f'E{row_number}',
                    'values': [[kwargs['script']]]
                })
            
            if 'audio_file' in kwargs:
                updates.append({
                    'range': f'F{row_number}',
                    'values': [[kwargs['audio_file']]]
                })
                
            if 'video_file' in kwargs:
                updates.append({
                    'range': f'G{row_number}',
                    'values': [[kwargs['video_file']]]
                })
                
            if 'youtube_url' in kwargs:
                updates.append({
                    'range': f'H{row_number}',
                    'values': [[kwargs['youtube_url']]]
                })
                
            if 'error_log' in kwargs:
                updates.append({
                    'range': f'I{row_number}',
                    'values': [[kwargs['error_log']]]
                })
            
            # Execute batch update
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            self.logger.info(f"Updated content ID {content_id} with status: {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update content status: {e}")
            return False
    
    def _get_next_id(self) -> int:
        """Get the next available ID for new content"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:A'
            ).execute()
            
            values = result.get('values', [])
            
            if len(values) <= 1:  # Only headers or empty
                return 1
            
            # Find highest ID
            max_id = 0
            for row in values[1:]:  # Skip header
                if row and row[0].isdigit():
                    max_id = max(max_id, int(row[0]))
            
            return max_id + 1
            
        except Exception as e:
            self.logger.error(f"Failed to get next ID: {e}")
            return 1
    
    def _find_row_by_id(self, content_id: str) -> Optional[int]:
        """Find the row number for a given content ID"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:A'
            ).execute()
            
            values = result.get('values', [])
            
            for i, row in enumerate(values[1:], start=2):  # Start from row 2
                if row and str(row[0]) == str(content_id):
                    return i
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find row by ID: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test the Google Sheets connection"""
        try:
            # Try to get spreadsheet metadata
            result = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            title = result.get('properties', {}).get('title', 'Unknown')
            self.logger.info(f"Successfully connected to spreadsheet: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
