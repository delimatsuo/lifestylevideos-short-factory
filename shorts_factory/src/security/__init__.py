"""
Security module for Shorts Factory
Provides secure credential management and configuration

This module replaces insecure credential handling with encrypted storage
"""

from .secure_credential_manager import SecureCredentialManager, get_credential_manager
from .secure_config import SecureConfig, secure_config
from .secure_path_validator import SecurePathValidator, get_secure_path_validator
from .secure_command_executor import SecureCommandExecutor, get_secure_command_executor
from .robust_resource_manager import RobustResourceManager, get_resource_manager
from .atomic_file_operations import AtomicFileOperations, get_atomic_file_operations
from .network_resilience import NetworkResilienceManager, get_network_resilience_manager
from .exception_handler import CentralizedExceptionHandler, get_exception_handler
from .input_validator import InputValidator, get_input_validator

# Make secure config the default config
config = secure_config

__all__ = [
    'SecureCredentialManager',
    'get_credential_manager', 
    'SecureConfig',
    'secure_config',
    'config',
    'SecurePathValidator',
    'get_secure_path_validator',
    'SecureCommandExecutor', 
    'get_secure_command_executor',
    'RobustResourceManager',
    'get_resource_manager',
    'AtomicFileOperations',
    'get_atomic_file_operations',
    'NetworkResilienceManager',
    'get_network_resilience_manager',
    'CentralizedExceptionHandler',
    'get_exception_handler',
    'InputValidator',
    'get_input_validator'
]
