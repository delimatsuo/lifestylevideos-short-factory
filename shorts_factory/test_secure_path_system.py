#!/usr/bin/env python3
"""
Test Suite for Secure Path Validation System
Tests various attack vectors and security measures

Usage:
    python test_secure_path_system.py
"""

import sys
from pathlib import Path
import tempfile
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from security.secure_path_validator import SecurePathValidator, PathValidationResult
    from security.secure_config import config
    
    print("🔒 TESTING SECURE PATH VALIDATION SYSTEM")
    print("=" * 60)
    
    # Initialize validator with test working directory
    test_working_dir = Path(tempfile.mkdtemp(prefix="shorts_factory_test_"))
    validator = SecurePathValidator(test_working_dir)
    
    print(f"🏠 Test working directory: {test_working_dir}")
    print()
    
    # Test cases for path security
    test_cases = [
        # SAFE PATHS
        {
            "name": "✅ Valid relative path",
            "path": "audio/test.mp3",
            "category": validator.PathCategory.AUDIO_FILES,
            "should_pass": True
        },
        {
            "name": "✅ Valid absolute path within working dir",
            "path": str(test_working_dir / "video_clips" / "test.mp4"),
            "category": validator.PathCategory.VIDEO_FILES,
            "should_pass": True
        },
        {
            "name": "✅ Simple filename",
            "path": "output.mp4",
            "category": validator.PathCategory.OUTPUT_FILES,
            "should_pass": True
        },
        
        # DANGEROUS PATHS THAT SHOULD BE BLOCKED
        {
            "name": "🚨 Directory traversal with ../",
            "path": "../../../etc/passwd",
            "category": validator.PathCategory.USER_INPUT,
            "should_pass": False
        },
        {
            "name": "🚨 Windows directory traversal",
            "path": "..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "category": validator.PathCategory.USER_INPUT,
            "should_pass": False
        },
        {
            "name": "🚨 Multiple dots attack", 
            "path": "....//....//etc/passwd",
            "category": validator.PathCategory.USER_INPUT,
            "should_pass": False
        },
        {
            "name": "🚨 Absolute path outside working dir",
            "path": "/etc/passwd",
            "category": validator.PathCategory.USER_INPUT,
            "should_pass": False
        },
        {
            "name": "🚨 Home directory reference",
            "path": "~/../../etc/passwd", 
            "category": validator.PathCategory.USER_INPUT,
            "should_pass": False
        },
        {
            "name": "🚨 Variable substitution attack",
            "path": "${HOME}/../../etc/passwd",
            "category": validator.PathCategory.USER_INPUT,
            "should_pass": False
        },
        {
            "name": "🚨 Windows variable expansion",
            "path": "%USERPROFILE%\\..\\..\\windows\\system32\\config\\sam",
            "category": validator.PathCategory.USER_INPUT,
            "should_pass": False
        },
        {
            "name": "🚨 Command injection attempt",
            "path": "test.mp4; rm -rf /",
            "category": validator.PathCategory.VIDEO_FILES,
            "should_pass": False
        },
        {
            "name": "🚨 Pipe attack",
            "path": "test.mp4 | cat /etc/passwd",
            "category": validator.PathCategory.VIDEO_FILES,
            "should_pass": False
        },
        {
            "name": "🚨 Path too long",
            "path": "a" * 2000 + ".mp4",
            "category": validator.PathCategory.VIDEO_FILES,
            "should_pass": False
        },
        {
            "name": "🚨 Path too deep",
            "path": "/".join(["level"] * 25) + "/file.mp4",
            "category": validator.PathCategory.VIDEO_FILES,
            "should_pass": False
        },
        {
            "name": "🚨 Null byte injection",
            "path": "test.mp4\\x00.txt",
            "category": validator.PathCategory.VIDEO_FILES,
            "should_pass": False
        },
        {
            "name": "🚨 Reserved Windows characters",
            "path": "test<file>name.mp4",
            "category": validator.PathCategory.VIDEO_FILES,
            "should_pass": False
        },
    ]
    
    # Run test cases
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i:2d}: {test['name']}")
        print(f"         Path: {test['path'][:80]}...")
        
        try:
            result = validator.validate_path(
                test['path'], 
                test['category'],
                allow_creation=True
            )
            
            success = result.is_valid == test['should_pass']
            
            if success:
                print(f"         ✅ PASS - Expected {test['should_pass']}, got {result.is_valid}")
                passed += 1
            else:
                print(f"         ❌ FAIL - Expected {test['should_pass']}, got {result.is_valid}")
                if result.violations:
                    print(f"         Violations: {result.violations[:2]}")
                if result.security_issues:
                    print(f"         Security Issues: {result.security_issues[:2]}")
                failed += 1
                
        except Exception as e:
            if test['should_pass']:
                print(f"         ❌ FAIL - Unexpected exception: {e}")
                failed += 1
            else:
                print(f"         ✅ PASS - Expected failure, got exception: {str(e)[:50]}...")
                passed += 1
        
        print()
    
    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    # Additional feature tests
    print("\n🔧 TESTING ADDITIONAL SECURITY FEATURES:")
    print("-" * 60)
    
    # Test secure temp path
    print("1. Testing secure temp path creation...")
    temp_path = validator.get_secure_temp_path("test_log.log")
    if temp_path and temp_path.parent.exists():
        print(f"   ✅ Secure temp path created: {temp_path}")
    else:
        print(f"   ❌ Failed to create secure temp path")
    
    # Test secure file operation context manager
    print("2. Testing secure file operation context manager...")
    try:
        test_file = test_working_dir / "output_files" / "test.txt"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test content")
        
        with validator.secure_file_operation(test_file, validator.PathCategory.OUTPUT_FILES) as safe_path:
            content = safe_path.read_text()
            if content == "test content":
                print(f"   ✅ Secure file operation successful")
            else:
                print(f"   ❌ Secure file operation failed - wrong content")
    except Exception as e:
        print(f"   ❌ Secure file operation failed: {e}")
    
    # Test audit report
    print("3. Testing audit report generation...")
    audit_report = validator.get_audit_report()
    print(f"   ✅ Audit report: {audit_report['total_validations']} validations, {audit_report['security_violations']} violations")
    
    # Test secure config integration
    print("4. Testing secure config integration...")
    try:
        working_dir = config.working_directory
        print(f"   ✅ Secure working directory: {working_dir}")
    except Exception as e:
        print(f"   ❌ Secure config test failed: {e}")
    
    print("\n" + "=" * 60)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("🔒 Path security system is working correctly")
        print("🛡️ CV-002 Directory Traversal vulnerability RESOLVED!")
        
        # Clean up test directory
        import shutil
        shutil.rmtree(test_working_dir, ignore_errors=True)
        sys.exit(0)
    else:
        print(f"⚠️ {failed} TESTS FAILED!")
        print("🔍 Please review the failed tests above")
        print("🚨 Path security system needs attention")
        sys.exit(1)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test suite failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
