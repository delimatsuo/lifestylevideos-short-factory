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
    'get_resource_manager'
]
