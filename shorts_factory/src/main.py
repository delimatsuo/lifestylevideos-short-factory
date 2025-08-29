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
from integrations.google_sheets import GoogleSheetsManager
from utils.logger import setup_logging


class ShortsFactory:
    """Main orchestration class for Shorts Factory"""
    
    def __init__(self):
        """Initialize Shorts Factory"""
        self.logger = logging.getLogger(__name__)
        self.sheets_manager = None
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
            # Phase 1: Content Ideation (will be implemented in Task 2)
            self.logger.info("💡 Phase 1: Content Ideation - TODO")
            
            # Phase 2: Process Approved Content (will be implemented in subsequent tasks)
            self.logger.info("🎬 Phase 2: Content Processing - TODO") 
            approved_content = self.sheets_manager.get_approved_content()
            
            if approved_content:
                self.logger.info(f"Found {len(approved_content)} approved content items")
                for content in approved_content:
                    self.logger.info(f"  - ID {content['id']}: {content['title']}")
                    # TODO: Process each approved content item
                    # This will be implemented in subsequent tasks
            else:
                self.logger.info("No approved content found to process")
            
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
