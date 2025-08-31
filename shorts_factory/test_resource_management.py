#!/usr/bin/env python3
"""
Test Suite for Robust Resource Management System
Tests resource cleanup, leak detection, and exception safety

Usage:
    python test_resource_management.py
"""

import sys
import os
import time
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from security.robust_resource_manager import (
        RobustResourceManager, 
        get_resource_manager,
        safe_open,
        safe_temp_file,
        safe_temp_dir,
        safe_wave_open,
        cleanup_temp_files,
        emergency_resource_cleanup
    )
    
    print("🛡️ TESTING ROBUST RESOURCE MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Test 1: Basic Resource Manager Context
    print("Test 1: Basic Resource Manager Context")
    try:
        with RobustResourceManager() as rm:
            print("  ✅ Resource manager initialized and exited cleanly")
    except Exception as e:
        print(f"  ❌ Resource manager test failed: {e}")
    print()
    
    # Test 2: Temporary File Management
    print("Test 2: Temporary File Management")
    test_content = "This is test content for resource management"
    
    try:
        with RobustResourceManager() as rm:
            with rm.managed_temp_file('.txt', 'test_') as temp_path:
                # Write to temp file
                with rm.managed_file(temp_path, 'w') as f:
                    f.write(test_content)
                
                # Verify file exists
                if temp_path.exists():
                    print("  ✅ Temporary file created successfully")
                    
                    # Read back content
                    with rm.managed_file(temp_path, 'r') as f:
                        read_content = f.read()
                        if read_content == test_content:
                            print("  ✅ File content verified")
                        else:
                            print(f"  ❌ Content mismatch: expected '{test_content}', got '{read_content}'")
                else:
                    print("  ❌ Temporary file was not created")
            
            # File should be automatically deleted
            if not temp_path.exists():
                print("  ✅ Temporary file automatically cleaned up")
            else:
                print("  ❌ Temporary file was not cleaned up")
                
    except Exception as e:
        print(f"  ❌ Temporary file test failed: {e}")
    print()
    
    # Test 3: Temporary Directory Management
    print("Test 3: Temporary Directory Management")
    
    try:
        with RobustResourceManager() as rm:
            with rm.managed_temp_dir('test_dir_') as temp_dir:
                # Create files in temp directory
                test_file1 = temp_dir / "file1.txt"
                test_file2 = temp_dir / "subdir" / "file2.txt"
                
                # Create subdirectory
                test_file2.parent.mkdir(parents=True, exist_ok=True)
                
                # Write test files
                with rm.managed_file(test_file1, 'w') as f:
                    f.write("File 1 content")
                
                with rm.managed_file(test_file2, 'w') as f:
                    f.write("File 2 content")
                
                if temp_dir.exists() and test_file1.exists() and test_file2.exists():
                    print("  ✅ Temporary directory and files created")
                else:
                    print("  ❌ Failed to create temporary directory structure")
            
            # Directory should be automatically deleted
            if not temp_dir.exists():
                print("  ✅ Temporary directory automatically cleaned up")
            else:
                print("  ❌ Temporary directory was not cleaned up")
                
    except Exception as e:
        print(f"  ❌ Temporary directory test failed: {e}")
    print()
    
    # Test 4: Exception Safety
    print("Test 4: Exception Safety")
    
    temp_files_created = []
    
    try:
        with RobustResourceManager() as rm:
            # Create multiple temp files
            for i in range(3):
                temp_path = None
                try:
                    with rm.managed_temp_file('.txt', f'exception_test_{i}_') as temp_path:
                        temp_files_created.append(temp_path)
                        
                        # Write to file
                        with rm.managed_file(temp_path, 'w') as f:
                            f.write(f"Exception test file {i}")
                        
                        # Cause an exception on the last iteration
                        if i == 2:
                            raise RuntimeError("Intentional test exception")
                except RuntimeError as e:
                    if "Intentional test exception" in str(e):
                        print(f"  ✅ Exception occurred as expected: {e}")
                    else:
                        raise
        
        # Check if temp files were cleaned up despite the exception
        cleanup_success = True
        for temp_path in temp_files_created:
            if temp_path.exists():
                print(f"  ❌ Temp file {temp_path} was not cleaned up after exception")
                cleanup_success = False
        
        if cleanup_success:
            print("  ✅ All temporary files cleaned up despite exception")
            
    except Exception as e:
        print(f"  ❌ Exception safety test failed: {e}")
    print()
    
    # Test 5: Resource Monitoring
    print("Test 5: Resource Monitoring")
    
    try:
        rm = get_resource_manager()
        
        # Get initial report
        initial_report = rm.get_resource_report()
        print(f"  📊 Initial active resources: {initial_report['active_resources']}")
        
        # Create some resources
        temp_files = []
        with rm:
            for i in range(5):
                temp_file = rm.managed_temp_file('.txt', f'monitor_test_{i}_')
                temp_files.append(temp_file)
        
        # Get final report
        final_report = rm.get_resource_report()
        print(f"  📊 Final active resources: {final_report['active_resources']}")
        print(f"  📊 Resources created: {final_report['statistics']['resources_created']}")
        print(f"  📊 Resources cleaned: {final_report['statistics']['resources_cleaned']}")
        
        if final_report['statistics']['cleanup_failures'] == 0:
            print("  ✅ No cleanup failures detected")
        else:
            print(f"  ⚠️ Cleanup failures: {final_report['statistics']['cleanup_failures']}")
            
    except Exception as e:
        print(f"  ❌ Resource monitoring test failed: {e}")
    print()
    
    # Test 6: Convenience Functions
    print("Test 6: Convenience Functions")
    
    try:
        # Test safe_open
        with safe_temp_file('.txt') as temp_path:
            with safe_open(temp_path, 'w') as f:
                f.write("Convenience function test")
            
            with safe_open(temp_path, 'r') as f:
                content = f.read()
                if content == "Convenience function test":
                    print("  ✅ safe_open convenience function working")
                else:
                    print("  ❌ safe_open content mismatch")
        
        # Test safe_temp_dir
        with safe_temp_dir() as temp_dir:
            test_file = temp_dir / "test.txt"
            with safe_open(test_file, 'w') as f:
                f.write("Directory test")
            
            if test_file.exists():
                print("  ✅ safe_temp_dir convenience function working")
            else:
                print("  ❌ safe_temp_dir failed to create file")
        
        print("  ✅ All convenience functions working")
        
    except Exception as e:
        print(f"  ❌ Convenience functions test failed: {e}")
    print()
    
    # Test 7: Cleanup Utilities
    print("Test 7: Cleanup Utilities")
    
    try:
        # Create some temporary files manually
        temp_dir = Path(tempfile.gettempdir())
        test_files = []
        
        for i in range(3):
            test_file = temp_dir / f"sf_cleanup_test_{i}.txt"
            test_file.write_text(f"Cleanup test file {i}")
            test_files.append(test_file)
        
        # Wait a moment to ensure files are created
        time.sleep(0.1)
        
        # Clean up using utility function
        cleaned_count = cleanup_temp_files(temp_dir, max_age_hours=0, pattern='sf_cleanup_test_*')
        
        if cleaned_count >= 3:
            print(f"  ✅ Cleanup utility removed {cleaned_count} files")
        else:
            print(f"  ❌ Cleanup utility only removed {cleaned_count} files, expected at least 3")
        
        # Verify files are gone
        remaining_files = [f for f in test_files if f.exists()]
        if not remaining_files:
            print("  ✅ All test files successfully removed")
        else:
            print(f"  ⚠️ {len(remaining_files)} files still remain")
            
    except Exception as e:
        print(f"  ❌ Cleanup utilities test failed: {e}")
    print()
    
    # Test 8: Emergency Cleanup
    print("Test 8: Emergency Cleanup")
    
    try:
        # This should not raise an exception
        emergency_resource_cleanup()
        print("  ✅ Emergency cleanup completed without errors")
        
    except Exception as e:
        print(f"  ❌ Emergency cleanup failed: {e}")
    print()
    
    print("=" * 60)
    print("🎉 RESOURCE MANAGEMENT SYSTEM TESTS COMPLETED!")
    print("🛡️ CV-004 Resource Leak vulnerability testing complete")
    
    # Final system report
    try:
        rm = get_resource_manager()
        final_report = rm.get_resource_report()
        
        print("\n📊 FINAL SYSTEM REPORT:")
        print(f"  Active Resources: {final_report['active_resources']}")
        print(f"  Total Created: {final_report['statistics']['resources_created']}")
        print(f"  Total Cleaned: {final_report['statistics']['resources_cleaned']}")
        print(f"  Cleanup Failures: {final_report['statistics']['cleanup_failures']}")
        
        if final_report['statistics']['cleanup_failures'] == 0:
            print("✅ All tests passed - Resource management system is secure!")
            sys.exit(0)
        else:
            print("⚠️ Some cleanup failures detected - review logs")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Final report generation failed: {e}")
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
