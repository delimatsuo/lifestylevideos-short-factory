#!/usr/bin/env python3
"""
Test JUST the script generation and saving - nothing else
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path  
sys.path.insert(0, 'src')

def test_script_generation():
    """Test just script generation and saving"""
    print("🧪 Testing script generation...")
    
    try:
        # Import only what we need
        sys.path.append('src/integrations')  
        sys.path.append('src/core')
        
        from integrations.google_sheets import GoogleSheetsManager
        from core.script_generator import ScriptGenerator
        
        print("📊 Initializing Google Sheets...")
        sheets = GoogleSheetsManager()
        
        print("📝 Initializing Script Generator...")
        script_gen = ScriptGenerator()
        
        if not script_gen.initialize():
            print("❌ Script generator failed to initialize")
            return False
        
        print("🔍 Getting approved content...")
        approved_content = sheets.get_approved_content()
        
        if not approved_content:
            print("❌ No approved content found")
            return False
        
        # Test with first item
        content = approved_content[0]
        content_id = content.get('id', '')
        title = content.get('title', 'Untitled')
        
        print(f"🎯 Testing with: {title} (ID: {content_id})")
        
        # Generate script
        print("📝 Generating script...")
        script = script_gen.generate_script_for_content(content)
        
        if not script:
            print("❌ Script generation failed")
            return False
        
        print(f"✅ Generated script: {script[:100]}...")
        
        # Save script using ScriptGenerator's built-in method
        print("💾 Saving script using ScriptGenerator...")
        save_result = script_gen.save_script_to_sheet(content_id, script)
        
        if save_result:
            print("✅ Script saved successfully!")
            
            # Verify by reading back
            print("🔍 Verifying script was saved...")
            updated_content = sheets.get_all_content()
            for item in updated_content:
                if item.get('id') == content_id:
                    saved_script = item.get('script', '')
                    if saved_script and script in saved_script:
                        print("✅ SUCCESS: Script verified in Google Sheets!")
                        return True
                    else:
                        print(f"❌ Script not found. Saved: {saved_script[:50]}...")
                        return False
            
            print("❌ Content item not found when verifying")
            return False
        else:
            print("❌ Script save failed")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_script_generation()
    print(f"\n🎯 Result: {'SUCCESS' if success else 'FAILED'}")

