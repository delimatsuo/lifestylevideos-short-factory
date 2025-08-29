#!/usr/bin/env python3
"""
Helper script to set up your .env file with the spreadsheet ID
"""

import os
from pathlib import Path

def setup_spreadsheet():
    """Interactive setup for spreadsheet ID"""
    print("🔧 Google Spreadsheet Setup Helper")
    print("=" * 40)
    
    print("\n📋 First, create your spreadsheet:")
    print("1. Go to: https://sheets.google.com/")
    print("2. Create a blank spreadsheet")
    print("3. Name it: 'Lifestylevideos Shorts Factory Dashboard'")
    print("4. Share it with: lifestyle-videos-service@lifestylevideos-470516.iam.gserviceaccount.com")
    print("   - Give 'Editor' permissions")
    print("   - Uncheck 'Notify people'")
    
    print("\n📝 Next, get your Spreadsheet ID:")
    print("Copy the long ID from your spreadsheet URL:")
    print("https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID_HERE/edit")
    print()
    
    # Get spreadsheet ID from user
    spreadsheet_id = input("📎 Paste your Spreadsheet ID here: ").strip()
    
    if not spreadsheet_id:
        print("❌ No Spreadsheet ID provided. Please try again.")
        return
    
    # Update .env file
    env_path = Path('.env')
    
    if env_path.exists():
        # Read existing .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update spreadsheet ID line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('GOOGLE_SHEETS_SPREADSHEET_ID='):
                lines[i] = f'GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}\n')
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(lines)
            
        print(f"✅ Updated .env file with Spreadsheet ID: {spreadsheet_id}")
    else:
        # Create new .env file
        env_content = f"""# Google Services API Keys
GOOGLE_SHEETS_API_KEY=not_needed_for_service_account
GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}
GOOGLE_CREDENTIALS_FILE=./config/credentials/google-service-account.json

# AI Services (for Task 2)
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Content Sources (for Task 2)  
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=ShortsFactory/1.0

# Media Services (for later tasks)
PEXELS_API_KEY=your_pexels_api_key_here

# YouTube API (for Task 10)
YOUTUBE_API_KEY=your_youtube_api_key_here  
YOUTUBE_CLIENT_SECRETS_FILE=./config/credentials/youtube_client_secrets.json

# Application Settings
LOG_LEVEL=INFO
WORKING_DIRECTORY=./working_directory
DAILY_EXECUTION_TIME=09:00
MAX_API_COST_PER_MONTH=100.0
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
            
        print(f"✅ Created .env file with Spreadsheet ID: {spreadsheet_id}")
    
    print("\n🧪 Next step: Test the connection")
    print("Run: python test_sheets.py")

if __name__ == '__main__':
    setup_spreadsheet()
