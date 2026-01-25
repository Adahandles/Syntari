"""
Syntari Web REPL - Backend Server
Provides WebSocket server for executing Syntari code in the browser
"""

import json
import sys
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

            # Get captured output
            stdout_value = output_buffer.getvalue()
            stderr_value = error_buffer.getvalue()

            # Store in history with size limit
            self._add_to_history(
                {"code": code, "success": True, "output": stdout_value, "result": result}
            )

            return {
                "success": True,
                "output": stdout_value,
                "error": stderr_value if stderr_value else None,
                "result": str(result) if result is not None else None,
            }

        except LexerError as e:
            error_msg = f"Lexer error: {e}"
            self._add_to_history({"code": code, "success": False, "error": error_msg})
            return {"success": False, "error": error_msg, "output": None, "result": None}

        except ParseError as e:
            error_msg = f"Parse error: {e}"
            self._add_to_history({"code": code, "success": False, "error": error_msg})
            return {"success": False, "error": error_msg, "output": None, "result": None}

        except SyntariRuntimeError as e:
            error_msg = f"Runtime error: {e}"
            self._add_to_history({"code": code, "success": False, "error": error_msg})
            return {"success": False, "error": error_msg, "output": None, "result": None}

        except Exception as e:
            # Security: Don't expose VMSecurityError details
            from runtime import VMSecurityError
            if isinstance(e, VMSecurityError):
                error_msg = "Security limit exceeded"
            else:
                error_msg = f"Unexpected error: {e}"
            self._add_to_history({"code": code, "success": False, "error": error_msg})
            return {"success": False, "error": error_msg, "output": None, "result": None}

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

# Maximum WebSocket message size (1MB)
MAX_MESSAGE_SIZE = 1024 * 1024


async def websocket_handler(request):
    """Handle WebSocket connections for REPL"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

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


async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({"status": "healthy", "version": "0.4.0"})


def create_app():
    """Create and configure the web application"""
    app = web.Application()

    # Add routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
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
