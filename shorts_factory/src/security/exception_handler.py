"""
Centralized Exception Handling System for Shorts Factory
Addresses HP-003: Exception Handling Vulnerabilities

This module provides comprehensive exception handling to replace bare except clauses by:
- Centralized error classification and handling patterns
- Comprehensive error logging with contextual information
- Error escalation procedures based on severity levels
- Recovery mechanisms and fallback strategies
- Security-aware exception handling to prevent information leakage
- Integration with monitoring and alerting systems

Author: Security Remediation Team
Date: August 31, 2025
Security Level: CRITICAL
"""

import os
import sys
import logging
import traceback
import threading
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Union, List, Type, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from contextlib import contextmanager
import functools


class ErrorSeverity(Enum):
    """Error severity levels for proper escalation"""
    LOW = "low"                    # Minor issues, continue operation
    MEDIUM = "medium"              # Significant issues, retry with fallback
    HIGH = "high"                  # Critical issues, requires intervention
    CRITICAL = "critical"          # System-threatening, immediate escalation


class ErrorCategory(Enum):
    """Categories of errors for proper handling"""
    NETWORK = "network"            # Network-related errors
    FILE_SYSTEM = "file_system"    # File/directory operations
    API = "api"                    # External API failures
    AUTHENTICATION = "auth"        # Authentication/authorization issues
    VALIDATION = "validation"      # Data validation errors
    RESOURCE = "resource"          # Resource allocation/management
    PROCESSING = "processing"      # Data processing errors
    SYSTEM = "system"              # System-level errors
    SECURITY = "security"          # Security-related errors
    UNKNOWN = "unknown"            # Unclassified errors


class ErrorAction(Enum):
    """Actions to take when handling errors"""
    CONTINUE = "continue"          # Continue operation
    RETRY = "retry"               # Retry the operation
    FALLBACK = "fallback"         # Use fallback mechanism
    ESCALATE = "escalate"         # Escalate to higher level
    ABORT = "abort"               # Abort current operation
    TERMINATE = "terminate"       # Terminate application


@dataclass
class ExceptionContext:
    """Context information for exception handling"""
    operation_name: str
    component: str
    user_data: Optional[Dict] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_info: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return asdict(self)


@dataclass
class ErrorHandlingRule:
    """Rule for handling specific exception types"""
    exception_types: List[Type[Exception]]
    severity: ErrorSeverity
    category: ErrorCategory
    action: ErrorAction
    max_retries: int = 0
    retry_delay: float = 1.0
    fallback_handler: Optional[Callable] = None
    custom_message: Optional[str] = None
    escalate_after_retries: bool = True
    
    def matches(self, exception: Exception) -> bool:
        """Check if this rule matches the given exception"""
        return any(isinstance(exception, exc_type) for exc_type in self.exception_types)


class SecurityAwareFormatter(logging.Formatter):
    """
    Logging formatter that sanitizes sensitive information
    """
    
    SENSITIVE_PATTERNS = [
        r'api[_-]?key["\s]*[:=]["\s]*([^"\s,}]+)',
        r'password["\s]*[:=]["\s]*([^"\s,}]+)',
        r'token["\s]*[:=]["\s]*([^"\s,}]+)',
        r'secret["\s]*[:=]["\s]*([^"\s,}]+)',
        r'authorization["\s]*[:=]["\s]*([^"\s,}]+)',
    ]
    
    def format(self, record):
        """Format log record while sanitizing sensitive data"""
        message = super().format(record)
        
        # Sanitize sensitive information
        import re
        for pattern in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, r'***REDACTED***', message, flags=re.IGNORECASE)
        
        return message


class CentralizedExceptionHandler:
    """
    Centralized exception handling system with comprehensive error management
    
    Features:
    - Rule-based exception handling with severity classification
    - Comprehensive error logging with contextual information
    - Error escalation procedures based on severity levels
    - Recovery mechanisms and fallback strategies
    - Security-aware logging that sanitizes sensitive data
    - Integration with monitoring and alerting systems
    
    Usage:
        handler = get_exception_handler()
        with handler.handle_operation("api_call", "pexels_integration"):
            # Your operation code here
            pass
    """
    
    def __init__(self, log_file: Optional[Path] = None):
        """Initialize the centralized exception handler"""
        self.logger = self._setup_logging(log_file)
        
        # Error handling rules
        self.rules: List[ErrorHandlingRule] = self._setup_default_rules()
        self.custom_handlers: Dict[str, Callable] = {}
        
        # Statistics and monitoring
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "errors_by_component": {},
            "recovery_success_rate": 0.0,
            "escalations": 0
        }
        
        # Thread safety
        self.stats_lock = threading.RLock()
        self.error_history: List[Dict] = []
        self.max_history_size = 1000
        
        self.logger.info("🛡️ Centralized Exception Handler initialized")
    
    def _setup_logging(self, log_file: Optional[Path] = None) -> logging.Logger:
        """Setup security-aware logging for exception handling"""
        logger = logging.getLogger("ExceptionHandler")
        logger.setLevel(logging.INFO)
        
        # Create formatter that sanitizes sensitive data
        formatter = SecurityAwareFormatter(
            '%(asctime)s | EXCEPTION_HANDLER | %(levelname)s | %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.error(f"Failed to setup file logging: {e}")
        
        return logger
    
    def _setup_default_rules(self) -> List[ErrorHandlingRule]:
        """Setup default exception handling rules"""
        rules = [
            # Network-related errors
            ErrorHandlingRule(
                exception_types=[ConnectionError, TimeoutError, OSError],
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.NETWORK,
                action=ErrorAction.RETRY,
                max_retries=3,
                retry_delay=2.0,
                custom_message="Network connectivity issue detected"
            ),
            
            # File system errors
            ErrorHandlingRule(
                exception_types=[FileNotFoundError, PermissionError],
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.FILE_SYSTEM,
                action=ErrorAction.ESCALATE,
                custom_message="File system access error"
            ),
            
            # API errors
            ErrorHandlingRule(
                exception_types=[ValueError, KeyError, TypeError],
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.API,
                action=ErrorAction.FALLBACK,
                max_retries=1,
                custom_message="API data processing error"
            ),
            
            # Resource errors
            ErrorHandlingRule(
                exception_types=[MemoryError, ResourceWarning],
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.RESOURCE,
                action=ErrorAction.ESCALATE,
                custom_message="Resource allocation error"
            ),
            
            # Security errors (SecurityError may not exist in all Python versions)
            ErrorHandlingRule(
                exception_types=[PermissionError],
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.SECURITY,
                action=ErrorAction.ESCALATE,
                custom_message="Security violation detected"
            ),
            
            # Import errors (development/deployment issues)
            ErrorHandlingRule(
                exception_types=[ImportError, ModuleNotFoundError],
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SYSTEM,
                action=ErrorAction.FALLBACK,
                custom_message="Module dependency error"
            ),
        ]
        
        return rules
    
    def add_rule(self, rule: ErrorHandlingRule):
        """Add custom exception handling rule"""
        self.rules.insert(0, rule)  # Custom rules have priority
        self.logger.info(f"Added custom exception handling rule for {rule.exception_types}")
    
    def add_custom_handler(self, name: str, handler: Callable):
        """Add custom exception handler function"""
        self.custom_handlers[name] = handler
        self.logger.info(f"Added custom exception handler: {name}")
    
    def find_matching_rule(self, exception: Exception) -> Optional[ErrorHandlingRule]:
        """Find the first rule that matches the given exception"""
        for rule in self.rules:
            if rule.matches(exception):
                return rule
        return None
    
    def _record_error(self, exception: Exception, context: ExceptionContext, 
                     rule: Optional[ErrorHandlingRule] = None):
        """Record error in statistics and history"""
        with self.stats_lock:
            self.error_stats["total_errors"] += 1
            
            if rule:
                # Update category stats
                category = rule.category.value
                self.error_stats["errors_by_category"][category] = \
                    self.error_stats["errors_by_category"].get(category, 0) + 1
                
                # Update severity stats
                severity = rule.severity.value
                self.error_stats["errors_by_severity"][severity] = \
                    self.error_stats["errors_by_severity"].get(severity, 0) + 1
            
            # Update component stats
            component = context.component
            self.error_stats["errors_by_component"][component] = \
                self.error_stats["errors_by_component"].get(component, 0) + 1
            
            # Add to history
            error_record = {
                "timestamp": datetime.now().isoformat(),
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "context": context.to_dict(),
                "rule_applied": rule.category.value if rule else "unknown",
                "severity": rule.severity.value if rule else "unknown"
            }
            
            self.error_history.append(error_record)
            
            # Trim history if too large
            if len(self.error_history) > self.max_history_size:
                self.error_history = self.error_history[-self.max_history_size//2:]
    
    def _log_exception(self, exception: Exception, context: ExceptionContext, 
                      rule: Optional[ErrorHandlingRule] = None):
        """Log exception with comprehensive contextual information"""
        severity = rule.severity.value if rule else "unknown"
        category = rule.category.value if rule else "unknown"
        
        # Determine log level based on severity
        if rule and rule.severity == ErrorSeverity.CRITICAL:
            log_level = logging.CRITICAL
        elif rule and rule.severity == ErrorSeverity.HIGH:
            log_level = logging.ERROR
        elif rule and rule.severity == ErrorSeverity.MEDIUM:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        # Create comprehensive log message
        log_data = {
            "operation": context.operation_name,
            "component": context.component,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "severity": severity,
            "category": category,
            "context": context.to_dict()
        }
        
        # Include custom message if available
        if rule and rule.custom_message:
            log_data["custom_message"] = rule.custom_message
        
        # Include traceback for high severity errors
        if rule and rule.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            log_data["traceback"] = traceback.format_exc()
        
        self.logger.log(log_level, json.dumps(log_data, indent=2))
    
    def _execute_action(self, exception: Exception, context: ExceptionContext,
                       rule: ErrorHandlingRule, operation_func: Callable, 
                       *args, **kwargs) -> Any:
        """Execute the action specified by the rule"""
        if rule.action == ErrorAction.RETRY:
            return self._retry_operation(exception, context, rule, operation_func, *args, **kwargs)
        elif rule.action == ErrorAction.FALLBACK:
            return self._execute_fallback(exception, context, rule, operation_func, *args, **kwargs)
        elif rule.action == ErrorAction.ESCALATE:
            self._escalate_error(exception, context, rule)
            raise exception
        elif rule.action == ErrorAction.ABORT:
            self.logger.warning(f"Aborting operation {context.operation_name} due to {type(exception).__name__}")
            return None
        elif rule.action == ErrorAction.TERMINATE:
            self.logger.critical(f"Terminating application due to critical error in {context.component}")
            sys.exit(1)
        else:  # CONTINUE
            self.logger.info(f"Continuing operation {context.operation_name} after {type(exception).__name__}")
            return None
    
    def _retry_operation(self, exception: Exception, context: ExceptionContext,
                        rule: ErrorHandlingRule, operation_func: Callable, 
                        *args, **kwargs) -> Any:
        """Retry operation with exponential backoff"""
        for attempt in range(rule.max_retries + 1):  # +1 for the initial attempt
            if attempt > 0:
                delay = rule.retry_delay * (2 ** (attempt - 1))
                self.logger.info(f"Retrying {context.operation_name} in {delay}s (attempt {attempt + 1}/{rule.max_retries + 1})")
                time.sleep(delay)
                
                try:
                    return operation_func(*args, **kwargs)
                except Exception as retry_exception:
                    if attempt == rule.max_retries:
                        if rule.escalate_after_retries:
                            self._escalate_error(retry_exception, context, rule)
                        raise retry_exception
                    continue
        
        # This shouldn't be reached, but just in case
        raise exception
    
    def _execute_fallback(self, exception: Exception, context: ExceptionContext,
                         rule: ErrorHandlingRule, operation_func: Callable, 
                         *args, **kwargs) -> Any:
        """Execute fallback handler if available"""
        if rule.fallback_handler:
            try:
                self.logger.info(f"Executing fallback for {context.operation_name}")
                return rule.fallback_handler(exception, context, *args, **kwargs)
            except Exception as fallback_exception:
                self.logger.error(f"Fallback handler failed: {fallback_exception}")
                self._escalate_error(fallback_exception, context, rule)
                raise fallback_exception
        else:
            # No fallback handler, escalate
            self._escalate_error(exception, context, rule)
            raise exception
    
    def _escalate_error(self, exception: Exception, context: ExceptionContext, 
                       rule: Optional[ErrorHandlingRule]):
        """Escalate error to higher level systems"""
        with self.stats_lock:
            self.error_stats["escalations"] += 1
        
        escalation_data = {
            "timestamp": datetime.now().isoformat(),
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "context": context.to_dict(),
            "severity": rule.severity.value if rule else "critical",
            "traceback": traceback.format_exc()
        }
        
        self.logger.critical(f"🚨 ERROR ESCALATION: {json.dumps(escalation_data, indent=2)}")
        
        # Here you could integrate with external alerting systems
        # like Slack, email, PagerDuty, etc.
    
    @contextmanager
    def handle_operation(self, operation_name: str, component: str, 
                        context: Optional[ExceptionContext] = None,
                        fallback_result: Any = None):
        """
        Context manager for handling operations with comprehensive error management
        
        Usage:
            with handler.handle_operation("file_download", "pexels_integration") as op:
                # Your operation code here
                result = download_file()
                op.set_result(result)
        """
        if context is None:
            context = ExceptionContext(
                operation_name=operation_name,
                component=component
            )
        
        class OperationResult:
            def __init__(self):
                self.result = fallback_result
                self.success = False
            
            def set_result(self, result):
                self.result = result
                self.success = True
        
        op_result = OperationResult()
        
        try:
            yield op_result
            if not op_result.success:
                self.logger.debug(f"Operation {operation_name} completed without explicit result")
                
        except KeyboardInterrupt:
            # Never catch KeyboardInterrupt - allow graceful shutdown
            self.logger.info(f"Operation {operation_name} interrupted by user")
            raise
            
        except SystemExit:
            # Never catch SystemExit - allow proper application termination
            self.logger.info(f"Application exit during {operation_name}")
            raise
            
        except Exception as e:
            # Find matching rule and handle accordingly
            rule = self.find_matching_rule(e)
            
            # Record error for monitoring
            self._record_error(e, context, rule)
            
            # Log with appropriate level
            self._log_exception(e, context, rule)
            
            if rule:
                self.logger.info(f"Applying {rule.action.value} action for {type(e).__name__} in {operation_name}")
                
                if rule.action in [ErrorAction.CONTINUE, ErrorAction.ABORT]:
                    # Don't re-raise, return fallback result
                    pass
                elif rule.action == ErrorAction.ESCALATE:
                    self._escalate_error(e, context, rule)
                    raise
                else:
                    # For RETRY and FALLBACK, we can't implement them in context manager
                    # These require the operation function to be passed
                    self.logger.warning(f"Action {rule.action.value} requires function-based handling")
                    raise
            else:
                # No rule matches, use default behavior
                self.logger.error(f"No rule matches {type(e).__name__} in {operation_name}, re-raising")
                raise
    
    def handle_function(self, operation_name: str, component: str, 
                       context: Optional[ExceptionContext] = None):
        """
        Decorator for handling function exceptions
        
        Usage:
            @handler.handle_function("api_call", "elevenlabs")
            def make_api_call():
                # Your function code here
                pass
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if context is None:
                    func_context = ExceptionContext(
                        operation_name=operation_name,
                        component=component,
                        additional_info={"function": func.__name__}
                    )
                else:
                    func_context = context
                
                try:
                    return func(*args, **kwargs)
                    
                except KeyboardInterrupt:
                    # Never catch KeyboardInterrupt
                    raise
                    
                except SystemExit:
                    # Never catch SystemExit
                    raise
                    
                except Exception as e:
                    # Find matching rule
                    rule = self.find_matching_rule(e)
                    
                    # Record and log error
                    self._record_error(e, func_context, rule)
                    self._log_exception(e, func_context, rule)
                    
                    if rule:
                        # Execute the appropriate action
                        return self._execute_action(e, func_context, rule, func, *args, **kwargs)
                    else:
                        # No matching rule, re-raise
                        self.logger.error(f"No rule matches {type(e).__name__} in {func.__name__}, re-raising")
                        raise
            
            return wrapper
        return decorator
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        with self.stats_lock:
            stats = self.error_stats.copy()
            stats["recent_errors"] = self.error_history[-10:] if self.error_history else []
            stats["error_trends"] = self._calculate_error_trends()
        
        return stats
    
    def _calculate_error_trends(self) -> Dict[str, Any]:
        """Calculate error trends over time"""
        if not self.error_history:
            return {"trend": "stable", "recent_increase": False}
        
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=1)
        older_cutoff = now - timedelta(hours=2)
        
        recent_errors = sum(1 for error in self.error_history 
                          if datetime.fromisoformat(error["timestamp"]) > recent_cutoff)
        older_errors = sum(1 for error in self.error_history 
                         if older_cutoff < datetime.fromisoformat(error["timestamp"]) <= recent_cutoff)
        
        if older_errors == 0:
            trend = "new" if recent_errors > 0 else "stable"
        else:
            ratio = recent_errors / older_errors
            if ratio > 1.5:
                trend = "increasing"
            elif ratio < 0.5:
                trend = "decreasing"
            else:
                trend = "stable"
        
        return {
            "trend": trend,
            "recent_increase": trend == "increasing",
            "recent_count": recent_errors,
            "previous_count": older_errors
        }
    
    def reset_statistics(self):
        """Reset error statistics (useful for testing)"""
        with self.stats_lock:
            self.error_stats = {
                "total_errors": 0,
                "errors_by_category": {},
                "errors_by_severity": {},
                "errors_by_component": {},
                "recovery_success_rate": 0.0,
                "escalations": 0
            }
            self.error_history.clear()
        
        self.logger.info("Error statistics reset")


# Global exception handler instance
_exception_handler = None
_handler_lock = threading.Lock()

def get_exception_handler(log_file: Optional[Path] = None) -> CentralizedExceptionHandler:
    """Get the global exception handler instance"""
    global _exception_handler
    if _exception_handler is None:
        with _handler_lock:
            if _exception_handler is None:
                _exception_handler = CentralizedExceptionHandler(log_file)
    return _exception_handler


# Convenience functions for common use cases

@contextmanager
def safe_operation(operation_name: str, component: str, fallback_result: Any = None):
    """Convenience function for safe operation handling"""
    handler = get_exception_handler()
    with handler.handle_operation(operation_name, component, fallback_result=fallback_result) as op:
        yield op


def safe_function(operation_name: str, component: str):
    """Convenience decorator for safe function handling"""
    handler = get_exception_handler()
    return handler.handle_function(operation_name, component)


def log_and_continue(func: Callable) -> Callable:
    """Simple decorator that logs exceptions and continues"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            handler = get_exception_handler()
            context = ExceptionContext(
                operation_name=func.__name__,
                component=func.__module__ or "unknown"
            )
            handler._log_exception(e, context)
            return None
    return wrapper
