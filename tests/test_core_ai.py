"""
Tests for src/core/ai.py
"""

from src.core import ai


def test_query_basic():
    """Test AI query function returns stub response"""
    result = ai.query("What is the meaning of life?")
    assert "[AI Stub v0.3]" in result
    assert "What is the meaning of life?" in result


def test_query_empty():
    """Test AI query with empty string"""
    result = ai.query("")
    assert "[AI Stub v0.3]" in result
    assert "Received query:" in result


def test_eval_basic():
    """Test AI eval function returns stub response"""
    result = ai.eval("x = 42")
    assert "[AI Stub v0.3]" in result
    assert "Code evaluation not yet implemented" in result


def test_eval_complex_code():
    """Test AI eval with complex code"""
    code = """
    fn factorial(n) {
        if n <= 1 { 1 }
        else { n * factorial(n - 1) }
    }
    """
    result = ai.eval(code)
    assert "[AI Stub v0.3]" in result


def test_suggest():
    """Test AI suggest function returns stub response"""
    result = ai.suggest()
    assert "[AI Stub v0.3]" in result
    assert "No suggestions available yet" in result
