"""
Tests for Syntari error handling system
"""

import pytest
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
    ERROR_CODES,
)


class TestErrorCode:
    """Tests for ErrorCode"""
    
    def test_error_code_creation(self):
        """Test creating an error code"""
        code = ErrorCode(ErrorCategory.LEXER, 1001)
        assert code.category == ErrorCategory.LEXER
        assert code.number == 1001
    
    def test_error_code_str(self):
        """Test error code string representation"""
        code = ErrorCode(ErrorCategory.PARSER, 2001)
        assert str(code) == "PARSER2001"
    
    def test_error_code_repr(self):
        """Test error code repr"""
        code = ErrorCode(ErrorCategory.RUNTIME, 3001)
        assert "ErrorCode" in repr(code)


class TestSyntariError:
    """Tests for base SyntariError"""
    
    def test_error_creation(self):
        """Test creating a basic error"""
        error = SyntariError("Test error")
        assert error.message == "Test error"
        assert error.severity == ErrorSeverity.ERROR
    
    def test_error_with_code(self):
        """Test error with code"""
        code = ErrorCode(ErrorCategory.LEXER, 1001)
        error = SyntariError("Test error", code=code)
        assert error.code == code
    
    def test_error_with_location(self):
        """Test error with source location"""
        error = SyntariError("Test error", file="test.syn", line=10, column=5)
        assert error.file == "test.syn"
        assert error.line == 10
        assert error.column == 5
    
    def test_error_with_details(self):
        """Test error with details"""
        error = SyntariError("Test error", details="Additional information")
        assert error.details == "Additional information"
    
    def test_error_with_suggestions(self):
        """Test error with suggestions"""
        suggestions = ["Try this", "Or try that"]
        error = SyntariError("Test error", suggestions=suggestions)
        assert len(error.suggestions) == 2
        assert "Try this" in error.suggestions
    
    def test_error_with_context(self):
        """Test error with context"""
        context = {"user": "test", "action": "compile"}
        error = SyntariError("Test error", context=context)
        assert error.context["user"] == "test"
    
    def test_error_str_basic(self):
        """Test basic error string"""
        error = SyntariError("Test error")
        s = str(error)
        assert "ERROR:" in s
        assert "Test error" in s
    
    def test_error_str_with_code(self):
        """Test error string with code"""
        code = ErrorCode(ErrorCategory.LEXER, 1001)
        error = SyntariError("Test error", code=code)
        s = str(error)
        assert "[LEXER1001]" in s
    
    def test_error_str_with_location(self):
        """Test error string with location"""
        error = SyntariError("Test error", file="test.syn", line=10)
        s = str(error)
        assert "test.syn:10" in s
    
    def test_error_str_with_suggestions(self):
        """Test error string with suggestions"""
        error = SyntariError("Test error", suggestions=["Fix 1", "Fix 2"])
        s = str(error)
        assert "Suggestions:" in s
        assert "Fix 1" in s
    
    def test_error_to_dict(self):
        """Test converting error to dict"""
        error = SyntariError(
            "Test error",
            code=ErrorCode(ErrorCategory.LEXER, 1001),
            file="test.syn",
            line=10,
        )
        d = error.to_dict()
        assert d["message"] == "Test error"
        assert d["code"] == "LEXER1001"
        assert d["file"] == "test.syn"
        assert d["line"] == 10


class TestSpecificErrors:
    """Tests for specific error types"""
    
    def test_lexer_error(self):
        """Test lexer error"""
        error = LexerError("Invalid character")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.LEXER
    
    def test_parse_error(self):
        """Test parse error"""
        error = ParseError("Unexpected token")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.PARSER
    
    def test_runtime_error(self):
        """Test runtime error"""
        error = RuntimeError("Undefined variable")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.RUNTIME
    
    def test_type_error(self):
        """Test type error"""
        error = TypeError("Type mismatch")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.TYPE
    
    def test_import_error(self):
        """Test import error"""
        error = ImportError("Module not found")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.IMPORT
    
    def test_io_error(self):
        """Test I/O error"""
        error = IOError("File not found")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.IO
    
    def test_system_error(self):
        """Test system error"""
        error = SystemError("Out of memory")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.SYSTEM
    
    def test_security_error(self):
        """Test security error"""
        error = SecurityError("Unauthorized access")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.SECURITY
        assert error.severity == ErrorSeverity.CRITICAL
    
    def test_network_error(self):
        """Test network error"""
        error = NetworkError("Connection failed")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.NETWORK
    
    def test_internal_error(self):
        """Test internal error"""
        error = InternalError("Compiler bug")
        assert isinstance(error, SyntariError)
        assert error.code.category == ErrorCategory.INTERNAL
        assert error.severity == ErrorSeverity.CRITICAL


class TestErrorHandler:
    """Tests for ErrorHandler"""
    
    def test_error_handler_creation(self):
        """Test creating error handler"""
        handler = ErrorHandler()
        assert not handler.strict
        assert len(handler.errors) == 0
    
    def test_error_handler_strict_mode(self):
        """Test strict mode"""
        handler = ErrorHandler(strict=True)
        assert handler.strict
        
        error = SyntariError("Test error")
        with pytest.raises(SyntariError):
            handler.handle(error)
    
    def test_handle_error(self):
        """Test handling an error"""
        handler = ErrorHandler()
        error = SyntariError("Test error")
        handler.handle(error)
        
        assert len(handler.errors) == 1
        assert handler.errors[0] == error
    
    def test_handle_warning(self):
        """Test handling a warning"""
        handler = ErrorHandler()
        warning = SyntariError("Test warning", severity=ErrorSeverity.WARNING)
        handler.handle(warning)
        
        assert len(handler.warnings) == 1
        assert len(handler.errors) == 0
    
    def test_handle_fatal_error(self):
        """Test handling fatal error"""
        handler = ErrorHandler()
        error = SyntariError("Fatal error")
        
        with pytest.raises(SyntariError):
            handler.handle(error, fatal=True)
    
    def test_handle_critical_error(self):
        """Test handling critical error"""
        handler = ErrorHandler()
        error = SecurityError("Critical security issue")
        
        with pytest.raises(SecurityError):
            handler.handle(error)
    
    def test_has_errors(self):
        """Test checking for errors"""
        handler = ErrorHandler()
        assert not handler.has_errors()
        
        handler.handle(SyntariError("Test"))
        assert handler.has_errors()
    
    def test_has_warnings(self):
        """Test checking for warnings"""
        handler = ErrorHandler()
        assert not handler.has_warnings()
        
        handler.handle(SyntariError("Test", severity=ErrorSeverity.WARNING))
        assert handler.has_warnings()
    
    def test_clear_errors(self):
        """Test clearing errors"""
        handler = ErrorHandler()
        handler.handle(SyntariError("Test"))
        assert handler.has_errors()
        
        handler.clear()
        assert not handler.has_errors()
    
    def test_get_error_summary(self):
        """Test getting error summary"""
        handler = ErrorHandler()
        
        # No errors
        summary = handler.get_error_summary()
        assert "No errors" in summary
        
        # With errors
        handler.handle(SyntariError("Error 1"))
        handler.handle(SyntariError("Error 2"))
        summary = handler.get_error_summary()
        assert "2 error(s)" in summary


class TestErrorRecovery:
    """Tests for error recovery"""
    
    def test_recover_from_syntax_error_unexpected(self):
        """Test recovery for unexpected token"""
        error = ParseError("Unexpected token, expected semicolon")
        recovery = recover_from_syntax_error(error)
        assert recovery is not None
        assert "punctuation" in recovery.lower()
    
    def test_recover_from_syntax_error_unterminated(self):
        """Test recovery for unterminated string"""
        error = ParseError("Unterminated string literal")
        recovery = recover_from_syntax_error(error)
        assert recovery is not None
        assert "closing" in recovery.lower()
    
    def test_recover_from_syntax_error_missing(self):
        """Test recovery for missing element"""
        error = ParseError("Missing closing brace")
        recovery = recover_from_syntax_error(error)
        assert recovery is not None
        assert "missing" in recovery.lower()
    
    def test_suggest_fix_lexer(self):
        """Test suggestions for lexer error"""
        error = LexerError("Invalid character")
        suggestions = suggest_fix(error)
        assert len(suggestions) > 0
        assert any("character" in s.lower() for s in suggestions)
    
    def test_suggest_fix_parser(self):
        """Test suggestions for parser error"""
        error = ParseError("Unexpected token")
        suggestions = suggest_fix(error)
        assert len(suggestions) > 0
        assert any("syntax" in s.lower() for s in suggestions)
    
    def test_suggest_fix_runtime(self):
        """Test suggestions for runtime error"""
        error = RuntimeError("Undefined variable")
        suggestions = suggest_fix(error)
        assert len(suggestions) > 0
        assert any("variable" in s.lower() for s in suggestions)
    
    def test_suggest_fix_type(self):
        """Test suggestions for type error"""
        error = TypeError("Type mismatch")
        suggestions = suggest_fix(error)
        assert len(suggestions) > 0
        assert any("type" in s.lower() for s in suggestions)


class TestErrorCodes:
    """Tests for predefined error codes"""
    
    def test_error_codes_defined(self):
        """Test that error codes are defined"""
        assert "INVALID_CHARACTER" in ERROR_CODES
        assert "UNEXPECTED_TOKEN" in ERROR_CODES
        assert "UNDEFINED_VARIABLE" in ERROR_CODES
    
    def test_get_error_code(self):
        """Test getting error code by name"""
        code = get_error_code("INVALID_CHARACTER")
        assert code is not None
        assert code.category == ErrorCategory.LEXER
    
    def test_get_nonexistent_code(self):
        """Test getting non-existent error code"""
        code = get_error_code("NONEXISTENT")
        assert code is None
    
    def test_lexer_codes(self):
        """Test lexer error codes"""
        code = get_error_code("INVALID_CHARACTER")
        assert code.category == ErrorCategory.LEXER
        assert 1000 <= code.number < 2000
    
    def test_parser_codes(self):
        """Test parser error codes"""
        code = get_error_code("UNEXPECTED_TOKEN")
        assert code.category == ErrorCategory.PARSER
        assert 2000 <= code.number < 3000
    
    def test_runtime_codes(self):
        """Test runtime error codes"""
        code = get_error_code("UNDEFINED_VARIABLE")
        assert code.category == ErrorCategory.RUNTIME
        assert 3000 <= code.number < 4000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
