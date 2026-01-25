"""
Tests for Syntari Web REPL
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.app import SyntariSession, create_app


class TestSyntariSession:
    """Tests for SyntariSession class"""

    def test_session_creation(self):
        """Test that a session can be created"""
        session = SyntariSession()
        assert session.interpreter is not None
        assert session.history == []

    def test_execute_simple_code(self):
        """Test executing simple Syntari code"""
        session = SyntariSession()
        result = session.execute("let x = 42")

        assert result["success"] is True
        assert result["error"] is None
        assert len(session.history) == 1

    def test_execute_print_statement(self):
        """Test executing code with print statement"""
        session = SyntariSession()
        result = session.execute('print("Hello, Syntari!")')

        assert result["success"] is True
        assert "Hello, Syntari!" in result["output"]
        assert result["error"] is None

    def test_execute_arithmetic(self):
        """Test executing arithmetic operations"""
        session = SyntariSession()
        result = session.execute("let x = 10 + 20")

        assert result["success"] is True
        assert result["error"] is None

    def test_execute_invalid_syntax(self):
        """Test executing invalid syntax"""
        session = SyntariSession()
        result = session.execute("let x = ")

        assert result["success"] is False
        assert result["error"] is not None
        assert "error" in result["error"].lower()

    def test_persistent_state(self):
        """Test that session maintains state across executions"""
        session = SyntariSession()

        # Define a variable
        result1 = session.execute("let x = 42")
        assert result1["success"] is True

        # Use the variable in next execution
        result2 = session.execute("print(x)")
        assert result2["success"] is True
        assert "42" in result2["output"]

    def test_history_tracking(self):
        """Test that execution history is tracked"""
        session = SyntariSession()

        session.execute("let x = 1")
        session.execute("let y = 2")
        session.execute("print(x + y)")

        history = session.get_history()
        assert len(history) == 3
        assert history[0]["code"] == "let x = 1"
        assert history[1]["code"] == "let y = 2"

    def test_clear_history(self):
        """Test clearing execution history"""
        session = SyntariSession()

        session.execute("let x = 1")
        session.execute("let y = 2")
        assert len(session.get_history()) == 2

        session.clear_history()
        assert len(session.get_history()) == 0

    def test_reset_session(self):
        """Test resetting the session"""
        session = SyntariSession()

        # Create some state
        session.execute("let x = 42")
        assert len(session.get_history()) == 1

        # Reset
        session.reset()

        # State should be cleared
        assert len(session.get_history()) == 0

        # Variable should no longer exist
        result = session.execute("print(x)")
        assert result["success"] is False
        assert "Undefined variable" in result["error"]

    def test_function_definition_and_call(self):
        """Test defining and calling functions"""
        session = SyntariSession()

        # Define function
        result1 = session.execute("""
fn add(a, b) {
    return a + b
}
""")
        assert result1["success"] is True

        # Call function
        result2 = session.execute("print(add(10, 20))")
        assert result2["success"] is True
        assert "30" in result2["output"]

    def test_error_isolation(self):
        """Test that errors don't crash the session"""
        session = SyntariSession()

        # Execute valid code
        result1 = session.execute("let x = 42")
        assert result1["success"] is True

        # Execute invalid code
        result2 = session.execute("let y = ")
        assert result2["success"] is False

        # Session should still work
        result3 = session.execute("print(x)")
        assert result3["success"] is True
        assert "42" in result3["output"]


class TestWebApp:
    """Tests for web application"""

    def test_app_creation(self):
        """Test that app can be created"""
        app = create_app()
        assert app is not None

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        app = create_app()
        from aiohttp.test_utils import TestClient, TestServer

        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health")
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "healthy"
            assert "version" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
