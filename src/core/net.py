"""
Syntari Networking Module

Provides HTTP client, WebSocket, and basic networking functionality.
Part of v0.4 development.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, Union
import socket


class HTTPResponse:
    """Represents an HTTP response."""

    def __init__(self, status_code: int, headers: Dict[str, str], body: str):
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def json(self) -> Any:
        """Parse response body as JSON."""
        try:
            return json.loads(self.body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Response is not valid JSON: {e}")

    def text(self) -> str:
        """Get response body as text."""
        return self.body

    def __repr__(self):
        return f"HTTPResponse(status={self.status_code}, body_length={len(self.body)})"


class NetworkError(Exception):
    """Base exception for network errors."""

    pass


class HTTPError(NetworkError):
    """Exception for HTTP errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")


class WebSocketError(NetworkError):
    """Exception for WebSocket errors."""

    pass


def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> HTTPResponse:
    """
    Perform an HTTP GET request.

    Args:
        url: The URL to request
        headers: Optional dictionary of headers to send
        timeout: Request timeout in seconds (default: 30)

    Returns:
        HTTPResponse object with status, headers, and body

    Raises:
        HTTPError: If the HTTP request fails
        NetworkError: If a network error occurs
    """
    try:
        req = urllib.request.Request(url, method="GET")

        # Add custom headers
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        # Perform request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            body = response.read().decode("utf-8")

            return HTTPResponse(status_code, response_headers, body)

    except urllib.error.HTTPError as e:
        raise HTTPError(e.code, e.reason)
    except urllib.error.URLError as e:
        raise NetworkError(f"Network error: {e.reason}")
    except socket.timeout:
        raise NetworkError(f"Request timed out after {timeout} seconds")
    except Exception as e:
        raise NetworkError(f"Unexpected error: {e}")


def http_post(
    url: str,
    data: Union[Dict[str, Any], str],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> HTTPResponse:
    """
    Perform an HTTP POST request.

    Args:
        url: The URL to request
        data: Data to send (dict will be JSON-encoded, str sent as-is)
        headers: Optional dictionary of headers to send
        timeout: Request timeout in seconds (default: 30)

    Returns:
        HTTPResponse object with status, headers, and body

    Raises:
        HTTPError: If the HTTP request fails
        NetworkError: If a network error occurs
    """
    try:
        # Prepare data
        if isinstance(data, dict):
            post_data = json.dumps(data).encode("utf-8")
            content_type = "application/json"
        else:
            post_data = data.encode("utf-8")
            content_type = "text/plain"

        # Create request
        req = urllib.request.Request(url, data=post_data, method="POST")
        req.add_header("Content-Type", content_type)
        req.add_header("Content-Length", str(len(post_data)))

        # Add custom headers
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        # Perform request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            body = response.read().decode("utf-8")

            return HTTPResponse(status_code, response_headers, body)

    except urllib.error.HTTPError as e:
        raise HTTPError(e.code, e.reason)
    except urllib.error.URLError as e:
        raise NetworkError(f"Network error: {e.reason}")
    except socket.timeout:
        raise NetworkError(f"Request timed out after {timeout} seconds")
    except Exception as e:
        raise NetworkError(f"Unexpected error: {e}")


def http_put(
    url: str,
    data: Union[Dict[str, Any], str],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> HTTPResponse:
    """
    Perform an HTTP PUT request.

    Args:
        url: The URL to request
        data: Data to send (dict will be JSON-encoded, str sent as-is)
        headers: Optional dictionary of headers to send
        timeout: Request timeout in seconds (default: 30)

    Returns:
        HTTPResponse object with status, headers, and body

    Raises:
        HTTPError: If the HTTP request fails
        NetworkError: If a network error occurs
    """
    try:
        # Prepare data
        if isinstance(data, dict):
            put_data = json.dumps(data).encode("utf-8")
            content_type = "application/json"
        else:
            put_data = data.encode("utf-8")
            content_type = "text/plain"

        # Create request
        req = urllib.request.Request(url, data=put_data, method="PUT")
        req.add_header("Content-Type", content_type)
        req.add_header("Content-Length", str(len(put_data)))

        # Add custom headers
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        # Perform request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            body = response.read().decode("utf-8")

            return HTTPResponse(status_code, response_headers, body)

    except urllib.error.HTTPError as e:
        raise HTTPError(e.code, e.reason)
    except urllib.error.URLError as e:
        raise NetworkError(f"Network error: {e.reason}")
    except socket.timeout:
        raise NetworkError(f"Request timed out after {timeout} seconds")
    except Exception as e:
        raise NetworkError(f"Unexpected error: {e}")


def http_delete(
    url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30
) -> HTTPResponse:
    """
    Perform an HTTP DELETE request.

    Args:
        url: The URL to request
        headers: Optional dictionary of headers to send
        timeout: Request timeout in seconds (default: 30)

    Returns:
        HTTPResponse object with status, headers, and body

    Raises:
        HTTPError: If the HTTP request fails
        NetworkError: If a network error occurs
    """
    try:
        req = urllib.request.Request(url, method="DELETE")

        # Add custom headers
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        # Perform request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            body = response.read().decode("utf-8")

            return HTTPResponse(status_code, response_headers, body)

    except urllib.error.HTTPError as e:
        raise HTTPError(e.code, e.reason)
    except urllib.error.URLError as e:
        raise NetworkError(f"Network error: {e.reason}")
    except socket.timeout:
        raise NetworkError(f"Request timed out after {timeout} seconds")
    except Exception as e:
        raise NetworkError(f"Unexpected error: {e}")


class WebSocket:
    """
    Basic WebSocket client implementation.
    Note: This is a simplified implementation for v0.4.
    For production use, consider using the `websockets` library.
    """

    def __init__(self, url: str):
        self.url = url
        self.socket = None
        self.connected = False

    def connect(self, timeout: int = 30):
        """
        Connect to the WebSocket server.

        Args:
            timeout: Connection timeout in seconds

        Raises:
            WebSocketError: If connection fails
        """
        raise NotImplementedError(
            "WebSocket support requires the 'websockets' library. "
            "This is a stub implementation for v0.4. "
            "To use WebSockets, install: pip install websockets"
        )

    def send(self, message: str):
        """
        Send a message over the WebSocket.

        Args:
            message: The message to send

        Raises:
            WebSocketError: If sending fails or not connected
        """
        if not self.connected:
            raise WebSocketError("Not connected to WebSocket server")
        raise NotImplementedError("WebSocket send not implemented in v0.4 stub")

    def receive(self, timeout: int = 30) -> str:
        """
        Receive a message from the WebSocket.

        Args:
            timeout: Receive timeout in seconds

        Returns:
            The received message

        Raises:
            WebSocketError: If receiving fails or not connected
        """
        if not self.connected:
            raise WebSocketError("Not connected to WebSocket server")
        raise NotImplementedError("WebSocket receive not implemented in v0.4 stub")

    def close(self):
        """Close the WebSocket connection."""
        if self.connected:
            self.connected = False
            if self.socket:
                self.socket.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Syntari-accessible functions for the interpreter
def net_get(url: str) -> Dict[str, Any]:
    """Syntari wrapper for HTTP GET."""
    try:
        response = http_get(url)
        return {
            "status": response.status_code,
            "headers": response.headers,
            "body": response.body,
            "ok": 200 <= response.status_code < 300,
        }
    except HTTPError as e:
        return {"status": e.status_code, "error": str(e), "ok": False}
    except NetworkError as e:
        return {"error": str(e), "ok": False}


def net_post(url: str, data: Any) -> Dict[str, Any]:
    """Syntari wrapper for HTTP POST."""
    try:
        response = http_post(url, data)
        return {
            "status": response.status_code,
            "headers": response.headers,
            "body": response.body,
            "ok": 200 <= response.status_code < 300,
        }
    except HTTPError as e:
        return {"status": e.status_code, "error": str(e), "ok": False}
    except NetworkError as e:
        return {"error": str(e), "ok": False}


def net_put(url: str, data: Any) -> Dict[str, Any]:
    """Syntari wrapper for HTTP PUT."""
    try:
        response = http_put(url, data)
        return {
            "status": response.status_code,
            "headers": response.headers,
            "body": response.body,
            "ok": 200 <= response.status_code < 300,
        }
    except HTTPError as e:
        return {"status": e.status_code, "error": str(e), "ok": False}
    except NetworkError as e:
        return {"error": str(e), "ok": False}


def net_delete(url: str) -> Dict[str, Any]:
    """Syntari wrapper for HTTP DELETE."""
    try:
        response = http_delete(url)
        return {
            "status": response.status_code,
            "headers": response.headers,
            "body": response.body,
            "ok": 200 <= response.status_code < 300,
        }
    except HTTPError as e:
        return {"status": e.status_code, "error": str(e), "ok": False}
    except NetworkError as e:
        return {"error": str(e), "ok": False}


def net_ws(url: str) -> Dict[str, Any]:
    """Syntari wrapper for WebSocket (stub for v0.4)."""
    return {
        "error": "WebSocket support not yet implemented in v0.4",
        "ok": False,
        "message": "This is a stub. Full WebSocket support coming in future release.",
    }
