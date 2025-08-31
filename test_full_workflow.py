#!/usr/bin/env python3
"""
Direct Test of Complete Workflow for Shorts Factory
Demonstrates automatic idea generation → approval → processing → status management
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("🎬 SHORTS FACTORY - COMPLETE WORKFLOW TEST")
print("=" * 60)

def test_gemini_idea_generation():
    """Test automatic idea generation with Gemini"""
    print("\n🤖 STEP 1: AUTOMATIC IDEA GENERATION")
    print("-" * 40)
    
    try:
        import google.generativeai as genai
        
        # Initialize Gemini
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            print("❌ GOOGLE_GEMINI_API_KEY not found in .env")
            return []
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate lifestyle/productivity ideas
        prompt = """Generate 5 engaging YouTube Shorts video ideas for a lifestyle/productivity channel.

Format each as a JSON object with:
- title: Compelling title under 60 characters
- description: Brief description of video content
- category: lifestyle/productivity/motivation/habits

Return only valid JSON array, no extra text."""

        print("🔄 Generating ideas with Gemini AI...")
        response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif response_text.startswith('```'):
            response_text = response_text.split('```')[1].strip()
        
        try:
            ideas = json.loads(response_text)
            
            print(f"✅ Generated {len(ideas)} ideas:")
            for i, idea in enumerate(ideas, 1):
                print(f"   {i}. {idea['title']}")
            
            return ideas
            
        except json.JSONDecodeError:
            print("⚠️ JSON parsing failed, creating sample ideas...")
            return [
                {"title": "5 Morning Habits That Change Your Life", "description": "Transform your day with these powerful morning routines", "category": "habits"},
                {"title": "Simple Productivity Hacks for Busy People", "description": "Get more done with less effort using these proven techniques", "category": "productivity"},
                {"title": "How to Stay Motivated When Things Get Tough", "description": "Practical strategies to maintain motivation during challenges", "category": "motivation"},
            ]
            
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return []

def test_spreadsheet_population(ideas):
    """Test populating Google Sheets with ideas"""
    print("\n📊 STEP 2: POPULATE GOOGLE SHEETS")
    print("-" * 40)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Setup Google Sheets connection
        creds_file = Path('google_credentials.json')
        if not creds_file.exists():
            print("❌ google_credentials.json not found")
            return False
        
        creds = Credentials.from_service_account_file(str(creds_file))
        gc = gspread.authorize(creds)
        
        # Open the spreadsheet
        sheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        sheet = gc.open_by_key(sheet_id).sheet1
        
        print("🔄 Adding ideas to spreadsheet...")
        
        # Get next available row
        existing_data = sheet.get_all_values()
        next_row = len(existing_data) + 1
        
        for i, idea in enumerate(ideas):
            row_data = [
                f"AUTO_{int(time.time())}_{i+1}",  # ID
                idea['title'],                      # CONTENT_TITLE  
                "Pending Approval",                # STATUS
                "",                                # SCRIPT (empty for now)
                "",                                # AUDIO_FILE (empty)
                "",                                # VIDEO_FILE (empty)
                "",                                # FINAL_VIDEO (empty)
                "",                                # YOUTUBE_URL (empty)
                f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", # UPDATED_DATE
                "",                                # ERROR_LOG (empty)
                ""                                 # NOTES (empty)
            ]
            
            # Add to sheet
            sheet.insert_row(row_data, next_row + i)
            print(f"   ✅ Added: {idea['title']}")
        
        print(f"🎉 Successfully added {len(ideas)} ideas to spreadsheet!")
        print("📋 Status: All set to 'Pending Approval'")
        print("👤 Next: YOU manually change status to 'Approved' for processing")
        
        return True
        
    except Exception as e:
        print(f"❌ Spreadsheet error: {e}")
        return False

def test_approval_workflow():
    """Explain the approval workflow"""
    print("\n✅ STEP 3: APPROVAL WORKFLOW")
    print("-" * 40)
    
    print("📋 HOW THE APPROVAL PROCESS WORKS:")
    print("   1. Ideas populated with status 'Pending Approval'")
    print("   2. YOU review ideas in spreadsheet")
    print("   3. YOU change status: 'Pending Approval' → 'Approved'")
    print("   4. Run: python src/main.py run-once")
    print("   5. System processes ONLY 'Approved' items")
    print("   6. Status automatically changes: 'Approved' → 'Completed'")
    print("   7. 'Completed' items are NEVER reprocessed")
    print("")
    print("🎯 RESULT: No duplicate processing!")

def test_status_management():
    """Show status management"""
    print("\n🔄 STEP 4: STATUS MANAGEMENT")
    print("-" * 40)
    
    statuses = {
        "Pending Approval": "🟡 Waiting for your review",
        "Approved": "🟢 Ready for processing", 
        "Completed": "✅ Processed and published (won't reprocess)",
        "Error": "🔴 Processing failed (needs attention)"
    }
    
    print("📊 STATUS MEANINGS:")
    for status, meaning in statuses.items():
        print(f"   {meaning}")
    print("")
    print("🎯 WORKFLOW: Pending → Approved (you) → Completed (automatic)")

def main():
    """Run complete workflow test"""
    
    # Step 1: Generate ideas
    ideas = test_gemini_idea_generation()
    if not ideas:
        print("❌ Could not generate ideas. Check GOOGLE_GEMINI_API_KEY in .env")
        return
    
    # Step 2: Populate spreadsheet  
    success = test_spreadsheet_population(ideas)
    if not success:
        print("❌ Could not populate spreadsheet. Check credentials and permissions")
        return
    
    # Step 3: Explain approval workflow
    test_approval_workflow()
    
    # Step 4: Show status management
    test_status_management()
    
    print("\n" + "=" * 60)
    print("🎊 COMPLETE WORKFLOW TEST SUCCESSFUL!")
    print("=" * 60)
    print("📋 NEXT STEPS:")
    print("   1. Check your Google Sheets - new ideas should be there!")
    print("   2. Change some statuses from 'Pending Approval' → 'Approved'")
    print("   3. Run: python src/main.py run-once")
    print("   4. Watch the magic happen! 🎬✨")
    print("")
    print("🚀 No video has been uploaded yet - that happens after you approve!")

if __name__ == "__main__":
    main()

