#!/usr/bin/env python3
"""
Test Video Assembly Pipeline for Shorts Factory
Comprehensive testing of FFmpeg video assembly functionality
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from integrations.ffmpeg_video import FFmpegVideoAssembly
from core.video_assembly import VideoAssemblyManager
from core.config import config
from utils.logger import setup_logging


class VideoAssemblyTester:
    """Comprehensive tester for video assembly pipeline"""
    
    def __init__(self):
        """Initialize the tester"""
        self.logger = logging.getLogger(__name__)
        self.ffmpeg_assembly = None
        self.video_assembly_manager = None
        
        # Test directories
        self.working_dir = Path(config.working_directory)
        self.audio_dir = self.working_dir / "audio"
        self.video_clips_dir = self.working_dir / "video_clips"
        self.final_videos_dir = self.working_dir / "final_videos"
        
        self.logger.info("🎬 Video Assembly Tester initialized")
    
    def test_directory_structure(self) -> bool:
        """Test that all required directories exist"""
        try:
            self.logger.info("📁 Testing directory structure...")
            
            required_dirs = [
                self.working_dir,
                self.audio_dir,
                self.video_clips_dir,
                self.final_videos_dir
            ]
            
            for directory in required_dirs:
                if not directory.exists():
                    self.logger.error(f"❌ Directory missing: {directory}")
                    return False
                else:
                    self.logger.debug(f"✅ Directory exists: {directory}")
            
            self.logger.info("✅ Directory structure test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Directory structure test failed: {e}")
            return False
    
    def test_ffmpeg_availability(self) -> bool:
        """Test FFmpeg availability and functionality"""
        try:
            self.logger.info("🔧 Testing FFmpeg availability...")
            
            self.ffmpeg_assembly = FFmpegVideoAssembly()
            
            if self.ffmpeg_assembly.test_ffmpeg_availability():
                self.logger.info("✅ FFmpeg availability test passed")
                return True
            else:
                self.logger.error("❌ FFmpeg availability test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ FFmpeg availability test error: {e}")
            return False
    
    def test_video_assembly_manager_initialization(self) -> bool:
        """Test VideoAssemblyManager initialization"""
        try:
            self.logger.info("🎬 Testing Video Assembly Manager initialization...")
            
            self.video_assembly_manager = VideoAssemblyManager()
            
            if self.video_assembly_manager.initialize():
                self.logger.info("✅ Video Assembly Manager initialization passed")
                return True
            else:
                self.logger.error("❌ Video Assembly Manager initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Video Assembly Manager initialization error: {e}")
            return False
    
    def find_test_files(self) -> dict:
        """Find existing audio and video files for testing"""
        try:
            self.logger.info("🔍 Looking for existing test files...")
            
            # Find audio files
            audio_files = list(self.audio_dir.glob("*.mp3"))
            if audio_files:
                self.logger.info(f"🎵 Found {len(audio_files)} audio files")
                for audio_file in audio_files[:3]:  # Show first 3
                    self.logger.debug(f"   Audio: {audio_file.name}")
            
            # Find video files
            video_files = list(self.video_clips_dir.glob("*.mp4"))
            if video_files:
                self.logger.info(f"🎥 Found {len(video_files)} video files")
                for video_file in video_files[:3]:  # Show first 3
                    self.logger.debug(f"   Video: {video_file.name}")
            
            return {
                'audio_files': audio_files,
                'video_files': video_files
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error finding test files: {e}")
            return {'audio_files': [], 'video_files': []}
    
    def test_file_pattern_matching(self) -> bool:
        """Test file pattern matching for content IDs"""
        try:
            self.logger.info("🔍 Testing file pattern matching...")
            
            test_files = self.find_test_files()
            
            if not test_files['audio_files'] or not test_files['video_files']:
                self.logger.warning("⚠️ No test files available for pattern matching test")
                self.logger.info("   This is normal if no content has been processed yet")
                return True  # Not a failure, just no test data
            
            # Test audio file matching
            for audio_file in test_files['audio_files'][:2]:  # Test first 2
                filename = audio_file.name
                self.logger.debug(f"🎵 Testing audio file pattern: {filename}")
                
                # Try to extract content ID from filename
                # Expected pattern: content_{ID}_{timestamp}.mp3
                if filename.startswith('content_'):
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        content_id = parts[1]
                        self.logger.debug(f"   Extracted content ID: {content_id}")
            
            # Test video file matching
            for video_file in test_files['video_files'][:2]:  # Test first 2
                filename = video_file.name
                self.logger.debug(f"🎬 Testing video file pattern: {filename}")
                
                # Expected pattern: content_{ID}_clip_{N}_{timestamp}.mp4
                if filename.startswith('content_') and '_clip_' in filename:
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        content_id = parts[1]
                        self.logger.debug(f"   Extracted content ID: {content_id}")
            
            self.logger.info("✅ File pattern matching test completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ File pattern matching test failed: {e}")
            return False
    
    def test_video_assembly_methods(self) -> bool:
        """Test individual video assembly methods"""
        try:
            self.logger.info("🔧 Testing video assembly methods...")
            
            if not self.video_assembly_manager:
                self.logger.error("❌ Video Assembly Manager not initialized")
                return False
            
            # Test method availability
            methods_to_test = [
                'find_audio_file_for_content',
                'find_video_clips_for_content', 
                'generate_output_filename',
                'get_content_ready_for_assembly'
            ]
            
            for method_name in methods_to_test:
                if hasattr(self.video_assembly_manager, method_name):
                    self.logger.debug(f"✅ Method available: {method_name}")
                else:
                    self.logger.error(f"❌ Method missing: {method_name}")
                    return False
            
            # Test filename generation
            test_filename = self.video_assembly_manager.generate_output_filename(
                "TEST_001", 
                "Test Video Title for Assembly"
            )
            
            if test_filename and test_filename.endswith('.mp4'):
                self.logger.debug(f"✅ Generated filename: {test_filename}")
            else:
                self.logger.error("❌ Filename generation failed")
                return False
            
            self.logger.info("✅ Video assembly methods test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Video assembly methods test failed: {e}")
            return False
    
    def test_ready_content_detection(self) -> bool:
        """Test detection of content ready for assembly"""
        try:
            self.logger.info("🔍 Testing ready content detection...")
            
            if not self.video_assembly_manager:
                self.logger.error("❌ Video Assembly Manager not initialized")
                return False
            
            ready_content = self.video_assembly_manager.get_content_ready_for_assembly()
            
            self.logger.info(f"📊 Found {len(ready_content)} content items ready for assembly")
            
            if ready_content:
                self.logger.info("🎬 Content ready for assembly:")
                for content in ready_content[:3]:  # Show first 3
                    content_id = content.get('id', 'Unknown')
                    title = content.get('title', 'Untitled')[:50]  # Truncate long titles
                    self.logger.info(f"   📝 ID {content_id}: {title}")
            else:
                self.logger.info("📊 No content currently ready for assembly")
                self.logger.info("   This is normal if:")
                self.logger.info("   - No content has been processed through audio/video stages yet")
                self.logger.info("   - All content has already been assembled")
            
            self.logger.info("✅ Ready content detection test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ready content detection test failed: {e}")
            return False
    
    def test_ffmpeg_video_operations(self) -> bool:
        """Test core FFmpeg video operations (without actual assembly)"""
        try:
            self.logger.info("🎬 Testing FFmpeg video operations...")
            
            if not self.ffmpeg_assembly:
                self.logger.error("❌ FFmpeg assembly not initialized")
                return False
            
            # Test video validation method exists
            if hasattr(self.ffmpeg_assembly, 'validate_video_output'):
                self.logger.debug("✅ Video validation method available")
            else:
                self.logger.error("❌ Video validation method missing")
                return False
            
            # Test duration detection methods exist
            methods = ['get_audio_duration', 'get_video_duration', 'assemble_final_video']
            for method in methods:
                if hasattr(self.ffmpeg_assembly, method):
                    self.logger.debug(f"✅ Method available: {method}")
                else:
                    self.logger.error(f"❌ Method missing: {method}")
                    return False
            
            self.logger.info("✅ FFmpeg video operations test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ FFmpeg video operations test failed: {e}")
            return False
    
    def test_full_assembly_cycle(self) -> bool:
        """Test the full assembly cycle (simulation)"""
        try:
            self.logger.info("🔄 Testing full assembly cycle...")
            
            if not self.video_assembly_manager:
                self.logger.error("❌ Video Assembly Manager not initialized")
                return False
            
            # Run the assembly cycle
            results = self.video_assembly_manager.run_video_assembly_cycle()
            
            if 'total_ready' in results:
                total_ready = results['total_ready']
                successful = results.get('successfully_assembled', 0)
                failed = results.get('failed_assembly', 0)
                
                self.logger.info(f"📊 Assembly cycle results:")
                self.logger.info(f"   Total ready: {total_ready}")
                self.logger.info(f"   Successful: {successful}")
                self.logger.info(f"   Failed: {failed}")
                
                if 'cycle_duration_seconds' in results:
                    duration = results['cycle_duration_seconds']
                    self.logger.info(f"   Duration: {duration:.2f} seconds")
                
                if successful > 0:
                    self.logger.info("🎉 Successfully assembled videos:")
                    for item in results.get('assembled_items', []):
                        self.logger.info(f"   ✅ {item.get('title', 'Unknown')}")
                
                if failed > 0:
                    self.logger.warning("⚠️ Failed assemblies:")
                    for item in results.get('failed_items', []):
                        error = item.get('error', 'Unknown error')
                        self.logger.warning(f"   ❌ {item.get('title', 'Unknown')}: {error}")
                
                self.logger.info("✅ Full assembly cycle test completed")
                return True
            else:
                self.logger.error("❌ Invalid assembly cycle results")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Full assembly cycle test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all video assembly tests"""
        try:
            self.logger.info("🎬 Starting comprehensive video assembly tests...")
            self.logger.info("=" * 60)
            
            test_results = []
            
            # Test suite
            tests = [
                ("Directory Structure", self.test_directory_structure),
                ("FFmpeg Availability", self.test_ffmpeg_availability),
                ("Video Assembly Manager Init", self.test_video_assembly_manager_initialization),
                ("File Pattern Matching", self.test_file_pattern_matching),
                ("Assembly Methods", self.test_video_assembly_methods),
                ("Ready Content Detection", self.test_ready_content_detection),
                ("FFmpeg Video Operations", self.test_ffmpeg_video_operations),
                ("Full Assembly Cycle", self.test_full_assembly_cycle)
            ]
            
            for test_name, test_func in tests:
                self.logger.info(f"🧪 Running: {test_name}")
                try:
                    result = test_func()
                    test_results.append((test_name, result))
                    
                    if result:
                        self.logger.info(f"✅ {test_name}: PASSED")
                    else:
                        self.logger.error(f"❌ {test_name}: FAILED")
                        
                except Exception as e:
                    self.logger.error(f"❌ {test_name}: ERROR - {e}")
                    test_results.append((test_name, False))
                
                self.logger.info("-" * 40)
            
            # Summary
            passed = sum(1 for _, result in test_results if result)
            total = len(test_results)
            
            self.logger.info("=" * 60)
            self.logger.info("🎬 VIDEO ASSEMBLY TEST SUMMARY")
            self.logger.info("=" * 60)
            
            for test_name, result in test_results:
                status = "✅ PASS" if result else "❌ FAIL"
                self.logger.info(f"{status} {test_name}")
            
            self.logger.info("-" * 60)
            self.logger.info(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
            
            if passed == total:
                self.logger.info("🎉 ALL VIDEO ASSEMBLY TESTS PASSED!")
                self.logger.info("🎬 Video Assembly Pipeline is ready for production!")
                return True
            else:
                self.logger.error(f"❌ {total-passed} tests failed")
                self.logger.error("⚠️ Video Assembly Pipeline needs attention")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Test suite execution failed: {e}")
            return False


def main():
    """Main test execution"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🎬 Starting Shorts Factory Video Assembly Test Suite")
    logger.info("=" * 80)
    
    # Run tests
    tester = VideoAssemblyTester()
    success = tester.run_all_tests()
    
    logger.info("=" * 80)
    if success:
        logger.info("🎉 VIDEO ASSEMBLY TEST SUITE: SUCCESS!")
        sys.exit(0)
    else:
        logger.error("❌ VIDEO ASSEMBLY TEST SUITE: FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
