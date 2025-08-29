#!/usr/bin/env python3
"""
Quick test script for Google Sheets credentials
Run this after setting up your credentials
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from integrations.google_sheets import GoogleSheetsManager
from utils.logger import setup_logging

def test_google_sheets():
    """Test Google Sheets connection"""
    print("🧪 Testing Google Sheets connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    try:
        # Initialize Google Sheets Manager
        sheets_manager = GoogleSheetsManager()
        
        # Test connection
        if sheets_manager.test_connection():
            print("✅ Google Sheets connection successful!")
            
            # Create headers
            if sheets_manager.create_dashboard_headers():
                print("✅ Dashboard headers created!")
                
                # Add a test entry
                test_id = sheets_manager.add_content_idea(
                    source="TEST",
                    title="Test connection - " + str(os.getpid())
                )
                
                if test_id:
                    print(f"✅ Test content added with ID: {test_id}")
                    print("🎉 All tests passed! Your Google Sheets integration is working!")
                else:
                    print("❌ Failed to add test content")
            else:
                print("❌ Failed to create dashboard headers")
        else:
            print("❌ Google Sheets connection failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n📋 Checklist:")
        print("- Is your JSON credentials file in the right location?")
        print("- Did you share the spreadsheet with the service account email?")
        print("- Is the GOOGLE_SHEETS_SPREADSHEET_ID correct in .env?")

if __name__ == '__main__':
    test_google_sheets()
