"""
Secure Command Execution System for Shorts Factory
Addresses CV-003: Command Injection Vulnerabilities

This module provides secure command execution by:
- Replacing unsafe os.system() calls with secure subprocess usage
- Implementing command input validation and sanitization
- Using argument arrays instead of shell command strings
- Providing command whitelist/blacklist system
- Adding comprehensive command execution logging and monitoring

Author: Security Remediation Team
Date: August 31, 2025
Security Level: CRITICAL
"""

import subprocess
import shlex
import re
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import tempfile
import json


class CommandResult:
    """Represents the result of a command execution"""
    
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "",
                 execution_time: float = 0.0, command: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time = execution_time
        self.command = command
        self.success = returncode == 0
    
    def __str__(self):
        return f"CommandResult(returncode={self.returncode}, success={self.success})"


class CommandCategory(Enum):
    """Categories of allowed commands with different security levels"""
    FFMPEG = "ffmpeg"           # Video/audio processing
    PYTHON = "python"           # Python package management
    SYSTEM_UTILS = "system"     # Basic system utilities (ls, cp, mv)
    DOWNLOAD = "download"       # Download utilities (wget, curl)
    DEVELOPMENT = "development" # Development tools (git, npm)
    FORBIDDEN = "forbidden"     # Explicitly forbidden commands


@dataclass
class CommandWhitelistEntry:
    """Represents an allowed command with its restrictions"""
    command: str
    category: CommandCategory
    allowed_args: List[str] = None  # Specific allowed arguments/flags
    forbidden_args: List[str] = None  # Forbidden arguments/flags
    max_execution_time: int = 60  # Maximum execution time in seconds
    description: str = ""


class SecureCommandExecutor:
    """
    Secure command execution system with comprehensive security measures
    
    Security Features:
    - Command injection prevention through argument arrays
    - Command whitelist/blacklist system  
    - Input validation and sanitization
    - Execution time limits and resource controls
    - Comprehensive audit logging
    - Path traversal protection
    - Environment variable sanitization
    
    Usage:
        executor = SecureCommandExecutor()
        result = executor.execute_command(['ffmpeg', '-i', 'input.mp4', 'output.mp4'])
    """
    
    # Default command whitelist with security restrictions
    DEFAULT_WHITELIST = [
        # FFmpeg (highest risk - needs strict validation)
        CommandWhitelistEntry(
            command="ffmpeg",
            category=CommandCategory.FFMPEG,
            forbidden_args=["-f", "lavfi", "-i", "pipe:", "$(", "`", "&", "|", ";"],
            max_execution_time=600,  # 10 minutes
            description="Video/audio processing"
        ),
        
        # Python package management
        CommandWhitelistEntry(
            command="python",
            category=CommandCategory.PYTHON,
            allowed_args=["-m", "pip", "install", "download", "spacy", "--version", "-V", "sys"],
            forbidden_args=["exec", "eval", "-c", "subprocess"],
            max_execution_time=300,  # 5 minutes
            description="Python package management"
        ),
        CommandWhitelistEntry(
            command="python3",
            category=CommandCategory.PYTHON,
            allowed_args=["-m", "pip", "install", "download", "spacy", "--version", "-V", "sys"],
            forbidden_args=["exec", "eval", "-c", "subprocess"],
            max_execution_time=300,
            description="Python package management"
        ),
        
        # System utilities (low risk)
        CommandWhitelistEntry(
            command="ls",
            category=CommandCategory.SYSTEM_UTILS,
            max_execution_time=30,
            description="List directory contents"
        ),
        CommandWhitelistEntry(
            command="cp",
            category=CommandCategory.SYSTEM_UTILS,
            forbidden_args=["--no-preserve", "/etc", "/bin", "/usr"],
            max_execution_time=120,
            description="Copy files"
        ),
        CommandWhitelistEntry(
            command="mv",
            category=CommandCategory.SYSTEM_UTILS,
            forbidden_args=["/etc", "/bin", "/usr"],
            max_execution_time=120,
            description="Move files"
        ),
        
        # Development tools (restricted)
        CommandWhitelistEntry(
            command="node",
            category=CommandCategory.DEVELOPMENT,
            max_execution_time=180,
            description="Node.js execution"
        ),
    ]
    
    # Commands that are explicitly forbidden
    FORBIDDEN_COMMANDS = [
        "rm", "rmdir", "del", "format", "fdisk",
        "chmod", "chown", "sudo", "su", "passwd",
        "curl", "wget", "nc", "netcat", "ssh",
        "telnet", "ftp", "scp", "rsync",
        "eval", "exec", "system", "bash", "sh",
        "cmd", "powershell", "wscript", "cscript"
    ]
    
    # Dangerous patterns to detect in arguments
    DANGEROUS_PATTERNS = [
        r'\$\(',           # Command substitution $(...)
        r'`[^`]*`',        # Command substitution `...`
        r'&&|;|\|\|',      # Command chaining
        r'>\s*/etc',       # Writing to system directories
        r'rm\s+-rf\s*/',   # Dangerous rm operations
        r'/etc/passwd',    # System file access
        r'/etc/shadow',    # System file access
        r'\.\./',          # Directory traversal
        r'%[A-Z_]+%',      # Windows environment variables
        r'\$[A-Z_]+',      # Unix environment variables in dangerous contexts
    ]
    
    def __init__(self, working_directory: Optional[Path] = None):
        """Initialize secure command executor"""
        self.logger = self._setup_secure_logging()
        
        # Set working directory with validation
        if working_directory:
            self.working_directory = working_directory.resolve()
        else:
            # Default secure working directory
            self.working_directory = Path.cwd()
        
        # Initialize command whitelist
        self.command_whitelist = {entry.command: entry for entry in self.DEFAULT_WHITELIST}
        
        # Audit trail
        self.execution_log = []
        self.security_violations = []
        
        # Compile dangerous patterns for performance
        self.dangerous_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]
        
        self.logger.info("🛡️ Secure Command Executor initialized")
        self.logger.info(f"🏠 Working directory: {self.working_directory}")
        self.logger.info(f"✅ {len(self.command_whitelist)} commands whitelisted")
    
    def _setup_secure_logging(self) -> logging.Logger:
        """Setup secure logging for command execution"""
        logger = logging.getLogger("SecureCommandExecutor")
        logger.setLevel(logging.INFO)
        
        # Create formatter that logs security events
        formatter = logging.Formatter(
            '%(asctime)s | COMMAND_SECURITY | %(levelname)s | %(message)s'
        )
        
        # Console handler only (avoid log file injection)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def validate_command(self, command_args: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate command arguments against security policies
        
        Args:
            command_args: List of command arguments
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        if not command_args:
            violations.append("Empty command")
            return False, violations
        
        command_name = command_args[0]
        
        # 1. Check if command is explicitly forbidden
        if command_name in self.FORBIDDEN_COMMANDS:
            violations.append(f"Forbidden command: {command_name}")
        
        # 2. Check if command is whitelisted
        if command_name not in self.command_whitelist:
            violations.append(f"Command not whitelisted: {command_name}")
        
        # 3. Validate arguments against dangerous patterns
        full_command = " ".join(command_args)
        for pattern in self.dangerous_patterns:
            if pattern.search(full_command):
                violations.append(f"Dangerous pattern detected: {pattern.pattern}")
        
        # 4. Whitelist-specific validation
        if command_name in self.command_whitelist:
            whitelist_entry = self.command_whitelist[command_name]
            
            # Check allowed arguments
            if whitelist_entry.allowed_args:
                for arg in command_args[1:]:
                    if not any(allowed in arg for allowed in whitelist_entry.allowed_args):
                        violations.append(f"Argument not in allowed list: {arg}")
            
            # Check forbidden arguments
            if whitelist_entry.forbidden_args:
                for arg in command_args[1:]:
                    if any(forbidden in arg for forbidden in whitelist_entry.forbidden_args):
                        violations.append(f"Forbidden argument detected: {arg}")
        
        # 5. Validate file paths in arguments
        for arg in command_args:
            if self._looks_like_path(arg):
                if not self._validate_path_safety(arg):
                    violations.append(f"Unsafe path detected: {arg}")
        
        return len(violations) == 0, violations
    
    def _looks_like_path(self, arg: str) -> bool:
        """Check if argument looks like a file path"""
        return (
            "/" in arg or
            "\\" in arg or
            arg.startswith(".") or
            arg.endswith((".mp4", ".mp3", ".txt", ".log", ".json", ".srt"))
        )
    
    def _validate_path_safety(self, path_str: str) -> bool:
        """Validate that a path is safe for command execution"""
        # Use existing path validator if available
        try:
            from .secure_path_validator import get_secure_path_validator
            validator = get_secure_path_validator()
            result = validator.validate_path(path_str, "user_input")
            return result.is_valid
        except ImportError:
            # Fallback basic validation
            dangerous_paths = ["/etc/", "/bin/", "/usr/bin/", "/root/", "/home/"]
            return not any(dangerous in path_str.lower() for dangerous in dangerous_paths)
    
    def _sanitize_environment(self) -> Dict[str, str]:
        """Create a sanitized environment for command execution"""
        # Start with a minimal environment
        safe_env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": str(Path.home()),
            "USER": os.getenv("USER", "unknown"),
            "PWD": str(self.working_directory),
        }
        
        # Add necessary environment variables for specific tools
        for key in ["PYTHONPATH", "NODE_PATH", "FFMPEG_PATH"]:
            if key in os.environ:
                safe_env[key] = os.environ[key]
        
        return safe_env
    
    def execute_command(
        self,
        command_args: List[str],
        timeout: Optional[int] = None,
        capture_output: bool = True,
        cwd: Optional[Path] = None
    ) -> CommandResult:
        """
        Securely execute a command with comprehensive validation
        
        Args:
            command_args: List of command arguments (no shell strings!)
            timeout: Execution timeout in seconds
            capture_output: Whether to capture stdout/stderr
            cwd: Working directory for execution
            
        Returns:
            CommandResult with execution details
        """
        start_time = datetime.now()
        command_str = " ".join(command_args)  # For logging only
        
        try:
            # 1. VALIDATE COMMAND
            is_valid, violations = self.validate_command(command_args)
            if not is_valid:
                self._log_security_violation(command_str, violations)
                return CommandResult(
                    returncode=-1,
                    stderr=f"Command validation failed: {'; '.join(violations)}",
                    command=command_str
                )
            
            # 2. SET UP EXECUTION ENVIRONMENT
            command_name = command_args[0]
            whitelist_entry = self.command_whitelist.get(command_name)
            
            # Use whitelist timeout or provided timeout
            if timeout is None and whitelist_entry:
                timeout = whitelist_entry.max_execution_time
            
            # Sanitize working directory
            exec_cwd = cwd or self.working_directory
            if not exec_cwd.exists():
                exec_cwd.mkdir(parents=True, exist_ok=True)
            
            # 3. PREPARE SECURE ENVIRONMENT
            secure_env = self._sanitize_environment()
            
            # 4. EXECUTE COMMAND SECURELY
            self.logger.info(f"🔧 Executing: {command_name} (timeout: {timeout}s)")
            self.logger.debug(f"Command args: {command_args}")
            
            result = subprocess.run(
                command_args,  # Use argument array - NO SHELL INTERPRETATION
                cwd=exec_cwd,
                env=secure_env,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            
            # 5. CREATE RESULT
            execution_time = (datetime.now() - start_time).total_seconds()
            cmd_result = CommandResult(
                returncode=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                execution_time=execution_time,
                command=command_str
            )
            
            # 6. LOG EXECUTION
            self._log_command_execution(cmd_result, whitelist_entry)
            
            return cmd_result
            
        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.warning(f"⏰ Command timed out after {timeout}s: {command_name}")
            return CommandResult(
                returncode=-2,
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=execution_time,
                command=command_str
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ Command execution failed: {e}")
            return CommandResult(
                returncode=-3,
                stderr=f"Execution error: {e}",
                execution_time=execution_time,
                command=command_str
            )
    
    def execute_ffmpeg_command(
        self,
        args: List[str],
        timeout: int = 600,
        description: str = "FFmpeg operation"
    ) -> CommandResult:
        """
        Securely execute FFmpeg commands with additional validation
        
        Args:
            args: FFmpeg arguments (without 'ffmpeg' command)
            timeout: Execution timeout in seconds
            description: Description for logging
            
        Returns:
            CommandResult with execution details
        """
        # Prepend ffmpeg command
        full_args = ["ffmpeg"] + args
        
        # Additional FFmpeg-specific validation
        ffmpeg_violations = []
        
        # Check for dangerous FFmpeg options
        dangerous_ffmpeg_args = ["-f", "lavfi", "-i", "pipe:", "-filter_complex"]
        for arg in args:
            if any(dangerous in arg for dangerous in dangerous_ffmpeg_args):
                # Allow specific safe uses
                if not self._is_safe_ffmpeg_arg(arg, args):
                    ffmpeg_violations.append(f"Potentially dangerous FFmpeg argument: {arg}")
        
        if ffmpeg_violations:
            self._log_security_violation(" ".join(full_args), ffmpeg_violations)
            return CommandResult(
                returncode=-1,
                stderr=f"FFmpeg validation failed: {'; '.join(ffmpeg_violations)}",
                command=" ".join(full_args)
            )
        
        self.logger.info(f"🎬 FFmpeg operation: {description}")
        return self.execute_command(full_args, timeout=timeout)
    
    def _is_safe_ffmpeg_arg(self, arg: str, all_args: List[str]) -> bool:
        """Check if potentially dangerous FFmpeg argument is used safely"""
        # This would contain specific logic for safe FFmpeg usage
        # For now, implement basic checks
        
        if "-f" in arg and "lavfi" not in arg:
            return True  # Format specifier without lavfi is generally safe
        
        if "-i" in arg and "pipe:" not in arg:
            return True  # Input specifier without pipe is generally safe
        
        return False
    
    def execute_python_command(
        self,
        module_args: List[str],
        timeout: int = 300,
        python_executable: str = "python3"
    ) -> CommandResult:
        """
        Securely execute Python module commands
        
        Args:
            module_args: Python module arguments (e.g., ['-m', 'spacy', 'download', 'en_core_web_sm'])
            timeout: Execution timeout
            python_executable: Python executable to use
            
        Returns:
            CommandResult with execution details
        """
        # Construct full command
        full_args = [python_executable] + module_args
        
        # Additional Python-specific validation
        if not module_args or module_args[0] != "-m":
            return CommandResult(
                returncode=-1,
                stderr="Python execution must use -m module format for security",
                command=" ".join(full_args)
            )
        
        self.logger.info(f"🐍 Python module execution: {' '.join(module_args[1:])}")
        return self.execute_command(full_args, timeout=timeout)
    
    def _log_command_execution(self, result: CommandResult, whitelist_entry: Optional[CommandWhitelistEntry]):
        """Log command execution for audit purposes"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": result.command,
            "returncode": result.returncode,
            "success": result.success,
            "execution_time": result.execution_time,
            "category": whitelist_entry.category.value if whitelist_entry else "unknown",
            "working_directory": str(self.working_directory)
        }
        
        self.execution_log.append(log_entry)
        
        # Log success or failure
        if result.success:
            self.logger.info(f"✅ Command completed: {result.command.split()[0]} ({result.execution_time:.2f}s)")
        else:
            self.logger.warning(f"❌ Command failed: {result.command.split()[0]} (code: {result.returncode})")
            if result.stderr:
                self.logger.debug(f"Error output: {result.stderr[:200]}...")
    
    def _log_security_violation(self, command: str, violations: List[str]):
        """Log security violations for audit purposes"""
        violation_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "violations": violations,
            "working_directory": str(self.working_directory)
        }
        
        self.security_violations.append(violation_entry)
        
        self.logger.warning(f"🚨 COMMAND SECURITY VIOLATION: {command[:50]}...")
        for violation in violations:
            self.logger.warning(f"   - {violation}")
    
    def add_command_to_whitelist(self, entry: CommandWhitelistEntry):
        """Add a new command to the whitelist"""
        self.command_whitelist[entry.command] = entry
        self.logger.info(f"✅ Added command to whitelist: {entry.command} ({entry.category.value})")
    
    def remove_command_from_whitelist(self, command: str):
        """Remove a command from the whitelist"""
        if command in self.command_whitelist:
            del self.command_whitelist[command]
            self.logger.warning(f"❌ Removed command from whitelist: {command}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security audit report"""
        return {
            "total_executions": len(self.execution_log),
            "security_violations": len(self.security_violations),
            "whitelisted_commands": len(self.command_whitelist),
            "recent_violations": self.security_violations[-10:] if self.security_violations else [],
            "recent_executions": self.execution_log[-10:] if self.execution_log else [],
            "command_categories": {
                category.value: sum(1 for entry in self.command_whitelist.values() 
                                 if entry.category == category)
                for category in CommandCategory
            }
        }


# Global secure command executor instance
_secure_command_executor = None

def get_secure_command_executor(working_directory: Optional[Path] = None) -> SecureCommandExecutor:
    """Get the global secure command executor instance"""
    global _secure_command_executor
    if _secure_command_executor is None:
        _secure_command_executor = SecureCommandExecutor(working_directory)
    return _secure_command_executor


# Convenience functions for easy migration from unsafe patterns

def secure_subprocess_run(command_args: List[str], **kwargs) -> CommandResult:
    """Secure replacement for subprocess.run()"""
    executor = get_secure_command_executor()
    
    # Extract common arguments
    timeout = kwargs.get('timeout')
    capture_output = kwargs.get('capture_output', True)
    cwd = kwargs.get('cwd')
    
    return executor.execute_command(command_args, timeout=timeout, 
                                  capture_output=capture_output, cwd=Path(cwd) if cwd else None)


def secure_ffmpeg_run(ffmpeg_args: List[str], **kwargs) -> CommandResult:
    """Secure replacement for FFmpeg command execution"""
    executor = get_secure_command_executor()
    
    timeout = kwargs.get('timeout', 600)
    description = kwargs.get('description', 'FFmpeg operation')
    
    return executor.execute_ffmpeg_command(ffmpeg_args, timeout=timeout, description=description)


def secure_system_call(command_string: str) -> CommandResult:
    """
    Secure replacement for os.system() calls
    
    WARNING: This function parses shell commands into argument arrays.
    Use direct argument arrays whenever possible for maximum security.
    """
    executor = get_secure_command_executor()
    
    # Parse shell command into arguments (basic implementation)
    # In production, consider using shlex.split() with additional validation
    try:
        # Use shlex to safely parse shell command
        args = shlex.split(command_string)
        executor.logger.warning(f"⚠️ Converting shell command to argument array: {command_string[:50]}...")
        return executor.execute_command(args)
    except ValueError as e:
        return CommandResult(
            returncode=-1,
            stderr=f"Failed to parse shell command: {e}",
            command=command_string
        )


# Legacy compatibility - mark for replacement
def os_system_replacement(command: str) -> int:
    """
    DEPRECATED: Direct replacement for os.system() 
    
    This function is provided for compatibility but should be replaced
    with direct secure_subprocess_run() calls using argument arrays.
    """
    result = secure_system_call(command)
    return result.returncode
