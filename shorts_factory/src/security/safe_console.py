"""
Safe Console and User Input Handling
Secure replacement for working_solution/utils/console.py with dangerous eval() usage

This module provides secure alternatives to dangerous user input handling by:
- Eliminating eval() usage with safe type conversion
- Comprehensive input validation and sanitization
- Secure option selection with proper validation
- Type-safe input processing with bounds checking
- XSS and injection attack prevention
- Comprehensive logging and monitoring

Author: Security Remediation Team
Date: August 31, 2025
Security Level: CRITICAL
"""

import re
import logging
from typing import Any, List, Optional, Union, Dict, Callable
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.table import Table

from .input_validator import get_input_validator, DataType, ValidationSeverity


class SafeConsole:
    """
    Secure console interface with comprehensive input validation
    
    Features:
    - Safe type conversion without eval()
    - Comprehensive input validation
    - Option selection with validation
    - XSS and injection prevention
    - Rich console formatting
    - Comprehensive error handling
    """
    
    def __init__(self):
        """Initialize safe console"""
        self.console = Console()
        self.validator = get_input_validator()
        self.logger = logging.getLogger("SafeConsole")
    
    def print_step(self, text: str, style: str = "bold blue") -> None:
        """Print a step with formatting"""
        self.console.print(f"🔸 {text}", style=style)
    
    def print_substep(self, text: str, style: str = "") -> None:
        """Print a substep with formatting"""
        self.console.print(f"  ↳ {text}", style=style)
    
    def print_table(self, data: Union[List, Dict], title: str = "") -> None:
        """Print data in table format"""
        table = Table(title=title)
        
        if isinstance(data, dict):
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="white")
            for key, value in data.items():
                # Sanitize output
                safe_key = self.validator.safe_string(key, max_length=50)
                safe_value = self.validator.safe_string(value, max_length=100)
                table.add_row(safe_key, safe_value)
        elif isinstance(data, list):
            table.add_column("Item", style="white")
            for item in data:
                safe_item = self.validator.safe_string(item, max_length=100)
                table.add_row(safe_item)
        
        self.console.print(table)
    
    def safe_input(
        self,
        message: str = "",
        data_type: str = "str",
        default: Any = None,
        optional: bool = False,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = 1000,
        options: Optional[List[str]] = None,
        pattern: Optional[str] = None,
        error_message: str = "Invalid input",
        retries: int = 3
    ) -> Any:
        """
        SECURE replacement for handle_input() function
        
        Eliminates dangerous eval() usage with safe type conversion
        
        Args:
            message: Input prompt message
            data_type: Expected data type ('str', 'int', 'float', 'bool')
            default: Default value if no input provided
            optional: Allow empty input
            min_val: Minimum numeric value
            max_val: Maximum numeric value  
            min_length: Minimum string length
            max_length: Maximum string length
            options: List of valid options
            pattern: Regex pattern to match
            error_message: Custom error message
            retries: Number of retry attempts
            
        Returns:
            Validated and converted input value
        """
        
        # Handle optional input
        if optional and default is not None:
            use_default = Confirm.ask(f"{message}\nUse default value '{default}'?")
            if use_default:
                return default
        
        # Type conversion mapping (SECURE - no eval())
        type_converters = {
            'str': self._safe_string_convert,
            'int': self._safe_int_convert,
            'float': self._safe_float_convert,
            'bool': self._safe_bool_convert,
        }
        
        if data_type not in type_converters:
            self.logger.error(f"Unsupported data type: {data_type}")
            raise ValueError(f"Unsupported data type: {data_type}")
        
        converter = type_converters[data_type]
        
        for attempt in range(retries):
            try:
                # Get user input
                raw_input = self.console.input(f"{message}: ")
                
                # Validate input length
                if max_length and len(raw_input) > max_length:
                    self.console.print(f"[red]Input too long (max {max_length} characters)[/red]")
                    continue
                
                # Handle empty input
                if not raw_input.strip():
                    if optional and default is not None:
                        return default
                    elif optional:
                        return None
                    else:
                        self.console.print("[red]Input is required[/red]")
                        continue
                
                # Validate input against dangerous patterns
                validation_result = self.validator.validate_input(
                    raw_input, 
                    context="console_input"
                )
                
                if not validation_result.is_valid:
                    self.console.print(f"[red]Invalid input: {'; '.join(validation_result.errors)}[/red]")
                    continue
                
                sanitized_input = validation_result.sanitized_value
                
                # Apply pattern matching if specified
                if pattern:
                    if not re.match(pattern, sanitized_input):
                        self.console.print(f"[red]{error_message}[/red]")
                        continue
                
                # Validate against options list
                if options:
                    if sanitized_input not in options:
                        self.console.print(f"[red]Invalid option. Choose from: {', '.join(options)}[/red]")
                        self.print_table(options, "Valid Options")
                        continue
                
                # Convert to target type
                converted_value = converter(
                    sanitized_input, 
                    min_val=min_val, 
                    max_val=max_val,
                    min_length=min_length,
                    max_length=max_length
                )
                
                self.logger.info(f"Successfully validated console input: {data_type}")
                return converted_value
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Input cancelled by user[/yellow]")
                raise
            except Exception as e:
                self.console.print(f"[red]Input error: {e}[/red]")
                if attempt == retries - 1:
                    if default is not None:
                        self.console.print(f"[yellow]Using default value: {default}[/yellow]")
                        return default
                    else:
                        raise ValueError(f"Failed to get valid input after {retries} attempts")
        
        # Should never reach here, but just in case
        if default is not None:
            return default
        raise ValueError(f"Failed to get valid input after {retries} attempts")
    
    def _safe_string_convert(self, value: str, **kwargs) -> str:
        """Safely convert to string with validation"""
        min_length = kwargs.get('min_length')
        max_length = kwargs.get('max_length')
        
        if min_length and len(value) < min_length:
            raise ValueError(f"String too short (minimum {min_length} characters)")
        
        if max_length and len(value) > max_length:
            raise ValueError(f"String too long (maximum {max_length} characters)")
        
        return self.validator.safe_string(value, max_length=max_length)
    
    def _safe_int_convert(self, value: str, **kwargs) -> int:
        """Safely convert to integer with bounds checking"""
        min_val = kwargs.get('min_val')
        max_val = kwargs.get('max_val')
        
        result = self.validator.safe_int(
            value, 
            default=None,
            min_val=int(min_val) if min_val is not None else None,
            max_val=int(max_val) if max_val is not None else None
        )
        
        if result is None:
            raise ValueError("Invalid integer format")
        
        return result
    
    def _safe_float_convert(self, value: str, **kwargs) -> float:
        """Safely convert to float with bounds checking"""
        min_val = kwargs.get('min_val')
        max_val = kwargs.get('max_val')
        
        result = self.validator.safe_float(
            value,
            default=None,
            min_val=min_val,
            max_val=max_val
        )
        
        if result is None:
            raise ValueError("Invalid float format")
        
        return result
    
    def _safe_bool_convert(self, value: str, **kwargs) -> bool:
        """Safely convert to boolean"""
        return self.validator.safe_bool(value)
    
    def select_option(
        self,
        message: str,
        options: List[str],
        default: Optional[str] = None,
        case_sensitive: bool = False
    ) -> str:
        """
        Secure option selection with validation
        
        Args:
            message: Selection prompt
            options: List of valid options
            default: Default option
            case_sensitive: Whether selection is case sensitive
            
        Returns:
            Selected option
        """
        if not options:
            raise ValueError("Options list cannot be empty")
        
        # Sanitize options
        safe_options = []
        for option in options:
            safe_option = self.validator.safe_string(option, max_length=100)
            safe_options.append(safe_option)
        
        # Display options
        self.print_table(safe_options, "Available Options")
        
        while True:
            try:
                choice = self.console.input(f"{message}: ")
                
                # Validate input
                validation_result = self.validator.validate_input(choice, context="option_selection")
                
                if not validation_result.is_valid:
                    self.console.print(f"[red]Invalid selection: {'; '.join(validation_result.errors)}[/red]")
                    continue
                
                sanitized_choice = validation_result.sanitized_value.strip()
                
                # Handle empty input with default
                if not sanitized_choice and default is not None:
                    return default
                
                # Find matching option
                if case_sensitive:
                    if sanitized_choice in safe_options:
                        return sanitized_choice
                else:
                    # Case-insensitive matching
                    for option in safe_options:
                        if sanitized_choice.lower() == option.lower():
                            return option
                
                self.console.print(f"[red]Invalid option. Please select from: {', '.join(safe_options)}[/red]")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Selection cancelled by user[/yellow]")
                raise
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Secure yes/no confirmation"""
        return Confirm.ask(message, default=default)
    
    def get_integer(
        self,
        message: str,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None,
        default: Optional[int] = None
    ) -> int:
        """Get validated integer input"""
        return IntPrompt.ask(
            message,
            default=default,
            show_default=default is not None
        )
    
    def get_float(
        self,
        message: str,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        default: Optional[float] = None
    ) -> float:
        """Get validated float input"""
        return FloatPrompt.ask(
            message,
            default=default,
            show_default=default is not None
        )


# Global safe console instance
_safe_console = None

def get_safe_console() -> SafeConsole:
    """Get the global safe console instance"""
    global _safe_console
    if _safe_console is None:
        _safe_console = SafeConsole()
    return _safe_console


# Convenience functions for easy replacement of dangerous console functions

def safe_handle_input(
    message: str = "",
    data_type: str = "str",
    default: Any = None,
    optional: bool = False,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    options: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    error_message: str = "Invalid input"
) -> Any:
    """
    SECURE drop-in replacement for handle_input() from utils/console.py
    
    Eliminates dangerous eval() usage with comprehensive validation
    """
    console = get_safe_console()
    return console.safe_input(
        message=message,
        data_type=data_type,
        default=default,
        optional=optional,
        min_val=min_val,
        max_val=max_val,
        options=options,
        pattern=pattern,
        error_message=error_message
    )


def safe_print_step(text: str, style: str = "bold blue") -> None:
    """Safe step printing"""
    console = get_safe_console()
    console.print_step(text, style)


def safe_print_substep(text: str, style: str = "") -> None:
    """Safe substep printing"""
    console = get_safe_console()
    console.print_substep(text, style)


def safe_print_table(data: Union[List, Dict], title: str = "") -> None:
    """Safe table printing"""
    console = get_safe_console()
    console.print_table(data, title)


def safe_select_option(
    message: str,
    options: List[str],
    default: Optional[str] = None,
    case_sensitive: bool = False
) -> str:
    """Safe option selection"""
    console = get_safe_console()
    return console.select_option(message, options, default, case_sensitive)


def safe_confirm(message: str, default: bool = False) -> bool:
    """Safe confirmation"""
    console = get_safe_console()
    return console.confirm(message, default)
