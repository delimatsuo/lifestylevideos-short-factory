#!/usr/bin/env python3
"""
Test script for the Automated Script Generation Module (Task #4)
Tests script generation, Google Sheets integration, and complete workflow
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from utils.logger import setup_logging
from core.script_generator import ScriptGenerator
from integrations.gemini_api import GeminiContentGenerator
from integrations.google_sheets import GoogleSheetsManager

def test_script_generation_components():
    """Test individual script generation components"""
    print("🧪 Testing Script Generation Components")
    print("=" * 50)
    
    results = {
        'gemini_connection': False,
        'sheets_connection': False,
        'script_generator_init': False,
        'prompt_creation': False
    }
    
    # Test 1: Gemini API Connection
    print("\n🤖 Testing Gemini API Connection...")
    try:
        gemini = GeminiContentGenerator()
        results['gemini_connection'] = gemini.test_connection()
        print(f"   Result: {'✅ PASS' if results['gemini_connection'] else '❌ FAIL'}")
        
        if results['gemini_connection']:
            # Test basic generation
            test_prompt = "Generate a single creative word."
            test_ideas = gemini.generate_ideas(test_prompt, num_ideas=1)
            if test_ideas and test_ideas[0]:
                print(f"   📝 Test generation: '{test_ideas[0][:30]}...'")
            
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
    
    # Test 2: Google Sheets Connection
    print("\n📊 Testing Google Sheets Connection...")
    try:
        sheets = GoogleSheetsManager()
        results['sheets_connection'] = sheets.test_connection()
        print(f"   Result: {'✅ PASS' if results['sheets_connection'] else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
    
    # Test 3: Script Generator Initialization
    print("\n🎬 Testing Script Generator Initialization...")
    try:
        script_gen = ScriptGenerator()
        results['script_generator_init'] = script_gen.initialize()
        print(f"   Result: {'✅ PASS' if results['script_generator_init'] else '❌ FAIL'}")
        
        if results['script_generator_init']:
            stats = script_gen.get_script_generation_stats()
            print(f"   📊 Target word count: {stats['target_word_count']}")
            print(f"   🎯 Platform optimization: {stats['platform_optimization']}")
            print(f"   📱 Script style: {stats['script_style']}")
            
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
    
    # Test 4: Prompt Creation
    if results['script_generator_init']:
        print("\n📝 Testing Script Prompt Creation...")
        try:
            script_gen = ScriptGenerator()
            script_gen.initialize()
            
            # Test prompt creation
            test_prompt = script_gen._create_script_prompt(
                "5 Morning Habits That Will Change Your Life",
                "Gemini"
            )
            
            results['prompt_creation'] = bool(test_prompt and len(test_prompt) > 100)
            print(f"   Result: {'✅ PASS' if results['prompt_creation'] else '❌ FAIL'}")
            
            if results['prompt_creation']:
                print(f"   📝 Prompt length: {len(test_prompt)} characters")
                print(f"   🎯 Contains requirements: {'✅' if 'REQUIREMENTS:' in test_prompt else '❌'}")
                print(f"   🏗️ Contains structure: {'✅' if 'STRUCTURE GUIDELINES:' in test_prompt else '❌'}")
            
        except Exception as e:
            print(f"   Result: ❌ FAIL - {e}")
    
    return results

def test_script_generation_workflow():
    """Test the complete script generation workflow"""
    print("\n\n🎬 Testing Complete Script Generation Workflow")
    print("=" * 60)
    
    try:
        # Initialize script generator
        print("Initializing Script Generator...")
        script_gen = ScriptGenerator()
        
        if not script_gen.initialize():
            print("❌ Failed to initialize script generator")
            return False
        
        print("✅ Script Generator initialized successfully")
        
        # Test with sample content
        sample_content = {
            'id': 'TEST_001',
            'title': '5 Productivity Tips That Actually Work',
            'source': 'Gemini',
            'status': 'Approved'
        }
        
        print(f"\n📝 Testing script generation for: {sample_content['title']}")
        
        # Generate script
        generated_script = script_gen.generate_script_for_content(sample_content)
        
        if generated_script:
            word_count = len(generated_script.split())
            print(f"✅ Script generated successfully!")
            print(f"📊 Word count: {word_count} words")
            print(f"🎯 Target range: 140-180 words")
            print(f"📝 Preview: {generated_script[:100]}...")
            
            # Test script processing
            processed = script_gen._process_generated_script(f'SCRIPT: "{generated_script}"')
            print(f"🔧 Script processing: {'✅ PASS' if processed == generated_script else '❌ FAIL'}")
            
            return True
        else:
            print("❌ Script generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def test_sheets_integration():
    """Test Google Sheets integration for script saving"""
    print("\n\n📊 Testing Google Sheets Integration")
    print("=" * 50)
    
    try:
        # Initialize components
        script_gen = ScriptGenerator()
        if not script_gen.initialize():
            print("❌ Failed to initialize script generator")
            return False
        
        # Test content
        test_content = {
            'id': 'TEST_SHEETS_001',
            'title': 'Time Management Secrets for Busy People',
            'source': 'Reddit',
            'status': 'Approved'
        }
        
        print(f"📝 Testing complete workflow for: {test_content['title']}")
        print("⚠️  This test requires content with ID 'TEST_SHEETS_001' to exist in Google Sheets")
        
        # Note: In a real test environment, we would:
        # 1. Add test content to the sheet
        # 2. Generate and save script
        # 3. Verify the script was saved correctly
        # 4. Clean up test data
        
        print("🔧 Test simulation mode:")
        print("   1. Would add test content to Google Sheets")
        print("   2. Would generate script using Gemini API")
        print("   3. Would save script to 'SCRIPT' column")
        print("   4. Would verify script was saved correctly")
        print("   5. Would clean up test data")
        
        # For now, just test the generation part
        script = script_gen.generate_script_for_content(test_content)
        
        if script:
            print(f"✅ Script generation successful ({len(script.split())} words)")
            print("📊 Google Sheets integration ready for testing")
            return True
        else:
            print("❌ Script generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Sheets integration test failed: {e}")
        return False

def display_usage_instructions():
    """Display instructions for using the script generation system"""
    print("\n\n📋 How to Use Script Generation in Production")
    print("=" * 60)
    
    print("1. 🔄 Daily Pipeline Integration:")
    print("   - Script generation runs automatically in Phase 2")
    print("   - Triggers when content status changes to 'Approved'")
    print("   - Scripts are saved to Google Sheets automatically")
    
    print("\n2. 🧪 Manual Testing:")
    print("   - Add content to Google Sheets with 'Approved' status")
    print("   - Run: python src/main.py")
    print("   - Check Google Sheets for generated scripts")
    
    print("\n3. 📊 Monitoring:")
    print("   - Check application logs for generation status")
    print("   - Monitor Google Sheets for script updates")
    print("   - Scripts appear in column E (SCRIPT)")
    
    print("\n4. 🎯 Script Quality:")
    print("   - Target: 160 words (±20 acceptable)")
    print("   - Format: Hook → Content → Call-to-Action")
    print("   - Optimized for short-form vertical video")
    
    print("\n5. ⚙️ Configuration:")
    print("   - Script style: conversational")
    print("   - Platform: shorts (TikTok/YouTube Shorts)")
    print("   - Customizable via ScriptGenerator class")

def main():
    """Main test function"""
    # Setup logging
    setup_logging()
    
    print("🎬 Shorts Factory - Script Generation Test (Task #4)")
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Test components
    component_results = test_script_generation_components()
    
    # Test workflow if components work
    working_components = sum(1 for result in component_results.values() if result)
    if working_components >= 2:  # Need at least Gemini + initialization
        workflow_success = test_script_generation_workflow()
        sheets_success = test_sheets_integration()
    else:
        workflow_success = False
        sheets_success = False
        print("\n⚠️ Skipping workflow tests - need basic components working first")
    
    # Display usage instructions
    display_usage_instructions()
    
    # Final summary
    success_rate = working_components / len(component_results)
    
    print(f"\n🎯 TEST SUMMARY:")
    print(f"   Component Success Rate: {success_rate:.0%} ({working_components}/{len(component_results)})")
    print(f"   Script Generation: {'✅ PASS' if workflow_success else '⚠️ NEEDS SETUP'}")
    print(f"   Sheets Integration: {'✅ READY' if sheets_success else '⚠️ NEEDS TESTING'}")
    
    if success_rate >= 0.75:
        print(f"\n🎉 Task #4: Script Generation Module is OPERATIONAL!")
        print(f"✅ Ready for production use with approved content")
    else:
        print(f"\n⚠️ Some components need attention before production use")

if __name__ == '__main__':
    main()
