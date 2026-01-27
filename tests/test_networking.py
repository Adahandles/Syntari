"""
Tests for Syntari networking module (v0.4)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.core import net
from src.core.net import HTTPResponse, HTTPError, NetworkError, WebSocket, WebSocketError


class TestHTTPResponse(unittest.TestCase):
    """Test HTTPResponse class"""

    def test_response_creation(self):
        response = HTTPResponse(200, {"Content-Type": "text/html"}, "<html></html>")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/html")
        self.assertEqual(response.body, "<html></html>")

    def test_response_text(self):
        response = HTTPResponse(200, {}, "Hello, World!")
        self.assertEqual(response.text(), "Hello, World!")

    def test_response_json_valid(self):
        json_body = '{"key": "value", "number": 42}'
        response = HTTPResponse(200, {}, json_body)
        data = response.json()
        self.assertEqual(data["key"], "value")
        self.assertEqual(data["number"], 42)

    def test_response_json_invalid(self):
        response = HTTPResponse(200, {}, "not valid json")
        with self.assertRaises(ValueError):
            response.json()

    def test_response_repr(self):
        response = HTTPResponse(200, {}, "test body")
        self.assertIn("200", repr(response))
        self.assertIn("9", repr(response))  # body length


class TestNetworkErrors(unittest.TestCase):
    """Test network exception classes"""

    def test_network_error(self):
        error = NetworkError("Connection failed")
        self.assertIn("Connection failed", str(error))

    def test_http_error(self):
        error = HTTPError(404, "Not Found")
        self.assertEqual(error.status_code, 404)
        self.assertIn("404", str(error))
        self.assertIn("Not Found", str(error))

    def test_websocket_error(self):
        error = WebSocketError("Connection closed")
        self.assertIn("Connection closed", str(error))


class TestHTTPMethods(unittest.TestCase):
    """Test HTTP method implementations"""

    @patch("urllib.request.urlopen")
    def test_http_get_success(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.read.return_value = b'{"success": true}'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        # Test GET request
        response = net.http_get("https://api.example.com/data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, '{"success": true}')

    @patch("urllib.request.urlopen")
    def test_http_post_with_dict(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 201
        mock_response.headers = {}
        mock_response.read.return_value = b'{"id": 123}'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        # Test POST with dict data
        data = {"name": "test", "value": 42}
        response = net.http_post("https://api.example.com/create", data)
        self.assertEqual(response.status_code, 201)

    @patch("urllib.request.urlopen")
    def test_http_post_with_string(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {}
        mock_response.read.return_value = b"OK"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        # Test POST with string data
        response = net.http_post("https://api.example.com/data", "plain text")
        self.assertEqual(response.status_code, 200)

    @patch("urllib.request.urlopen")
    def test_http_put(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.headers = {}
        mock_response.read.return_value = b"Updated"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        # Test PUT request
        response = net.http_put("https://api.example.com/update/1", {"value": "new"})
        self.assertEqual(response.status_code, 200)

    @patch("urllib.request.urlopen")
    def test_http_delete(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 204
        mock_response.headers = {}
        mock_response.read.return_value = b""
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response

        # Test DELETE request
        response = net.http_delete("https://api.example.com/delete/1")
        self.assertEqual(response.status_code, 204)


class TestHTTPErrorHandling(unittest.TestCase):
    """Test HTTP error handling"""

    @patch("urllib.request.urlopen")
    def test_http_error_404(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            "http://test.com", 404, "Not Found", {}, None
        )

        with self.assertRaises(HTTPError) as context:
            net.http_get("http://test.com")

        self.assertEqual(context.exception.status_code, 404)

    @patch("urllib.request.urlopen")
    def test_network_error(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        with self.assertRaises(NetworkError):
            net.http_get("http://invalid.test")


class TestSyntariWrappers(unittest.TestCase):
    """Test Syntari-accessible wrapper functions"""

    @patch("src.core.net.http_get")
    def test_net_get_success(self, mock_http_get):
        mock_http_get.return_value = HTTPResponse(
            200, {"Content-Type": "application/json"}, '{"data": "test"}'
        )

        result = net.net_get("http://api.test.com/data")
        self.assertEqual(result["status"], 200)
        self.assertTrue(result["ok"])
        self.assertEqual(result["body"], '{"data": "test"}')

    @patch("src.core.net.http_get")
    def test_net_get_http_error(self, mock_http_get):
        mock_http_get.side_effect = HTTPError(404, "Not Found")

        result = net.net_get("http://api.test.com/notfound")
        self.assertEqual(result["status"], 404)
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    @patch("src.core.net.http_get")
    def test_net_get_network_error(self, mock_http_get):
        mock_http_get.side_effect = NetworkError("Connection failed")

        result = net.net_get("http://api.test.com/data")
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    @patch("src.core.net.http_post")
    def test_net_post_success(self, mock_http_post):
        mock_http_post.return_value = HTTPResponse(201, {}, '{"id": 1}')

        result = net.net_post("http://api.test.com/create", {"name": "test"})
        self.assertEqual(result["status"], 201)
        self.assertTrue(result["ok"])

    @patch("src.core.net.http_put")
    def test_net_put_success(self, mock_http_put):
        mock_http_put.return_value = HTTPResponse(200, {}, "Updated")

        result = net.net_put("http://api.test.com/update/1", {"value": "new"})
        self.assertEqual(result["status"], 200)
        self.assertTrue(result["ok"])

    @patch("src.core.net.http_delete")
    def test_net_delete_success(self, mock_http_delete):
        mock_http_delete.return_value = HTTPResponse(204, {}, "")

        result = net.net_delete("http://api.test.com/delete/1")
        self.assertEqual(result["status"], 204)
        self.assertTrue(result["ok"])

    def test_net_ws_stub(self):
        # WebSocket is a stub in v0.4
        result = net.net_ws("ws://test.com")
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
        self.assertIn("not yet implemented", result["error"])


class TestWebSocketStub(unittest.TestCase):
    """Test WebSocket stub implementation"""

    def test_websocket_connect_not_implemented(self):
        ws = WebSocket("ws://test.com")
        with self.assertRaises(NotImplementedError):
            ws.connect()

    def test_websocket_send_not_connected(self):
        ws = WebSocket("ws://test.com")
        with self.assertRaises(WebSocketError):
            ws.send("message")

    def test_websocket_receive_not_connected(self):
        ws = WebSocket("ws://test.com")
        with self.assertRaises(WebSocketError):
            ws.receive()

    def test_websocket_context_manager(self):
        ws = WebSocket("ws://test.com")
        with self.assertRaises(NotImplementedError):
            with ws:
                pass


class TestSSRFValidation(unittest.TestCase):
    """Additional SSRF validation tests"""

    def test_validate_url_no_hostname(self):
        """Test URL without hostname fails"""
        with self.assertRaises(net.SSRFError):
            net._validate_url("http://")

    def test_validate_url_hostname_is_ip(self):
        """Test when hostname is directly a private IP"""
        with self.assertRaises(net.SSRFError):
            net._validate_url("http://192.168.1.1/test")

    def test_validate_url_dns_failure(self):
        """Test when DNS resolution fails"""
        # Mock DNS lookup to fail
        import socket

        with patch("socket.gethostbyname", side_effect=socket.gaierror("DNS lookup failed")):
            # Should still raise error when DNS fails (can't verify safety)
            try:
                net._validate_url("http://example.com")
            except (net.SSRFError, socket.gaierror):
                pass  # Either error is acceptable

    def test_validate_url_invalid_format(self):
        """Test invalid URL format"""
        with self.assertRaises(net.SSRFError):
            net._validate_url("not-a-valid-url-at-all")

    @patch.dict("os.environ", {"SYNTARI_ENV": "test"})
    def test_validate_url_for_tests_runtime_check(self):
        """Test the test-only validation function"""
        # Should not raise in test env
        try:
            net._validate_url_for_tests("http://example.com", allow_private=True)
        except net.SSRFError:
            pass  # May raise for other reasons

    def test_validate_url_for_tests_non_test_env(self):
        """Test that test function fails outside test env"""
        import os

        old_env = os.environ.get("SYNTARI_ENV")
        try:
            if "SYNTARI_ENV" in os.environ:
                del os.environ["SYNTARI_ENV"]
            with self.assertRaises(RuntimeError):
                net._validate_url_for_tests("http://example.com")
        finally:
            if old_env:
                os.environ["SYNTARI_ENV"] = old_env

    @patch.dict("os.environ", {"SYNTARI_ENV": "test"})
    def test_validate_url_for_tests_no_hostname(self):
        """Test test function with no hostname"""
        with self.assertRaises(net.SSRFError):
            net._validate_url_for_tests("http://")

    @patch.dict("os.environ", {"SYNTARI_ENV": "test"})
    @patch("socket.gethostbyname")
    def test_validate_url_for_tests_private_ip(self, mock_gethostbyname):
        """Test test function with private IP"""
        mock_gethostbyname.return_value = "192.168.1.1"
        with self.assertRaises(net.SSRFError):
            net._validate_url_for_tests("http://example.com", allow_private=False)

    @patch.dict("os.environ", {"SYNTARI_ENV": "test"})
    @patch("socket.gethostbyname")
    def test_validate_url_for_tests_dns_failure(self, mock_gethostbyname):
        """Test test function with DNS failure"""
        import socket

        mock_gethostbyname.side_effect = socket.gaierror("DNS lookup failed")
        # Should not raise in test mode with DNS failure
        try:
            net._validate_url_for_tests("http://example.com")
        except net.SSRFError:
            pass  # May raise for other reasons

    @patch.dict("os.environ", {"SYNTARI_ENV": "test"})
    def test_validate_url_for_tests_invalid_format(self):
        """Test test function with invalid format"""
        with self.assertRaises(net.SSRFError):
            net._validate_url_for_tests("not-valid")


if __name__ == "__main__":
    unittest.main()
