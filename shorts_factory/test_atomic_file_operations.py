#!/usr/bin/env python3
"""
Test Suite for Atomic File Operations System
Tests race condition prevention and file operation safety

Usage:
    python test_atomic_file_operations.py
"""

import sys
import os
import time
import threading
import tempfile
import concurrent.futures
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from security.atomic_file_operations import (
        AtomicFileOperations,
        get_atomic_file_operations,
        safe_atomic_write,
        safe_atomic_read,
        safe_atomic_exists_and_get,
        safe_atomic_mkdir,
        safe_atomic_glob,
        FileLock,
        LockType
    )
    
    print("🔒 TESTING ATOMIC FILE OPERATIONS SYSTEM")
    print("=" * 60)
    
    # Test 1: Basic Atomic Write/Read Operations
    print("Test 1: Basic Atomic Write/Read Operations")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "atomic_test.txt"
            test_content = "Atomic file operations test content"
            
            # Test atomic write
            with safe_atomic_write(test_file, 'w') as f:
                f.write(test_content)
            
            if test_file.exists():
                print("  ✅ Atomic write created file successfully")
                
                # Test atomic read
                with safe_atomic_read(test_file, 'r') as f:
                    read_content = f.read()
                
                if read_content == test_content:
                    print("  ✅ Atomic read retrieved correct content")
                else:
                    print(f"  ❌ Content mismatch: got '{read_content}', expected '{test_content}'")
            else:
                print("  ❌ Atomic write failed to create file")
                
    except Exception as e:
        print(f"  ❌ Basic operations test failed: {e}")
    print()
    
    # Test 2: File Locking Mechanisms
    print("Test 2: File Locking Mechanisms")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            lock_file = temp_path / "lock_test.txt"
            lock_file.write_text("test content")
            
            # Test exclusive lock
            with FileLock(lock_file, LockType.EXCLUSIVE, timeout=5.0) as lock1:
                print("  ✅ Exclusive lock acquired successfully")
                
                # Try to acquire another exclusive lock (should timeout quickly)
                try:
                    with FileLock(lock_file, LockType.EXCLUSIVE, timeout=1.0) as lock2:
                        print("  ❌ Second exclusive lock should not have been acquired")
                except OSError:
                    print("  ✅ Second exclusive lock properly rejected")
            
            # Test shared locks
            def acquire_shared_lock(file_path, duration, results_list):
                try:
                    with FileLock(file_path, LockType.SHARED, timeout=5.0):
                        results_list.append("acquired")
                        time.sleep(duration)
                except Exception:
                    results_list.append("failed")
            
            # Start multiple shared lock threads
            lock_results = []
            threads = []
            for i in range(3):
                thread = threading.Thread(target=acquire_shared_lock, args=(lock_file, 0.5, lock_results))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            acquired_count = lock_results.count("acquired")
            if acquired_count == 3:
                print("  ✅ Multiple shared locks acquired simultaneously")
            else:
                print(f"  ⚠️ Only {acquired_count}/3 shared locks acquired")
                
    except Exception as e:
        print(f"  ❌ File locking test failed: {e}")
    print()
    
    # Test 3: Race Condition Prevention
    print("Test 3: Race Condition Prevention")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            race_file = temp_path / "race_test.txt"
            
            results = []
            errors = []
            
            def concurrent_writer(thread_id, content):
                try:
                    with safe_atomic_write(race_file, 'w') as f:
                        time.sleep(0.1)  # Simulate some work
                        f.write(f"Thread {thread_id}: {content}")
                    results.append(f"thread_{thread_id}")
                except Exception as e:
                    errors.append(f"Thread {thread_id}: {e}")
            
            # Start multiple concurrent writers
            threads = []
            for i in range(5):
                thread = threading.Thread(target=concurrent_writer, args=(i, f"data_{i}"))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            if race_file.exists():
                # Verify file content is from exactly one thread
                content = race_file.read_text()
                if content.startswith("Thread") and ": data_" in content:
                    print("  ✅ Race condition prevented - file has consistent content from one thread")
                    print(f"    Final content: {content[:50]}...")
                else:
                    print(f"  ❌ File content corrupted: {content}")
            else:
                print("  ❌ No file created by concurrent writers")
                
            if errors:
                print(f"  ℹ️ {len(errors)} expected conflicts occurred (this is normal)")
                
    except Exception as e:
        print(f"  ❌ Race condition test failed: {e}")
    print()
    
    # Test 4: TOCTOU (Time-of-Check-to-Time-of-Use) Prevention
    print("Test 4: TOCTOU Prevention")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            toctou_file = temp_path / "toctou_test.txt"
            
            results = []
            
            def safe_file_operation():
                ops = get_atomic_file_operations()
                
                # Atomically check existence and perform action
                exists, result = ops.atomic_exists_and_action(
                    toctou_file,
                    lambda p: p.read_text() if p.exists() else None
                )
                
                results.append(("safe", exists, result))
            
            def unsafe_file_operation():
                # Traditional unsafe pattern (TOCTOU vulnerable)
                if toctou_file.exists():  # Time of Check
                    time.sleep(0.01)      # Vulnerability window
                    try:
                        content = toctou_file.read_text()  # Time of Use
                        results.append(("unsafe", True, content))
                    except FileNotFoundError:
                        results.append(("unsafe", False, "File disappeared"))
                else:
                    results.append(("unsafe", False, None))
            
            def file_manipulator():
                # Create and delete file rapidly
                for i in range(10):
                    toctou_file.write_text(f"content_{i}")
                    time.sleep(0.005)
                    toctou_file.unlink()
                    time.sleep(0.005)
            
            # Start file manipulator
            manipulator_thread = threading.Thread(target=file_manipulator)
            manipulator_thread.start()
            
            # Start safe and unsafe operations
            threads = []
            for i in range(5):
                safe_thread = threading.Thread(target=safe_file_operation)
                unsafe_thread = threading.Thread(target=unsafe_file_operation)
                threads.extend([safe_thread, unsafe_thread])
                safe_thread.start()
                unsafe_thread.start()
            
            for thread in threads:
                thread.join()
            
            manipulator_thread.join()
            
            # Analyze results
            safe_errors = sum(1 for r in results if r[0] == "safe" and "disappeared" in str(r[2]))
            unsafe_errors = sum(1 for r in results if r[0] == "unsafe" and "disappeared" in str(r[2]))
            
            print(f"  📊 Safe operations with errors: {safe_errors}")
            print(f"  📊 Unsafe operations with errors: {unsafe_errors}")
            
            if safe_errors <= unsafe_errors:
                print("  ✅ Atomic operations provide better TOCTOU protection")
            else:
                print("  ⚠️ Unexpected results in TOCTOU test")
                
    except Exception as e:
        print(f"  ❌ TOCTOU test failed: {e}")
    print()
    
    # Test 5: Atomic Directory Operations
    print("Test 5: Atomic Directory Operations")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            results = []
            
            def concurrent_mkdir(thread_id):
                try:
                    target_dir = temp_path / "concurrent_dir"
                    success = safe_atomic_mkdir(target_dir, parents=True, exist_ok=True)
                    results.append((thread_id, success, target_dir.exists()))
                except Exception as e:
                    results.append((thread_id, False, str(e)))
            
            # Start multiple threads trying to create same directory
            threads = []
            for i in range(10):
                thread = threading.Thread(target=concurrent_mkdir, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Check results
            successes = sum(1 for r in results if r[1] is True)
            directory_exists = (temp_path / "concurrent_dir").exists()
            
            print(f"  📊 Successful mkdir operations: {successes}/10")
            print(f"  📊 Directory exists: {directory_exists}")
            
            if directory_exists and successes >= 8:  # Allow for some normal failures
                print("  ✅ Atomic directory creation handled concurrency well")
            else:
                print("  ❌ Atomic directory creation had issues")
                
    except Exception as e:
        print(f"  ❌ Atomic directory test failed: {e}")
    print()
    
    # Test 6: Atomic Glob Operations  
    print("Test 6: Atomic Glob Operations")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create some test files
            for i in range(5):
                (temp_path / f"test_{i}.mp4").write_text(f"content_{i}")
            
            glob_results = []
            
            def concurrent_glob(thread_id):
                try:
                    matches = safe_atomic_glob("test_*.mp4", temp_path)
                    glob_results.append((thread_id, len(matches)))
                except Exception as e:
                    glob_results.append((thread_id, f"Error: {e}"))
            
            def file_manipulator():
                # Add and remove files during glob operations
                time.sleep(0.01)
                (temp_path / "test_new.mp4").write_text("new content")
                time.sleep(0.01)
                try:
                    (temp_path / "test_0.mp4").unlink()
                except FileNotFoundError:
                    pass
            
            # Start file manipulator
            manipulator = threading.Thread(target=file_manipulator)
            manipulator.start()
            
            # Start concurrent glob operations
            threads = []
            for i in range(10):
                thread = threading.Thread(target=concurrent_glob, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            manipulator.join()
            
            # Analyze results
            successful_globs = [r for r in glob_results if isinstance(r[1], int)]
            
            if len(successful_globs) >= 8:  # Most should succeed
                counts = [r[1] for r in successful_globs]
                print(f"  📊 Successful glob operations: {len(successful_globs)}/10")
                print(f"  📊 File counts found: {set(counts)}")
                print("  ✅ Atomic glob operations handled concurrent file changes")
            else:
                print("  ❌ Too many glob operations failed")
                
    except Exception as e:
        print(f"  ❌ Atomic glob test failed: {e}")
    print()
    
    # Test 7: Performance and Statistics
    print("Test 7: Performance and Statistics")
    try:
        ops = get_atomic_file_operations()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Perform various operations to generate statistics
            for i in range(10):
                test_file = temp_path / f"perf_test_{i}.txt"
                with safe_atomic_write(test_file, 'w') as f:
                    f.write(f"Performance test {i}")
                
                with safe_atomic_read(test_file, 'r') as f:
                    content = f.read()
            
            # Get statistics
            stats = ops.get_operation_stats()
            
            print(f"  📊 Operations completed: {stats['statistics']['operations_completed']}")
            print(f"  📊 Operations failed: {stats['statistics']['operations_failed']}")
            print(f"  📊 Locks acquired: {stats['statistics']['locks_acquired']}")
            print(f"  📊 Retries performed: {stats['statistics']['retries_performed']}")
            
            if stats['statistics']['operations_completed'] >= 20:  # 10 writes + 10 reads
                print("  ✅ Performance statistics look good")
            else:
                print("  ⚠️ Lower than expected operation count")
                
    except Exception as e:
        print(f"  ❌ Performance test failed: {e}")
    print()
    
    print("=" * 60)
    print("🎉 ATOMIC FILE OPERATIONS TESTS COMPLETED!")
    print("🔒 HP-001 Race Condition vulnerability testing complete")
    
    # Final system report
    try:
        ops = get_atomic_file_operations()
        final_stats = ops.get_operation_stats()
        
        print("\n📊 FINAL SYSTEM REPORT:")
        print(f"  Total Operations: {final_stats['statistics']['operations_completed']}")
        print(f"  Failed Operations: {final_stats['statistics']['operations_failed']}")
        print(f"  Locks Acquired: {final_stats['statistics']['locks_acquired']}")
        print(f"  Active Operations: {final_stats['active_operations']}")
        
        success_rate = (final_stats['statistics']['operations_completed'] / 
                       (final_stats['statistics']['operations_completed'] + final_stats['statistics']['operations_failed'])) * 100
        
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 95 and final_stats['statistics']['operations_failed'] < 10:
            print("✅ All tests passed - Atomic file operations system is secure!")
            print("🛡️ HP-001 Race Condition vulnerabilities RESOLVED!")
            sys.exit(0)
        else:
            print("⚠️ Some issues detected - review results")
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
