"""
Syntari Error Handling System
Provides comprehensive error management with error codes, recovery strategies, and user-friendly messages
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


class ErrorCategory(Enum):
    """Error categories for classification"""
    LEXER = "lexer"
    PARSER = "parser"
    RUNTIME = "runtime"
    TYPE = "type"
    IMPORT = "import"
    IO = "io"
    SYSTEM = "system"
    SECURITY = "security"
    NETWORK = "network"
    INTERNAL = "internal"


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorCode:
    """Structured error code with category and number"""
    category: ErrorCategory
    number: int
    
    def __str__(self) -> str:
        return f"{self.category.value.upper()}{self.number:04d}"
    
    def __repr__(self) -> str:
        return f"ErrorCode({self.category.value}, {self.number})"


class SyntariError(Exception):
    """
    Base exception class for all Syntari errors.
    
    Provides structured error information including:
    - Error code
    - User-friendly message
    - Technical details
    - Source location
    - Suggestions for fixing
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[ErrorCode] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        file: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Syntari error.
        
        Args:
            message: User-friendly error message
            code: Error code
            severity: Error severity
            file: Source file name
            line: Line number (1-indexed)
            column: Column number (1-indexed)
            details: Technical details
            suggestions: List of suggestions to fix the error
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.severity = severity
        self.file = file
        self.line = line
        self.column = column
        self.details = details
        self.suggestions = suggestions or []
        self.context = context or {}
    
    def __str__(self) -> str:
        """Format error for display"""
        parts = []
        
        # Error code and severity
        if self.code:
            parts.append(f"[{self.code}]")
        parts.append(f"{self.severity.value.upper()}:")
        
        # Location
        if self.file:
            location = self.file
            if self.line:
                location += f":{self.line}"
                if self.column:
                    location += f":{self.column}"
            parts.append(location)
            parts.append("-")
        
        # Message
        parts.append(self.message)
        
        result = " ".join(parts)
        
        # Details
        if self.details:
            result += f"\n\nDetails: {self.details}"
        
        # Suggestions
        if self.suggestions:
            result += "\n\nSuggestions:"
            for i, suggestion in enumerate(self.suggestions, 1):
                result += f"\n  {i}. {suggestion}"
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "message": self.message,
            "code": str(self.code) if self.code else None,
            "severity": self.severity.value,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "details": self.details,
            "suggestions": self.suggestions,
            "context": self.context,
        }


# Specific error types


class LexerError(SyntariError):
    """Lexer/tokenization errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.LEXER, 1000)
        super().__init__(message, **kwargs)


class ParseError(SyntariError):
    """Parser/syntax errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.PARSER, 2000)
        super().__init__(message, **kwargs)


class RuntimeError(SyntariError):
    """Runtime execution errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.RUNTIME, 3000)
        super().__init__(message, **kwargs)


class TypeError(SyntariError):
    """Type errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.TYPE, 4000)
        super().__init__(message, **kwargs)


class ImportError(SyntariError):
    """Import/module errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.IMPORT, 5000)
        super().__init__(message, **kwargs)


class IOError(SyntariError):
    """I/O errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.IO, 6000)
        super().__init__(message, **kwargs)


class SystemError(SyntariError):
    """System-level errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.SYSTEM, 7000)
        super().__init__(message, **kwargs)


class SecurityError(SyntariError):
    """Security-related errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.SECURITY, 8000)
        kwargs["severity"] = ErrorSeverity.CRITICAL
        super().__init__(message, **kwargs)


class NetworkError(SyntariError):
    """Network-related errors"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.NETWORK, 9000)
        super().__init__(message, **kwargs)


class InternalError(SyntariError):
    """Internal compiler/interpreter errors (bugs)"""
    
    def __init__(self, message: str, **kwargs):
        if "code" not in kwargs:
            kwargs["code"] = ErrorCode(ErrorCategory.INTERNAL, 9999)
        kwargs["severity"] = ErrorSeverity.CRITICAL
        super().__init__(
            message,
            details="This is an internal error. Please report this bug.",
            **kwargs,
        )


# Error handling utilities


class ErrorHandler:
    """Centralized error handler with recovery strategies"""
    
    def __init__(self, strict: bool = False, logger=None):
        """
        Initialize error handler.
        
        Args:
            strict: If True, all errors are fatal
            logger: Logger instance for error logging
        """
        self.strict = strict
        self.logger = logger
        self.errors: List[SyntariError] = []
        self.warnings: List[SyntariError] = []
    
    def handle(self, error: SyntariError, fatal: bool = False):
        """
        Handle an error.
        
        Args:
            error: Error to handle
            fatal: If True, raise immediately
        
        Raises:
            SyntariError: If fatal or strict mode
        """
        # Log error
        if self.logger:
            if error.severity == ErrorSeverity.WARNING:
                self.logger.warning(str(error), **error.context)
            elif error.severity == ErrorSeverity.CRITICAL:
                self.logger.critical(str(error), **error.context)
            else:
                self.logger.error(str(error), **error.context)
        
        # Store error
        if error.severity == ErrorSeverity.WARNING:
            self.warnings.append(error)
        else:
            self.errors.append(error)
        
        # Raise if fatal or strict
        if fatal or self.strict or error.severity == ErrorSeverity.CRITICAL:
            raise error
    
    def has_errors(self) -> bool:
        """Check if any errors occurred"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings occurred"""
        return len(self.warnings) > 0
    
    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()
    
    def get_error_summary(self) -> str:
        """Get a summary of all errors"""
        if not self.errors and not self.warnings:
            return "No errors or warnings."
        
        parts = []
        
        if self.errors:
            parts.append(f"{len(self.errors)} error(s):")
            for error in self.errors:
                parts.append(f"  - {error}")
        
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s):")
            for warning in self.warnings:
                parts.append(f"  - {warning}")
        
        return "\n".join(parts)


# Error recovery strategies


def recover_from_syntax_error(error: ParseError) -> Optional[str]:
    """
    Suggest recovery from syntax error.
    
    Args:
        error: Parse error
    
    Returns:
        Recovery suggestion or None
    """
    message = error.message.lower()
    
    if "unexpected" in message and "expected" in message:
        return "Check for missing or extra punctuation"
    
    if "unterminated" in message:
        return "Add the closing delimiter"
    
    if "missing" in message:
        return "Add the missing syntax element"
    
    return "Review the syntax and try again"


def suggest_fix(error: SyntariError) -> List[str]:
    """
    Generate fix suggestions for an error.
    
    Args:
        error: Error to suggest fixes for
    
    Returns:
        List of suggestions
    """
    suggestions = []
    
    if isinstance(error, LexerError):
        suggestions.append("Check for invalid characters in the source code")
        suggestions.append("Ensure string literals are properly quoted")
    
    elif isinstance(error, ParseError):
        suggestions.append("Review the syntax specification")
        suggestions.append("Check for missing or mismatched brackets/braces")
        recovery = recover_from_syntax_error(error)
        if recovery:
            suggestions.append(recovery)
    
    elif isinstance(error, RuntimeError):
        suggestions.append("Check the values being used")
        suggestions.append("Ensure variables are defined before use")
    
    elif isinstance(error, TypeError):
        suggestions.append("Check the types of the operands")
        suggestions.append("Add explicit type conversions if needed")
    
    elif isinstance(error, ImportError):
        suggestions.append("Verify the module name is correct")
        suggestions.append("Ensure the module is installed")
    
    elif isinstance(error, IOError):
        suggestions.append("Check that the file exists and is readable")
        suggestions.append("Verify file permissions")
    
    elif isinstance(error, SecurityError):
        suggestions.append("Review security policies")
        suggestions.append("Check for suspicious code patterns")
    
    elif isinstance(error, NetworkError):
        suggestions.append("Check network connectivity")
        suggestions.append("Verify the URL or address is correct")
    
    return suggestions


# Predefined error codes

ERROR_CODES = {
    # Lexer errors (1000-1999)
    "INVALID_CHARACTER": ErrorCode(ErrorCategory.LEXER, 1001),
    "UNTERMINATED_STRING": ErrorCode(ErrorCategory.LEXER, 1002),
    "INVALID_NUMBER": ErrorCode(ErrorCategory.LEXER, 1003),
    
    # Parser errors (2000-2999)
    "UNEXPECTED_TOKEN": ErrorCode(ErrorCategory.PARSER, 2001),
    "MISSING_SEMICOLON": ErrorCode(ErrorCategory.PARSER, 2002),
    "MISSING_BRACE": ErrorCode(ErrorCategory.PARSER, 2003),
    "MISSING_PAREN": ErrorCode(ErrorCategory.PARSER, 2004),
    "INVALID_SYNTAX": ErrorCode(ErrorCategory.PARSER, 2005),
    
    # Runtime errors (3000-3999)
    "UNDEFINED_VARIABLE": ErrorCode(ErrorCategory.RUNTIME, 3001),
    "UNDEFINED_FUNCTION": ErrorCode(ErrorCategory.RUNTIME, 3002),
    "DIVISION_BY_ZERO": ErrorCode(ErrorCategory.RUNTIME, 3003),
    "INDEX_OUT_OF_BOUNDS": ErrorCode(ErrorCategory.RUNTIME, 3004),
    "NULL_REFERENCE": ErrorCode(ErrorCategory.RUNTIME, 3005),
    
    # Type errors (4000-4999)
    "TYPE_MISMATCH": ErrorCode(ErrorCategory.TYPE, 4001),
    "INVALID_OPERATION": ErrorCode(ErrorCategory.TYPE, 4002),
    "INCOMPATIBLE_TYPES": ErrorCode(ErrorCategory.TYPE, 4003),
    
    # Import errors (5000-5999)
    "MODULE_NOT_FOUND": ErrorCode(ErrorCategory.IMPORT, 5001),
    "CIRCULAR_IMPORT": ErrorCode(ErrorCategory.IMPORT, 5002),
    
    # I/O errors (6000-6999)
    "FILE_NOT_FOUND": ErrorCode(ErrorCategory.IO, 6001),
    "PERMISSION_DENIED": ErrorCode(ErrorCategory.IO, 6002),
    "DISK_FULL": ErrorCode(ErrorCategory.IO, 6003),
    
    # System errors (7000-7999)
    "OUT_OF_MEMORY": ErrorCode(ErrorCategory.SYSTEM, 7001),
    "STACK_OVERFLOW": ErrorCode(ErrorCategory.SYSTEM, 7002),
    
    # Security errors (8000-8999)
    "UNAUTHORIZED_ACCESS": ErrorCode(ErrorCategory.SECURITY, 8001),
    "SANDBOX_VIOLATION": ErrorCode(ErrorCategory.SECURITY, 8002),
    
    # Network errors (9000-9998)
    "CONNECTION_FAILED": ErrorCode(ErrorCategory.NETWORK, 9001),
    "TIMEOUT": ErrorCode(ErrorCategory.NETWORK, 9002),
    "DNS_ERROR": ErrorCode(ErrorCategory.NETWORK, 9003),
}


def get_error_code(name: str) -> Optional[ErrorCode]:
    """Get error code by name"""
    return ERROR_CODES.get(name)
