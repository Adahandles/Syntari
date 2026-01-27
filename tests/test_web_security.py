"""
Tests for Web REPL security module
"""

import pytest
import time
from web.security import (
    RateLimiter,
    SessionManager,
    ResourceMonitor,
    RateLimitConfig,
    SessionConfig,
    sanitize_output,
    validate_code_safety,
)


class TestRateLimiter:
    """Tests for rate limiting functionality"""

    def test_basic_rate_limit(self):
        """Test basic rate limiting"""
        config = RateLimitConfig(requests_per_minute=5, requests_per_hour=10)
        limiter = RateLimiter(config)

        ip = "192.168.1.1"

        # First 5 requests should succeed
        for i in range(5):
            allowed, reason = limiter.check_rate_limit(ip)
            assert allowed, f"Request {i+1} should be allowed"
            assert reason is None

        # 6th request should fail (per-minute limit)
        allowed, reason = limiter.check_rate_limit(ip)
        assert not allowed
        assert "requests/minute" in reason

    def test_ban_after_violations(self):
        """Test that clients are banned after repeated violations"""
        config = RateLimitConfig(
            requests_per_minute=2, ban_threshold=3, ban_duration=1  # 1 second for testing
        )
        limiter = RateLimiter(config)

        ip = "192.168.1.2"

        # Trigger violations by exceeding rate limit
        for i in range(5):
            limiter.check_rate_limit(ip)

        # Client should now be banned
        stats = limiter.get_client_stats(ip)
        assert stats is not None
        assert stats["is_banned"]

        # Wait for ban to expire
        time.sleep(1.5)

        # Clear old requests so we don't immediately hit rate limit again
        limiter.clients[ip].requests.clear()

        # Should be unbanned now and able to make request
        allowed, reason = limiter.check_rate_limit(ip)
        assert allowed

    def test_code_length_limit(self):
        """Test code length limiting"""
        config = RateLimitConfig(max_code_length=100)
        limiter = RateLimiter(config)

        ip = "192.168.1.3"

        # Short code should pass
        short_code = "x = 1"
        allowed, reason = limiter.check_code_length(short_code, ip)
        assert allowed
        assert reason is None

        # Long code should fail
        long_code = "x = 1\n" * 100  # More than 100 characters
        allowed, reason = limiter.check_code_length(long_code, ip)
        assert not allowed
        assert "Code length exceeds limit" in reason

    def test_execution_time_recording(self):
        """Test execution time recording"""
        config = RateLimitConfig(max_execution_time=0.1)
        limiter = RateLimiter(config)

        ip = "192.168.1.4"

        # Initialize client first
        limiter.check_rate_limit(ip)

        # Record normal execution
        limiter.record_execution_time(ip, 0.05, 50, True)
        stats = limiter.get_client_stats(ip)
        assert stats is not None
        assert stats["total_violations"] == 0

        # Record slow execution (should trigger violation)
        limiter.record_execution_time(ip, 0.5, 50, True)
        stats = limiter.get_client_stats(ip)
        assert stats is not None
        assert stats["total_violations"] == 1

    def test_per_hour_limit(self):
        """Test per-hour rate limiting"""
        config = RateLimitConfig(requests_per_minute=100, requests_per_hour=5)
        limiter = RateLimiter(config)

        ip = "192.168.1.5"

        # Make exactly 5 requests (hourly limit)
        for i in range(5):
            allowed, reason = limiter.check_rate_limit(ip)
            assert allowed, f"Request {i+1} should be allowed"

        # 6th request should fail (per-hour limit)
        allowed, reason = limiter.check_rate_limit(ip)
        assert not allowed
        assert "requests/hour" in reason

    def test_multiple_clients(self):
        """Test that rate limits are per-client"""
        config = RateLimitConfig(requests_per_minute=2)
        limiter = RateLimiter(config)

        # Two different IPs
        ip1 = "192.168.1.10"
        ip2 = "192.168.1.11"

        # Both should be able to make 2 requests
        for ip in [ip1, ip2]:
            for i in range(2):
                allowed, reason = limiter.check_rate_limit(ip)
                assert allowed

        # Both should hit limit on 3rd request
        for ip in [ip1, ip2]:
            allowed, reason = limiter.check_rate_limit(ip)
            assert not allowed

    def test_stats_aggregation(self):
        """Test statistics aggregation"""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        # Create some client activity
        limiter.check_rate_limit("192.168.1.20")
        limiter.check_rate_limit("192.168.1.21")

        stats = limiter.get_all_stats()
        assert stats["total_clients"] == 2
        assert stats["active_clients"] >= 0


class TestSessionManager:
    """Tests for session management"""

    def test_create_session(self):
        """Test session creation"""
        manager = SessionManager()

        ip = "192.168.1.30"
        result = manager.create_session(ip)

        assert result is not None
        session_id, session_token = result
        assert len(session_id) > 0
        assert len(session_token) > 0

    def test_validate_session(self):
        """Test session validation"""
        manager = SessionManager()

        ip = "192.168.1.31"
        session_id, session_token = manager.create_session(ip)

        # Valid session should validate
        assert manager.validate_session(session_id, session_token, ip)

        # Invalid token should fail
        assert not manager.validate_session(session_id, "wrong-token", ip)

        # Wrong IP should fail
        assert not manager.validate_session(session_id, session_token, "192.168.1.99")

    def test_session_timeout(self):
        """Test session timeout"""
        config = SessionConfig(session_timeout=1)  # 1 second timeout
        manager = SessionManager(config)

        ip = "192.168.1.32"
        session_id, session_token = manager.create_session(ip)

        # Should be valid immediately
        assert manager.validate_session(session_id, session_token, ip)

        # Wait for timeout
        time.sleep(1.1)

        # Should be invalid after timeout
        assert not manager.validate_session(session_id, session_token, ip)

    def test_max_sessions_per_ip(self):
        """Test maximum sessions per IP limit"""
        config = SessionConfig(max_sessions_per_ip=2)
        manager = SessionManager(config)

        ip = "192.168.1.33"

        # First 2 sessions should succeed
        session1 = manager.create_session(ip)
        session2 = manager.create_session(ip)
        assert session1 is not None
        assert session2 is not None

        # 3rd session should fail
        session3 = manager.create_session(ip)
        assert session3 is None

    def test_session_removal(self):
        """Test session removal"""
        manager = SessionManager()

        ip = "192.168.1.34"
        session_id, session_token = manager.create_session(ip)

        # Should be valid
        assert manager.validate_session(session_id, session_token, ip)

        # Remove session
        manager.remove_session(session_id, session_token)

        # Should be invalid after removal
        assert not manager.validate_session(session_id, session_token, ip)

    def test_session_stats(self):
        """Test session statistics"""
        manager = SessionManager()

        # Create some sessions
        manager.create_session("192.168.1.40")
        manager.create_session("192.168.1.41")
        manager.create_session("192.168.1.42")

        stats = manager.get_stats()
        assert stats["total_sessions"] == 3
        assert stats["unique_ips"] == 3


class TestResourceMonitor:
    """Tests for resource monitoring"""

    def test_record_execution(self):
        """Test recording execution metrics"""
        monitor = ResourceMonitor()

        identifier = "session-123"
        monitor.record_execution(identifier, 0.5, 10.0)

        metrics = monitor.get_metrics(identifier)
        assert metrics["count"] == 1
        assert metrics["avg_execution_time"] == 0.5
        assert metrics["max_execution_time"] == 0.5

    def test_metrics_window(self):
        """Test metrics time window"""
        monitor = ResourceMonitor()

        identifier = "session-124"

        # Record old execution (outside window)
        monitor.execution_times[identifier].append(
            {
                "timestamp": time.time() - 120,  # 2 minutes ago
                "execution_time": 1.0,
                "memory_mb": 5.0,
            }
        )

        # Record recent execution
        monitor.record_execution(identifier, 0.5, 10.0)

        # Only recent execution should be in 60-second window
        metrics = monitor.get_metrics(identifier, window=60)
        assert metrics["count"] == 1
        assert metrics["avg_execution_time"] == 0.5

    def test_multiple_executions(self):
        """Test multiple execution recordings"""
        monitor = ResourceMonitor()

        identifier = "session-125"

        # Record multiple executions
        for i in range(5):
            monitor.record_execution(identifier, 0.1 * (i + 1), 5.0)

        metrics = monitor.get_metrics(identifier)
        assert metrics["count"] == 5
        assert metrics["max_execution_time"] == 0.5  # 0.1 * 5


class TestSecurityHelpers:
    """Tests for security helper functions"""

    def test_sanitize_output_basic(self):
        """Test basic output sanitization"""
        text = "Hello, world!"
        result = sanitize_output(text)
        assert result == "Hello, world!"

    def test_sanitize_output_html(self):
        """Test HTML entity encoding"""
        text = '<script>alert("XSS")</script>'
        result = sanitize_output(text)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
        assert "&quot;" in result

    def test_sanitize_output_length_limit(self):
        """Test output length limiting"""
        long_text = "A" * 20000
        result = sanitize_output(long_text, max_length=1000)
        assert len(result) < 1100  # Should be truncated with message
        assert "truncated" in result

    def test_sanitize_output_control_chars(self):
        """Test control character removal"""
        text = "Hello\x00\x01\x02World"
        result = sanitize_output(text)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "HelloWorld" in result

    def test_sanitize_output_preserves_newlines(self):
        """Test that newlines are preserved"""
        text = "Line 1\nLine 2\nLine 3"
        result = sanitize_output(text)
        assert "\n" in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_validate_code_safety_clean(self):
        """Test code safety validation with clean code"""
        code = """
        fn main() {
            let x = 5
            print(x)
        }
        """
        safe, reason = validate_code_safety(code)
        assert safe
        assert reason is None

    def test_validate_code_safety_dangerous(self):
        """Test code safety validation with dangerous patterns"""
        dangerous_codes = [
            "__import__('os')",
            "eval('malicious')",
            "exec('bad code')",
            "open('/etc/passwd')",
            "__builtins__.eval",
        ]

        for code in dangerous_codes:
            safe, reason = validate_code_safety(code)
            assert not safe, f"Code '{code}' should be flagged as unsafe"
            assert reason is not None


class TestRateLimitConfig:
    """Tests for rate limit configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = RateLimitConfig()
        assert config.requests_per_minute == 30
        assert config.requests_per_hour == 500
        assert config.max_code_length == 10000
        assert config.max_execution_time == 5.0

    def test_custom_config(self):
        """Test custom configuration"""
        config = RateLimitConfig(
            requests_per_minute=10,
            requests_per_hour=100,
            max_code_length=5000,
        )
        assert config.requests_per_minute == 10
        assert config.requests_per_hour == 100
        assert config.max_code_length == 5000


class TestSessionConfig:
    """Tests for session configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = SessionConfig()
        assert config.session_timeout == 3600
        assert config.max_sessions_per_ip == 5

    def test_custom_config(self):
        """Test custom configuration"""
        config = SessionConfig(
            session_timeout=1800,
            max_sessions_per_ip=3,
        )
        assert config.session_timeout == 1800
        assert config.max_sessions_per_ip == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
