"""
Secure Configuration Management for Shorts Factory
Replacement for config.py that uses encrypted credential storage

This module provides the same interface as the original config.py
but retrieves sensitive credentials from encrypted storage instead 
of plain text .env files.

Author: Security Remediation Team  
Date: August 31, 2025
Security Level: CRITICAL
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from .secure_credential_manager import SecureCredentialManager
from .secure_path_validator import SecurePathValidator


class SecureConfig:
    """
    Secure configuration class that uses encrypted credential storage
    
    This class maintains the same interface as the original Config class
    but retrieves sensitive credentials from the secure credential manager
    instead of environment variables.
    
    Security Features:
    - All API keys retrieved from encrypted keychain storage
    - No sensitive data in environment variables
    - Access logging for all credential retrieval
    - Fallback to environment variables for non-sensitive configs
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize secure configuration"""
        # Initialize credential manager
        self.credential_manager = SecureCredentialManager()
        
        # Initialize secure path validator
        self.path_validator = None  # Will be initialized when needed
        
        # Still load .env for non-sensitive configurations
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from project root for non-sensitive configs
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / '.env'
            if env_path.exists():
                load_dotenv(env_path)
    
    # =================================================================
    # SECURE CREDENTIAL PROPERTIES (Retrieved from encrypted storage)
    # =================================================================
    
    @property
    def google_gemini_api_key(self) -> str:
        """Get Google Gemini API key from secure storage"""
        # Try secure storage first
        gemini_key = self.credential_manager.get_credential('GOOGLE_GEMINI_API_KEY')
        if gemini_key:
            return gemini_key
        
        # Fallback for Google API key
        google_key = self.credential_manager.get_credential('GOOGLE_API_KEY')
        if google_key:
            return google_key
        
        # Last resort: check environment (but log warning)
        env_key = os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if env_key and not env_key.startswith('your_'):
            self.credential_manager.logger.warning(
                "⚠️ Using API key from environment - migrate to secure storage!"
            )
            return env_key
        
        raise ValueError("No valid Google API key found in secure storage. Run credential migration.")
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key from secure storage"""
        key = self.credential_manager.get_credential('OPENAI_API_KEY')
        if key:
            return key
        
        # Fallback to environment with warning
        env_key = os.getenv('OPENAI_API_KEY')
        if env_key:
            self.credential_manager.logger.warning(
                "⚠️ Using OpenAI key from environment - migrate to secure storage!"
            )
            return env_key
        
        raise ValueError("OPENAI_API_KEY not found in secure storage. Run credential migration.")
    
    @property
    def elevenlabs_api_key(self) -> str:
        """Get ElevenLabs API key from secure storage"""
        key = self.credential_manager.get_credential('ELEVENLABS_API_KEY')
        if key:
            return key
        
        # Fallback to environment with warning  
        env_key = os.getenv('ELEVENLABS_API_KEY')
        if env_key:
            self.credential_manager.logger.warning(
                "⚠️ Using ElevenLabs key from environment - migrate to secure storage!"
            )
            return env_key
        
        raise ValueError("ELEVENLABS_API_KEY not found in secure storage. Run credential migration.")
    
    @property
    def reddit_client_secret(self) -> str:
        """Get Reddit client secret from secure storage"""
        secret = self.credential_manager.get_credential('REDDIT_CLIENT_SECRET')
        if secret:
            return secret
        
        # Fallback to environment with warning
        env_secret = os.getenv('REDDIT_CLIENT_SECRET')
        if env_secret:
            self.credential_manager.logger.warning(
                "⚠️ Using Reddit secret from environment - migrate to secure storage!"
            )
            return env_secret
        
        raise ValueError("REDDIT_CLIENT_SECRET not found in secure storage. Run credential migration.")
    
    @property
    def pexels_api_key(self) -> str:
        """Get Pexels API key from secure storage"""
        key = self.credential_manager.get_credential('PEXELS_API_KEY')
        if key:
            return key
        
        # Fallback to environment with warning
        env_key = os.getenv('PEXELS_API_KEY')
        if env_key:
            self.credential_manager.logger.warning(
                "⚠️ Using Pexels key from environment - migrate to secure storage!"
            )
            return env_key
        
        raise ValueError("PEXELS_API_KEY not found in secure storage. Run credential migration.")
    
    # =================================================================
    # NON-SENSITIVE PROPERTIES (Still from environment variables)
    # =================================================================
    
    @property
    def google_sheets_api_key(self) -> str:
        """Get Google Sheets API key (usually not needed for service accounts)"""
        return self._get_env_var('GOOGLE_SHEETS_API_KEY', 'not_needed_for_service_account')
    
    @property
    def google_sheets_spreadsheet_id(self) -> str:
        """Get Google Sheets spreadsheet ID (not sensitive)"""
        return self._get_required_env('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    @property
    def google_credentials_file(self) -> str:
        """Get path to Google credentials file"""
        return self._get_required_env('GOOGLE_CREDENTIALS_FILE')
    
    @property
    def reddit_client_id(self) -> str:
        """Get Reddit client ID (not sensitive)"""
        return self._get_required_env('REDDIT_CLIENT_ID')
    
    @property
    def reddit_user_agent(self) -> str:
        """Get Reddit user agent (not sensitive)"""
        return os.getenv('REDDIT_USER_AGENT', 'ShortsFactory/1.0')
    
    @property
    def youtube_api_key(self) -> str:
        """Get YouTube API key (often not needed for OAuth)"""
        return self._get_env_var('YOUTUBE_API_KEY', 'not_needed_for_oauth2_flow')
    
    @property
    def youtube_client_secrets_file(self) -> str:
        """Get path to YouTube client secrets file"""
        return self._get_required_env('YOUTUBE_CLIENT_SECRETS_FILE')
    
    @property
    def log_level(self) -> str:
        """Get log level (not sensitive)"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()
    
    @property
    def working_directory(self) -> Path:
        """Get working directory path with comprehensive security validation"""
        default_path = Path(__file__).parent.parent.parent / 'working_directory'
        path_str = os.getenv('WORKING_DIRECTORY', str(default_path))
        
        # Initialize path validator if not already done
        if self.path_validator is None:
            # Use default path for initial validator setup
            self.path_validator = SecurePathValidator(default_path)
        
        # Validate path using comprehensive security checks
        result = self.path_validator.validate_path(
            path_str, 
            SecurePathValidator.PathCategory.WORKING_DIRECTORY,
            allow_creation=True
        )
        
        if result.is_valid and result.sanitized_path:
            # Update validator with new working directory
            if str(result.sanitized_path) != str(self.path_validator.working_directory):
                self.path_validator = SecurePathValidator(result.sanitized_path)
            return result.sanitized_path
        else:
            # Security validation failed - log violations and use default
            self.credential_manager.logger.error(
                f"❌ SECURITY: Working directory validation failed: {result.violations}"
            )
            for violation in result.violations:
                self.credential_manager.logger.warning(f"🚨 PATH SECURITY: {violation}")
            
            # Fall back to secure default
            secure_default = default_path.resolve()
            secure_default.mkdir(parents=True, exist_ok=True)
            self.path_validator = SecurePathValidator(secure_default)
            return secure_default
    
    @property
    def daily_execution_time(self) -> str:
        """Get daily execution time (not sensitive)"""
        return os.getenv('DAILY_EXECUTION_TIME', '09:00')
    
    @property
    def max_api_cost_per_month(self) -> float:
        """Get maximum API cost per month (not sensitive)"""
        return float(os.getenv('MAX_API_COST_PER_MONTH', '100.0'))
    
    # =================================================================
    # HELPER METHODS
    # =================================================================
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
    
    def _get_env_var(self, key: str, default: str) -> str:
        """Get environment variable with default value"""
        return os.getenv(key, default)
    
    def validate_config(self) -> list[str]:
        """
        Validate configuration and return list of errors
        
        This method checks both secure credentials and environment variables
        """
        errors = []
        
        # Check secure credentials
        secure_credentials = [
            'GOOGLE_GEMINI_API_KEY',
            'OPENAI_API_KEY', 
            'ELEVENLABS_API_KEY',
            'REDDIT_CLIENT_SECRET',
            'PEXELS_API_KEY'
        ]
        
        for cred in secure_credentials:
            try:
                # Try to access the credential (this will check secure storage first)
                getattr(self, cred.lower())
            except ValueError as e:
                errors.append(str(e))
        
        # Check required environment variables (non-sensitive)
        required_env_vars = [
            'GOOGLE_SHEETS_SPREADSHEET_ID',
            'GOOGLE_CREDENTIALS_FILE',
            'REDDIT_CLIENT_ID',
            'YOUTUBE_CLIENT_SECRETS_FILE'
        ]
        
        for var in required_env_vars:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")
        
        # Validate file paths
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
        if credentials_file and not Path(credentials_file).exists():
            errors.append(f"Google credentials file not found: {credentials_file}")
            
        youtube_secrets = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE')
        if youtube_secrets and not Path(youtube_secrets).exists():
            errors.append(f"YouTube client secrets file not found: {youtube_secrets}")
        
        return errors
    
    def migrate_credentials_from_env(self, env_file_path: Optional[Path] = None) -> Dict[str, bool]:
        """
        Migrate credentials from .env file to secure storage
        
        Args:
            env_file_path: Path to .env file (optional)
            
        Returns:
            Dict[str, bool]: Migration results
        """
        if env_file_path is None:
            project_root = Path(__file__).parent.parent.parent
            env_file_path = project_root / '.env'
        
        return self.credential_manager.migrate_from_env_file(env_file_path)
    
    def verify_security_status(self) -> Dict[str, Any]:
        """Verify the security status of the configuration system"""
        return self.credential_manager.verify_system_security()


# Global secure config instance  
secure_config = SecureConfig()

# Backward compatibility - replace the original config import
config = secure_config
