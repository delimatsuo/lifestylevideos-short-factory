#!/usr/bin/env python3
"""
🎬 Create Viral Videos - Simple Command Interface
Theme-based viral content creation with one command
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the viral factory
try:
    from viral_shorts_factory import ViralShortsFactory, ContentTheme
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed and paths are correct.")
    sys.exit(1)

def print_usage():
    """Print usage instructions"""
    print("""
🎬 VIRAL SHORTS FACTORY v2.0 - Simple Command Interface

USAGE:
    python create_viral_videos.py <theme> [count]

THEMES:
    family     - Emotional family stories (TikTok-style)
    selfhelp   - Personal transformation and motivation stories  
    news       - Current events and trending topic stories
    reddit     - Internet culture and community stories
    mixed      - Random mix across all themes

EXAMPLES:
    python create_viral_videos.py family
    python create_viral_videos.py selfhelp 3
    python create_viral_videos.py mixed 10
    
FEATURES:
    ✅ Viral-optimized scripts with engagement hooks
    ✅ Theme-specific content targeting
    ✅ YouTube Shorts algorithm optimization  
    ✅ 60-180 second duration range
    ✅ Professional production pipeline
    ✅ Saves to external drive for review
""")

async def main():
    """Main entry point"""
    
    # Parse command line arguments with validation
    try:
        from src.security.input_validator import get_input_validator, DataType
        validator = get_input_validator()
        
        if len(sys.argv) < 2:
            print_usage()
            return
        
        # Validate theme argument
        theme_result = validator.validate_input(sys.argv[1], DataType.STRING, context="cli_theme")
        if not theme_result.is_valid:
            print(f"❌ Invalid theme argument: {'; '.join(theme_result.errors)}")
            print_usage()
            return
        theme_arg = theme_result.sanitized_value.lower()
        
        # Validate count argument if provided
        count = 5  # Default
        if len(sys.argv) > 2:
            count_result = validator.safe_int(sys.argv[2], default=5, min_val=1, max_val=20)
            if count_result is None:
                print(f"❌ Invalid count argument: {sys.argv[2]} (must be 1-20)")
                print_usage()
                return
            count = count_result
            
    except ImportError:
        # Fallback to basic validation if security modules not available
        if len(sys.argv) < 2:
            print_usage()
            return
        
        theme_arg = str(sys.argv[1]).lower()
        try:
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            if count < 1 or count > 20:
                print(f"❌ Count must be between 1 and 20, got: {count}")
                return
        except ValueError:
            print(f"❌ Invalid count argument: {sys.argv[2]}")
            return
    
    # Validate theme
    valid_themes = ['family', 'selfhelp', 'news', 'reddit', 'mixed']
    if theme_arg not in valid_themes:
        print(f"❌ Invalid theme: {theme_arg}")
        print(f"Valid themes: {', '.join(valid_themes)}")
        return
    
    # Convert to enum
    theme = ContentTheme(theme_arg)
    
    print(f"""
🚀 VIRAL SHORTS FACTORY v2.0
═══════════════════════════════════════════════

🎭 Theme: {theme.value.upper()}
📊 Videos: {count}
🎯 Target: Maximum viral engagement
⏱️ Duration: 60-180 seconds each

Starting viral content creation...
""")
    
    try:
        # Initialize factory
        factory = ViralShortsFactory()
        
        # Create viral batch
        results = await factory.create_viral_batch(theme, count)
        
        # Print results
        factory.print_results_summary(results)
        
        # Success message
        if results.get('success'):
            print(f"""
🎉 SUCCESS! Your viral {theme.value} videos are ready!

📁 Location: {results.get('output_directory')}
🔥 Average Viral Score: {results.get('avg_viral_score')}/10
⏱️ Processing Time: {results.get('processing_time_seconds')}s

Next steps:
1. Review videos on your external drive
2. Select your favorites for upload
3. Upload to YouTube with generated metadata
4. Monitor engagement and optimize future batches

Run again with: python create_viral_videos.py {theme.value} {count}
""")
        else:
            print(f"""
❌ Batch processing encountered issues.
Check the logs above for details.

Try running again or contact support.
""")
            
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💥 Failed to start: {e}")
        print("\nTroubleshooting:")
        print("1. Check that all dependencies are installed")
        print("2. Verify API keys are configured")
        print("3. Ensure external drive is connected")
        print("4. Check file permissions")

