#!/usr/bin/env python3
"""
FIXED: Generate and Produce Videos - Properly handles 5 unique videos
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment
load_dotenv()

# Add src to path  
sys.path.insert(0, 'src')

def generate_and_produce_videos():
    """Generate 5 NEW ideas and produce 5 UNIQUE videos"""
    print("🎬 SHORTS FACTORY - FIXED BATCH PRODUCER")
    print("=" * 60)
    
    try:
        # Import components (avoiding circular imports)
        sys.path.append('src/integrations')
        sys.path.append('src/core')
        
        from integrations.google_sheets import GoogleSheetsManager
        from core.content_ideation_engine import ContentIdeationEngine
        from core.script_generator import ScriptGenerator
        from core.audio_generator import AudioGenerator
        from core.video_sourcing import VideoSourcingManager
        from core.video_assembly import VideoAssemblyManager
        from core.caption_manager import CaptionManager
        from core.metadata_manager import MetadataManager
        
        print("📊 Connecting to Google Sheets...")
        sheets = GoogleSheetsManager()
        
        # Record starting state
        initial_content = sheets.get_all_content()
        initial_count = len(initial_content)
        print(f"📈 Initial content count: {initial_count}")
        
        # STEP 1: Generate exactly 5 NEW ideas
        print("\n💡 STEP 1: Generating 5 NEW video ideas...")
        print("-" * 40)
        
        ideation_engine = ContentIdeationEngine()
        if not ideation_engine.initialize():
            print("❌ Failed to initialize ideation engine")
            return False
        
        # Generate 5 new ideas
        result = ideation_engine.run_ideation_cycle(
            gemini_ideas=5,
            reddit_stories=0
        )
        
        print(f"✅ Ideation result: {result.get('successful_uploads', 0)} ideas created")
        
        # Verify new content was actually created
        updated_content = sheets.get_all_content()
        new_content_count = len(updated_content) - initial_count
        
        if new_content_count < 5:
            print(f"⚠️ Warning: Only {new_content_count} new ideas were created (expected 5)")
        
        # STEP 2: Find the NEWEST "Pending Approval" items (the ones we just created)
        print("\n🔍 STEP 2: Finding newly created content...")
        print("-" * 40)
        
        # Get the newest items that have "Pending Approval" status
        pending_content = [c for c in updated_content if c.get('status', '').lower() == 'pending approval']
        
        # Sort by ID (descending) to get the newest items first
        try:
            pending_content_sorted = sorted(pending_content, key=lambda x: int(x.get('id', '0')), reverse=True)
        except (ValueError, TypeError) as e:
            print(f"Warning: Failed to sort content by ID: {e}")
            pending_content_sorted = pending_content
        except Exception as e:
            print(f"Error: Unexpected error sorting content: {e}")
            pending_content_sorted = pending_content
        
        # Take the first 5 (newest) pending items
        newest_pending = pending_content_sorted[:5]
        
        print(f"🔍 Found {len(newest_pending)} pending items to process:")
        for item in newest_pending:
            print(f"  - ID {item.get('id')}: {item.get('title', 'Untitled')[:60]}...")
        
        if not newest_pending:
            print("❌ No pending content found to approve")
            return False
        
        # STEP 3: Auto-approve ONLY the newest content
        print("\n✅ STEP 3: Auto-approving newest content...")
        print("-" * 40)
        
        approved_for_production = []
        for content in newest_pending:
            content_id = content.get('id', '')
            title = content.get('title', 'Untitled')
            
            if sheets.update_content_status(content_id, 'Approved'):
                approved_for_production.append(content)
                print(f"✅ Approved: {title[:50]}... (ID: {content_id})")
            else:
                print(f"❌ Failed to approve: {title[:50]}... (ID: {content_id})")
        
        if not approved_for_production:
            print("❌ No content was approved for production")
            return False
        
        print(f"\n🎯 Ready to produce {len(approved_for_production)} unique videos")
        
        # STEP 4: Initialize production components
        print("\n🔧 STEP 4: Initializing production components...")
        print("-" * 40)
        
        script_gen = ScriptGenerator()
        if not script_gen.initialize():
            print("❌ Script generator initialization failed")
            return False
        print("✅ Script generator ready")
        
        audio_gen = AudioGenerator()
        if not audio_gen.initialize():
            print("❌ Audio generator initialization failed")
            return False
        print("✅ Audio generator ready")
        
        video_sourcing = VideoSourcingManager()
        if not video_sourcing.initialize():
            print("❌ Video sourcing initialization failed")
            return False
        print("✅ Video sourcing ready")
        
        video_assembly = VideoAssemblyManager()
        if not video_assembly.initialize():
            print("❌ Video assembly initialization failed")
            return False
        print("✅ Video assembly ready")
        
        caption_mgr = CaptionManager()
        if not caption_mgr.initialize():
            print("❌ Caption manager initialization failed")
            return False
        print("✅ Caption manager ready")
        
        metadata_mgr = MetadataManager()
        if not metadata_mgr.initialize():
            print("❌ Metadata manager initialization failed")
            return False
        print("✅ Metadata manager ready")
        
        # STEP 5: Produce each video individually
        print("\n🎬 STEP 5: PRODUCING VIDEOS...")
        print("=" * 60)
        
        videos_produced = 0
        
        for i, content in enumerate(approved_for_production, 1):
            content_id = content.get('id', '')
            title = content.get('title', 'Untitled')
            
            print(f"\n🎬 PRODUCING VIDEO {i}/5: {title}")
            print(f"📋 Content ID: {content_id}")
            print("-" * 50)
            
            try:
                # Set status to In Progress
                sheets.update_content_status(content_id, 'In Progress')
                
                # Script Generation
                print("📝 1. Generating script...")
                script = script_gen.generate_script_for_content(content)
                if script:
                    print("   ✅ Script generated")
                    script_gen.save_script_to_sheet(content_id, script)
                    print("   ✅ Script saved to Google Sheets")
                else:
                    print("   ❌ Script generation failed")
                    sheets.update_content_status(content_id, 'Failed', error_log="Script generation failed")
                    continue
                
                # Get updated content with script
                updated_content_item = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                
                # Audio Generation
                print("🎙️ 2. Creating audio narration...")
                audio_file = audio_gen.generate_audio_for_content(updated_content_item)
                if audio_file:
                    print(f"   ✅ Audio generated: {Path(audio_file).name}")
                    sheets.update_content_status(content_id, 'In Progress', audio_file=audio_file)
                else:
                    print("   ❌ Audio generation failed")
                    sheets.update_content_status(content_id, 'Failed', error_log="Audio generation failed")
                    continue
                
                # Video Sourcing
                print("🎥 3. Sourcing video clips...")
                updated_content_item = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                video_result = video_sourcing.source_videos_for_content(updated_content_item)
                if video_result:
                    print("   ✅ Video clips downloaded")
                else:
                    print("   ❌ Video sourcing failed")
                    sheets.update_content_status(content_id, 'Failed', error_log="Video sourcing failed")
                    continue
                
                # Video Assembly
                print("🎬 4. Assembling final video...")
                updated_content_item = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                assembly_result = video_sourcing.source_videos_for_content(updated_content_item)
                if assembly_result:
                    print("   ✅ Video assembled")
                    sheets.update_content_status(content_id, 'In Progress', video_file=assembly_result)
                else:
                    print("   ❌ Video assembly failed")
                    sheets.update_content_status(content_id, 'Failed', error_log="Video assembly failed")
                    continue
                
                # Caption Generation
                print("📄 5. Adding captions...")
                updated_content_item = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                caption_result = caption_mgr.generate_captions_for_content(updated_content_item)
                if caption_result:
                    print("   ✅ Captions added")
                else:
                    print("   ❌ Caption generation failed")
                    sheets.update_content_status(content_id, 'Failed', error_log="Caption generation failed")
                    continue
                
                # Metadata Generation
                print("📊 6. Generating YouTube metadata...")
                updated_content_item = next((c for c in sheets.get_all_content() if c.get('id') == content_id), content)
                metadata_result = metadata_mgr.generate_metadata_for_content(updated_content_item)
                if metadata_result:
                    print("   ✅ Metadata generated")
                else:
                    print("   ❌ Metadata generation failed")
                    sheets.update_content_status(content_id, 'Failed', error_log="Metadata generation failed")
                    continue
                
                # Mark as completed
                sheets.update_content_status(content_id, 'Complete')
                videos_produced += 1
                
                print(f"🎉 VIDEO {i} COMPLETED SUCCESSFULLY!")
                print(f"📁 Check: /Volumes/Extreme Pro/ShortsFactory/captioned_videos/")
                
            except Exception as e:
                print(f"❌ ERROR producing video {i}: {e}")
                sheets.update_content_status(content_id, 'Failed', error_log=str(e))
                continue
        
        # FINAL RESULTS
        print("\n" + "=" * 60)
        print("🎊 BATCH PRODUCTION COMPLETE!")
        print("=" * 60)
        print(f"✅ Videos successfully produced: {videos_produced}/5")
        print(f"📁 Location: /Volumes/Extreme Pro/ShortsFactory/captioned_videos/")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if videos_produced == 5:
            print("🏆 PERFECT! All 5 videos produced successfully!")
        elif videos_produced > 0:
            print(f"⚠️ Partial success: {videos_produced} videos produced")
        else:
            print("❌ No videos were produced")
        
        print("\n🎬 Your videos are ready for review and upload!")
        
        return videos_produced > 0
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_and_produce_videos()
    if success:
        print("\n🚀 SUCCESS! Check your videos on the external drive!")
    else:
        print("\n💥 FAILED! Check the logs above for errors.")

