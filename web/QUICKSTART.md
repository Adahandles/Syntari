# Starting the Syntari Web REPL

## Quick Start

1. Ensure dependencies are installed:
```bash
pip install aiohttp aiohttp-cors
```

2. Start the Web REPL server:
```bash
cd web
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

## What You'll See

The Web REPL provides a split-panel interface:
- **Left Panel**: Code editor where you write Syntari code
- **Right Panel**: Output panel showing execution results

## Features

- **Run Code**: Click "Run" button or press Ctrl+Enter
- **Examples**: Use the dropdown to load example code
- **Clear Output**: Clear the output panel
- **Reset Session**: Clear all variables and state

## Example Usage

Try this in the editor:
```syntari
let x = 42
let y = 58
print(x + y)
```

Press Ctrl+Enter to execute. You'll see:
```
>>> let x = 42...
100
```

## Troubleshooting

If the server fails to start:
- Check if port 8080 is already in use
- Ensure all dependencies are installed
- Check Python version (requires 3.8+)

For more details, see `web/README.md`
