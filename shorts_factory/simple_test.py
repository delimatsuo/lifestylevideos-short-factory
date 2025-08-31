#!/usr/bin/env python3
"""
Minimal test - just check what's happening with script saving
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_sheets_only():
    """Test just Google Sheets operations"""
    print("🧪 Simple Google Sheets Test")
    
    try:
        # Import GoogleSheetsManager directly to avoid circular imports
        from integrations.google_sheets import GoogleSheetsManager
        
        print("📊 Initializing Google Sheets...")
        sheets = GoogleSheetsManager()
        
        print("🔍 Getting approved content...")
        approved_content = sheets.get_approved_content()
        
        if not approved_content:
            print("❌ No approved content found")
            return False
        
        # Take the first item
        content = approved_content[0] 
        content_id = content.get('id', '')
        title = content.get('title', 'Untitled')
        
        print(f"🎯 Found content: {title} (ID: {content_id})")
        print(f"📄 Current script: {content.get('script', 'NONE')[:50]}...")
        
        # Try to save a test script
        test_script = "This is a test script to verify saving works correctly."
        print(f"💾 Attempting to save script with 'SCRIPT' field name...")
        
        result = sheets.update_content_field(content_id, 'SCRIPT', test_script)
        print(f"💾 Save result: {result}")
        
        if result:
            # Read it back to verify
            print("🔍 Reading back to verify...")
            updated_content = sheets.get_all_content()
            for item in updated_content:
                if item.get('id') == content_id:
                    saved_script = item.get('script', '')
                    print(f"📄 Retrieved script: {saved_script[:50]}...")
                    if saved_script == test_script:
                        print("✅ SUCCESS: Script saved and verified!")
                        return True
                    else:
                        print("❌ MISMATCH: Script was not saved correctly")
                        return False
        
        print("❌ FAILED: Script save returned False")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sheets_only()
    print(f"\n🎯 Result: {'SUCCESS' if success else 'FAILED'}")

