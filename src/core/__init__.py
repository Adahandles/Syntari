"""
Syntari Core Module
Provides core functionality including logging, system operations, AI integration, and networking
"""

from src.core.logging import (
    SyntariLogger,
    LogLevel,
    LogFormat,
    PerformanceLogger,
    get_logger,
    configure_logging,
    debug,
    info,
    warning,
    error,
    critical,
    exception,
)

from src.core.errors import (
    ErrorCategory,
    ErrorSeverity,
    ErrorCode,
    SyntariError,
    LexerError,
    ParseError,
    RuntimeError,
    TypeError,
    ImportError,
    IOError,
    SystemError,
    SecurityError,
    NetworkError,
    InternalError,
    ErrorHandler,
    recover_from_syntax_error,
    suggest_fix,
    get_error_code,
)

__all__ = [
    # Logging
    "SyntariLogger",
    "LogLevel",
    "LogFormat",
    "PerformanceLogger",
    "get_logger",
    "configure_logging",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    # Error Handling
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorCode",
    "SyntariError",
    "LexerError",
    "ParseError",
    "RuntimeError",
    "TypeError",
    "ImportError",
    "IOError",
    "SystemError",
    "SecurityError",
    "NetworkError",
    "InternalError",
    "ErrorHandler",
    "recover_from_syntax_error",
    "suggest_fix",
    "get_error_code",
]
