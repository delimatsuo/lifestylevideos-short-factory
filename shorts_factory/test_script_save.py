#!/usr/bin/env python3
"""
Simple test to verify script saving works
"""

import sys
import logging
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from integrations.google_sheets import GoogleSheetsManager
from core.script_generator import ScriptGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_script_save():
    """Test script generation and saving"""
    print("🧪 Testing script generation and saving...")
    
    # Initialize components
    print("📊 Initializing Google Sheets...")
    sheets = GoogleSheetsManager()
    
    print("📝 Initializing Script Generator...")
    script_gen = ScriptGenerator()
    if not script_gen.initialize():
        print("❌ Script generator failed to initialize")
        return False
    
    # Get one approved item to test with
    print("🔍 Finding approved content...")
    approved_content = sheets.get_approved_content()
    if not approved_content:
        print("❌ No approved content found")
        return False
    
    # Take the first item
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
    
    # Save script directly
    print("💾 Saving script to sheets...")
    result = sheets.update_content_field(content_id, 'SCRIPT', script)
    print(f"💾 Save result: {result}")
    
    if result:
        # Verify it was saved by reading it back
        print("🔍 Verifying script was saved...")
        all_content = sheets.get_all_content()
        for item in all_content:
            if item.get('id') == content_id:
                saved_script = item.get('script', '')
                if saved_script:
                    print("✅ Script successfully saved and verified!")
                    print(f"📄 Saved script: {saved_script[:100]}...")
                    return True
                else:
                    print("❌ Script not found in saved content")
                    return False
    
    print("❌ Script save failed")
    return False

if __name__ == "__main__":
    success = test_script_save()
    print(f"\n🎯 Test result: {'SUCCESS' if success else 'FAILED'}")

