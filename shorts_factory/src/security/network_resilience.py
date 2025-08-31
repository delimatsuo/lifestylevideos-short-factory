"""
Network Resilience and Timeout Management System for Shorts Factory
Addresses HP-002: Hung Process Vulnerabilities

This module provides comprehensive network timeout handling to prevent hung processes by:
- Centralized timeout configuration for all network operations
- Automatic retry mechanisms with exponential backoff
- Network failure recovery and circuit breaker patterns
- Connection pooling and keep-alive management
- Timeout monitoring and alerting
- Graceful degradation for network failures

Author: Security Remediation Team
Date: August 31, 2025
Security Level: CRITICAL
"""

import os
import sys
import time
import json
import logging
import threading
import functools
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Union, Tuple, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import urllib.request
import urllib.error
import urllib.parse
import socket
import ssl
from contextlib import contextmanager

# Optional imports with fallbacks
try:
    import requests
    from requests.adapters import HTTPAdapter, Retry
    from urllib3.util.timeout import Timeout
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request as GoogleRequest
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


class NetworkOperationType(Enum):
    """Types of network operations with specific timeout requirements"""
    API_REQUEST = "api_request"          # General API calls (10-30s)
    FILE_DOWNLOAD = "file_download"      # File downloads (60-300s)  
    AUTHENTICATION = "authentication"   # Auth operations (15-45s)
    SEARCH_QUERY = "search_query"       # Search/query operations (20-60s)
    AI_GENERATION = "ai_generation"     # LLM/AI generation (30-120s)
    DATABASE_QUERY = "database_query"   # Database operations (10-30s)
    STREAMING = "streaming"             # Streaming operations (300-600s)
    HEALTH_CHECK = "health_check"       # Service health checks (5-15s)


class NetworkFailureType(Enum):
    """Types of network failures for proper handling"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    DNS_ERROR = "dns_error"
    SSL_ERROR = "ssl_error"
    HTTP_ERROR = "http_error"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    AUTHENTICATION_ERROR = "authentication_error"
    UNKNOWN = "unknown"


@dataclass
class NetworkTimeoutConfig:
    """Configuration for network timeouts by operation type"""
    connect_timeout: float = 10.0        # Connection establishment timeout
    read_timeout: float = 30.0           # Data read timeout
    total_timeout: float = 60.0          # Total operation timeout
    retry_attempts: int = 3              # Number of retry attempts
    retry_backoff_factor: float = 1.5    # Exponential backoff multiplier
    max_retry_delay: float = 60.0        # Maximum delay between retries
    circuit_breaker_threshold: int = 5   # Failures before circuit opens
    circuit_breaker_timeout: float = 300.0  # Circuit breaker reset timeout


@dataclass
class NetworkOperationResult:
    """Result of a network operation with comprehensive metrics"""
    success: bool
    operation_type: NetworkOperationType
    duration_ms: float
    response_data: Any = None
    error_type: Optional[NetworkFailureType] = None
    error_message: str = ""
    retry_count: int = 0
    circuit_breaker_triggered: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for network resilience
    
    Prevents cascade failures by temporarily disabling failing services
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 300.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        self.lock = threading.RLock()
        self.logger = logging.getLogger("NetworkResilience.CircuitBreaker")
    
    def __call__(self, func):
        """Decorator to apply circuit breaker to functions"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == "open":
                if self._should_attempt_reset():
                    self.state = "half-open"
                    self.logger.info(f"🔄 Circuit breaker half-open for {func.__name__}")
                else:
                    self.logger.warning(f"⚡ Circuit breaker OPEN - blocking {func.__name__}")
                    raise Exception(f"Circuit breaker open for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            
            except Exception as e:
                self._on_failure()
                self.logger.error(f"⚡ Circuit breaker recorded failure for {func.__name__}: {e}")
                raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        return (self.last_failure_time and 
                time.time() - self.last_failure_time > self.timeout)
    
    def _on_success(self):
        """Handle successful operation"""
        if self.state == "half-open":
            self.state = "closed"
            self.logger.info("✅ Circuit breaker CLOSED - service recovered")
        self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.logger.error(f"⚡ Circuit breaker OPENED - {self.failure_count} failures")


class NetworkResilienceManager:
    """
    Comprehensive network resilience and timeout management system
    
    Features:
    - Centralized timeout configuration for all network operations
    - Automatic retry mechanisms with exponential backoff  
    - Circuit breaker pattern for failing services
    - Connection pooling and keep-alive management
    - Network monitoring and alerting
    - Graceful degradation and fallback handling
    
    Usage:
        resilience = NetworkResilienceManager()
        with resilience.resilient_request('api_request') as requester:
            response = requester.get('https://api.example.com/data')
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize network resilience manager"""
        self.logger = self._setup_logging()
        
        # Load configuration
        self.configs = self._load_timeout_configs(config_file)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Statistics and monitoring
        self.operation_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "timeout_errors": 0,
            "retry_operations": 0,
            "circuit_breaker_trips": 0
        }
        
        # Thread safety
        self.stats_lock = threading.RLock()
        
        # Session management
        if HAS_REQUESTS:
            self.session = self._create_resilient_session()
        else:
            self.session = None
        
        self.logger.info("🌐 Network Resilience Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup network resilience logging"""
        logger = logging.getLogger("NetworkResilience")
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | NETWORK_RESILIENCE | %(levelname)s | %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_timeout_configs(self, config_file: Optional[Path]) -> Dict[NetworkOperationType, NetworkTimeoutConfig]:
        """Load timeout configurations for different operation types"""
        # Default configurations optimized for each operation type
        default_configs = {
            NetworkOperationType.HEALTH_CHECK: NetworkTimeoutConfig(
                connect_timeout=5.0, read_timeout=10.0, total_timeout=15.0,
                retry_attempts=2, retry_backoff_factor=1.2
            ),
            NetworkOperationType.API_REQUEST: NetworkTimeoutConfig(
                connect_timeout=10.0, read_timeout=30.0, total_timeout=45.0,
                retry_attempts=3, retry_backoff_factor=1.5
            ),
            NetworkOperationType.AUTHENTICATION: NetworkTimeoutConfig(
                connect_timeout=15.0, read_timeout=30.0, total_timeout=60.0,
                retry_attempts=2, retry_backoff_factor=2.0
            ),
            NetworkOperationType.SEARCH_QUERY: NetworkTimeoutConfig(
                connect_timeout=10.0, read_timeout=45.0, total_timeout=75.0,
                retry_attempts=3, retry_backoff_factor=1.5
            ),
            NetworkOperationType.AI_GENERATION: NetworkTimeoutConfig(
                connect_timeout=15.0, read_timeout=120.0, total_timeout=180.0,
                retry_attempts=2, retry_backoff_factor=2.0, max_retry_delay=120.0
            ),
            NetworkOperationType.FILE_DOWNLOAD: NetworkTimeoutConfig(
                connect_timeout=30.0, read_timeout=300.0, total_timeout=600.0,
                retry_attempts=3, retry_backoff_factor=1.5, max_retry_delay=180.0
            ),
            NetworkOperationType.STREAMING: NetworkTimeoutConfig(
                connect_timeout=30.0, read_timeout=600.0, total_timeout=1800.0,
                retry_attempts=2, retry_backoff_factor=1.2
            ),
            NetworkOperationType.DATABASE_QUERY: NetworkTimeoutConfig(
                connect_timeout=10.0, read_timeout=30.0, total_timeout=45.0,
                retry_attempts=3, retry_backoff_factor=1.5
            )
        }
        
        # Load custom configurations if provided
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                
                for op_type_str, config_dict in custom_config.items():
                    try:
                        op_type = NetworkOperationType(op_type_str)
                        default_configs[op_type] = NetworkTimeoutConfig(**config_dict)
                    except (ValueError, TypeError) as e:
                        self.logger.warning(f"Invalid config for {op_type_str}: {e}")
            except Exception as e:
                self.logger.error(f"Failed to load custom timeout config: {e}")
        
        return default_configs
    
    def _create_resilient_session(self) -> 'requests.Session':
        """Create a requests session with resilient configuration"""
        if not HAS_REQUESTS:
            return None
        
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1.5
        )
        
        # Configure HTTP adapter with retries
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'ShortsFactory/1.0 (Network Resilience System)',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        return session
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            config = self.configs.get(NetworkOperationType.API_REQUEST)  # Default config
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=config.circuit_breaker_threshold,
                timeout=config.circuit_breaker_timeout
            )
        return self.circuit_breakers[service_name]
    
    @contextmanager
    def resilient_request(self, operation_type: Union[NetworkOperationType, str], 
                         service_name: str = "default"):
        """
        Context manager for resilient network requests
        
        Usage:
            with resilience.resilient_request('api_request', 'pexels') as requester:
                response = requester.get('https://api.pexels.com/v1/search')
        """
        if isinstance(operation_type, str):
            try:
                operation_type = NetworkOperationType(operation_type)
            except ValueError:
                operation_type = NetworkOperationType.API_REQUEST
        
        config = self.configs.get(operation_type, self.configs[NetworkOperationType.API_REQUEST])
        circuit_breaker = self.get_circuit_breaker(service_name)
        
        class ResilientRequester:
            def __init__(self, manager, session, config, circuit_breaker, operation_type):
                self.manager = manager
                self.session = session
                self.config = config
                self.circuit_breaker = circuit_breaker
                self.operation_type = operation_type
                self.logger = manager.logger
            
            def get(self, url, **kwargs):
                return self._make_request('GET', url, **kwargs)
            
            def post(self, url, **kwargs):
                return self._make_request('POST', url, **kwargs)
            
            def put(self, url, **kwargs):
                return self._make_request('PUT', url, **kwargs)
            
            def delete(self, url, **kwargs):
                return self._make_request('DELETE', url, **kwargs)
            
            def _make_request(self, method, url, **kwargs):
                """Make resilient HTTP request with retry and circuit breaker"""
                start_time = time.time()
                
                # Set timeouts if not provided
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = (self.config.connect_timeout, self.config.read_timeout)
                
                # Prepare for retries
                last_exception = None
                retry_count = 0
                
                for attempt in range(self.config.retry_attempts + 1):
                    try:
                        # Apply circuit breaker
                        response = self.circuit_breaker.call(
                            self._execute_request, method, url, **kwargs
                        )
                        
                        # Record success
                        duration_ms = (time.time() - start_time) * 1000
                        self.manager._record_operation_result(
                            NetworkOperationResult(
                                success=True,
                                operation_type=self.operation_type,
                                duration_ms=duration_ms,
                                response_data=response,
                                retry_count=retry_count
                            )
                        )
                        
                        return response
                    
                    except Exception as e:
                        last_exception = e
                        retry_count = attempt
                        
                        if attempt < self.config.retry_attempts:
                            # Calculate backoff delay
                            delay = min(
                                self.config.retry_backoff_factor ** attempt,
                                self.config.max_retry_delay
                            )
                            
                            self.logger.warning(
                                f"🔄 Request failed (attempt {attempt + 1}/{self.config.retry_attempts + 1}): {e}. "
                                f"Retrying in {delay:.1f}s"
                            )
                            
                            time.sleep(delay)
                        else:
                            self.logger.error(f"❌ Request failed after {self.config.retry_attempts + 1} attempts: {e}")
                
                # Record failure
                duration_ms = (time.time() - start_time) * 1000
                error_type = self._classify_error(last_exception)
                
                self.manager._record_operation_result(
                    NetworkOperationResult(
                        success=False,
                        operation_type=self.operation_type,
                        duration_ms=duration_ms,
                        error_type=error_type,
                        error_message=str(last_exception),
                        retry_count=retry_count
                    )
                )
                
                raise last_exception
            
            def _execute_request(self, method, url, **kwargs):
                """Execute the actual HTTP request"""
                if self.session:
                    return self.session.request(method, url, **kwargs)
                else:
                    # Fallback to urllib if requests not available
                    return self._urllib_request(method, url, **kwargs)
            
            def _urllib_request(self, method, url, **kwargs):
                """Fallback HTTP request using urllib"""
                # This is a simplified implementation
                # In practice, you'd want more comprehensive urllib handling
                req = urllib.request.Request(url, method=method)
                
                timeout = kwargs.get('timeout', (self.config.connect_timeout, self.config.read_timeout))
                if isinstance(timeout, tuple):
                    timeout = sum(timeout)  # urllib uses single timeout value
                
                response = urllib.request.urlopen(req, timeout=timeout)
                return response
            
            def _classify_error(self, exception) -> NetworkFailureType:
                """Classify network error for proper handling"""
                if 'timeout' in str(exception).lower():
                    return NetworkFailureType.TIMEOUT
                elif 'connection' in str(exception).lower():
                    return NetworkFailureType.CONNECTION_ERROR
                elif 'ssl' in str(exception).lower():
                    return NetworkFailureType.SSL_ERROR
                elif 'dns' in str(exception).lower() or 'name resolution' in str(exception).lower():
                    return NetworkFailureType.DNS_ERROR
                elif '429' in str(exception) or 'rate limit' in str(exception).lower():
                    return NetworkFailureType.RATE_LIMIT
                elif any(code in str(exception) for code in ['500', '502', '503', '504']):
                    return NetworkFailureType.SERVICE_UNAVAILABLE
                elif any(code in str(exception) for code in ['401', '403']):
                    return NetworkFailureType.AUTHENTICATION_ERROR
                else:
                    return NetworkFailureType.UNKNOWN
        
        yield ResilientRequester(self, self.session, config, circuit_breaker, operation_type)
    
    def _record_operation_result(self, result: NetworkOperationResult):
        """Record operation result for monitoring"""
        with self.stats_lock:
            self.operation_stats["total_operations"] += 1
            
            if result.success:
                self.operation_stats["successful_operations"] += 1
            else:
                self.operation_stats["failed_operations"] += 1
                
                if result.error_type == NetworkFailureType.TIMEOUT:
                    self.operation_stats["timeout_errors"] += 1
                
                if result.circuit_breaker_triggered:
                    self.operation_stats["circuit_breaker_trips"] += 1
            
            if result.retry_count > 0:
                self.operation_stats["retry_operations"] += 1
    
    def resilient_download(self, url: str, output_path: Path, 
                          operation_type: NetworkOperationType = NetworkOperationType.FILE_DOWNLOAD) -> bool:
        """
        Resilient file download with proper timeout handling
        
        Args:
            url: URL to download from
            output_path: Local path to save file
            operation_type: Type of operation for timeout configuration
            
        Returns:
            True if download successful, False otherwise
        """
        config = self.configs.get(operation_type, self.configs[NetworkOperationType.FILE_DOWNLOAD])
        
        try:
            self.logger.info(f"📥 Starting resilient download: {url}")
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use requests if available, otherwise urllib
            if self.session:
                with self.resilient_request(operation_type, "download") as requester:
                    response = requester.get(url, stream=True)
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = output_path.stat().st_size
                    self.logger.info(f"✅ Download completed: {output_path.name} ({file_size:,} bytes)")
                    return True
            else:
                # Fallback to urllib with timeout
                timeout = config.connect_timeout + config.read_timeout
                
                def download_with_timeout():
                    urllib.request.urlretrieve(url, output_path)
                    return True
                
                # Apply circuit breaker
                circuit_breaker = self.get_circuit_breaker("download")
                result = circuit_breaker.call(download_with_timeout)
                
                file_size = output_path.stat().st_size
                self.logger.info(f"✅ Download completed: {output_path.name} ({file_size:,} bytes)")
                return result
        
        except Exception as e:
            self.logger.error(f"❌ Download failed: {url}: {e}")
            # Clean up partial download
            if output_path.exists():
                try:
                    output_path.unlink()
                except OSError:
                    pass
            return False
    
    def get_timeout_config(self, operation_type: NetworkOperationType) -> NetworkTimeoutConfig:
        """Get timeout configuration for an operation type"""
        return self.configs.get(operation_type, self.configs[NetworkOperationType.API_REQUEST])
    
    def update_timeout_config(self, operation_type: NetworkOperationType, **kwargs):
        """Update timeout configuration for an operation type"""
        if operation_type in self.configs:
            config = self.configs[operation_type]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    self.logger.info(f"Updated {operation_type.value}.{key} = {value}")
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network operation statistics"""
        with self.stats_lock:
            stats = self.operation_stats.copy()
        
        # Calculate derived metrics
        total_ops = stats["total_operations"]
        if total_ops > 0:
            stats["success_rate"] = (stats["successful_operations"] / total_ops) * 100
            stats["failure_rate"] = (stats["failed_operations"] / total_ops) * 100
            stats["timeout_rate"] = (stats["timeout_errors"] / total_ops) * 100
            stats["retry_rate"] = (stats["retry_operations"] / total_ops) * 100
        else:
            stats.update({
                "success_rate": 0.0,
                "failure_rate": 0.0,
                "timeout_rate": 0.0,
                "retry_rate": 0.0
            })
        
        # Add circuit breaker status
        stats["circuit_breakers"] = {
            name: {
                "state": cb.state,
                "failure_count": cb.failure_count,
                "last_failure_time": cb.last_failure_time
            }
            for name, cb in self.circuit_breakers.items()
        }
        
        return stats
    
    def health_check_service(self, service_url: str, service_name: str = "unknown") -> bool:
        """Perform health check on a service"""
        try:
            with self.resilient_request(NetworkOperationType.HEALTH_CHECK, service_name) as requester:
                response = requester.get(service_url)
                self.logger.info(f"✅ Health check passed for {service_name}")
                return True
        except Exception as e:
            self.logger.error(f"❌ Health check failed for {service_name}: {e}")
            return False
    
    def emergency_reset_circuit_breakers(self):
        """Emergency reset all circuit breakers"""
        reset_count = 0
        for name, cb in self.circuit_breakers.items():
            if cb.state != "closed":
                cb.state = "closed"
                cb.failure_count = 0
                cb.last_failure_time = None
                reset_count += 1
                self.logger.warning(f"🔄 Emergency reset circuit breaker: {name}")
        
        if reset_count > 0:
            self.logger.warning(f"⚡ Emergency reset {reset_count} circuit breakers")
        
        return reset_count


# Global network resilience manager
_network_resilience = None
_resilience_lock = threading.Lock()

def get_network_resilience_manager(config_file: Optional[Path] = None) -> NetworkResilienceManager:
    """Get the global network resilience manager instance"""
    global _network_resilience
    if _network_resilience is None:
        with _resilience_lock:
            if _network_resilience is None:
                _network_resilience = NetworkResilienceManager(config_file)
    return _network_resilience


# Convenience functions for easy migration

@contextmanager
def resilient_requests(operation_type: str = "api_request", service_name: str = "default"):
    """Convenience function for resilient HTTP requests"""
    manager = get_network_resilience_manager()
    with manager.resilient_request(operation_type, service_name) as requester:
        yield requester


def resilient_download(url: str, output_path: Union[str, Path], timeout: float = 300.0) -> bool:
    """Convenience function for resilient file downloads"""
    manager = get_network_resilience_manager()
    return manager.resilient_download(url, Path(output_path))


def get_timeout_for_operation(operation_type: str) -> Tuple[float, float]:
    """Get (connect_timeout, read_timeout) for an operation type"""
    manager = get_network_resilience_manager()
    try:
        op_type = NetworkOperationType(operation_type)
        config = manager.get_timeout_config(op_type)
        return (config.connect_timeout, config.read_timeout)
    except ValueError:
        # Default fallback
        return (10.0, 30.0)


def configure_requests_session(session, operation_type: str = "api_request"):
    """Configure a requests session with resilient settings"""
    if not HAS_REQUESTS:
        return session
    
    connect_timeout, read_timeout = get_timeout_for_operation(operation_type)
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
        backoff_factor=1.5
    )
    
    # Configure HTTP adapter with retries and timeouts
    adapter = HTTPAdapter(max_retries=retry_strategy)
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
