"""
Configuration management for Shorts Factory
Handles environment variables and application settings
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for Shorts Factory application"""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration with optional env file path"""
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from project root
            project_root = Path(__file__).parent.parent.parent
            env_path = project_root / '.env'
            if env_path.exists():
                load_dotenv(env_path)
    
    # Google Services Configuration
    @property
    def google_sheets_api_key(self) -> str:
        return self._get_required_env('GOOGLE_SHEETS_API_KEY')
    
    @property
    def google_sheets_spreadsheet_id(self) -> str:
        return self._get_required_env('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    @property
    def google_credentials_file(self) -> str:
        return self._get_required_env('GOOGLE_CREDENTIALS_FILE')
    
    # AI Services Configuration
    @property
    def google_gemini_api_key(self) -> str:
        # Try GOOGLE_GEMINI_API_KEY first, fallback to GOOGLE_API_KEY
        gemini_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if gemini_key and not gemini_key.startswith('your_'):
            return gemini_key
        elif google_key and not google_key.startswith('your_'):
            return google_key
        else:
            raise ValueError("No valid Google API key found. Set either GOOGLE_GEMINI_API_KEY or GOOGLE_API_KEY")
    
    @property
    def elevenlabs_api_key(self) -> str:
        return self._get_required_env('ELEVENLABS_API_KEY')
    
    # Content Sources Configuration
    @property
    def reddit_client_id(self) -> str:
        return self._get_required_env('REDDIT_CLIENT_ID')
    
    @property
    def reddit_client_secret(self) -> str:
        return self._get_required_env('REDDIT_CLIENT_SECRET')
    
    @property
    def reddit_user_agent(self) -> str:
        return os.getenv('REDDIT_USER_AGENT', 'ShortsFactory/1.0')
    
    # Media Services Configuration
    @property
    def pexels_api_key(self) -> str:
        return self._get_required_env('PEXELS_API_KEY')
    
    # YouTube API Configuration
    @property
    def youtube_api_key(self) -> str:
        return self._get_required_env('YOUTUBE_API_KEY')
    
    @property
    def youtube_client_secrets_file(self) -> str:
        return self._get_required_env('YOUTUBE_CLIENT_SECRETS_FILE')
    
    # Application Settings
    @property
    def log_level(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO').upper()
    
    @property
    def working_directory(self) -> Path:
        default_path = Path(__file__).parent.parent.parent / 'working_directory'
        path_str = os.getenv('WORKING_DIRECTORY', str(default_path))
        return Path(path_str)
    
    @property
    def daily_execution_time(self) -> str:
        return os.getenv('DAILY_EXECUTION_TIME', '09:00')
    
    @property
    def max_api_cost_per_month(self) -> float:
        return float(os.getenv('MAX_API_COST_PER_MONTH', '100.0'))
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
    
    def validate_config(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        required_vars = [
            'GOOGLE_SHEETS_API_KEY',
            'GOOGLE_SHEETS_SPREADSHEET_ID', 
            'GOOGLE_CREDENTIALS_FILE',
            'GOOGLE_GEMINI_API_KEY',
            'ELEVENLABS_API_KEY',
            'REDDIT_CLIENT_ID',
            'REDDIT_CLIENT_SECRET',
            'PEXELS_API_KEY',
            'YOUTUBE_API_KEY',
            'YOUTUBE_CLIENT_SECRETS_FILE'
        ]
        
        for var in required_vars:
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


# Global config instance
config = Config()
