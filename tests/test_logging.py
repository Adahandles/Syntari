"""
Tests for Syntari logging infrastructure
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.core.logging import (
    SyntariLogger,
    LogLevel,
    LogFormat,
    JsonFormatter,
    StructuredFormatter,
    PerformanceLogger,
    get_logger,
    configure_logging,
)


class TestLogLevel:
    """Tests for LogLevel enum"""
    
    def test_log_levels_exist(self):
        """Test all log levels are defined"""
        assert LogLevel.DEBUG
        assert LogLevel.INFO
        assert LogLevel.WARNING
        assert LogLevel.ERROR
        assert LogLevel.CRITICAL


class TestSyntariLogger:
    """Tests for SyntariLogger"""
    
    def test_logger_creation(self):
        """Test creating a logger"""
        logger = SyntariLogger(name="test", console=False)
        assert logger.name == "test"
        assert logger.level == LogLevel.INFO
        assert logger.format_type == LogFormat.TEXT
    
    def test_logger_with_level(self):
        """Test logger with custom level"""
        logger = SyntariLogger(name="test", level=LogLevel.DEBUG, console=False)
        assert logger.level == LogLevel.DEBUG
    
    def test_logger_with_format(self):
        """Test logger with custom format"""
        logger = SyntariLogger(name="test", format_type=LogFormat.JSON, console=False)
        assert logger.format_type == LogFormat.JSON
    
    def test_log_debug(self):
        """Test debug logging"""
        logger = SyntariLogger(name="test", level=LogLevel.DEBUG, console=False)
        logger.debug("Test message")  # Should not raise
    
    def test_log_info(self):
        """Test info logging"""
        logger = SyntariLogger(name="test", console=False)
        logger.info("Test message")  # Should not raise
    
    def test_log_warning(self):
        """Test warning logging"""
        logger = SyntariLogger(name="test", console=False)
        logger.warning("Test message")  # Should not raise
    
    def test_log_error(self):
        """Test error logging"""
        logger = SyntariLogger(name="test", console=False)
        logger.error("Test message")  # Should not raise
    
    def test_log_critical(self):
        """Test critical logging"""
        logger = SyntariLogger(name="test", console=False)
        logger.critical("Test message")  # Should not raise
    
    def test_log_exception(self):
        """Test exception logging"""
        logger = SyntariLogger(name="test", console=False)
        try:
            raise ValueError("Test error")
        except ValueError:
            logger.exception("Caught exception")  # Should not raise
    
    def test_add_context(self):
        """Test adding context"""
        logger = SyntariLogger(name="test", console=False)
        logger.add_context(user="test_user", session="abc123")
        assert "user" in logger.context
        assert "session" in logger.context
        assert logger.context["user"] == "test_user"
    
    def test_remove_context(self):
        """Test removing context"""
        logger = SyntariLogger(name="test", console=False)
        logger.add_context(user="test_user", session="abc123")
        logger.remove_context("user")
        assert "user" not in logger.context
        assert "session" in logger.context
    
    def test_clear_context(self):
        """Test clearing all context"""
        logger = SyntariLogger(name="test", console=False)
        logger.add_context(user="test_user", session="abc123")
        logger.clear_context()
        assert len(logger.context) == 0
    
    def test_set_level(self):
        """Test changing log level"""
        logger = SyntariLogger(name="test", level=LogLevel.INFO, console=False)
        logger.set_level(LogLevel.DEBUG)
        assert logger.level == LogLevel.DEBUG
    
    def test_log_with_extra_fields(self):
        """Test logging with extra fields"""
        logger = SyntariLogger(name="test", console=False)
        logger.info("Test", user_id=123, action="login")  # Should not raise
    
    def test_file_logging(self):
        """Test logging to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = SyntariLogger(name="test", log_file=str(log_file), console=False)
            logger.info("Test message")
            
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content
    
    def test_log_rotation(self):
        """Test log file rotation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = SyntariLogger(
                name="test",
                log_file=str(log_file),
                max_bytes=100,  # Small size to trigger rotation
                backup_count=2,
                console=False,
            )
            
            # Write enough to trigger rotation
            for i in range(50):
                logger.info(f"Message {i} with some padding text")
            
            # Check that log file exists
            assert log_file.exists()


class TestJsonFormatter:
    """Tests for JSON formatter"""
    
    def test_json_formatter_creation(self):
        """Test creating JSON formatter"""
        formatter = JsonFormatter()
        assert formatter is not None
    
    def test_json_format_basic(self):
        """Test basic JSON formatting"""
        import logging
        
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert "timestamp" in data


class TestStructuredFormatter:
    """Tests for structured formatter"""
    
    def test_structured_formatter_creation(self):
        """Test creating structured formatter"""
        formatter = StructuredFormatter()
        assert formatter is not None
    
    def test_structured_format_basic(self):
        """Test basic structured formatting"""
        import logging
        
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        output = formatter.format(record)
        
        assert 'level="INFO"' in output
        assert 'message="Test message"' in output
        assert "timestamp=" in output


class TestPerformanceLogger:
    """Tests for performance logger"""
    
    def test_performance_logger_creation(self):
        """Test creating performance logger"""
        base_logger = SyntariLogger(name="test", console=False)
        perf_logger = PerformanceLogger(base_logger)
        assert perf_logger is not None
    
    def test_log_execution_time(self):
        """Test logging execution time"""
        base_logger = SyntariLogger(name="test", console=False)
        perf_logger = PerformanceLogger(base_logger)
        
        perf_logger.log_execution_time("test_op", 123.45)
        
        assert "test_op" in perf_logger.metrics
        assert len(perf_logger.metrics["test_op"]) == 1
        assert perf_logger.metrics["test_op"][0] == 123.45
    
    def test_log_memory_usage(self):
        """Test logging memory usage"""
        base_logger = SyntariLogger(name="test", console=False)
        perf_logger = PerformanceLogger(base_logger)
        
        perf_logger.log_memory_usage("test_op", 1024 * 1024)  # 1MB
        # Should not raise
    
    def test_get_stats(self):
        """Test getting statistics"""
        base_logger = SyntariLogger(name="test", console=False)
        perf_logger = PerformanceLogger(base_logger)
        
        perf_logger.log_execution_time("test_op", 100)
        perf_logger.log_execution_time("test_op", 200)
        perf_logger.log_execution_time("test_op", 300)
        
        stats = perf_logger.get_stats("test_op")
        
        assert stats["count"] == 3
        assert stats["total_ms"] == 600
        assert stats["avg_ms"] == 200
        assert stats["min_ms"] == 100
        assert stats["max_ms"] == 300
    
    def test_get_stats_empty(self):
        """Test getting stats for non-existent operation"""
        base_logger = SyntariLogger(name="test", console=False)
        perf_logger = PerformanceLogger(base_logger)
        
        stats = perf_logger.get_stats("nonexistent")
        assert stats == {}
    
    def test_log_stats(self):
        """Test logging statistics"""
        base_logger = SyntariLogger(name="test", console=False)
        perf_logger = PerformanceLogger(base_logger)
        
        perf_logger.log_execution_time("test_op", 100)
        perf_logger.log_execution_time("test_op", 200)
        
        perf_logger.log_stats("test_op")  # Should not raise


class TestGlobalFunctions:
    """Tests for global convenience functions"""
    
    def test_get_logger(self):
        """Test getting global logger"""
        logger = get_logger()
        assert logger is not None
        assert isinstance(logger, SyntariLogger)
    
    def test_configure_logging(self):
        """Test configuring global logging"""
        configure_logging(level=LogLevel.DEBUG, format_type=LogFormat.JSON)
        logger = get_logger()
        assert logger.level == LogLevel.DEBUG
        assert logger.format_type == LogFormat.JSON
    
    def test_convenience_functions(self):
        """Test convenience logging functions"""
        from src.core import logging as log_module
        
        # These should not raise
        log_module.debug("Debug message")
        log_module.info("Info message")
        log_module.warning("Warning message")
        log_module.error("Error message")
        log_module.critical("Critical message")


class TestLogFormats:
    """Tests for different log formats"""
    
    def test_text_format(self):
        """Test text log format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = SyntariLogger(
                name="test",
                format_type=LogFormat.TEXT,
                log_file=str(log_file),
                console=False,
            )
            logger.info("Test message")
            
            content = log_file.read_text()
            assert "[INFO]" in content
            assert "Test message" in content
    
    def test_json_format(self):
        """Test JSON log format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = SyntariLogger(
                name="test",
                format_type=LogFormat.JSON,
                log_file=str(log_file),
                console=False,
            )
            logger.info("Test message")
            
            content = log_file.read_text().strip()
            data = json.loads(content)
            assert data["level"] == "INFO"
            assert data["message"] == "Test message"
    
    def test_structured_format(self):
        """Test structured log format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = SyntariLogger(
                name="test",
                format_type=LogFormat.STRUCTURED,
                log_file=str(log_file),
                console=False,
            )
            logger.info("Test message")
            
            content = log_file.read_text()
            assert 'level="INFO"' in content
            assert 'message="Test message"' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
