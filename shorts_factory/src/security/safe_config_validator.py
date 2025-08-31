"""
Safe Configuration Validation and Processing
Secure replacement for working_solution/utils/settings.py with dangerous eval() usage

This module provides secure configuration handling by:
- Eliminating eval() usage with safe type conversion
- Comprehensive configuration validation and sanitization
- Type-safe configuration processing with bounds checking
- Schema-based configuration validation
- Secure TOML/JSON configuration loading
- Configuration integrity checking and verification

Author: Security Remediation Team  
Date: August 31, 2025
Security Level: CRITICAL
"""

import os
import toml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable, Type
from dataclasses import dataclass, field
from enum import Enum

from .input_validator import get_input_validator, DataType, ValidationResult
from .safe_console import get_safe_console


class ConfigValidationType(Enum):
    """Configuration validation types"""
    STRING = "string"
    INTEGER = "integer" 
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    PATH = "path"
    URL = "url"
    EMAIL = "email"


@dataclass
class ConfigRule:
    """Configuration validation rule"""
    key: str
    validation_type: ConfigValidationType
    required: bool = True
    default: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None
    description: Optional[str] = None
    example: Optional[str] = None


class SafeConfigValidator:
    """
    Secure configuration validation system
    
    Features:
    - Safe type conversion without eval()
    - Schema-based configuration validation
    - Comprehensive input sanitization  
    - Configuration file integrity checking
    - Interactive configuration setup
    - Secure default value handling
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize safe config validator"""
        self.logger = logging.getLogger("SafeConfigValidator")
        self.validator = get_input_validator()
        self.console = get_safe_console()
        self.config_file = config_file
        self.schema: Dict[str, ConfigRule] = {}
        self.config_data: Dict[str, Any] = {}
        
        self.logger.info("🛡️ Safe Configuration Validator initialized")
    
    def add_rule(self, rule: ConfigRule):
        """Add a configuration validation rule"""
        self.schema[rule.key] = rule
        self.logger.debug(f"Added config rule: {rule.key}")
    
    def add_rules(self, rules: List[ConfigRule]):
        """Add multiple configuration rules"""
        for rule in rules:
            self.add_rule(rule)
    
    def load_config_file(self, config_path: Path, create_if_missing: bool = True) -> bool:
        """
        Safely load configuration file
        
        Args:
            config_path: Path to configuration file
            create_if_missing: Create file if it doesn't exist
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not config_path.exists():
                if create_if_missing:
                    self.logger.info(f"Configuration file not found, creating: {config_path}")
                    self._create_config_file(config_path)
                    return True
                else:
                    self.logger.error(f"Configuration file not found: {config_path}")
                    return False
            
            # Validate file size (prevent large file attacks)
            file_size = config_path.stat().st_size
            max_size = 10 * 1024 * 1024  # 10MB max
            if file_size > max_size:
                self.logger.error(f"Configuration file too large: {file_size} bytes")
                return False
            
            # Load and validate file content
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate content
            content_result = self.validator.validate_input(
                content,
                context=f"config_file:{config_path.name}"
            )
            
            if not content_result.is_valid:
                self.logger.error(f"Invalid config file content: {content_result.errors}")
                return False
            
            # Parse configuration based on file extension
            if config_path.suffix.lower() == '.toml':
                self.config_data = self._safe_load_toml(content_result.sanitized_value)
            elif config_path.suffix.lower() == '.json':
                self.config_data = self._safe_load_json(content_result.sanitized_value)
            else:
                self.logger.error(f"Unsupported config file format: {config_path.suffix}")
                return False
            
            self.logger.info(f"Successfully loaded configuration: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load config file {config_path}: {e}")
            return False
    
    def _safe_load_toml(self, content: str) -> Dict[str, Any]:
        """Safely load TOML configuration"""
        try:
            return toml.loads(content)
        except toml.TomlDecodeError as e:
            self.logger.error(f"Invalid TOML format: {e}")
            raise ValueError(f"Invalid TOML configuration: {e}")
    
    def _safe_load_json(self, content: str) -> Dict[str, Any]:
        """Safely load JSON configuration"""
        return self.validator.safe_json_loads(content, default={})
    
    def _create_config_file(self, config_path: Path):
        """Create a new configuration file with defaults"""
        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate default configuration
            default_config = {}
            for key, rule in self.schema.items():
                if rule.default is not None:
                    default_config[key] = rule.default
            
            # Save configuration
            if config_path.suffix.lower() == '.toml':
                with open(config_path, 'w', encoding='utf-8') as f:
                    toml.dump(default_config, f)
            elif config_path.suffix.lower() == '.json':
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
            
            # Set secure permissions
            os.chmod(config_path, 0o600)
            
            self.config_data = default_config
            self.logger.info(f"Created default configuration file: {config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create config file {config_path}: {e}")
            raise
    
    def validate_config(self, interactive: bool = False) -> Dict[str, ValidationResult]:
        """
        Validate configuration against schema
        
        Args:
            interactive: Prompt user for missing/invalid values
            
        Returns:
            Dictionary of validation results per key
        """
        results = {}
        
        for key, rule in self.schema.items():
            try:
                value = self.config_data.get(key)
                
                # Handle missing required values
                if value is None and rule.required:
                    if interactive:
                        value = self._interactive_config_input(rule)
                        self.config_data[key] = value
                    elif rule.default is not None:
                        value = rule.default
                        self.config_data[key] = value
                    else:
                        results[key] = ValidationResult(
                            is_valid=False,
                            original_value=None,
                            errors=[f"Required configuration key '{key}' is missing"]
                        )
                        continue
                
                # Handle optional missing values
                if value is None and not rule.required:
                    if rule.default is not None:
                        value = rule.default
                        self.config_data[key] = value
                    else:
                        results[key] = ValidationResult(
                            is_valid=True,
                            original_value=None,
                            sanitized_value=None
                        )
                        continue
                
                # Validate the value
                validation_result = self._validate_config_value(value, rule)
                results[key] = validation_result
                
                # Update config with sanitized value
                if validation_result.is_valid and validation_result.sanitized_value is not None:
                    self.config_data[key] = validation_result.sanitized_value
                
            except Exception as e:
                self.logger.error(f"Error validating config key '{key}': {e}")
                results[key] = ValidationResult(
                    is_valid=False,
                    original_value=value,
                    errors=[f"Validation error: {str(e)}"]
                )
        
        return results
    
    def _validate_config_value(self, value: Any, rule: ConfigRule) -> ValidationResult:
        """Validate a configuration value against a rule"""
        
        # Type validation and conversion
        converted_value = self._safe_type_convert(value, rule.validation_type)
        if converted_value is None:
            return ValidationResult(
                is_valid=False,
                original_value=value,
                errors=[f"Invalid {rule.validation_type.value} format"]
            )
        
        # Additional validation based on type
        if rule.validation_type == ConfigValidationType.STRING:
            return self._validate_string_config(converted_value, rule)
        elif rule.validation_type in [ConfigValidationType.INTEGER, ConfigValidationType.FLOAT]:
            return self._validate_numeric_config(converted_value, rule)
        elif rule.validation_type == ConfigValidationType.PATH:
            return self._validate_path_config(converted_value, rule)
        elif rule.validation_type == ConfigValidationType.URL:
            return self._validate_url_config(converted_value, rule)
        elif rule.validation_type == ConfigValidationType.EMAIL:
            return self._validate_email_config(converted_value, rule)
        else:
            # Basic validation
            result = self.validator.validate_input(
                converted_value,
                context=f"config:{rule.key}"
            )
            return result
    
    def _safe_type_convert(self, value: Any, config_type: ConfigValidationType) -> Any:
        """
        SECURE type conversion - replacement for dangerous eval() usage
        
        This replaces the eval(checks["type"])(value) pattern in settings.py
        """
        try:
            if config_type == ConfigValidationType.STRING:
                return self.validator.safe_string(value)
            elif config_type == ConfigValidationType.INTEGER:
                return self.validator.safe_int(value)
            elif config_type == ConfigValidationType.FLOAT:
                return self.validator.safe_float(value)
            elif config_type == ConfigValidationType.BOOLEAN:
                return self.validator.safe_bool(value)
            elif config_type == ConfigValidationType.LIST:
                if isinstance(value, list):
                    return value
                elif isinstance(value, str):
                    # Try to parse as JSON list
                    parsed = self.validator.safe_json_loads(value)
                    return parsed if isinstance(parsed, list) else [value]
                else:
                    return [value]
            elif config_type == ConfigValidationType.DICT:
                if isinstance(value, dict):
                    return value
                elif isinstance(value, str):
                    # Try to parse as JSON dict
                    parsed = self.validator.safe_json_loads(value)
                    return parsed if isinstance(parsed, dict) else {"value": value}
                else:
                    return {"value": value}
            else:
                return str(value)
                
        except Exception as e:
            self.logger.error(f"Type conversion error for {config_type}: {e}")
            return None
    
    def _validate_string_config(self, value: str, rule: ConfigRule) -> ValidationResult:
        """Validate string configuration value"""
        errors = []
        
        # Length validation
        if rule.min_length and len(value) < rule.min_length:
            errors.append(f"String too short (minimum {rule.min_length} characters)")
        
        if rule.max_length and len(value) > rule.max_length:
            errors.append(f"String too long (maximum {rule.max_length} characters)")
        
        # Allowed values validation
        if rule.allowed_values and value not in rule.allowed_values:
            errors.append(f"Value not in allowed list: {rule.allowed_values}")
        
        # Pattern validation
        if rule.pattern and not re.match(rule.pattern, value):
            errors.append(f"Value does not match required pattern")
        
        # Basic security validation
        base_result = self.validator.validate_input(value, DataType.STRING, context=f"config:{rule.key}")
        
        return ValidationResult(
            is_valid=len(errors) == 0 and base_result.is_valid,
            original_value=value,
            sanitized_value=base_result.sanitized_value,
            errors=errors + base_result.errors,
            warnings=base_result.warnings
        )
    
    def _validate_numeric_config(self, value: Union[int, float], rule: ConfigRule) -> ValidationResult:
        """Validate numeric configuration value"""
        errors = []
        
        # Range validation
        if rule.min_value is not None and value < rule.min_value:
            errors.append(f"Value too small (minimum {rule.min_value})")
        
        if rule.max_value is not None and value > rule.max_value:
            errors.append(f"Value too large (maximum {rule.max_value})")
        
        # Allowed values validation
        if rule.allowed_values and value not in rule.allowed_values:
            errors.append(f"Value not in allowed list: {rule.allowed_values}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            original_value=value,
            sanitized_value=value,
            errors=errors
        )
    
    def _validate_path_config(self, value: str, rule: ConfigRule) -> ValidationResult:
        """Validate path configuration value"""
        path_result = self.validator.validate_input(value, DataType.PATH, context=f"config_path:{rule.key}")
        return path_result
    
    def _validate_url_config(self, value: str, rule: ConfigRule) -> ValidationResult:
        """Validate URL configuration value"""
        url_result = self.validator.validate_input(value, DataType.URL, context=f"config_url:{rule.key}")
        return url_result
    
    def _validate_email_config(self, value: str, rule: ConfigRule) -> ValidationResult:
        """Validate email configuration value"""
        email_result = self.validator.validate_input(value, DataType.EMAIL, context=f"config_email:{rule.key}")
        return email_result
    
    def _interactive_config_input(self, rule: ConfigRule) -> Any:
        """Interactive configuration input with validation"""
        message = f"Enter {rule.key}"
        if rule.description:
            message += f" ({rule.description})"
        
        # Map config types to console input types
        type_map = {
            ConfigValidationType.STRING: "str",
            ConfigValidationType.INTEGER: "int", 
            ConfigValidationType.FLOAT: "float",
            ConfigValidationType.BOOLEAN: "bool",
            ConfigValidationType.PATH: "str",
            ConfigValidationType.URL: "str",
            ConfigValidationType.EMAIL: "str",
        }
        
        input_type = type_map.get(rule.validation_type, "str")
        
        return self.console.safe_input(
            message=message,
            data_type=input_type,
            default=rule.default,
            optional=not rule.required,
            min_val=rule.min_value,
            max_val=rule.max_value,
            min_length=rule.min_length,
            max_length=rule.max_length,
            options=rule.allowed_values
        )
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback"""
        return self.config_data.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> bool:
        """Set configuration value with validation"""
        if key in self.schema:
            rule = self.schema[key]
            result = self._validate_config_value(value, rule)
            
            if result.is_valid:
                self.config_data[key] = result.sanitized_value
                return True
            else:
                self.logger.error(f"Invalid value for {key}: {result.errors}")
                return False
        else:
            # No rule defined, basic validation only
            result = self.validator.validate_input(value, context=f"config_set:{key}")
            if result.is_valid:
                self.config_data[key] = result.sanitized_value
                return True
            else:
                self.logger.error(f"Invalid value for {key}: {result.errors}")
                return False
    
    def save_config(self, config_path: Optional[Path] = None) -> bool:
        """Save configuration to file"""
        try:
            path = config_path or self.config_file
            if not path:
                raise ValueError("No configuration file path specified")
            
            # Backup existing file
            if path.exists():
                backup_path = path.with_suffix(path.suffix + '.backup')
                path.rename(backup_path)
            
            # Save configuration
            if path.suffix.lower() == '.toml':
                with open(path, 'w', encoding='utf-8') as f:
                    toml.dump(self.config_data, f)
            elif path.suffix.lower() == '.json':
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(path, 0o600)
            
            self.logger.info(f"Configuration saved to: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get configuration validation summary"""
        results = self.validate_config(interactive=False)
        
        summary = {
            "total_keys": len(self.schema),
            "valid_keys": sum(1 for r in results.values() if r.is_valid),
            "invalid_keys": sum(1 for r in results.values() if not r.is_valid),
            "missing_required": [],
            "validation_errors": {}
        }
        
        for key, result in results.items():
            if not result.is_valid:
                summary["validation_errors"][key] = result.errors
                
                if key in self.schema and self.schema[key].required and result.original_value is None:
                    summary["missing_required"].append(key)
        
        return summary


# Secure replacement functions for dangerous settings.py usage

def safe_check_config_value(value: Any, checks: Dict[str, Any], default_result: Any = False) -> Any:
    """
    SECURE replacement for check() function in settings.py
    
    Eliminates dangerous eval() usage with safe validation
    """
    validator = get_input_validator()
    
    # Handle empty or None values
    if not value:
        return default_result
    
    # Type validation (SECURE - no eval())
    if "type" in checks:
        type_name = checks["type"]
        
        # Safe type conversion mapping
        type_converters = {
            "int": validator.safe_int,
            "float": validator.safe_float, 
            "bool": validator.safe_bool,
            "str": validator.safe_string,
        }
        
        if type_name in type_converters:
            converter = type_converters[type_name]
            try:
                converted_value = converter(value)
                if converted_value is None and type_name != "str":
                    return default_result
                value = converted_value
            except Exception:
                return default_result
    
    # Options validation
    if "options" in checks and value not in checks["options"]:
        return default_result
    
    # Range validation
    if "min" in checks and isinstance(value, (int, float)) and value < checks["min"]:
        return default_result
    
    if "max" in checks and isinstance(value, (int, float)) and value > checks["max"]:
        return default_result
    
    # Pattern validation
    if "regex" in checks:
        import re
        if not re.match(checks["regex"], str(value)):
            return default_result
    
    return value


def create_safe_config_validator(config_file: Path, schema_rules: List[ConfigRule]) -> SafeConfigValidator:
    """Create a safe configuration validator with predefined rules"""
    validator = SafeConfigValidator(config_file)
    validator.add_rules(schema_rules)
    return validator
