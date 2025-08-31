"""
Robust Resource Management System for Shorts Factory
Addresses CV-004: Resource Leak Vulnerabilities

This module provides comprehensive resource management by:
- Automatic cleanup of files, processes, and handles using context managers
- Resource usage monitoring and leak detection
- Exception-safe resource handling with guaranteed cleanup
- Centralized resource tracking and management
- Memory leak prevention and detection

Author: Security Remediation Team
Date: August 31, 2025
Security Level: CRITICAL
"""

import os
import sys
import tempfile
import weakref
import threading
import logging
import wave
import psutil
from pathlib import Path
from typing import List, Dict, Optional, Any, Union, Set, Callable
from contextlib import contextmanager, ExitStack, closing
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from enum import Enum
import gc
import subprocess
import time


class ResourceType(Enum):
    """Types of resources tracked by the system"""
    FILE_HANDLE = "file_handle"
    TEMP_FILE = "temp_file"
    TEMP_DIR = "temp_directory" 
    PROCESS = "process"
    AUDIO_FILE = "audio_file"
    VIDEO_FILE = "video_file"
    NETWORK_CONNECTION = "network"
    MEMORY_BUFFER = "memory"
    THREAD = "thread"
    OTHER = "other"


@dataclass
class ResourceInfo:
    """Information about a tracked resource"""
    resource_id: str
    resource_type: ResourceType
    name: str
    path: Optional[str] = None
    size_bytes: int = 0
    created_at: datetime = None
    last_accessed: datetime = None
    process_id: int = None
    thread_id: int = None
    cleanup_registered: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_accessed is None:
            self.last_accessed = self.created_at
        if self.process_id is None:
            self.process_id = os.getpid()
        if self.thread_id is None:
            self.thread_id = threading.get_ident()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['resource_type'] = self.resource_type.value
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data


class ResourceLeakDetector:
    """Detects and reports resource leaks"""
    
    def __init__(self, check_interval: int = 300):  # 5 minutes
        self.check_interval = check_interval
        self.initial_stats = self._get_system_stats()
        self.last_check = datetime.now()
        self.leak_warnings = []
        
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource statistics"""
        try:
            process = psutil.Process()
            return {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "open_files": len(process.open_files()),
                "threads": process.num_threads(),
                "cpu_percent": process.cpu_percent(),
                "timestamp": datetime.now()
            }
        except Exception:
            return {}
    
    def check_for_leaks(self, current_resources: Dict[str, ResourceInfo]) -> List[str]:
        """Check for potential resource leaks"""
        warnings = []
        current_stats = self._get_system_stats()
        
        if not self.initial_stats or not current_stats:
            return warnings
        
        # Check memory growth
        memory_growth = current_stats["memory_mb"] - self.initial_stats["memory_mb"]
        if memory_growth > 100:  # More than 100MB growth
            warnings.append(f"Memory usage increased by {memory_growth:.1f}MB")
        
        # Check file handle growth
        if "open_files" in current_stats and "open_files" in self.initial_stats:
            file_growth = current_stats["open_files"] - self.initial_stats["open_files"]
            if file_growth > 50:  # More than 50 additional file handles
                warnings.append(f"Open file handles increased by {file_growth}")
        
        # Check for old temporary resources
        now = datetime.now()
        old_resources = [
            res for res in current_resources.values()
            if res.resource_type in [ResourceType.TEMP_FILE, ResourceType.TEMP_DIR]
            and (now - res.created_at).total_seconds() > 3600  # Older than 1 hour
        ]
        
        if old_resources:
            warnings.append(f"Found {len(old_resources)} old temporary resources")
        
        self.leak_warnings.extend(warnings)
        return warnings


class RobustResourceManager:
    """
    Comprehensive resource management system with automatic cleanup
    
    Features:
    - Context managers for all resource types
    - Automatic cleanup on exceptions and normal exit
    - Resource leak detection and monitoring
    - Centralized resource tracking
    - Exception-safe resource handling
    - Process and thread-safe operations
    
    Usage:
        with RobustResourceManager() as rm:
            with rm.managed_temp_file('.mp3') as temp_file:
                # Use temporary file safely
                pass
            # File automatically cleaned up
    """
    
    def __init__(self, enable_monitoring: bool = True):
        """Initialize resource manager"""
        self.logger = self._setup_logging()
        self.enable_monitoring = enable_monitoring
        
        # Resource tracking
        self.active_resources: Dict[str, ResourceInfo] = {}
        self.cleanup_callbacks: List[Callable] = []
        self.resource_lock = threading.RLock()
        
        # Monitoring
        if enable_monitoring:
            self.leak_detector = ResourceLeakDetector()
        else:
            self.leak_detector = None
        
        # Statistics
        self.stats = {
            "resources_created": 0,
            "resources_cleaned": 0,
            "cleanup_failures": 0,
            "memory_peak_mb": 0
        }
        
        self.logger.info("🛡️ Robust Resource Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup resource management logging"""
        logger = logging.getLogger("RobustResourceManager")
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | RESOURCE_MGR | %(levelname)s | %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def __enter__(self):
        """Enter context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with cleanup"""
        self.cleanup_all_resources()
        
        # Log any leaks detected
        if self.leak_detector:
            leaks = self.leak_detector.check_for_leaks(self.active_resources)
            if leaks:
                self.logger.warning(f"🚨 Resource leaks detected: {leaks}")
    
    def register_resource(self, resource_info: ResourceInfo) -> str:
        """Register a resource for tracking and automatic cleanup"""
        with self.resource_lock:
            self.active_resources[resource_info.resource_id] = resource_info
            self.stats["resources_created"] += 1
            
            self.logger.debug(f"📝 Registered resource: {resource_info.name} ({resource_info.resource_type.value})")
            return resource_info.resource_id
    
    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource"""
        with self.resource_lock:
            if resource_id in self.active_resources:
                resource = self.active_resources.pop(resource_id)
                self.stats["resources_cleaned"] += 1
                
                self.logger.debug(f"✅ Unregistered resource: {resource.name}")
                return True
            return False
    
    def add_cleanup_callback(self, callback: Callable):
        """Add a cleanup callback to be called on exit"""
        self.cleanup_callbacks.append(callback)
    
    @contextmanager
    def managed_temp_file(self, suffix: str = '.tmp', prefix: str = 'sf_', 
                         dir: Optional[str] = None, delete_on_exit: bool = True):
        """
        Context manager for temporary files with guaranteed cleanup
        
        Usage:
            with rm.managed_temp_file('.mp3') as temp_path:
                with open(temp_path, 'wb') as f:
                    f.write(audio_data)
                # File exists and is usable
            # File automatically deleted
        """
        temp_fd = None
        temp_path = None
        resource_id = None
        
        try:
            # Create temporary file
            temp_fd, temp_path_str = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
            temp_path = Path(temp_path_str)
            
            # Close the file descriptor immediately - we only need the path
            os.close(temp_fd)
            temp_fd = None
            
            # Register resource
            resource_info = ResourceInfo(
                resource_id=f"temp_file_{id(temp_path)}",
                resource_type=ResourceType.TEMP_FILE,
                name=temp_path.name,
                path=str(temp_path),
                size_bytes=0
            )
            
            resource_id = self.register_resource(resource_info)
            
            self.logger.debug(f"📁 Created temporary file: {temp_path}")
            
            yield temp_path
            
        except Exception as e:
            self.logger.error(f"❌ Error in managed temp file: {e}")
            raise
            
        finally:
            # Cleanup
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass
            
            if temp_path and temp_path.exists() and delete_on_exit:
                try:
                    temp_path.unlink()
                    self.logger.debug(f"🗑️ Deleted temporary file: {temp_path}")
                except OSError as e:
                    self.logger.warning(f"⚠️ Failed to delete temp file {temp_path}: {e}")
                    self.stats["cleanup_failures"] += 1
            
            if resource_id:
                self.unregister_resource(resource_id)
    
    @contextmanager
    def managed_temp_dir(self, prefix: str = 'sf_temp_', 
                        dir: Optional[str] = None, delete_on_exit: bool = True):
        """
        Context manager for temporary directories with guaranteed cleanup
        
        Usage:
            with rm.managed_temp_dir() as temp_dir:
                work_file = temp_dir / 'work.txt'
                work_file.write_text('data')
            # Directory and all contents automatically deleted
        """
        temp_dir = None
        resource_id = None
        
        try:
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix=prefix, dir=dir))
            
            # Register resource
            resource_info = ResourceInfo(
                resource_id=f"temp_dir_{id(temp_dir)}",
                resource_type=ResourceType.TEMP_DIR,
                name=temp_dir.name,
                path=str(temp_dir)
            )
            
            resource_id = self.register_resource(resource_info)
            
            self.logger.debug(f"📂 Created temporary directory: {temp_dir}")
            
            yield temp_dir
            
        except Exception as e:
            self.logger.error(f"❌ Error in managed temp directory: {e}")
            raise
            
        finally:
            # Cleanup
            if temp_dir and temp_dir.exists() and delete_on_exit:
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    self.logger.debug(f"🗑️ Deleted temporary directory: {temp_dir}")
                except OSError as e:
                    self.logger.warning(f"⚠️ Failed to delete temp dir {temp_dir}: {e}")
                    self.stats["cleanup_failures"] += 1
            
            if resource_id:
                self.unregister_resource(resource_id)
    
    @contextmanager
    def managed_file(self, file_path: Union[str, Path], mode: str = 'r', 
                    encoding: str = 'utf-8', **kwargs):
        """
        Context manager for file operations with resource tracking
        
        Usage:
            with rm.managed_file('data.txt', 'w') as f:
                f.write('content')
            # File automatically closed and tracked
        """
        file_obj = None
        resource_id = None
        file_path = Path(file_path)
        
        try:
            # Open file
            file_obj = open(file_path, mode, encoding=encoding, **kwargs)
            
            # Register resource
            resource_info = ResourceInfo(
                resource_id=f"file_{id(file_obj)}",
                resource_type=ResourceType.FILE_HANDLE,
                name=file_path.name,
                path=str(file_path)
            )
            
            resource_id = self.register_resource(resource_info)
            
            self.logger.debug(f"📄 Opened file: {file_path} (mode: {mode})")
            
            yield file_obj
            
        except Exception as e:
            self.logger.error(f"❌ Error in managed file {file_path}: {e}")
            raise
            
        finally:
            # Cleanup
            if file_obj and not file_obj.closed:
                try:
                    file_obj.close()
                    self.logger.debug(f"🔒 Closed file: {file_path}")
                except OSError as e:
                    self.logger.warning(f"⚠️ Failed to close file {file_path}: {e}")
                    self.stats["cleanup_failures"] += 1
            
            if resource_id:
                self.unregister_resource(resource_id)
    
    @contextmanager  
    def managed_wave_file(self, file_path: Union[str, Path], mode: str = 'rb'):
        """
        Context manager for wave file operations with guaranteed closure
        
        Usage:
            with rm.managed_wave_file('audio.wav', 'rb') as wf:
                frames = wf.readframes(1024)
            # Wave file automatically closed
        """
        wave_obj = None
        resource_id = None
        file_path = Path(file_path)
        
        try:
            # Open wave file
            wave_obj = wave.open(str(file_path), mode)
            
            # Register resource
            resource_info = ResourceInfo(
                resource_id=f"wave_{id(wave_obj)}",
                resource_type=ResourceType.AUDIO_FILE,
                name=file_path.name,
                path=str(file_path)
            )
            
            resource_id = self.register_resource(resource_info)
            
            self.logger.debug(f"🎵 Opened wave file: {file_path}")
            
            yield wave_obj
            
        except Exception as e:
            self.logger.error(f"❌ Error in managed wave file {file_path}: {e}")
            raise
            
        finally:
            # Cleanup
            if wave_obj:
                try:
                    wave_obj.close()
                    self.logger.debug(f"🔒 Closed wave file: {file_path}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to close wave file {file_path}: {e}")
                    self.stats["cleanup_failures"] += 1
            
            if resource_id:
                self.unregister_resource(resource_id)
    
    @contextmanager
    def managed_process(self, command_args: List[str], **popen_kwargs):
        """
        Context manager for subprocess operations with guaranteed cleanup
        
        Usage:
            with rm.managed_process(['ffmpeg', '-i', 'input.mp4']) as proc:
                stdout, stderr = proc.communicate()
            # Process automatically terminated if needed
        """
        process = None
        resource_id = None
        
        try:
            # Start process
            process = subprocess.Popen(command_args, **popen_kwargs)
            
            # Register resource
            resource_info = ResourceInfo(
                resource_id=f"process_{process.pid}",
                resource_type=ResourceType.PROCESS,
                name=f"cmd_{command_args[0]}",
                process_id=process.pid
            )
            
            resource_id = self.register_resource(resource_info)
            
            self.logger.debug(f"🚀 Started process: {command_args[0]} (PID: {process.pid})")
            
            yield process
            
        except Exception as e:
            self.logger.error(f"❌ Error in managed process: {e}")
            raise
            
        finally:
            # Cleanup
            if process:
                try:
                    # Check if process is still running
                    if process.poll() is None:
                        # Give process time to finish gracefully
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            # Force terminate if needed
                            process.terminate()
                            try:
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                process.kill()
                                process.wait()
                        
                    self.logger.debug(f"✅ Process cleanup complete: PID {process.pid}")
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to cleanup process: {e}")
                    self.stats["cleanup_failures"] += 1
            
            if resource_id:
                self.unregister_resource(resource_id)
    
    def cleanup_all_resources(self):
        """Force cleanup of all tracked resources"""
        self.logger.info("🧹 Starting comprehensive resource cleanup...")
        
        # Execute cleanup callbacks first
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"❌ Cleanup callback failed: {e}")
        
        # Cleanup tracked resources
        resources_to_cleanup = list(self.active_resources.values())
        
        for resource in resources_to_cleanup:
            try:
                self._cleanup_resource(resource)
            except Exception as e:
                self.logger.error(f"❌ Failed to cleanup {resource.name}: {e}")
                self.stats["cleanup_failures"] += 1
        
        # Force garbage collection
        gc.collect()
        
        # Final statistics
        self.logger.info(f"✅ Resource cleanup complete. Stats: {self.stats}")
    
    def _cleanup_resource(self, resource: ResourceInfo):
        """Cleanup a specific resource"""
        if resource.resource_type == ResourceType.TEMP_FILE:
            if resource.path and Path(resource.path).exists():
                Path(resource.path).unlink()
                
        elif resource.resource_type == ResourceType.TEMP_DIR:
            if resource.path and Path(resource.path).exists():
                import shutil
                shutil.rmtree(resource.path)
        
        elif resource.resource_type == ResourceType.PROCESS:
            # Find and terminate process if still running
            try:
                if resource.process_id:
                    import psutil
                    if psutil.pid_exists(resource.process_id):
                        proc = psutil.Process(resource.process_id)
                        proc.terminate()
            except Exception:
                pass
        
        self.unregister_resource(resource.resource_id)
    
    def get_resource_report(self) -> Dict[str, Any]:
        """Generate resource usage report"""
        with self.resource_lock:
            resources_by_type = {}
            total_size = 0
            
            for resource in self.active_resources.values():
                resource_type = resource.resource_type.value
                if resource_type not in resources_by_type:
                    resources_by_type[resource_type] = 0
                resources_by_type[resource_type] += 1
                total_size += resource.size_bytes
            
            # Get current system stats
            current_stats = {}
            if self.leak_detector:
                current_stats = self.leak_detector._get_system_stats()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "active_resources": len(self.active_resources),
                "resources_by_type": resources_by_type,
                "total_size_mb": total_size / 1024 / 1024,
                "statistics": self.stats,
                "system_stats": current_stats,
                "recent_leaks": self.leak_detector.leak_warnings[-10:] if self.leak_detector else []
            }


# Global resource manager instance
_global_resource_manager = None
_manager_lock = threading.Lock()

def get_resource_manager() -> RobustResourceManager:
    """Get the global resource manager instance"""
    global _global_resource_manager
    if _global_resource_manager is None:
        with _manager_lock:
            if _global_resource_manager is None:
                _global_resource_manager = RobustResourceManager()
    return _global_resource_manager


# Context managers for easy migration from unsafe patterns

@contextmanager
def safe_open(file_path: Union[str, Path], mode: str = 'r', encoding: str = 'utf-8', **kwargs):
    """Safe file opening with automatic resource management"""
    rm = get_resource_manager()
    with rm.managed_file(file_path, mode, encoding, **kwargs) as f:
        yield f


@contextmanager
def safe_temp_file(suffix: str = '.tmp', prefix: str = 'sf_', dir: Optional[str] = None):
    """Safe temporary file creation with automatic cleanup"""
    rm = get_resource_manager()
    with rm.managed_temp_file(suffix, prefix, dir) as temp_path:
        yield temp_path


@contextmanager
def safe_temp_dir(prefix: str = 'sf_temp_', dir: Optional[str] = None):
    """Safe temporary directory creation with automatic cleanup"""
    rm = get_resource_manager()
    with rm.managed_temp_dir(prefix, dir) as temp_dir:
        yield temp_dir


@contextmanager
def safe_wave_open(file_path: Union[str, Path], mode: str = 'rb'):
    """Safe wave file opening with automatic cleanup"""
    rm = get_resource_manager()
    with rm.managed_wave_file(file_path, mode) as wave_file:
        yield wave_file


@contextmanager
def safe_subprocess(command_args: List[str], **kwargs):
    """Safe subprocess execution with automatic process cleanup"""
    rm = get_resource_manager()
    with rm.managed_process(command_args, **kwargs) as process:
        yield process


# Resource cleanup utilities

def cleanup_temp_files(directory: Optional[Union[str, Path]] = None, 
                      max_age_hours: int = 24, pattern: str = 'sf_*'):
    """Clean up old temporary files"""
    if directory is None:
        directory = Path(tempfile.gettempdir())
    else:
        directory = Path(directory)
    
    if not directory.exists():
        return 0
    
    cleaned = 0
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    for temp_file in directory.glob(pattern):
        try:
            if temp_file.is_file():
                # Check file age
                file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                if file_time < cutoff_time:
                    temp_file.unlink()
                    cleaned += 1
            elif temp_file.is_dir():
                # Check directory age
                dir_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                if dir_time < cutoff_time:
                    import shutil
                    shutil.rmtree(temp_file)
                    cleaned += 1
        except OSError:
            continue
    
    return cleaned


def emergency_resource_cleanup():
    """Emergency cleanup of all resources - call on critical errors"""
    try:
        rm = get_resource_manager()
        rm.cleanup_all_resources()
        
        # Additional emergency cleanup
        temp_cleaned = cleanup_temp_files(max_age_hours=0)  # Clean all temp files
        
        # Force garbage collection
        gc.collect()
        
        logging.getLogger("RobustResourceManager").warning(
            f"🚨 Emergency resource cleanup completed. Cleaned {temp_cleaned} temp files."
        )
        
    except Exception as e:
        logging.getLogger("RobustResourceManager").critical(
            f"💥 Emergency cleanup failed: {e}"
        )
