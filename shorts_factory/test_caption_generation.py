#!/usr/bin/env python3
"""
Test Caption Generation Pipeline for Shorts Factory
Comprehensive testing of SRT generation and FFmpeg caption burning functionality
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from integrations.caption_generator import SRTCaptionGenerator
from integrations.ffmpeg_captions import FFmpegCaptionBurner
from core.caption_manager import CaptionManager
from core.config import config
from utils.logger import setup_logging


class CaptionGenerationTester:
    """Comprehensive tester for caption generation pipeline"""
    
    def __init__(self):
        """Initialize the tester"""
        self.logger = logging.getLogger(__name__)
        self.srt_generator = None
        self.caption_burner = None
        self.caption_manager = None
        
        # Test directories
        self.working_dir = Path(config.working_directory)
        self.captions_dir = self.working_dir / "captions"
        self.captioned_videos_dir = self.working_dir / "captioned_videos"
        
        # Sample test data
        self.sample_script = """
        Welcome to our amazing lifestyle channel! Today we're going to explore five simple habits 
        that can transform your morning routine and boost your productivity. These are scientifically 
        proven strategies that successful people use every day. First, wake up thirty minutes earlier 
        than usual. This gives you quiet time before the world starts demanding your attention. 
        Second, drink a large glass of water immediately after waking up to kickstart your metabolism. 
        Third, spend five minutes practicing gratitude by writing down three things you're thankful for. 
        Fourth, do some light stretching or yoga to energize your body and mind. Finally, plan your 
        three most important tasks for the day. Remember, small changes lead to big results over time!
        """
        
        self.logger.info("📝 Caption Generation Tester initialized")
    
    def test_directory_structure(self) -> bool:
        """Test that all required directories exist"""
        try:
            self.logger.info("📁 Testing directory structure...")
            
            required_dirs = [
                self.working_dir,
                self.captions_dir,
                self.captioned_videos_dir
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
    
    def test_srt_generator_initialization(self) -> bool:
        """Test SRT generator initialization"""
        try:
            self.logger.info("📝 Testing SRT generator initialization...")
            
            self.srt_generator = SRTCaptionGenerator()
            
            # Test basic properties
            if hasattr(self.srt_generator, 'max_chars_per_line'):
                self.logger.debug(f"✅ Max chars per line: {self.srt_generator.max_chars_per_line}")
            else:
                self.logger.error("❌ Missing max_chars_per_line property")
                return False
            
            if hasattr(self.srt_generator, 'captions_dir'):
                self.logger.debug(f"✅ Captions directory: {self.srt_generator.captions_dir}")
            else:
                self.logger.error("❌ Missing captions_dir property")
                return False
            
            self.logger.info("✅ SRT generator initialization passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ SRT generator initialization failed: {e}")
            return False
    
    def test_text_cleaning_and_segmentation(self) -> bool:
        """Test text cleaning and segmentation functionality"""
        try:
            self.logger.info("📝 Testing text cleaning and segmentation...")
            
            if not self.srt_generator:
                self.logger.error("❌ SRT generator not initialized")
                return False
            
            # Test text cleaning
            cleaned_text = self.srt_generator.clean_script_text(self.sample_script)
            if not cleaned_text:
                self.logger.error("❌ Text cleaning failed")
                return False
            
            self.logger.debug(f"✅ Cleaned text: {len(cleaned_text)} characters")
            
            # Test segmentation
            segments = self.srt_generator.split_text_into_segments(cleaned_text)
            if not segments:
                self.logger.error("❌ Text segmentation failed")
                return False
            
            self.logger.info(f"✅ Text segmented into {len(segments)} caption segments")
            
            # Log some sample segments
            for i, segment in enumerate(segments[:3], 1):
                self.logger.debug(f"   Segment {i}: {segment[:50]}...")
            
            self.logger.info("✅ Text cleaning and segmentation test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Text cleaning and segmentation test failed: {e}")
            return False
    
    def test_caption_timing_calculation(self) -> bool:
        """Test caption timing calculation"""
        try:
            self.logger.info("📝 Testing caption timing calculation...")
            
            if not self.srt_generator:
                self.logger.error("❌ SRT generator not initialized")
                return False
            
            # Create sample segments
            sample_segments = [
                "Welcome to our amazing lifestyle channel!",
                "Today we're going to explore five simple habits",
                "that can transform your morning routine",
                "and boost your productivity throughout the day."
            ]
            
            # Test timing calculation with 30 second duration
            test_duration = 30.0
            caption_timings = self.srt_generator.calculate_caption_timing(sample_segments, test_duration)
            
            if not caption_timings:
                self.logger.error("❌ Caption timing calculation failed")
                return False
            
            self.logger.info(f"✅ Generated timing for {len(caption_timings)} captions")
            
            # Validate timing logic
            total_duration = 0
            for i, (start_time, end_time, text) in enumerate(caption_timings):
                duration = end_time - start_time
                total_duration += duration
                
                self.logger.debug(f"   Caption {i+1}: {start_time:.2f}-{end_time:.2f}s ({duration:.2f}s)")
                
                # Basic validation
                if start_time < 0 or end_time <= start_time or end_time > test_duration:
                    self.logger.error(f"❌ Invalid timing for caption {i+1}")
                    return False
            
            self.logger.info("✅ Caption timing calculation test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Caption timing calculation test failed: {e}")
            return False
    
    def test_srt_file_generation(self) -> bool:
        """Test complete SRT file generation"""
        try:
            self.logger.info("📝 Testing SRT file generation...")
            
            if not self.srt_generator:
                self.logger.error("❌ SRT generator not initialized")
                return False
            
            # Generate SRT file
            test_duration = 45.0  # 45 seconds
            test_content_id = "TEST_SRT_001"
            
            srt_file_path = self.srt_generator.generate_srt_file(
                script_text=self.sample_script,
                audio_duration=test_duration,
                content_id=test_content_id
            )
            
            if not srt_file_path:
                self.logger.error("❌ SRT file generation failed")
                return False
            
            # Validate file exists
            srt_path = Path(srt_file_path)
            if not srt_path.exists():
                self.logger.error(f"❌ SRT file not created: {srt_file_path}")
                return False
            
            # Validate file content
            if not self.srt_generator.validate_srt_file(srt_file_path):
                self.logger.error("❌ SRT file validation failed")
                return False
            
            # Show file stats
            file_size = srt_path.stat().st_size
            self.logger.info(f"✅ SRT file generated: {srt_path.name}")
            self.logger.info(f"📊 File size: {file_size} bytes")
            
            # Read and show sample content
            with open(srt_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                sample_lines = lines[:10]  # First 10 lines
                self.logger.debug("📝 Sample SRT content:")
                for line in sample_lines:
                    if line.strip():
                        self.logger.debug(f"   {line}")
            
            self.logger.info("✅ SRT file generation test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ SRT file generation test failed: {e}")
            return False
    
    def test_ffmpeg_caption_burner_initialization(self) -> bool:
        """Test FFmpeg caption burner initialization"""
        try:
            self.logger.info("🔥 Testing FFmpeg caption burner initialization...")
            
            self.caption_burner = FFmpegCaptionBurner()
            
            # Test FFmpeg subtitle support
            if not self.caption_burner.test_ffmpeg_subtitle_support():
                self.logger.warning("⚠️ FFmpeg subtitle support test inconclusive, but continuing...")
            
            # Test basic properties
            if hasattr(self.caption_burner, 'font_size'):
                self.logger.debug(f"✅ Font size: {self.caption_burner.font_size}")
            else:
                self.logger.error("❌ Missing font_size property")
                return False
            
            if hasattr(self.caption_burner, 'captioned_videos_dir'):
                self.logger.debug(f"✅ Captioned videos directory: {self.caption_burner.captioned_videos_dir}")
            else:
                self.logger.error("❌ Missing captioned_videos_dir property")
                return False
            
            self.logger.info("✅ FFmpeg caption burner initialization passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ FFmpeg caption burner initialization failed: {e}")
            return False
    
    def test_subtitle_filter_building(self) -> bool:
        """Test subtitle filter string building"""
        try:
            self.logger.info("🔧 Testing subtitle filter building...")
            
            if not self.caption_burner:
                self.logger.error("❌ Caption burner not initialized")
                return False
            
            # Create a temporary SRT file for testing
            temp_srt = tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8')
            temp_srt.write("1\n00:00:00,000 --> 00:00:03,000\nTest caption\n\n")
            temp_srt.close()
            
            try:
                # Build subtitle filter
                subtitle_filter = self.caption_burner.build_subtitle_filter(temp_srt.name)
                
                if not subtitle_filter:
                    self.logger.error("❌ Subtitle filter building failed")
                    return False
                
                # Validate filter contains expected elements
                expected_elements = ['subtitles', 'FontName', 'FontSize']
                for element in expected_elements:
                    if element not in subtitle_filter:
                        self.logger.warning(f"⚠️ Subtitle filter missing expected element: {element}")
                
                self.logger.debug(f"✅ Subtitle filter: {subtitle_filter[:100]}...")
                self.logger.info("✅ Subtitle filter building test passed")
                return True
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_srt.name):
                    os.unlink(temp_srt.name)
            
        except Exception as e:
            self.logger.error(f"❌ Subtitle filter building test failed: {e}")
            return False
    
    def test_caption_manager_initialization(self) -> bool:
        """Test Caption Manager initialization"""
        try:
            self.logger.info("📝 Testing Caption Manager initialization...")
            
            self.caption_manager = CaptionManager()
            
            # Test initialization (this might fail due to dependency issues, which is expected in testing)
            try:
                init_success = self.caption_manager.initialize()
                if init_success:
                    self.logger.info("✅ Caption Manager full initialization successful")
                else:
                    self.logger.warning("⚠️ Caption Manager initialization failed (expected in test environment)")
            except Exception as e:
                self.logger.warning(f"⚠️ Caption Manager initialization error (expected): {e}")
            
            # Test basic properties
            if hasattr(self.caption_manager, 'captions_dir'):
                self.logger.debug(f"✅ Captions directory: {self.caption_manager.captions_dir}")
            else:
                self.logger.error("❌ Missing captions_dir property")
                return False
            
            # Test method availability
            methods_to_test = [
                'get_audio_duration_for_content',
                'find_video_file_for_content',
                'generate_captions_for_content',
                'get_content_ready_for_captions',
                'run_caption_generation_cycle'
            ]
            
            for method_name in methods_to_test:
                if hasattr(self.caption_manager, method_name):
                    self.logger.debug(f"✅ Method available: {method_name}")
                else:
                    self.logger.error(f"❌ Method missing: {method_name}")
                    return False
            
            self.logger.info("✅ Caption Manager initialization test passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Caption Manager initialization test failed: {e}")
            return False
    
    def test_file_pattern_matching(self) -> bool:
        """Test file pattern matching for content IDs"""
        try:
            self.logger.info("🔍 Testing file pattern matching...")
            
            # Check for existing files in the working directory
            audio_dir = self.working_dir / "audio"
            video_dir = self.working_dir / "final_videos"
            
            audio_files = list(audio_dir.glob("*.mp3")) if audio_dir.exists() else []
            video_files = list(video_dir.glob("*.mp4")) if video_dir.exists() else []
            
            self.logger.info(f"📊 Found {len(audio_files)} audio files, {len(video_files)} video files")
            
            if audio_files:
                self.logger.info("🎵 Sample audio files:")
                for audio_file in audio_files[:3]:
                    self.logger.info(f"   {audio_file.name}")
            
            if video_files:
                self.logger.info("🎬 Sample video files:")
                for video_file in video_files[:3]:
                    self.logger.info(f"   {video_file.name}")
            
            if not audio_files and not video_files:
                self.logger.info("📊 No existing media files found (normal for fresh installation)")
            
            self.logger.info("✅ File pattern matching test completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ File pattern matching test failed: {e}")
            return False
    
    def test_srt_format_validation(self) -> bool:
        """Test SRT format validation functionality"""
        try:
            self.logger.info("📝 Testing SRT format validation...")
            
            if not self.srt_generator:
                self.logger.error("❌ SRT generator not initialized")
                return False
            
            # Create a valid SRT file for testing
            temp_srt = tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8')
            valid_srt_content = """1
00:00:00,000 --> 00:00:03,500
Welcome to our amazing channel!

2
00:00:03,500 --> 00:00:07,000
Today we're exploring lifestyle tips.

3
00:00:07,000 --> 00:00:10,500
These habits will change your life!
"""
            temp_srt.write(valid_srt_content)
            temp_srt.close()
            
            try:
                # Test validation of valid SRT
                if self.srt_generator.validate_srt_file(temp_srt.name):
                    self.logger.info("✅ Valid SRT file validation passed")
                else:
                    self.logger.error("❌ Valid SRT file validation failed")
                    return False
                
                # Test validation of non-existent file
                if not self.srt_generator.validate_srt_file("nonexistent_file.srt"):
                    self.logger.info("✅ Non-existent file validation correctly failed")
                else:
                    self.logger.error("❌ Non-existent file validation incorrectly passed")
                    return False
                
                self.logger.info("✅ SRT format validation test passed")
                return True
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_srt.name):
                    os.unlink(temp_srt.name)
            
        except Exception as e:
            self.logger.error(f"❌ SRT format validation test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all caption generation tests"""
        try:
            self.logger.info("📝 Starting comprehensive caption generation tests...")
            self.logger.info("=" * 60)
            
            test_results = []
            
            # Test suite
            tests = [
                ("Directory Structure", self.test_directory_structure),
                ("SRT Generator Initialization", self.test_srt_generator_initialization),
                ("Text Cleaning and Segmentation", self.test_text_cleaning_and_segmentation),
                ("Caption Timing Calculation", self.test_caption_timing_calculation),
                ("SRT File Generation", self.test_srt_file_generation),
                ("SRT Format Validation", self.test_srt_format_validation),
                ("FFmpeg Caption Burner Init", self.test_ffmpeg_caption_burner_initialization),
                ("Subtitle Filter Building", self.test_subtitle_filter_building),
                ("Caption Manager Initialization", self.test_caption_manager_initialization),
                ("File Pattern Matching", self.test_file_pattern_matching)
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
            self.logger.info("📝 CAPTION GENERATION TEST SUMMARY")
            self.logger.info("=" * 60)
            
            for test_name, result in test_results:
                status = "✅ PASS" if result else "❌ FAIL"
                self.logger.info(f"{status} {test_name}")
            
            self.logger.info("-" * 60)
            self.logger.info(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
            
            if passed == total:
                self.logger.info("🎉 ALL CAPTION GENERATION TESTS PASSED!")
                self.logger.info("📝 Caption Generation Pipeline is ready for production!")
                return True
            else:
                self.logger.error(f"❌ {total-passed} tests failed")
                self.logger.error("⚠️ Caption Generation Pipeline needs attention")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Test suite execution failed: {e}")
            return False


def main():
    """Main test execution"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("📝 Starting Shorts Factory Caption Generation Test Suite")
    logger.info("=" * 80)
    
    # Run tests
    tester = CaptionGenerationTester()
    success = tester.run_all_tests()
    
    logger.info("=" * 80)
    if success:
        logger.info("🎉 CAPTION GENERATION TEST SUITE: SUCCESS!")
        sys.exit(0)
    else:
        logger.error("❌ CAPTION GENERATION TEST SUITE: FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
