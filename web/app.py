"""
Syntari Web REPL - Backend Server
Provides WebSocket server for executing Syntari code in the browser
"""

import json
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiohttp import web
import aiohttp_cors
from src.interpreter.lexer import tokenize, LexerError
from src.interpreter.parser import parse, ParseError
from src.interpreter.interpreter import Interpreter, RuntimeError as SyntariRuntimeError
import io
from contextlib import redirect_stdout, redirect_stderr

# Import security module
from web.security import (
    RateLimiter, 
    SessionManager, 
    ResourceMonitor,
    RateLimitConfig,
    SessionConfig,
    sanitize_output,
    validate_code_safety,
)

# Import VMSecurityError for proper exception handling
try:
    from runtime import VMSecurityError
except ImportError:
    # If runtime module is not available, define a dummy class
    class VMSecurityError(Exception):
        pass


class SyntariSession:
    """Manages a persistent Syntari interpreter session for a user"""

    # Maximum number of history entries to prevent memory exhaustion
    MAX_HISTORY_SIZE = 100

    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []

    def execute(self, code: str) -> dict:
        """
        Execute Syntari code and return result

        Returns:
            dict with keys: success, output, error, result
        """
        start_time = time.time()
        
        try:
            # Capture stdout and stderr
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()

            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                # Tokenize
                tokens = tokenize(code)

                # Parse
                tree = parse(tokens)

                # Interpret
                result = self.interpreter.interpret(tree)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Get captured output and sanitize
            stdout_value = sanitize_output(output_buffer.getvalue())
            stderr_value = sanitize_output(error_buffer.getvalue()) if error_buffer.getvalue() else None

            # Store in history with size limit
            self._add_to_history(
                {
                    "code": code, 
                    "success": True, 
                    "output": stdout_value, 
                    "result": result,
                    "execution_time": execution_time,
                }
            )

            return {
                "success": True,
                "output": stdout_value,
                "error": stderr_value,
                "result": str(result) if result is not None else None,
                "execution_time": execution_time,
            }

        except LexerError as e:
            execution_time = time.time() - start_time
            error_msg = sanitize_output(f"Lexer error: {e}")
            self._add_to_history({"code": code, "success": False, "error": error_msg, "execution_time": execution_time})
            return {"success": False, "error": error_msg, "output": None, "result": None, "execution_time": execution_time}

        except ParseError as e:
            execution_time = time.time() - start_time
            error_msg = sanitize_output(f"Parse error: {e}")
            self._add_to_history({"code": code, "success": False, "error": error_msg, "execution_time": execution_time})
            return {"success": False, "error": error_msg, "output": None, "result": None, "execution_time": execution_time}

        except SyntariRuntimeError as e:
            execution_time = time.time() - start_time
            error_msg = sanitize_output(f"Runtime error: {e}")
            self._add_to_history({"code": code, "success": False, "error": error_msg, "execution_time": execution_time})
            return {"success": False, "error": error_msg, "output": None, "result": None, "execution_time": execution_time}

        except VMSecurityError as e:
            execution_time = time.time() - start_time
            # Security: Don't expose VMSecurityError details that could reveal internal limits
            error_msg = "Security limit exceeded"
            self._add_to_history({"code": code, "success": False, "error": error_msg, "execution_time": execution_time})
            return {"success": False, "error": error_msg, "output": None, "result": None, "execution_time": execution_time}

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = sanitize_output(f"Unexpected error: {e}")
            self._add_to_history({"code": code, "success": False, "error": error_msg, "execution_time": execution_time})
            return {"success": False, "error": error_msg, "output": None, "result": None, "execution_time": execution_time}

    def _add_to_history(self, entry: dict):
        """Add entry to history with size limit"""
        self.history.append(entry)
        # Trim history if it exceeds max size
        if len(self.history) > self.MAX_HISTORY_SIZE:
            self.history.pop(0)

    def get_history(self) -> list:
        """Get execution history"""
        return self.history

    def clear_history(self):
        """Clear execution history"""
        self.history = []

    def reset(self):
        """Reset interpreter session"""
        self.interpreter = Interpreter()
        self.history = []


# Store sessions per WebSocket connection
sessions = {}

# Initialize security components
rate_limiter = RateLimiter()
session_manager = SessionManager()
resource_monitor = ResourceMonitor()

# Maximum WebSocket message size (1MB)
MAX_MESSAGE_SIZE = 1024 * 1024


def get_client_ip(request) -> str:
    """Extract client IP address from request"""
    # Check for proxy headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to peername
    peername = request.transport.get_extra_info("peername")
    if peername:
        return peername[0]
    
    return "unknown"


async def websocket_handler(request):
    """Handle WebSocket connections for REPL"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Get client IP
    client_ip = get_client_ip(request)

    # Check rate limit for initial connection
    allowed, reason = rate_limiter.check_rate_limit(client_ip)
    if not allowed:
        await ws.send_json({"type": "error", "data": {"error": f"Rate limit: {reason}"}})
        await ws.close()
        return ws

    # Create new session
    session_id = id(ws)
    sessions[session_id] = SyntariSession()

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # Security: Check message size to prevent memory exhaustion
                if len(msg.data) > MAX_MESSAGE_SIZE:
                    await ws.send_json(
                        {"type": "error", "data": {"error": "Message size exceeds limit"}}
                    )
                    continue

                try:
                    data = json.loads(msg.data)
                    command = data.get("command")

                    if command == "execute":
                        code = data.get("code", "")
                        
                        # Check rate limit
                        allowed, reason = rate_limiter.check_rate_limit(client_ip)
                        if not allowed:
                            await ws.send_json({"type": "error", "data": {"error": f"Rate limit: {reason}"}})
                            continue
                        
                        # Check code length
                        allowed, reason = rate_limiter.check_code_length(code, client_ip)
                        if not allowed:
                            await ws.send_json({"type": "error", "data": {"error": reason}})
                            continue
                        
                        # Validate code safety
                        safe, reason = validate_code_safety(code)
                        if not safe:
                            await ws.send_json({"type": "error", "data": {"error": reason}})
                            continue
                        
                        # Execute code
                        result = sessions[session_id].execute(code)
                        
                        # Record metrics
                        execution_time = result.get("execution_time", 0)
                        rate_limiter.record_execution_time(
                            client_ip, 
                            execution_time, 
                            len(code), 
                            result.get("success", False)
                        )
                        resource_monitor.record_execution(client_ip, execution_time)
                        
                    command = data.get("command")

                    if command == "execute":
                        code = data.get("code", "")
                        result = sessions[session_id].execute(code)
                        await ws.send_json({"type": "result", "data": result})

                    elif command == "history":
                        history = sessions[session_id].get_history()
                        await ws.send_json({"type": "history", "data": history})

                    elif command == "clear":
                        sessions[session_id].clear_history()
                        await ws.send_json({"type": "cleared", "data": {}})

                    elif command == "reset":
                        sessions[session_id].reset()
                        await ws.send_json({"type": "reset", "data": {}})

                    else:
                        await ws.send_json(
                            {"type": "error", "data": {"error": f"Unknown command: {command}"}}
                        )

                except json.JSONDecodeError:
                    await ws.send_json(
                        {"type": "error", "data": {"error": "Invalid JSON"}}
                    )
                except Exception as e:
                    await ws.send_json(
                        {"type": "error", "data": {"error": str(e)}}
                    )

            elif msg.type == web.WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")

    finally:
        # Clean up session
        if session_id in sessions:
            del sessions[session_id]

    return ws


async def index_handler(request):
    """Serve the main REPL page"""
    html_file = Path(__file__).parent / "index.html"
    if html_file.exists():
        return web.FileResponse(html_file)
    else:
        return web.Response(text="Web REPL index.html not found", status=404)


async def admin_handler(request):
    """Serve the admin dashboard"""
    html_file = Path(__file__).parent / "admin.html"
    if html_file.exists():
        return web.FileResponse(html_file)
    else:
        return web.Response(text="Admin dashboard not found", status=404)


async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy", 
        "version": "0.4.0",
        "security": {
            "rate_limiting": "enabled",
            "session_management": "enabled",
            "resource_monitoring": "enabled",
        }
    })


async def stats_handler(request):
    """Statistics endpoint for monitoring"""
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Simple authentication check (you should use proper auth in production)
    auth_token = request.headers.get("Authorization")
    if not auth_token or auth_token != "Bearer admin-token-change-me":
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    # Gather statistics
    stats = {
        "rate_limiter": rate_limiter.get_all_stats(),
        "sessions": session_manager.get_stats(),
        "active_connections": len(sessions),
        "resource_metrics": {
            ip: resource_monitor.get_metrics(ip, window=300)
            for ip in set(c.ip_address for c in rate_limiter.clients.values())
        },
    }
    
    return web.json_response(stats)


async def client_stats_handler(request):
    """Get statistics for the current client"""
    client_ip = get_client_ip(request)
    
    stats = {
        "rate_limit": rate_limiter.get_client_stats(client_ip),
        "resources": resource_monitor.get_metrics(client_ip, window=300),
    }
    
    return web.json_response(stats)


def create_app():
    """Create and configure the web application"""
    app = web.Application()

    # Add routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/admin", admin_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/stats", stats_handler)
    app.router.add_get("/client-stats", client_stats_handler)
    app.router.add_get("/ws", websocket_handler)

    # Serve static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.router.add_static("/static/", path=static_dir, name="static")

    # Configure CORS - Development only
    # For production, configure this with specific trusted origins
    import os
    cors_origin = os.environ.get("SYNTARI_CORS_ORIGIN", "http://localhost:8080")
    
    cors = aiohttp_cors.setup(
        app,
        defaults={
            cors_origin: aiohttp_cors.ResourceOptions(
                allow_credentials=False,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )

    # Apply CORS to all routes
    for route in list(app.router.routes()):
        if not isinstance(route.resource, web.StaticResource):
            cors.add(route)

    return app


def main():
    """Run the web server"""
    app = create_app()
    print("=" * 60)
    print("Syntari Web REPL Server")
    print("=" * 60)
    print("Server starting on http://localhost:8080")
    print("Open your browser and navigate to http://localhost:8080")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    web.run_app(app, host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
