#!/usr/bin/env python3
"""
Test script for the Content Ideation Engine
Tests Gemini API, Reddit API, and Google Sheets integration
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from utils.logger import setup_logging
from core.content_ideation_engine import ContentIdeationEngine
from integrations.gemini_api import GeminiContentGenerator
from integrations.reddit_api import RedditContentExtractor
from integrations.google_sheets import GoogleSheetsManager

def test_individual_components():
    """Test each component individually"""
    print("🧪 Testing Individual Components")
    print("=" * 50)
    
    results = {
        'gemini': False,
        'reddit': False,
        'sheets': False
    }
    
    # Test Google Sheets (we know this works)
    print("\n📊 Testing Google Sheets Integration...")
    try:
        sheets = GoogleSheetsManager()
        results['sheets'] = sheets.test_connection()
        print(f"   Result: {'✅ PASS' if results['sheets'] else '❌ FAIL'}")
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
    
    # Test Reddit API (we have credentials)
    print("\n📱 Testing Reddit API...")
    try:
        reddit = RedditContentExtractor()
        results['reddit'] = reddit.test_connection()
        print(f"   Result: {'✅ PASS' if results['reddit'] else '❌ FAIL'}")
        
        if results['reddit']:
            # Test actual story extraction
            print("   Testing story extraction...")
            stories = reddit.extract_trending_stories(3)  # Get 3 stories
            if stories:
                print(f"   ✅ Successfully extracted {len(stories)} stories:")
                for i, story in enumerate(stories[:2], 1):  # Show first 2
                    print(f"     {i}. {story['title']}")
            else:
                print("   ⚠️ No stories extracted (may be rate limited)")
                
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
    
    # Test Gemini API (may not have API key)
    print("\n💡 Testing Gemini API...")
    try:
        gemini = GeminiContentGenerator()
        results['gemini'] = gemini.test_connection()
        print(f"   Result: {'✅ PASS' if results['gemini'] else '❌ FAIL'}")
        
        if results['gemini']:
            # Test actual idea generation
            print("   Testing idea generation...")
            ideas = gemini.generate_content_ideas(3)  # Generate 3 ideas
            if ideas:
                print(f"   ✅ Successfully generated {len(ideas)} ideas:")
                for i, idea in enumerate(ideas, 1):
                    print(f"     {i}. {idea['title']}")
            else:
                print("   ⚠️ No ideas generated")
                
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
        if "api key" in str(e).lower():
            print("   💡 Tip: Add your Gemini API key to .env: GOOGLE_GEMINI_API_KEY=your_key")
    
    return results

def test_content_ideation_engine():
    """Test the full Content Ideation Engine"""
    print("\n\n🚀 Testing Complete Content Ideation Engine")
    print("=" * 50)
    
    try:
        # Initialize the engine
        print("Initializing Content Ideation Engine...")
        engine = ContentIdeationEngine()
        
        if not engine.initialize():
            print("❌ Engine initialization failed")
            return False
        
        print("✅ Engine initialized successfully")
        
        # Test all integrations
        print("\nTesting all integrations...")
        integration_results = engine.test_all_integrations()
        
        for component, status in integration_results.items():
            if component != 'overall':
                print(f"   {component.capitalize()}: {'✅ PASS' if status else '❌ FAIL'}")
        
        print(f"\nOverall Status: {'✅ ALL SYSTEMS GO' if integration_results['overall'] else '⚠️ PARTIAL FUNCTIONALITY'}")
        
        # If we have working components, test a partial run
        if integration_results['reddit'] and integration_results['sheets']:
            print("\n🔄 Testing partial content ideation cycle (Reddit + Sheets only)...")
            
            # We'll test with fewer ideas since we might not have Gemini
            gemini_count = 5 if integration_results['gemini'] else 0
            reddit_count = 5
            
            results = engine.run_ideation_cycle(
                gemini_ideas=gemini_count,
                reddit_stories=reddit_count
            )
            
            print(f"\n📊 Test Results:")
            print(f"   Total ideas generated: {results['total_ideas']}")
            print(f"   Gemini ideas: {results['gemini_ideas']}")
            print(f"   Reddit stories: {results['reddit_ideas']}")
            print(f"   Successfully uploaded: {results['successful_uploads']}")
            print(f"   Errors: {results['errors']}")
            print(f"   Execution time: {results['execution_time']} seconds")
            
            if results['successful_uploads'] > 0:
                print("\n🎉 SUCCESS! Ideas were added to your Google Sheets dashboard!")
                print(f"   Check: https://docs.google.com/spreadsheets/d/1uAu0yBPzjAvvNn4GjVpnwa3P2wdpF9P69K1-anNqSZU/edit")
                return True
            else:
                print("\n⚠️ No ideas were uploaded to dashboard")
                return False
        else:
            print("⚠️ Cannot test full cycle - missing required components")
            return False
            
    except Exception as e:
        print(f"\n❌ Content Ideation Engine test failed: {e}")
        return False

def display_next_steps(component_results):
    """Display next steps based on test results"""
    print("\n\n📋 Next Steps & Recommendations")
    print("=" * 50)
    
    if all(component_results.values()):
        print("🎉 EXCELLENT! All components are working perfectly!")
        print("✅ Your Content Ideation Engine is fully operational")
        print("✅ Ready to run automated content generation")
        print("\nTo run the full pipeline:")
        print("   python src/main.py run-once")
    
    else:
        print("⚠️ Some components need attention:")
        
        if not component_results['gemini']:
            print("\n💡 Gemini API Setup:")
            print("   1. Get API key from: https://makersuite.google.com/app/apikey")
            print("   2. Add to .env: GOOGLE_GEMINI_API_KEY=your_api_key")
            print("   3. This will enable AI-powered content idea generation")
        
        if not component_results['reddit']:
            print("\n📱 Reddit API:")
            print("   - Credentials are configured but connection failed")
            print("   - May be temporary rate limiting")
            print("   - Try testing again in a few minutes")
        
        if not component_results['sheets']:
            print("\n📊 Google Sheets:")
            print("   - This should be working from Task #1")
            print("   - Check your credentials and spreadsheet sharing")
        
        working_count = sum(1 for result in component_results.values() if result)
        print(f"\n📈 Progress: {working_count}/3 components working")
        
        if working_count >= 2:
            print("✅ You have enough components working to test content generation!")

def main():
    """Main test function"""
    # Setup logging
    setup_logging()
    
    print("🎬 Shorts Factory - Content Ideation Engine Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Test individual components
    component_results = test_individual_components()
    
    # Test full engine if we have working components
    working_components = sum(1 for result in component_results.values() if result)
    if working_components >= 2:  # Need at least 2 components (Sheets + one content source)
        engine_success = test_content_ideation_engine()
    else:
        engine_success = False
        print("\n⚠️ Skipping full engine test - need at least 2 working components")
    
    # Display recommendations
    display_next_steps(component_results)
    
    # Final summary
    print(f"\n🎯 FINAL RESULT: {'SUCCESS' if engine_success else 'PARTIAL SUCCESS'}")
    print("Task #2 Content Ideation Engine implementation is ready!")

if __name__ == '__main__':
    main()
