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
            config.working_directory / 'background_loops',
            config.working_directory / 'logs'
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
                                        
                                        # Mark as completed with both script and audio generation info
                                        self.approval_monitor.mark_as_completed(
                                            content_id, 
                                            {
                                                'script_generated': 'Yes',
                                                'audio_generated': 'Yes',
                                                'processed_stage': 'Audio Generation (Task #5)',
                                                'next_stage': 'Visual Content (Task #6)'
                                            }
                                        )
                                        self.logger.info(f"🎉 Content processing complete (Tasks #4 & #5): {title}")
                                        
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
            
            # Phase 3: Video Assembly (will be implemented in Task 7)  
            self.logger.info("🎥 Phase 3: Video Assembly - TODO")
            
            # Phase 4: Distribution (will be implemented in Task 10)
            self.logger.info("📤 Phase 4: Distribution - TODO")
            
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
                
                # Test status update
                success = self.sheets_manager.update_content_status(
                    str(test_id),
                    GoogleSheetsManager.Status.IN_PROGRESS,
                    script="This is a test script generated by the system test."
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
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
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
