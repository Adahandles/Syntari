"""
Tests for src/core/system.py
"""

import sys
import os
import io
import pytest
from unittest.mock import patch, MagicMock
from src.core import system


def test_print_basic():
    """Test basic print functionality"""
    output = io.StringIO()
    system.print("Hello", file=output)
    assert output.getvalue() == "Hello\n"


def test_print_multiple_args():
    """Test print with multiple arguments"""
    output = io.StringIO()
    system.print("Hello", "World", file=output)
    assert output.getvalue() == "Hello World\n"


def test_print_custom_separator():
    """Test print with custom separator"""
    output = io.StringIO()
    system.print("Hello", "World", sep=", ", file=output)
    assert output.getvalue() == "Hello, World\n"


def test_print_custom_end():
    """Test print with custom end character"""
    output = io.StringIO()
    system.print("Hello", end="!!!", file=output)
    assert output.getvalue() == "Hello!!!"


def test_print_to_stdout():
    """Test print to stdout (default)"""
    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        system.print("Test")
        assert "Test\n" in mock_stdout.getvalue()


def test_trace():
    """Test trace function prints stack trace"""
    with patch("traceback.print_stack") as mock_print_stack:
        system.trace()
        mock_print_stack.assert_called_once()


def test_exit():
    """Test exit function"""
    with pytest.raises(SystemExit) as exc_info:
        system.exit(42)
    assert exc_info.value.code == 42


def test_exit_default():
    """Test exit with default code"""
    with pytest.raises(SystemExit) as exc_info:
        system.exit()
    assert exc_info.value.code == 0


def test_env():
    """Test env function gets environment variable"""
    with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        assert system.env("TEST_VAR") == "test_value"


def test_env_missing():
    """Test env function returns None for missing variable"""
    assert system.env("NONEXISTENT_VAR_12345") is None


def test_time():
    """Test time function returns timestamp"""
    timestamp = system.time()
    assert isinstance(timestamp, float)
    assert timestamp > 0


def test_input_basic():
    """Test input function with basic input"""
    with patch("sys.stdin", io.StringIO("test input\n")):
        with patch("sys.stdout", new_callable=io.StringIO):
            result = system.input()
            assert result == "test input"


def test_input_with_prompt():
    """Test input function with prompt"""
    with patch("sys.stdin", io.StringIO("answer\n")):
        output = io.StringIO()
        with patch("sys.stdout", output):
            result = system.input("Enter: ")
            assert result == "answer"
            assert "Enter: " in output.getvalue()


def test_input_strips_newline():
    """Test input strips trailing newline"""
    with patch("sys.stdin", io.StringIO("text\n")):
        with patch("sys.stdout", new_callable=io.StringIO):
            result = system.input()
            assert result == "text"
            assert "\n" not in result


def test_input_max_length():
    """Test input enforces maximum length"""
    # Create input that exceeds MAX_INPUT_LENGTH
    large_input = "x" * 100001 + "\n"
    with patch("sys.stdin", io.StringIO(large_input)):
        with patch("sys.stdout", new_callable=io.StringIO):
            with pytest.raises(RuntimeError) as exc_info:
                system.input()
            assert "Input error" in str(exc_info.value)


def test_input_error_handling():
    """Test input handles errors gracefully"""
    mock_stdin = MagicMock()
    mock_stdin.readline.side_effect = IOError("Read error")
    
    with patch("sys.stdin", mock_stdin):
        with patch("sys.stdout", new_callable=io.StringIO):
            with pytest.raises(RuntimeError) as exc_info:
                system.input()
            assert "Input error" in str(exc_info.value)
