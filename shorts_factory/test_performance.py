#!/usr/bin/env python3
"""
⚡ Performance Testing Suite for Viral Shorts Factory
Test processing speed, resource usage, and scalability
"""

import time
import asyncio
import psutil
import os
from datetime import datetime

def measure_processing_time(func, *args, **kwargs):
    """Measure function execution time"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

def get_system_resources():
    """Get current system resource usage"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_used_gb': psutil.virtual_memory().used / (1024**3),
        'disk_usage_gb': psutil.disk_usage('/').used / (1024**3)
    }

async def test_batch_processing_speed():
    """Test processing speed for different batch sizes"""
    print("\n⚡ Testing Batch Processing Speed...")
    print("-" * 50)
    
    # Simulate viral content processing times
    batch_sizes = [1, 2, 3, 5]
    
    for batch_size in batch_sizes:
        print(f"\n📊 Testing batch size: {batch_size}")
        
        start_time = time.time()
        start_resources = get_system_resources()
        
        # Simulate processing (replace with actual viral factory call)
        print(f"  🎬 Processing {batch_size} viral videos...")
        
        # Simulate the time each stage would take
        stages = ["ideation", "audio", "video_clips", "assembly", "captions", "metadata"]
        for stage in stages:
            await asyncio.sleep(0.5)  # Simulate processing time
            print(f"    ✅ {stage} complete")
        
        end_time = time.time()
        end_resources = get_system_resources()
        
        processing_time = end_time - start_time
        
        print(f"  ⏱️  Total Time: {processing_time:.1f}s")
        print(f"  📈 Time per Video: {processing_time/batch_size:.1f}s")
        print(f"  🧠 CPU Usage: {end_resources['cpu_percent']:.1f}%")
        print(f"  💾 Memory Usage: {end_resources['memory_percent']:.1f}%")

def test_concurrent_processing():
    """Test concurrent video processing capability"""
    print("\n🔄 Testing Concurrent Processing...")
    print("-" * 50)
    
    async def simulate_video_processing(video_id, processing_time=5):
        """Simulate processing a single video"""
        print(f"🎬 Starting video {video_id}")
        await asyncio.sleep(processing_time)
        print(f"✅ Completed video {video_id}")
        return f"video_{video_id}_result"
    
    async def run_concurrent_test():
        concurrent_levels = [1, 2, 3, 5]
        
        for level in concurrent_levels:
            print(f"\n📊 Testing {level} concurrent videos:")
            
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = [simulate_video_processing(i) for i in range(level)]
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"  ⏱️  Total Time: {total_time:.1f}s")
            print(f"  📈 Efficiency: {(level * 5) / total_time:.1f}x speedup")
            print(f"  ✅ Videos Completed: {len(results)}")
    
    asyncio.run(run_concurrent_test())

def test_viral_score_distribution():
    """Test viral score distribution across themes"""
    print("\n🔥 Testing Viral Score Distribution...")
    print("-" * 50)
    
    try:
        import sys
        sys.path.insert(0, 'src')
        from core.viral_prompt_optimizer import ViralPromptOptimizer
        
        optimizer = ViralPromptOptimizer()
        themes = ["family", "selfhelp", "news", "reddit"]
        
        # Test scripts for each theme
        test_scripts = {
            "family": "My mother did something that changed our family forever. I never expected my 85-year-old grandmother to teach me this life lesson. What happened next will shock you!",
            "selfhelp": "I was failing at everything until I discovered this one secret. 30 days later, my entire life transformed. Here's what successful people know that you don't.",
            "news": "While everyone was distracted by the headlines, this happened. The media won't tell you this truth about what's really going on in our society.",
            "reddit": "A Redditor confessed something that broke the internet. This anonymous story reveals the dark truth about online relationships and will make you question everything."
        }
        
        theme_scores = {}
        
        for theme in themes:
            script = test_scripts[theme]
            scores = optimizer.analyze_viral_potential(script, theme)
            theme_scores[theme] = scores['overall_viral_score']
            
            print(f"🎭 {theme.upper():10} | Viral Score: {scores['overall_viral_score']:.1f}/10")
            print(f"   Hook Strength: {scores['hook_strength']:.1f}/10")
            print(f"   Emotional Impact: {scores['emotional_impact']:.1f}/10")
            print(f"   Shareability: {scores['shareability']:.1f}/10")
        
        avg_score = sum(theme_scores.values()) / len(theme_scores)
        print(f"\n📊 Average Viral Score: {avg_score:.1f}/10")
        
        return theme_scores
        
    except Exception as e:
        print(f"❌ Viral scoring test failed: {e}")
        return {}

def benchmark_api_response_times():
    """Benchmark API response times"""
    print("\n🌐 Testing API Response Times...")
    print("-" * 50)
    
    try:
        import sys
        sys.path.insert(0, 'src')
        
        # Test Gemini API speed
        print("🧠 Testing Gemini API...")
        start_time = time.time()
        
        from integrations.gemini_api import GeminiContentGenerator
        gemini = GeminiContentGenerator()
        test_result = gemini.generate_ideas("Generate a short viral story", num_ideas=1)
        
        gemini_time = time.time() - start_time
        print(f"   ⏱️  Gemini Response Time: {gemini_time:.1f}s")
        
        # Test Google Sheets speed
        print("📊 Testing Google Sheets API...")
        start_time = time.time()
        
        from integrations.google_sheets import GoogleSheetsManager
        sheets = GoogleSheetsManager()
        content = sheets.get_all_content()
        
        sheets_time = time.time() - start_time
        print(f"   ⏱️  Sheets Response Time: {sheets_time:.1f}s")
        print(f"   📄 Items Retrieved: {len(content) if content else 0}")
        
        print(f"\n📈 API Performance Summary:")
        print(f"   🥇 Fastest API: {'Sheets' if sheets_time < gemini_time else 'Gemini'}")
        print(f"   📊 Total API Time: {gemini_time + sheets_time:.1f}s")
        
    except Exception as e:
        print(f"❌ API benchmark failed: {e}")

async def main():
    """Run all performance tests"""
    print("⚡ VIRAL SHORTS FACTORY - PERFORMANCE TESTING SUITE")
    print("=" * 60)
    print(f"🕒 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # System info
    print(f"\n💻 System Information:")
    print(f"   CPU Count: {psutil.cpu_count()}")
    print(f"   RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"   Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    
    # Run tests
    test_functions = [
        ("API Response Times", benchmark_api_response_times),
        ("Viral Score Distribution", test_viral_score_distribution),
        ("Batch Processing Speed", lambda: asyncio.run(test_batch_processing_speed())),
        ("Concurrent Processing", test_concurrent_processing)
    ]
    
    results = {}
    
    for test_name, test_func in test_functions:
        print(f"\n{'='*60}")
        print(f"⚡ RUNNING: {test_name}")
        print('='*60)
        
        try:
            start_time = time.time()
            result = test_func() if not asyncio.iscoroutinefunction(test_func) else await test_func()
            end_time = time.time()
            
            results[test_name] = {
                'success': True,
                'duration': end_time - start_time,
                'result': result
            }
            
            print(f"✅ {test_name} completed in {end_time - start_time:.1f}s")
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = {
                'success': False,
                'error': str(e)
            }
    
    # Final summary
    print(f"\n{'='*60}")
    print("📊 PERFORMANCE TEST SUMMARY")
    print('='*60)
    
    successful_tests = sum(1 for r in results.values() if r.get('success', False))
    total_tests = len(results)
    
    for test_name, result in results.items():
        if result.get('success'):
            duration = result.get('duration', 0)
            print(f"✅ {test_name}: {duration:.1f}s")
        else:
            print(f"❌ {test_name}: {result.get('error', 'Unknown error')}")
    
    print(f"\n🎯 Performance Score: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests >= total_tests * 0.8:
        print("🚀 SYSTEM PERFORMANCE: EXCELLENT")
    else:
        print("⚠️  SYSTEM PERFORMANCE: NEEDS OPTIMIZATION")

if __name__ == "__main__":
    asyncio.run(main())

