# Syntari Web REPL

A browser-based Read-Eval-Print Loop (REPL) for Syntari programming language.

## Features

- **Live Code Execution**: Write and run Syntari code directly in your browser
- **Persistent Sessions**: Maintains interpreter state across multiple executions
- **Syntax Examples**: Built-in examples for quick learning
- **Real-time Output**: See results immediately with color-coded output
- **WebSocket Communication**: Fast, bidirectional communication with the server
- **Keyboard Shortcuts**: Ctrl+Enter to execute code quickly

## Installation

1. Install dependencies:
```bash
pip install aiohttp aiohttp-cors
```

2. Run the server:
```bash
cd web
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

## Usage

### Running Code

1. Type or paste your Syntari code in the editor panel
2. Click "Run" or press Ctrl+Enter
3. View the output in the output panel

### Loading Examples

Use the dropdown menu to load pre-built examples:
- Hello World
- Arithmetic Operations
- Variables
- Functions
- Control Flow

### Commands

- **Run**: Execute the code in the editor
- **Clear Output**: Clear the output panel
- **Reset Session**: Reset the interpreter state (clears all variables and history)

## WebSocket API

The server exposes a WebSocket endpoint at `/ws` with the following commands:

### Execute Code
```json
{
  "command": "execute",
  "code": "print('Hello, Syntari!')"
}
```

Response:
```json
{
  "type": "result",
  "data": {
    "success": true,
    "output": "Hello, Syntari!\n",
    "error": null,
    "result": null
  }
}
```

### Get History
```json
{
  "command": "history"
}
```

### Clear History
```json
{
  "command": "clear"
}
```

### Reset Session
```json
{
  "command": "reset"
}
```

## Architecture

### Backend (app.py)
- **Framework**: aiohttp for async WebSocket server
- **Session Management**: One interpreter session per WebSocket connection
- **Output Capture**: Redirects stdout/stderr to capture execution output
- **Error Handling**: Catches and reports lexer, parser, and runtime errors

### Frontend (index.html)
- **Pure JavaScript**: No frameworks required
- **WebSocket Client**: Maintains persistent connection to backend
- **Code Editor**: Simple textarea with syntax highlighting support
- **Output Display**: Color-coded results (input, output, errors, results)

## Security

The Web REPL includes security features:
- Runs on localhost by default (127.0.0.1)
- Inherits all security protections from the Syntari interpreter:
  - SSRF prevention in network operations
  - Path traversal protection in file operations
  - Resource limits (stack size, execution time, memory)
  - Input validation

### Production Deployment

For production deployment, consider:
1. Add authentication (JWT, OAuth, etc.)
2. Use HTTPS/WSS (TLS encryption)
3. Implement rate limiting
4. Add session timeouts
5. Configure CORS properly
6. Use reverse proxy (nginx, Apache)
7. Implement user sandboxing
8. Add execution time limits per request

## Customization

### Changing the Port

Edit `app.py`:
```python
web.run_app(app, host="127.0.0.1", port=YOUR_PORT)
```

### Adding More Examples

Edit the `examples` object in `index.html`:
```javascript
const examples = {
    yourExample: `// Your Example Code
let x = 42
print(x)`,
    // ... more examples
};
```

Then add to the dropdown:
```html
<option value="yourExample">Your Example</option>
```

### Styling

The CSS is embedded in `index.html`. Customize colors, fonts, and layout as needed.

## Troubleshooting

### Connection Issues

If you see "Disconnected" status:
1. Ensure the server is running: `python app.py`
2. Check that port 8080 is not in use
3. Check browser console for WebSocket errors
4. Try a different browser

### Execution Errors

If code doesn't execute:
1. Check the output panel for error messages
2. Verify your code syntax against Syntari v0.3 grammar
3. Try the built-in examples to verify the system is working
4. Check server logs for Python exceptions

### Performance Issues

If execution is slow:
1. The interpreter may be handling complex operations
2. Check for infinite loops in your code
3. Reduce problem size for testing
4. Consider using the bytecode compiler for better performance

## Future Enhancements

Planned features for future versions:
- [ ] Syntax highlighting in editor (CodeMirror/Monaco integration)
- [ ] Code completion and intellisense
- [ ] Multi-file projects
- [ ] Debugging support (breakpoints, step-through)
- [ ] Collaborative editing (multiple users)
- [ ] Persistent storage (save projects)
- [ ] User authentication and accounts
- [ ] Embedded documentation browser
- [ ] Performance profiling
- [ ] Mobile responsive improvements

## Development

To contribute to the Web REPL:

1. Make changes to `app.py` or `index.html`
2. Test locally by running the server
3. Ensure all existing functionality works
4. Add tests if adding new features
5. Follow the Syntari contributing guidelines

## License

Part of the Syntari project. See main repository for license information.

## Support

For issues or questions:
- Open an issue on the Syntari GitHub repository
- Check the main Syntari documentation
- Contact: legal@deuos.io
