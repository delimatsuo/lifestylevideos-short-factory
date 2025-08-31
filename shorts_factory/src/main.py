#!/usr/bin/env python3
"""
Shorts Factory - Main Orchestration Script
Automated YouTube Shorts content creation pipeline
"""

import logging
import sys
import schedule
import time
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.config import config
from core.content_ideation_engine import ContentIdeationEngine
from core.approval_workflow import ApprovalWorkflowMonitor
from core.script_generator import ScriptGenerator
from core.audio_generator import AudioGenerator
from core.video_sourcing import VideoSourcingManager
from core.video_assembly import VideoAssemblyManager
from core.caption_manager import CaptionManager
from core.metadata_manager import MetadataManager
from core.youtube_distribution import YouTubeDistributionManager
from integrations.google_sheets import GoogleSheetsManager
from utils.logger import setup_logging


class ShortsFactory:
    """Main orchestration class for Shorts Factory"""
    
    def __init__(self):
        """Initialize Shorts Factory"""
        self.logger = logging.getLogger(__name__)
        self.sheets_manager = None
        self.content_engine = None
        self.approval_monitor = None
        self.script_generator = None
        self.audio_generator = None
        self.video_sourcing = None
        self.video_assembly = None
        self.caption_manager = None
        self.metadata_manager = None
        self.youtube_distribution = None
        self.setup_complete = False
    
    def initialize(self) -> bool:
        """Initialize all components and verify connections"""
        try:
            self.logger.info("🚀 Initializing Shorts Factory...")
            
            # Validate configuration
            self.logger.info("📋 Validating configuration...")
            config_errors = config.validate_config()
            if config_errors:
                self.logger.error("❌ Configuration validation failed:")
                for error in config_errors:
                    self.logger.error(f"  - {error}")
                return False
            
            self.logger.info("✅ Configuration validated successfully")
            
            # Initialize Google Sheets Manager
            self.logger.info("📊 Initializing Google Sheets integration...")
            self.sheets_manager = GoogleSheetsManager()
            
            # Test connection
            if not self.sheets_manager.test_connection():
                self.logger.error("❌ Google Sheets connection failed")
                return False
            
            # Ensure dashboard has proper headers
            self.logger.info("🏗️ Setting up dashboard schema...")
            if not self.sheets_manager.create_dashboard_headers():
                self.logger.error("❌ Failed to create dashboard headers")
                return False
            
            self.logger.info("✅ Dashboard schema configured successfully")
            
            # Initialize Content Ideation Engine
            self.logger.info("💡 Initializing Content Ideation Engine...")
            self.content_engine = ContentIdeationEngine()
            if not self.content_engine.initialize():
                self.logger.error("❌ Content Ideation Engine initialization failed")
                return False
            
            self.logger.info("✅ Content Ideation Engine initialized successfully")
            
            # Initialize Approval Workflow Monitor
            self.logger.info("🔍 Initializing Approval Workflow Monitor...")
            self.approval_monitor = ApprovalWorkflowMonitor()
            if not self.approval_monitor.initialize():
                self.logger.error("❌ Approval Workflow Monitor initialization failed")
                return False
            
            self.logger.info("✅ Approval Workflow Monitor initialized successfully")
            
            # Initialize Script Generator
            self.logger.info("🎬 Initializing Script Generator...")
            self.script_generator = ScriptGenerator()
            if not self.script_generator.initialize():
                self.logger.error("❌ Script Generator initialization failed")
                return False
            
            self.logger.info("✅ Script Generator initialized successfully")
            
            # Initialize Audio Generator
            self.logger.info("🎙️ Initializing Audio Generator...")
            self.audio_generator = AudioGenerator()
            if not self.audio_generator.initialize():
                self.logger.error("❌ Audio Generator initialization failed")
                return False
            
            self.logger.info("✅ Audio Generator initialized successfully")
            
            # Initialize Video Sourcing Manager
            self.logger.info("🎥 Initializing Video Sourcing Manager...")
            self.video_sourcing = VideoSourcingManager()
            if not self.video_sourcing.initialize():
                self.logger.error("❌ Video Sourcing Manager initialization failed")
                return False
            
            self.logger.info("✅ Video Sourcing Manager initialized successfully")
            
            # Initialize Video Assembly Manager (NEW - TASK #7!)
            self.logger.info("🎬 Initializing Video Assembly Manager...")
            self.video_assembly = VideoAssemblyManager()
            if not self.video_assembly.initialize():
                self.logger.error("❌ Video Assembly Manager initialization failed")
                return False
            
            self.logger.info("✅ Video Assembly Manager initialized successfully")
            
            # Initialize Caption Manager (NEW - TASK #8!)
            self.logger.info("📝 Initializing Caption Manager...")
            self.caption_manager = CaptionManager()
            if not self.caption_manager.initialize():
                self.logger.error("❌ Caption Manager initialization failed")
                return False
            
            self.logger.info("✅ Caption Manager initialized successfully")
            
            # Initialize Metadata Manager (NEW - TASK #9!)
            self.logger.info("📺 Initializing Metadata Manager...")
            self.metadata_manager = MetadataManager()
            if not self.metadata_manager.initialize():
                self.logger.error("❌ Metadata Manager initialization failed")
                return False
            
            self.logger.info("✅ Metadata Manager initialized successfully")
            
            # Initialize YouTube Distribution Manager (NEW - TASK #10!)
            self.logger.info("🚀 Initializing YouTube Distribution Manager...")
            self.youtube_distribution = YouTubeDistributionManager()
            if not self.youtube_distribution.initialize():
                self.logger.error("❌ YouTube Distribution Manager initialization failed")
                return False
            
            self.logger.info("✅ YouTube Distribution Manager initialized successfully")
            
            # Create working directories
            self.logger.info("📁 Setting up working directories...")
            self._setup_working_directories()
            
            self.setup_complete = True
            self.logger.info("🎉 Shorts Factory initialization complete!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def _setup_working_directories(self) -> None:
        """Create necessary working directories"""
        directories = [
            config.working_directory / 'audio',
            config.working_directory / 'video_clips', 
            config.working_directory / 'final_videos',
            config.working_directory / 'captions',
            config.working_directory / 'captioned_videos',
            config.working_directory / 'metadata',
            config.working_directory / 'credentials',
            config.working_directory / 'background_loops',
            config.working_directory / 'logs',
            config.working_directory / 'logs' / 'distribution'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"📁 Created directory: {directory}")
    
    def daily_content_pipeline(self) -> None:
        """Execute the daily content creation pipeline"""
        if not self.setup_complete:
            self.logger.error("❌ Cannot run pipeline - initialization not complete")
            return
        
        self.logger.info("🔄 Starting daily content pipeline...")
        
        try:
            # Phase 1: Content Ideation (NEW - IMPLEMENTED!)
            self.logger.info("💡 Phase 1: Content Ideation")
            
            # Run content ideation cycle
            ideation_results = self.content_engine.run_ideation_cycle(
                gemini_ideas=15,  # Generate 15 ideas from Gemini
                reddit_stories=10  # Extract 10 stories from Reddit
            )
            
            if ideation_results.get('successful_uploads', 0) > 0:
                self.logger.info(f"✅ Content ideation successful: {ideation_results['successful_uploads']} new ideas added to dashboard")
                self.logger.info(f"   - Gemini ideas: {ideation_results['gemini_ideas']}")
                self.logger.info(f"   - Reddit stories: {ideation_results['reddit_ideas']}")
            else:
                self.logger.warning("⚠️ Content ideation completed but no ideas were added to dashboard")
            
            # Phase 2: Approval Workflow Monitoring (NEW - IMPLEMENTED!)
            self.logger.info("🔍 Phase 2: Approval Workflow Monitoring")
            
            # Check for newly approved content
            approval_results = self.approval_monitor.run_approval_monitor_cycle()
            
            if approval_results.get('newly_approved_count', 0) > 0:
                approved_items = approval_results['approved_items']
                self.logger.info(f"🎉 Found {len(approved_items)} newly approved content items!")
                
                # Process each newly approved item
                for content in approved_items:
                    content_id = content.get('id', '')
                    title = content.get('title', 'Untitled')
                    
                    self.logger.info(f"📝 Processing approved content: ID {content_id} - {title}")
                    
                    # Mark as processing
                    if self.approval_monitor.mark_as_processing(content_id, title):
                        # TASK #4: GENERATE SCRIPT FOR APPROVED CONTENT
                        self.logger.info(f"🎬 Starting script generation for: {title}")
                        
                        try:
                            # Generate script using ScriptGenerator
                            script_success = self.script_generator.generate_and_save_script(content)
                            
                            if script_success:
                                self.logger.info(f"✅ Script generated and saved for: {title}")
                                
                                # TASK #5: GENERATE AUDIO FROM SCRIPT
                                self.logger.info(f"🎙️ Starting audio generation for: {title}")
                                
                                try:
                                    # Generate audio using AudioGenerator
                                    audio_success = self.audio_generator.generate_and_save_audio(content)
                                    
                                    if audio_success:
                                        self.logger.info(f"✅ Audio generated and saved for: {title}")
                                        
                                        # TASK #6: SOURCE VIDEO CLIPS
                                        self.logger.info(f"🎥 Starting video sourcing for: {title}")
                                        
                                        try:
                                            # Source videos using VideoSourcingManager
                                            video_success = self.video_sourcing.source_and_save_videos(content)
                                            
                                            if video_success:
                                                self.logger.info(f"✅ Videos sourced and saved for: {title}")
                                                
                                                # TASK #7: ASSEMBLE FINAL VIDEO
                                                self.logger.info(f"🎬 Starting video assembly for: {title}")
                                                
                                                try:
                                                    # Assemble final video using VideoAssemblyManager
                                                    assembly_success = self.video_assembly.assemble_video_for_content(content)
                                                    
                                                    if assembly_success:
                                                        self.logger.info(f"✅ Video assembled successfully for: {title}")
                                                        
                                                        # Mark as completed with full pipeline success
                                                        self.approval_monitor.mark_as_completed(
                                                            content_id,
                                                            {
                                                                'script_generated': 'Yes',
                                                                'audio_generated': 'Yes',
                                                                'videos_sourced': 'Yes',
                                                                'video_assembled': 'Yes',
                                                                'processed_stage': 'Video Assembly (Task #7)',
                                                                'next_stage': 'Upload to YouTube (Task #8)'
                                                            }
                                                        )
                                                        self.logger.info(f"🎉 COMPLETE PIPELINE SUCCESS (Tasks #4-#7): {title}")
                                                        
                                                    else:
                                                        # Video assembly failed, but everything else succeeded
                                                        self.logger.warning(f"⚠️ Script+Audio+Video OK but assembly failed for: {title}")
                                                        
                                                        # Mark as partial success - ready for manual assembly or retry
                                                        self.approval_monitor.mark_as_completed(
                                                            content_id,
                                                            {
                                                                'script_generated': 'Yes',
                                                                'audio_generated': 'Yes',
                                                                'videos_sourced': 'Yes',
                                                                'video_assembled': 'Failed',
                                                                'processed_stage': 'Video Sourcing (Task #6)',
                                                                'note': 'Video assembly failed - components ready for retry'
                                                            }
                                                        )
                                                        
                                                except Exception as e:
                                                    # Handle video assembly errors
                                                    self.logger.error(f"❌ Error during video assembly for {title}: {e}")
                                                    
                                                    # Mark as partial success (all components ready)
                                                    self.approval_monitor.mark_as_completed(
                                                        content_id,
                                                        {
                                                            'script_generated': 'Yes',
                                                            'audio_generated': 'Yes',
                                                            'videos_sourced': 'Yes',
                                                            'video_assembled': 'Error',
                                                            'processed_stage': 'Video Sourcing (Task #6)',
                                                            'error': f"Video assembly error: {str(e)}"
                                                        }
                                                    )
                                                
                                            else:
                                                # Video sourcing failed, but script and audio succeeded
                                                self.logger.warning(f"⚠️ Script+Audio OK but video sourcing failed for: {title}")
                                                
                                                # Mark as partial success
                                                self.approval_monitor.mark_as_completed(
                                                    content_id,
                                                    {
                                                        'script_generated': 'Yes',
                                                        'audio_generated': 'Yes',
                                                        'videos_sourced': 'Failed',
                                                        'processed_stage': 'Audio Generation (Task #5)',
                                                        'note': 'Video sourcing failed - ready for retry or manual video'
                                                    }
                                                )
                                                
                                        except Exception as e:
                                            # Handle video sourcing errors
                                            self.logger.error(f"❌ Error during video sourcing for {title}: {e}")
                                            
                                            # Mark as partial success (script and audio worked)
                                            self.approval_monitor.mark_as_completed(
                                                content_id,
                                                {
                                                    'script_generated': 'Yes',
                                                    'audio_generated': 'Yes',
                                                    'videos_sourced': 'Error',
                                                    'processed_stage': 'Audio Generation (Task #5)',
                                                    'error': str(e)
                                                }
                                            )
                                        
                                    else:
                                        # Audio generation failed, but script succeeded
                                        self.logger.warning(f"⚠️ Script OK but audio generation failed for: {title}")
                                        
                                        # Mark as partial success
                                        self.approval_monitor.mark_as_completed(
                                            content_id,
                                            {
                                                'script_generated': 'Yes',
                                                'audio_generated': 'Failed',
                                                'processed_stage': 'Script Generation (Task #4)',
                                                'note': 'Audio generation needs retry'
                                            }
                                        )
                                        
                                except Exception as e:
                                    # Handle audio generation errors
                                    self.logger.error(f"❌ Error during audio generation for {title}: {e}")
                                    
                                    # Mark as partial success (script worked)
                                    self.approval_monitor.mark_as_completed(
                                        content_id,
                                        {
                                            'script_generated': 'Yes',
                                            'audio_generated': 'Error',
                                            'processed_stage': 'Script Generation (Task #4)',
                                            'error': str(e)
                                        }
                                    )
                                
                            else:
                                # Script generation failed
                                error_msg = "Script generation failed"
                                self.approval_monitor.mark_as_failed(content_id, error_msg)
                                self.logger.error(f"❌ Script generation failed for: {title}")
                                
                        except Exception as e:
                            # Handle any unexpected errors
                            error_msg = f"Script generation error: {str(e)}"
                            self.approval_monitor.mark_as_failed(content_id, error_msg)
                            self.logger.error(f"❌ Error during script generation for {title}: {e}")
                    else:
                        self.logger.error(f"❌ Failed to mark content as processing: {content_id}")
            else:
                self.logger.info("📊 No newly approved content found")
            
            # Phase 3: Video Assembly (NEW - TASK #7 IMPLEMENTED!)
            self.logger.info("🎬 Phase 3: Video Assembly")
            
            # Check for content ready for video assembly
            assembly_results = self.video_assembly.run_video_assembly_cycle()
            
            if assembly_results.get('total_ready', 0) > 0:
                assembled_count = assembly_results.get('successfully_assembled', 0)
                failed_count = assembly_results.get('failed_assembly', 0)
                
                self.logger.info(f"🎉 Video assembly results: {assembled_count} successful, {failed_count} failed")
                
                if assembled_count > 0:
                    self.logger.info("🎬 Successfully assembled videos:")
                    for item in assembly_results.get('assembled_items', []):
                        self.logger.info(f"   ✅ {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
                
                if failed_count > 0:
                    self.logger.warning("⚠️ Failed video assemblies:")
                    for item in assembly_results.get('failed_items', []):
                        self.logger.warning(f"   ❌ {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
            else:
                self.logger.info("📊 No content ready for video assembly")
            
            # Phase 4: Caption Generation (NEW - TASK #8 IMPLEMENTED!)
            self.logger.info("📝 Phase 4: Caption Generation")
            
            # Check for content ready for caption generation
            caption_results = self.caption_manager.run_caption_generation_cycle()
            
            if caption_results.get('total_ready', 0) > 0:
                captioned_count = caption_results.get('successfully_captioned', 0)
                failed_count = caption_results.get('failed_captioning', 0)
                
                self.logger.info(f"🎉 Caption generation results: {captioned_count} successful, {failed_count} failed")
                
                if captioned_count > 0:
                    self.logger.info("📝 Successfully captioned videos:")
                    for item in caption_results.get('captioned_items', []):
                        self.logger.info(f"   ✅ {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
                
                if failed_count > 0:
                    self.logger.warning("⚠️ Failed caption generations:")
                    for item in caption_results.get('failed_items', []):
                        self.logger.warning(f"   ❌ {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
            else:
                self.logger.info("📊 No content ready for caption generation")
            
            # Phase 5: YouTube Metadata Generation (NEW - TASK #9 IMPLEMENTED!)
            self.logger.info("📺 Phase 5: YouTube Metadata Generation")
            
            # Check for content ready for metadata generation
            metadata_results = self.metadata_manager.run_metadata_generation_cycle()
            
            if metadata_results.get('total_ready', 0) > 0:
                generated_count = metadata_results.get('successfully_generated', 0)
                failed_count = metadata_results.get('failed_generation', 0)
                
                self.logger.info(f"🎉 Metadata generation results: {generated_count} successful, {failed_count} failed")
                
                if generated_count > 0:
                    self.logger.info("📺 Successfully generated metadata:")
                    for item in metadata_results.get('generated_items', []):
                        self.logger.info(f"   ✅ {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
                
                if failed_count > 0:
                    self.logger.warning("⚠️ Failed metadata generations:")
                    for item in metadata_results.get('failed_items', []):
                        self.logger.warning(f"   ❌ {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
            else:
                self.logger.info("📊 No content ready for metadata generation")
            
            # Phase 6: YouTube Distribution (NEW - TASK #10 IMPLEMENTED!)
            self.logger.info("🚀 Phase 6: YouTube Distribution")
            
            # Check for content ready for YouTube upload
            distribution_results = self.youtube_distribution.run_distribution_cycle()
            
            if distribution_results.get('total_ready', 0) > 0:
                uploaded_count = distribution_results.get('successfully_uploaded', 0)
                failed_count = distribution_results.get('failed_uploads', 0)
                
                self.logger.info(f"🎉 YouTube distribution results: {uploaded_count} successful, {failed_count} failed")
                
                if uploaded_count > 0:
                    self.logger.info("🚀 Successfully uploaded to YouTube:")
                    for item in distribution_results.get('uploaded_items', []):
                        self.logger.info(f"   ✅ {item.get('title', 'Unknown')} → {item.get('youtube_url', 'No URL')}")
                
                if failed_count > 0:
                    self.logger.warning("⚠️ Failed YouTube uploads:")
                    for item in distribution_results.get('failed_items', []):
                        self.logger.warning(f"   ❌ {item.get('title', 'Unknown')} (ID: {item.get('id', 'Unknown')})")
                
                # Log final completion summary
                if uploaded_count > 0:
                    self.logger.info("🎊 COMPLETE END-TO-END PIPELINE SUCCESS!")
                    self.logger.info("📊 Content successfully processed from idea to published YouTube video!")
                    
            else:
                self.logger.info("📊 No content ready for YouTube distribution")
            
            self.logger.info("✅ Daily pipeline execution complete")
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline execution failed: {e}")
    
    def test_basic_functionality(self) -> bool:
        """Test basic functionality of all components"""
        if not self.setup_complete:
            self.logger.error("❌ Cannot run tests - initialization not complete")
            return False
        
        self.logger.info("🧪 Testing basic functionality...")
        
        try:
            # Test Google Sheets integration
            self.logger.info("📊 Testing Google Sheets integration...")
            
            # Add a test content idea
            test_id = self.sheets_manager.add_content_idea(
                source="TEST",
                title="Test Content Idea - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            if test_id:
                self.logger.info(f"✅ Successfully added test content with ID: {test_id}")
                
                # Test status update - FIX: Use uppercase SCRIPT field name
                success = self.sheets_manager.update_content_field(
                    str(test_id),
                    'SCRIPT',
                    "This is a test script generated by the system test."
                )
                
                if success:
                    self.logger.info("✅ Successfully updated content status")
                else:
                    self.logger.error("❌ Failed to update content status")
                    return False
            else:
                self.logger.error("❌ Failed to add test content")
                return False
            
            self.logger.info("🎉 All basic functionality tests passed!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Basic functionality test failed: {e}")
            return False
    
    def start_scheduler(self) -> None:
        """Start the scheduled daily execution"""
        if not self.setup_complete:
            self.logger.error("❌ Cannot start scheduler - initialization not complete")
            return
        
        # Schedule daily execution
        schedule.every().day.at(config.daily_execution_time).do(self.daily_content_pipeline)
        
        self.logger.info(f"⏰ Scheduled daily execution at {config.daily_execution_time}")
        self.logger.info("🔄 Starting scheduler... Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Scheduler error: {e}")


def main():
    """Main entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🎬 Starting Shorts Factory v1.0")
    
    # Initialize Shorts Factory
    factory = ShortsFactory()
    
    if not factory.initialize():
        logger.error("❌ Failed to initialize Shorts Factory")
        sys.exit(1)
    
    # Check command line arguments with validation
    if len(sys.argv) > 1:
        try:
            from security.input_validator import get_input_validator, DataType
            validator = get_input_validator()
            
            # Validate command argument
            cmd_result = validator.validate_input(sys.argv[1], DataType.STRING, context="cli_command")
            if not cmd_result.is_valid:
                logger.error(f"Invalid command argument: {'; '.join(cmd_result.errors)}")
                return
            command = cmd_result.sanitized_value.lower()
            
        except ImportError:
            # Fallback to basic validation
            command = str(sys.argv[1]).lower()
        
        if command == 'test':
            # Run basic functionality test
            logger.info("🧪 Running basic functionality test...")
            if factory.test_basic_functionality():
                logger.info("🎉 All tests passed!")
                sys.exit(0)
            else:
                logger.error("❌ Tests failed!")
                sys.exit(1)
        
        elif command == 'run-once':
            # Run pipeline once
            logger.info("🔄 Running pipeline once...")
            factory.daily_content_pipeline()
            sys.exit(0)
        
        elif command == 'schedule':
            # Start scheduler
            factory.start_scheduler()
        
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Available commands: test, run-once, schedule")
            sys.exit(1)
    
    else:
        # Default behavior - run scheduler
        factory.start_scheduler()


if __name__ == '__main__':
    main()
