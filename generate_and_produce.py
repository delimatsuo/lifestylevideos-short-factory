#!/usr/bin/env python3
"""
Generate 5 Ideas and Immediately Produce Videos
No approval step - straight from ideas to finished videos
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)

def main():
    """Generate ideas and immediately produce videos"""
    logger = logging.getLogger(__name__)
    
    print("🎬 AUTOMATED VIDEO PRODUCTION")
    print("=" * 50)
    print("1. Generate 5 ideas with AI")
    print("2. Immediately produce videos")
    print("3. Save to external drive for review")
    print()
    
    try:
        # Import core components (skip YouTube)
        from core.content_ideation_engine import ContentIdeationEngine
        from core.script_generator import ScriptGenerator
        from core.audio_generator import AudioGenerator
        from core.video_sourcing import VideoSourcingManager
        from core.video_assembly import VideoAssemblyManager
        from core.caption_manager import CaptionManager
        from core.metadata_manager import MetadataManager
        from integrations.google_sheets import GoogleSheetsManager
        
        print("✅ Components imported successfully")
        
        # Initialize Google Sheets
        print("\n📊 Initializing Google Sheets...")
        sheets = GoogleSheetsManager()
        print("✅ Google Sheets connected")
        
        # Initialize Content Ideation Engine
        print("\n💡 Initializing Content Ideation Engine...")
        ideation_engine = ContentIdeationEngine()
        if not ideation_engine.initialize():
            print("❌ Content Ideation Engine failed")
            return False
        print("✅ Content Ideation Engine ready")
        
        # Initialize production components
        print("\n🏭 Initializing production pipeline...")
        
        script_gen = ScriptGenerator()
        script_gen.initialize()
        print("✅ Script Generator ready")
        
        audio_gen = AudioGenerator()  
        audio_gen.initialize()
        print("✅ Audio Generator ready")
        
        video_sourcing = VideoSourcingManager()
        video_sourcing.initialize()
        print("✅ Video Sourcing ready")
        
        video_assembly = VideoAssemblyManager()
        video_assembly.initialize()
        print("✅ Video Assembly ready")
        
        caption_mgr = CaptionManager()
        caption_mgr.initialize()
        print("✅ Caption Manager ready")
        
        metadata_mgr = MetadataManager()
        metadata_mgr.initialize()
        print("✅ Metadata Manager ready")
        
        print("\n🎯 ALL SYSTEMS READY - STARTING PRODUCTION")
        print("=" * 50)
        
        # STEP 1: Generate 5 ideas
        print("\n💡 STEP 1: Generating 5 video ideas...")
        ideation_results = ideation_engine.run_ideation_cycle(
            gemini_ideas=5,
            reddit_stories=0  # Focus on Gemini for now
        )
        
        if ideation_results['successful_uploads'] == 0:
            print("❌ No ideas were generated")
            return False
            
        print(f"✅ Generated {ideation_results['successful_uploads']} ideas")
        
        # STEP 2: Get all pending ideas and auto-approve them
        print("\n🔄 STEP 2: Auto-approving all generated ideas...")
        all_content = sheets.get_all_content()
        pending_content = [c for c in all_content if c.get('status', '').lower() == 'pending approval']
        
        newly_approved_content = []  # Track only the content we just approved
        approved_count = 0
        for content in pending_content:
            content_id = content.get('id', '')
            if content_id and sheets.update_content_status(content_id, 'Approved'):
                approved_count += 1
                newly_approved_content.append(content)  # Add to our production list
                print(f"✅ Auto-approved: {content.get('title', content_id)}")
        
        print(f"✅ Auto-approved {approved_count} ideas for production")
        
        if approved_count == 0:
            print("❌ No content to process")
            return False
        
        # STEP 3: Process ONLY the newly approved content (not all approved content)
        print("\n🎬 STEP 3: Producing videos...")
        print("=" * 40)
        
        # Use only the content we just approved, not all approved content
        approved_content = newly_approved_content
        
        videos_produced = 0
        for content in approved_content:
            content_id = content.get('id', '')
            title = content.get('title', '')
            
            print(f"\n🎬 PRODUCING: {title}")
            print("-" * 30)
            
            try:
                # Script Generation
                print("📝 Generating script...")
                script = script_gen.generate_script_for_content(content)
                if script:
                    print("✅ Script generated")
                    # Save script using ScriptGenerator's built-in method
                    save_success = script_gen.save_script_to_sheet(content_id, script)
                    if save_success:
                        print("✅ Script saved to Google Sheets")
                    else:
                        print("❌ Script save failed")
                        continue
                else:
                    print("❌ Script generation failed")
                    continue
                
                # Audio Generation  
                print("🎙️ Creating audio...")
                # Refresh content to get the saved script
                updated_content = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                audio_file = audio_gen.generate_audio_for_content(updated_content)
                if audio_file:
                    print("✅ Audio generated")
                    sheets.update_content_status(content_id, 'Approved', audio_file=audio_file)
                else:
                    print("❌ Audio generation failed")
                    continue
                
                # Video Sourcing
                print("🎥 Sourcing video clips...")
                # Get the most up-to-date content with script
                updated_content = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                video_result = video_sourcing.source_videos_for_content(updated_content)
                if video_result:
                    print("✅ Video clips downloaded")
                else:
                    print("❌ Video sourcing failed")
                    continue
                
                # Video Assembly
                print("🎬 Assembling video...")
                # Get the most up-to-date content
                updated_content = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                assembly_result = video_assembly.assemble_video_for_content(updated_content)
                if assembly_result:
                    print("✅ Video assembled")
                    sheets.update_content_status(content_id, 'Approved', video_file=assembly_result)
                else:
                    print("❌ Video assembly failed")
                    continue
                
                # Caption Generation
                print("📄 Adding captions...")
                # Get the most up-to-date content
                updated_content = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                caption_result = caption_mgr.generate_captions_for_content(updated_content)
                if caption_result:
                    print("✅ Captions added")
                else:
                    print("❌ Caption generation failed")
                    continue
                
                # Metadata Generation
                print("📊 Generating metadata...")
                # Get the most up-to-date content
                updated_content = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                metadata_result = metadata_mgr.generate_metadata_for_content(updated_content)
                if metadata_result:
                    print("✅ Metadata generated")
                else:
                    print("❌ Metadata generation failed")
                    continue
                
                # Mark as completed
                sheets.update_content_status(content_id, 'Complete')
                videos_produced += 1
                
                print(f"🎊 COMPLETED: {title}")
                
            except Exception as e:
                print(f"❌ Failed to produce {title}: {e}")
                sheets.update_content_status(content_id, 'Failed', error_log=str(e))
                continue
        
        print("\n" + "=" * 50)
        print("🎊 PRODUCTION COMPLETE!")
        print("=" * 50)
        print(f"✅ Videos produced: {videos_produced}")
        print(f"📁 Location: /Volumes/Extreme Pro/ShortsFactory/captioned_videos/")
        print()
        print("🎬 READY FOR REVIEW:")
        print("1. Check your external drive for finished videos")
        print("2. Review and select your favorites") 
        print("3. Upload manually to YouTube")
        print()
        print("🚀 Your automated video production is complete!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Production failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SUCCESS! Check your videos on the external drive!")
    else:
        print("\n❌ Production failed - check errors above")
