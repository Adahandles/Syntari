"""
Syntari Logging Infrastructure
Provides structured logging with multiple levels, formatters, and handlers
"""

import sys
import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Log levels for Syntari"""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormat(Enum):
    """Log output formats"""

    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"


class SyntariLogger:
    """
    Centralized logger for Syntari with structured logging support.

    Features:
    - Multiple log levels
    - File and console handlers
    - Log rotation
    - Structured (JSON) logging
    - Context injection
    - Performance tracking
    """

    def __init__(
        self,
        name: str = "syntari",
        level: LogLevel = LogLevel.INFO,
        format_type: LogFormat = LogFormat.TEXT,
        log_file: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console: bool = True,
    ):
        """
        Initialize Syntari logger.

        Args:
            name: Logger name
            level: Minimum log level
            format_type: Output format (text/json/structured)
            log_file: Path to log file (None = no file logging)
            max_bytes: Max log file size before rotation
            backup_count: Number of backup files to keep
            console: Whether to log to console
        """
        self.name = name
        self.level = level
        self.format_type = format_type
        self.context: Dict[str, Any] = {}

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        self.logger.handlers.clear()  # Remove any existing handlers

        # Console handler
        if console:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(level.value)
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)

        # File handler with rotation
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(level.value)
            file_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(file_handler)

    def _get_formatter(self) -> logging.Formatter:
        """Get formatter based on format type"""
        if self.format_type == LogFormat.JSON:
            return JsonFormatter()
        elif self.format_type == LogFormat.STRUCTURED:
            return StructuredFormatter()
        else:
            return logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

    def add_context(self, **kwargs):
        """Add context fields to all log messages"""
        self.context.update(kwargs)

    def remove_context(self, *keys):
        """Remove context fields"""
        for key in keys:
            self.context.pop(key, None)

    def clear_context(self):
        """Clear all context"""
        self.context.clear()

    def _build_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Build message with context"""
        if not extra:
            extra = {}

        # Merge context
        full_context = {**self.context, **extra}

        if self.format_type == LogFormat.TEXT:
            if full_context:
                context_str = " ".join(f"{k}={v}" for k, v in full_context.items())
                return f"{message} | {context_str}"
            return message
        else:
            return message

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        msg = self._build_message(message, kwargs)
        self.logger.debug(msg, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        msg = self._build_message(message, kwargs)
        self.logger.info(msg, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        msg = self._build_message(message, kwargs)
        self.logger.warning(msg, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        msg = self._build_message(message, kwargs)
        self.logger.error(msg, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        msg = self._build_message(message, kwargs)
        self.logger.critical(msg, extra=kwargs)

    def exception(self, message: str, exc_info=True, **kwargs):
        """Log exception with traceback"""
        msg = self._build_message(message, kwargs)
        self.logger.exception(msg, exc_info=exc_info, extra=kwargs)

    def set_level(self, level: LogLevel):
        """Change log level"""
        self.level = level
        self.logger.setLevel(level.value)
        for handler in self.logger.handlers:
            handler.setLevel(level.value)


class JsonFormatter(logging.Formatter):
    """JSON log formatter"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


class StructuredFormatter(logging.Formatter):
    """Structured (key=value) log formatter"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with key=value pairs"""
        fields = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                fields[key] = value

        # Format as key=value
        parts = [f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}" for k, v in fields.items()]

        # Add exception if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info).replace("\n", " | ")
            parts.append(f'exception="{exc_text}"')

        return " ".join(parts)


class PerformanceLogger:
    """Logger for performance metrics"""

    def __init__(self, logger: SyntariLogger):
        self.logger = logger
        self.metrics: Dict[str, list] = {}

    def log_execution_time(self, operation: str, duration_ms: float, **kwargs):
        """Log execution time for an operation"""
        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(duration_ms)

        self.logger.debug(
            f"Performance: {operation}",
            duration_ms=duration_ms,
            operation=operation,
            **kwargs,
        )

    def log_memory_usage(self, operation: str, bytes_used: int, **kwargs):
        """Log memory usage"""
        mb_used = bytes_used / (1024 * 1024)
        self.logger.debug(
            f"Memory: {operation}",
            memory_mb=round(mb_used, 2),
            memory_bytes=bytes_used,
            operation=operation,
            **kwargs,
        )

    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}

        times = self.metrics[operation]
        return {
            "count": len(times),
            "total_ms": sum(times),
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
        }

    def log_stats(self, operation: str):
        """Log statistics for an operation"""
        stats = self.get_stats(operation)
        if stats:
            self.logger.info(
                f"Stats for {operation}",
                operation=operation,
                **stats,
            )


# Global logger instance
_global_logger: Optional[SyntariLogger] = None


def get_logger(
    name: str = "syntari",
    level: Optional[LogLevel] = None,
    format_type: Optional[LogFormat] = None,
    **kwargs,
) -> SyntariLogger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name
        level: Log level (None = use default)
        format_type: Format type (None = use default)
        **kwargs: Additional logger arguments

    Returns:
        SyntariLogger instance
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = SyntariLogger(
            name=name,
            level=level or LogLevel.INFO,
            format_type=format_type or LogFormat.TEXT,
            **kwargs,
        )

    return _global_logger


def configure_logging(
    level: LogLevel = LogLevel.INFO,
    format_type: LogFormat = LogFormat.TEXT,
    log_file: Optional[str] = None,
    **kwargs,
):
    """
    Configure global logging settings.

    Args:
        level: Log level
        format_type: Format type
        log_file: Path to log file
        **kwargs: Additional logger arguments
    """
    global _global_logger

    _global_logger = SyntariLogger(
        name="syntari",
        level=level,
        format_type=format_type,
        log_file=log_file,
        **kwargs,
    )


# Convenience functions
def debug(message: str, **kwargs):
    """Log debug message using global logger"""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message using global logger"""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message using global logger"""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs):
    """Log error message using global logger"""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message using global logger"""
    get_logger().critical(message, **kwargs)


def exception(message: str, **kwargs):
    """Log exception using global logger"""
    get_logger().exception(message, **kwargs)
