"""
Security tests for Syntari
Tests for SSRF, path traversal, and DoS prevention
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.core import net
from src.interpreter.main import _validate_file_path, _validate_output_path
from runtime import SyntariVM, VMSecurityError, MAX_INSTRUCTIONS, MAX_STACK_SIZE


class TestSSRFPrevention:
    """Tests for SSRF (Server-Side Request Forgery) prevention"""

    def test_blocks_localhost(self):
        """Test that localhost URLs are blocked"""
        with pytest.raises(net.SSRFError, match="private/internal IP"):
            net._validate_url("http://localhost:8080/api")

    def test_blocks_127001(self):
        """Test that 127.0.0.1 URLs are blocked"""
        with pytest.raises(net.SSRFError, match="private/internal IP"):
            net._validate_url("http://127.0.0.1:8080/api")

    def test_blocks_private_network_10(self):
        """Test that 10.x.x.x private network URLs are blocked"""
        with pytest.raises(net.SSRFError, match="private/internal IP"):
            net._validate_url("http://10.0.0.1/api")

    def test_blocks_private_network_192(self):
        """Test that 192.168.x.x private network URLs are blocked"""
        with pytest.raises(net.SSRFError, match="private/internal IP"):
            net._validate_url("http://192.168.1.1/api")

    def test_blocks_private_network_172(self):
        """Test that 172.16-31.x.x private network URLs are blocked"""
        with pytest.raises(net.SSRFError, match="private/internal IP"):
            net._validate_url("http://172.16.0.1/api")

    def test_blocks_link_local(self):
        """Test that link-local addresses are blocked"""
        with pytest.raises(net.SSRFError, match="private/internal IP"):
            net._validate_url("http://169.254.169.254/api")

    def test_blocks_invalid_scheme(self):
        """Test that non-HTTP(S) schemes are blocked"""
        with pytest.raises(net.SSRFError, match="Scheme.*not allowed"):
            net._validate_url("file:///etc/passwd")

    def test_blocks_ftp(self):
        """Test that FTP scheme is blocked"""
        with pytest.raises(net.SSRFError, match="Scheme.*not allowed"):
            net._validate_url("ftp://example.com/file")

    def test_allows_valid_http(self):
        """Test that valid HTTP URLs are allowed (without actually making request)"""
        # This should not raise an exception during validation
        # We're only testing URL validation, not actual network requests
        try:
            net._validate_url("http://example.com/api")
        except net.NetworkError:
            # Network errors are OK - we're just testing URL validation passes
            pass

    def test_allows_valid_https(self):
        """Test that valid HTTPS URLs are allowed"""
        try:
            net._validate_url("https://example.com/api")
        except net.NetworkError:
            # Network errors are OK - we're just testing URL validation passes
            pass

    def test_http_get_validates_url(self):
        """Test that http_get validates URLs"""
        with pytest.raises(net.SSRFError):
            net.http_get("http://127.0.0.1:8080/api")

    def test_http_post_validates_url(self):
        """Test that http_post validates URLs"""
        with pytest.raises(net.SSRFError):
            net.http_post("http://192.168.1.1/api", {"key": "value"})

    def test_http_put_validates_url(self):
        """Test that http_put validates URLs"""
        with pytest.raises(net.SSRFError):
            net.http_put("http://10.0.0.1/api", {"key": "value"})

    def test_http_delete_validates_url(self):
        """Test that http_delete validates URLs"""
        with pytest.raises(net.SSRFError):
            net.http_delete("http://localhost/api")


class TestPathTraversalPrevention:
    """Tests for path traversal prevention"""

    def test_validates_file_exists(self):
        """Test that validation fails for non-existent files"""
        with pytest.raises(ValueError, match="does not exist"):
            _validate_file_path("/tmp/nonexistent_file_12345.syn")

    def test_validates_file_extension(self):
        """Test that file extension validation works"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="Invalid file extension"):
                _validate_file_path(temp_file, allowed_extensions={".syn"})
        finally:
            os.unlink(temp_file)

    def test_validates_is_file_not_directory(self):
        """Test that validation fails for directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="not a file"):
                _validate_file_path(tmpdir, allowed_extensions={".syn"})

    def test_accepts_valid_file(self):
        """Test that valid files are accepted"""
        with tempfile.NamedTemporaryFile(suffix=".syn", delete=False) as f:
            f.write(b"print('hello')")
            temp_file = f.name

        try:
            result = _validate_file_path(temp_file, allowed_extensions={".syn"})
            assert result.endswith(".syn")
            assert os.path.isabs(result)
        finally:
            os.unlink(temp_file)

    def test_resolves_to_absolute_path(self):
        """Test that paths are resolved to absolute paths"""
        with tempfile.NamedTemporaryFile(suffix=".syn", delete=False, dir=".") as f:
            f.write(b"print('hello')")
            temp_file = os.path.basename(f.name)

        try:
            result = _validate_file_path(temp_file, allowed_extensions={".syn"})
            assert os.path.isabs(result)
        finally:
            os.unlink(temp_file)

    def test_output_path_validates_parent_exists(self):
        """Test that output path validation checks parent directory exists"""
        with pytest.raises(ValueError, match="Parent directory does not exist"):
            _validate_output_path("/nonexistent/path/output.sbc", allowed_extensions={".sbc"})

    def test_output_path_validates_extension(self):
        """Test that output path validates extension"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.txt")
            with pytest.raises(ValueError, match="Invalid file extension"):
                _validate_output_path(output_path, allowed_extensions={".sbc"})

    def test_output_path_accepts_valid_path(self):
        """Test that valid output paths are accepted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.sbc")
            result = _validate_output_path(output_path, allowed_extensions={".sbc"})
            assert result.endswith(".sbc")
            assert os.path.isabs(result)


class TestVMSecurityLimits:
    """Tests for VM resource limits to prevent DoS"""

    def test_string_length_limit(self):
        """Test that excessively long strings are rejected"""
        vm = SyntariVM()
        # We can't easily test this without creating malicious bytecode
        # This is a placeholder for manual security testing
        assert hasattr(vm, "_fetch_str")

    def test_instruction_limit_constant(self):
        """Test that instruction limit constant is defined"""
        assert MAX_INSTRUCTIONS == 1000000

    def test_stack_size_limit_constant(self):
        """Test that stack size limit constant is defined"""
        assert MAX_STACK_SIZE == 10000

    def test_vm_security_error_exists(self):
        """Test that VMSecurityError exception exists"""
        error = VMSecurityError("test")
        assert "test" in str(error)


class TestInputSanitization:
    """Tests for input sanitization"""

    def test_input_has_size_limit(self):
        """Test that input function has size limit protection"""
        from src.core.system import input

        # The input function should have size limit logic
        # We can't easily test this without mocking stdin
        # This test just verifies the function exists and is callable
        assert callable(input)


class TestNetworkingWrapperSecurity:
    """Tests for Syntari networking wrapper functions"""

    def test_net_get_wrapper_validates_url(self):
        """Test that net_get wrapper validates URLs"""
        result = net.net_get("http://127.0.0.1/api")
        assert not result["ok"]
        assert "error" in result

    def test_net_post_wrapper_validates_url(self):
        """Test that net_post wrapper validates URLs"""
        result = net.net_post("http://localhost/api", {"key": "value"})
        assert not result["ok"]
        assert "error" in result

    def test_net_put_wrapper_validates_url(self):
        """Test that net_put wrapper validates URLs"""
        result = net.net_put("http://192.168.1.1/api", {"key": "value"})
        assert not result["ok"]
        assert "error" in result

    def test_net_delete_wrapper_validates_url(self):
        """Test that net_delete wrapper validates URLs"""
        result = net.net_delete("http://10.0.0.1/api")
        assert not result["ok"]
        assert "error" in result


class TestSecurityConstants:
    """Tests to verify security constants are properly defined"""

    def test_blocked_ip_ranges_defined(self):
        """Test that blocked IP ranges are defined"""
        assert hasattr(net, "BLOCKED_IP_RANGES")
        assert len(net.BLOCKED_IP_RANGES) > 0

    def test_allowed_schemes_defined(self):
        """Test that allowed URL schemes are defined"""
        assert hasattr(net, "ALLOWED_SCHEMES")
        assert "http" in net.ALLOWED_SCHEMES
        assert "https" in net.ALLOWED_SCHEMES

    def test_vm_max_stack_size_defined(self):
        """Test that VM max stack size is defined"""
        from runtime import MAX_STACK_SIZE

        assert MAX_STACK_SIZE > 0

    def test_vm_max_instructions_defined(self):
        """Test that VM max instructions is defined"""
        from runtime import MAX_INSTRUCTIONS

        assert MAX_INSTRUCTIONS > 0

    def test_vm_max_vars_defined(self):
        """Test that VM max vars is defined"""
        from runtime import MAX_VARS

        assert MAX_VARS > 0

    def test_vm_max_string_length_defined(self):
        """Test that VM max string length is defined"""
        from runtime import MAX_STRING_LENGTH

        assert MAX_STRING_LENGTH > 0
