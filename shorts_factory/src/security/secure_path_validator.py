"""
Secure Path Validation and Sanitization System for Shorts Factory
Addresses CV-002: Directory Traversal and Path Injection Vulnerabilities

This module provides comprehensive path security by:
- Validating all path inputs against whitelisted directories
- Detecting and blocking directory traversal attempts  
- Sanitizing path components to prevent injection attacks
- Enforcing secure file operations within approved boundaries

Author: Security Remediation Team
Date: August 31, 2025  
Security Level: CRITICAL
"""

import os
import re
from pathlib import Path, PurePath
from typing import Optional, List, Dict, Set, Union, Tuple
from dataclasses import dataclass
import logging
from contextlib import contextmanager
from datetime import datetime
import tempfile


@dataclass
class PathValidationResult:
    """Result of path validation with security details"""
    is_valid: bool
    sanitized_path: Optional[Path] = None
    violations: List[str] = None
    security_issues: List[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.security_issues is None:
            self.security_issues = []


class SecurePathValidator:
    """
    Comprehensive path validation and sanitization system
    
    Security Features:
    - Directory traversal attack detection and blocking
    - Path injection attack prevention
    - Whitelist-based path validation
    - Secure path construction utilities
    - Audit logging of all path operations
    - Path canonicalization and normalization
    
    Usage:
        validator = SecurePathValidator()
        result = validator.validate_path("/some/path", PathCategory.WORKING_DIRECTORY)
        if result.is_valid:
            safe_path = result.sanitized_path
    """
    
    # Path categories for different security levels
    class PathCategory:
        WORKING_DIRECTORY = "working_directory"
        LOG_FILES = "log_files"
        CONFIG_FILES = "config_files" 
        TEMP_FILES = "temp_files"
        VIDEO_FILES = "video_files"
        AUDIO_FILES = "audio_files"
        CACHE_FILES = "cache_files"
        OUTPUT_FILES = "output_files"
        USER_INPUT = "user_input"
    
    # Security patterns to detect and block
    DANGEROUS_PATTERNS = [
        r'\.\.',           # Directory traversal
        r'/\.\.',          # Unix directory traversal  
        r'\\\.\.',         # Windows directory traversal
        r'\.{2,}',         # Multiple dots
        r'[<>"|*?:]',      # Windows reserved characters
        r'~[/\\]',         # Home directory references
        r'\$\{.*\}',       # Variable substitution
        r'%.*%',           # Windows variable expansion
        r'`.*`',           # Command substitution
        r'\|',             # Pipe operators
        r'&',              # Command chaining
        r';',              # Command separation
        r'\n',             # Newlines
        r'\r',             # Carriage returns
    ]
    
    # Approved base directories (will be set during initialization)
    SECURE_BASE_DIRECTORIES: Set[Path] = set()
    
    def __init__(self, working_directory: Optional[Path] = None):
        """Initialize secure path validator"""
        self.logger = self._setup_secure_logging()
        
        # Set up secure base directories
        if working_directory:
            self.working_directory = working_directory.resolve()
        else:
            # Default secure working directory
            default_work_dir = Path.home() / "ShortsFactory" / "secure_workspace"
            default_work_dir.mkdir(parents=True, exist_ok=True)
            self.working_directory = default_work_dir.resolve()
        
        # Initialize approved directories
        self._initialize_secure_directories()
        
        # Compile security patterns for performance
        self.security_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]
        
        # Path operation audit log
        self.audit_log = []
        
        self.logger.info("🔒 Secure Path Validator initialized")
        self.logger.info(f"🏠 Working directory: {self.working_directory}")
        
    def _setup_secure_logging(self) -> logging.Logger:
        """Setup secure logging for path operations"""
        logger = logging.getLogger("SecurePathValidator")
        logger.setLevel(logging.INFO)
        
        # Create formatter that doesn't expose sensitive paths
        formatter = logging.Formatter(
            '%(asctime)s | PATH_SECURITY | %(levelname)s | %(message)s'
        )
        
        # Only console handler to avoid path injection in log files
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_secure_directories(self):
        """Initialize the whitelist of approved base directories"""
        self.SECURE_BASE_DIRECTORIES = {
            self.working_directory,
            self.working_directory / "audio",
            self.working_directory / "video_clips", 
            self.working_directory / "final_videos",
            self.working_directory / "captioned_videos",
            self.working_directory / "scripts",
            self.working_directory / "metadata",
            self.working_directory / "cache",
            Path(tempfile.gettempdir()) / "shorts_factory",  # Secure temp directory
        }
        
        # Create directories if they don't exist
        for directory in self.SECURE_BASE_DIRECTORIES:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                # Set restrictive permissions (owner only)
                os.chmod(directory, 0o700)
            except Exception as e:
                self.logger.error(f"❌ Failed to create secure directory {directory}: {e}")
    
    def validate_path(self, path_input: Union[str, Path], 
                     category: str = PathCategory.USER_INPUT,
                     allow_creation: bool = False) -> PathValidationResult:
        """
        Comprehensively validate and sanitize a path
        
        Args:
            path_input: The path to validate (string or Path object)
            category: Path category for appropriate security level
            allow_creation: Whether to allow creation of non-existent paths
            
        Returns:
            PathValidationResult with validation status and sanitized path
        """
        result = PathValidationResult(is_valid=False)
        
        try:
            # Convert to string for initial processing
            path_str = str(path_input).strip()
            
            # 1. DETECT DANGEROUS PATTERNS
            security_issues = self._detect_security_patterns(path_str, category)
            if security_issues:
                result.security_issues = security_issues
                self._log_security_violation(path_str, security_issues, category)
                return result
            
            # 2. SANITIZE PATH COMPONENTS  
            sanitized_str = self._sanitize_path_string(path_str)
            if not sanitized_str:
                result.violations.append("Path sanitization resulted in empty path")
                return result
            
            # 3. CREATE AND RESOLVE PATH OBJECT
            try:
                path_obj = Path(sanitized_str)
                
                # Handle relative paths by making them relative to working directory
                if not path_obj.is_absolute():
                    path_obj = self.working_directory / path_obj
                
                # Resolve to canonical absolute path
                resolved_path = path_obj.resolve()
                
            except (ValueError, OSError) as e:
                result.violations.append(f"Invalid path format: {e}")
                return result
            
            # 4. VALIDATE AGAINST APPROVED DIRECTORIES
            if not self._is_path_approved(resolved_path, category):
                result.violations.append(f"Path outside approved directories: {resolved_path}")
                self._log_security_violation(str(resolved_path), ["Path outside whitelist"], category)
                return result
            
            # 5. ADDITIONAL CATEGORY-SPECIFIC VALIDATION
            category_issues = self._validate_path_category(resolved_path, category)
            if category_issues:
                result.violations.extend(category_issues)
                return result
            
            # 6. CHECK FILE EXISTENCE (if required)
            if not allow_creation and not resolved_path.exists():
                result.violations.append(f"Path does not exist: {resolved_path}")
                return result
            
            # 7. SUCCESS - PATH IS SECURE
            result.is_valid = True
            result.sanitized_path = resolved_path
            
            self._log_path_access(str(resolved_path), category, "VALIDATED")
            return result
            
        except Exception as e:
            result.violations.append(f"Path validation error: {e}")
            self.logger.error(f"❌ Path validation failed for {path_input}: {e}")
            return result
    
    def _detect_security_patterns(self, path_str: str, category: str) -> List[str]:
        """Detect dangerous patterns in path string"""
        issues = []
        
        for i, pattern in enumerate(self.security_patterns):
            if pattern.search(path_str):
                pattern_name = self.DANGEROUS_PATTERNS[i]
                issues.append(f"Dangerous pattern detected: {pattern_name}")
        
        # Additional specific checks
        if len(path_str) > 1000:  # Prevent path length attacks
            issues.append("Path too long (>1000 chars)")
            
        if path_str.count('/') > 20 or path_str.count('\\') > 20:  # Prevent deep traversal
            issues.append("Path too deep (>20 levels)")
        
        # Check for suspicious absolute paths only in user input context  
        if category == SecurePathValidator.PathCategory.USER_INPUT:
            if path_str.strip().startswith('/') and not self._is_absolute_path_safe(path_str):
                issues.append("Suspicious absolute path from user input")
            
        return issues
    
    def _is_absolute_path_safe(self, path_str: str) -> bool:
        """Check if an absolute path is safe (not pointing to system directories)"""
        dangerous_absolute_paths = [
            '/etc/', '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/',
            '/root/', '/home/', '/var/log/', '/sys/', '/proc/',
            '/dev/', '/boot/', '/lib/', '/lib64/', '/opt/',
            'C:\\Windows\\', 'C:\\Program Files\\', 'C:\\Users\\',
            'C:\\System32\\', '/System/', '/Library/', '/Applications/'
        ]
        
        path_lower = path_str.lower()
        return not any(dangerous_prefix in path_lower for dangerous_prefix in dangerous_absolute_paths)
    
    def _sanitize_path_string(self, path_str: str) -> str:
        """Sanitize path string by removing/replacing dangerous elements"""
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', path_str)
        
        # Remove multiple consecutive dots (except single dots for relative paths)
        sanitized = re.sub(r'\.{3,}', '.', sanitized)
        
        # Remove trailing/leading whitespace and normalize separators
        sanitized = sanitized.strip()
        
        # Convert backslashes to forward slashes for consistency
        sanitized = sanitized.replace('\\', '/')
        
        # Remove duplicate slashes
        sanitized = re.sub(r'/+', '/', sanitized)
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>"|*?:]', '_', sanitized)
        
        return sanitized
    
    def _is_path_approved(self, path: Path, category: str) -> bool:
        """Check if path is within approved base directories"""
        try:
            # Check against each approved base directory
            for base_dir in self.SECURE_BASE_DIRECTORIES:
                try:
                    # Use relative_to to check if path is under base_dir
                    path.relative_to(base_dir)
                    return True  # Path is under this approved directory
                except ValueError:
                    continue  # Try next base directory
            
            # Special handling for certain categories
            if category == self.PathCategory.LOG_FILES:
                # Allow logs in system temp directory
                temp_path = Path(tempfile.gettempdir())
                try:
                    path.relative_to(temp_path)
                    return True
                except ValueError:
                    pass
            
            return False  # Path not under any approved directory
            
        except Exception as e:
            self.logger.error(f"❌ Error checking path approval: {e}")
            return False
    
    def _validate_path_category(self, path: Path, category: str) -> List[str]:
        """Perform category-specific validation"""
        issues = []
        
        if category == self.PathCategory.VIDEO_FILES:
            if path.suffix.lower() not in ['.mp4', '.avi', '.mov', '.mkv']:
                issues.append("Invalid video file extension")
                
        elif category == self.PathCategory.AUDIO_FILES:
            if path.suffix.lower() not in ['.mp3', '.wav', '.aac', '.m4a']:
                issues.append("Invalid audio file extension")
                
        elif category == self.PathCategory.LOG_FILES:
            if path.suffix.lower() not in ['.log', '.txt']:
                issues.append("Invalid log file extension")
                
        elif category == self.PathCategory.CONFIG_FILES:
            if path.suffix.lower() not in ['.json', '.yaml', '.yml', '.toml', '.ini', '.env']:
                issues.append("Invalid config file extension")
        
        # Check for reasonable filename length
        if len(path.name) > 255:
            issues.append("Filename too long (>255 chars)")
            
        # Check for valid filename characters
        if re.search(r'[<>:"|?*\x00-\x1f]', path.name):
            issues.append("Invalid characters in filename")
        
        return issues
    
    def _log_security_violation(self, path: str, violations: List[str], category: str):
        """Log security violations for audit purposes"""
        violation_summary = "; ".join(violations)
        self.logger.warning(f"🚨 PATH SECURITY VIOLATION: {violation_summary}")
        self.logger.warning(f"🔍 Category: {category}")
        
        # Add to audit log (with sanitized path for security)
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "violation_type": "path_security", 
            "category": category,
            "violations": violations,
            "path_hash": hash(path)  # Don't store actual path for security
        }
        self.audit_log.append(audit_entry)
    
    def _log_path_access(self, path: str, category: str, operation: str):
        """Log legitimate path access for audit purposes"""
        self.logger.debug(f"✅ Path {operation}: {category}")
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "category": category,
            "path_hash": hash(path)  # Don't store actual path
        }
        self.audit_log.append(audit_entry)
    
    def create_secure_path(self, relative_path: str, 
                          category: str = PathCategory.OUTPUT_FILES) -> Optional[Path]:
        """
        Create a secure path within approved directories
        
        Args:
            relative_path: Path relative to working directory
            category: Path category for validation
            
        Returns:
            Secure Path object or None if invalid
        """
        result = self.validate_path(relative_path, category, allow_creation=True)
        
        if result.is_valid:
            return result.sanitized_path
        else:
            self.logger.error(f"❌ Cannot create secure path: {result.violations}")
            return None
    
    def get_secure_temp_path(self, filename: str) -> Optional[Path]:
        """Get a secure temporary file path"""
        # Create secure temp directory if it doesn't exist
        secure_temp = Path(tempfile.gettempdir()) / "shorts_factory"
        secure_temp.mkdir(parents=True, exist_ok=True)
        os.chmod(secure_temp, 0o700)  # Owner only
        
        temp_path = secure_temp / filename
        result = self.validate_path(temp_path, self.PathCategory.TEMP_FILES, allow_creation=True)
        
        if result.is_valid:
            return result.sanitized_path
        else:
            return None
    
    @contextmanager
    def secure_file_operation(self, path: Union[str, Path], 
                             category: str = PathCategory.USER_INPUT):
        """
        Context manager for secure file operations
        
        Usage:
            with validator.secure_file_operation('/path/to/file') as safe_path:
                with open(safe_path, 'r') as f:
                    content = f.read()
        """
        result = self.validate_path(path, category)
        
        if not result.is_valid:
            raise ValueError(f"Insecure path: {result.violations}")
        
        try:
            yield result.sanitized_path
        finally:
            # Clean up or additional security checks could go here
            pass
    
    def get_audit_report(self) -> Dict[str, any]:
        """Generate security audit report"""
        return {
            "total_validations": len(self.audit_log),
            "security_violations": len([entry for entry in self.audit_log 
                                      if entry.get("violation_type") == "path_security"]),
            "approved_directories": len(self.SECURE_BASE_DIRECTORIES),
            "recent_activity": self.audit_log[-10:] if self.audit_log else []
        }


# Global secure path validator instance
_secure_path_validator = None

def get_secure_path_validator(working_directory: Optional[Path] = None) -> SecurePathValidator:
    """Get the global secure path validator instance"""
    global _secure_path_validator
    if _secure_path_validator is None:
        _secure_path_validator = SecurePathValidator(working_directory)
    return _secure_path_validator


# Convenience functions for easy migration
def validate_secure_path(path: Union[str, Path], 
                        category: str = SecurePathValidator.PathCategory.USER_INPUT) -> Optional[Path]:
    """Validate path and return secure Path object if valid"""
    validator = get_secure_path_validator()
    result = validator.validate_path(path, category)
    return result.sanitized_path if result.is_valid else None


def create_secure_working_path(relative_path: str) -> Optional[Path]:
    """Create secure path within working directory"""
    validator = get_secure_path_validator()
    return validator.create_secure_path(relative_path, SecurePathValidator.PathCategory.WORKING_DIRECTORY)
