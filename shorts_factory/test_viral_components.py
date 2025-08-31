#!/usr/bin/env python3
"""
🧪 Viral Shorts Factory - Component Testing Suite
Test individual components of the viral content creation system
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def test_viral_prompt_optimizer():
    """Test the viral prompt optimization engine"""
    print("\n🧠 Testing Viral Prompt Optimizer...")
    print("-" * 50)
    
    try:
        from core.viral_prompt_optimizer import ViralPromptOptimizer
        
        optimizer = ViralPromptOptimizer()
        
        # Test each theme
        themes = ["family", "selfhelp", "news", "reddit"]
        
        for theme in themes:
            print(f"\n🎭 Testing {theme.upper()} theme:")
            
            # Generate viral prompt
            prompt = optimizer.generate_viral_optimized_prompt(
                theme=theme,
                target_duration=90
            )
            
            print(f"✅ Prompt generated ({len(prompt)} chars)")
            
            # Test viral analysis
            mock_script = f"You won't believe what happened in my {theme} journey. This changed everything and now I want to share it with you!"
            
            scores = optimizer.analyze_viral_potential(mock_script, theme)
            print(f"✅ Viral Analysis - Overall Score: {scores['overall_viral_score']:.1f}/10")
            
            # Test metadata optimization
            metadata = optimizer.optimize_metadata_for_viral_reach(mock_script, theme, scores)
            print(f"✅ Metadata Generated - Title: {metadata['title'][:40]}...")
        
        print(f"\n🎉 Viral Prompt Optimizer: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Viral Prompt Optimizer FAILED: {e}")
        return False

def test_api_connections():
    """Test all API connections"""
    print("\n🔌 Testing API Connections...")
    print("-" * 50)
    
    results = {}
    
    # Test Gemini API
    try:
        from integrations.gemini_api import GeminiContentGenerator
        gemini = GeminiContentGenerator()
        test_ideas = gemini.generate_ideas("Generate a short test story about success", num_ideas=1)
        results["Gemini"] = "✅ PASS" if test_ideas else "❌ FAIL"
        print(f"Gemini API: {results['Gemini']}")
    except Exception as e:
        results["Gemini"] = f"❌ FAIL: {e}"
        print(f"Gemini API: {results['Gemini']}")
    
    # Test Google Sheets
    try:
        from integrations.google_sheets import GoogleSheetsManager
        sheets = GoogleSheetsManager()
        content = sheets.get_all_content()
        results["Sheets"] = "✅ PASS" if content is not None else "❌ FAIL"
        print(f"Google Sheets: {results['Sheets']}")
    except Exception as e:
        results["Sheets"] = f"❌ FAIL: {e}"
        print(f"Google Sheets: {results['Sheets']}")
    
    # Test ElevenLabs
    try:
        from integrations.elevenlabs_api import ElevenLabsTextToSpeech
        elevenlabs = ElevenLabsTextToSpeech()
        voices = elevenlabs.get_available_voices()
        results["ElevenLabs"] = "✅ PASS" if voices else "❌ FAIL"
        print(f"ElevenLabs: {results['ElevenLabs']}")
    except Exception as e:
        results["ElevenLabs"] = f"❌ FAIL: {e}"
        print(f"ElevenLabs: {results['ElevenLabs']}")
    
    # Test Pexels
    try:
        from integrations.pexels_api import PexelsVideoSourcing
        pexels = PexelsVideoSourcing()
        test_result = pexels.test_connection()
        results["Pexels"] = "✅ PASS" if test_result else "❌ FAIL"
        print(f"Pexels: {results['Pexels']}")
    except Exception as e:
        results["Pexels"] = f"❌ FAIL: {e}"
        print(f"Pexels: {results['Pexels']}")
    
    # Summary
    passed = len([r for r in results.values() if "✅ PASS" in r])
    total = len(results)
    
    print(f"\n📊 API Connection Summary: {passed}/{total} PASSED")
    return passed == total

def test_content_generation():
    """Test content generation pipeline"""
    print("\n📝 Testing Content Generation Pipeline...")
    print("-" * 50)
    
    try:
        from integrations.gemini_api import GeminiContentGenerator
        from core.viral_prompt_optimizer import ViralPromptOptimizer
        
        optimizer = ViralPromptOptimizer()
        gemini = GeminiContentGenerator()
        
        # Test viral content generation
        themes = ["family", "selfhelp"]
        
        for theme in themes:
            print(f"\n🎭 Testing {theme} content generation...")
            
            # Generate viral prompt
            viral_prompt = optimizer.generate_viral_optimized_prompt(
                theme=theme,
                target_duration=60
            )
            
            # Generate content with viral prompt
            content = gemini.generate_ideas(viral_prompt, num_ideas=1)
            
            if content and content[0]:
                # Analyze viral potential
                scores = optimizer.analyze_viral_potential(content[0], theme)
                print(f"✅ Generated {theme} content (Viral Score: {scores['overall_viral_score']:.1f}/10)")
            else:
                print(f"❌ Failed to generate {theme} content")
                return False
        
        print(f"\n🎉 Content Generation: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Content Generation FAILED: {e}")
        return False

def test_file_structure():
    """Test working directory structure"""
    print("\n📁 Testing File Structure...")
    print("-" * 50)
    
    working_dir = Path(os.getenv('WORKING_DIRECTORY', '/Volumes/Extreme Pro/ShortsFactory'))
    required_dirs = [
        'audio',
        'video_clips', 
        'final_videos',
        'captions',
        'captioned_videos',
        'metadata',
        'credentials'
    ]
    
    results = {}
    
    for dir_name in required_dirs:
        dir_path = working_dir / dir_name
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            results[dir_name] = "✅ CREATED/EXISTS" if dir_path.exists() else "❌ FAILED"
        except Exception as e:
            results[dir_name] = f"❌ ERROR: {e}"
        
        print(f"{dir_name}: {results[dir_name]}")
    
    # Check external drive
    drive_accessible = working_dir.parent.exists()
    print(f"External Drive: {'✅ ACCESSIBLE' if drive_accessible else '❌ NOT FOUND'}")
    
    passed = len([r for r in results.values() if "✅" in r])
    total = len(results)
    
    print(f"\n📊 File Structure: {passed}/{total} directories ready")
    return passed == total and drive_accessible

async def test_minimal_pipeline():
    """Test minimal end-to-end pipeline"""
    print("\n🔄 Testing Minimal Pipeline...")
    print("-" * 50)
    
    try:
        # Import components
        from integrations.gemini_api import GeminiContentGenerator
        from integrations.google_sheets import GoogleSheetsManager
        from core.viral_prompt_optimizer import ViralPromptOptimizer
        
        # Initialize
        optimizer = ViralPromptOptimizer()
        gemini = GeminiContentGenerator()
        sheets = GoogleSheetsManager()
        
        print("✅ All components initialized")
        
        # Generate viral content
        viral_prompt = optimizer.generate_viral_optimized_prompt("family", 60)
        content = gemini.generate_ideas(viral_prompt, num_ideas=1)
        
        if not content or not content[0]:
            raise Exception("Content generation failed")
        
        print("✅ Viral content generated")
        
        # Analyze viral potential
        scores = optimizer.analyze_viral_potential(content[0], "family")
        print(f"✅ Viral analysis complete (Score: {scores['overall_viral_score']:.1f}/10)")
        
        # Test sheets integration (get content, don't add to avoid spam)
        all_content = sheets.get_all_content()
        print(f"✅ Sheets integration working ({len(all_content)} items found)")
        
        print(f"\n🎉 Minimal Pipeline: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Minimal Pipeline FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all component tests"""
    print("🚀 VIRAL SHORTS FACTORY - COMPONENT TESTING SUITE")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("API Connections", test_api_connections),
        ("Viral Prompt Optimizer", test_viral_prompt_optimizer),
        ("Content Generation", test_content_generation),
        ("Minimal Pipeline", lambda: asyncio.run(test_minimal_pipeline()))
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 RUNNING: {test_name}")
        print('='*60)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
            results[test_name] = False
    
    # Final Summary
    print(f"\n{'='*60}")
    print("📊 FINAL TEST SUMMARY")
    print('='*60)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("🎉 SYSTEM READY FOR VIRAL CONTENT CREATION!")
    else:
        print("⚠️  Some components need attention before full deployment")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

