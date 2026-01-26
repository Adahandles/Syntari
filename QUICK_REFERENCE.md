# Syntari v0.4.0 - Quick Reference Card

## Installation
```bash
git clone https://github.com/Adahandles/Syntari.git
cd Syntari
./setup.sh
```

## Basic Commands
```bash
# Run a program
python3 main.py script.syn

# Interactive REPL
python3 main.py --repl

# Show version
python3 main.py --version

# Debug mode
python3 main.py --debug script.syn

# Profile performance
python3 main.py --profile script.syn
```

## Make Commands
```bash
make help          # Show all commands
make test          # Run tests
make lint          # Run linters
make format        # Format code
make security      # Security scan
make docker-build  # Build Docker image
make docker-run    # Run in Docker
make benchmark     # Run benchmarks
```

## Package Manager
```bash
syntari pkg init              # Initialize package
syntari pkg install <name>    # Install package
syntari pkg list              # List installed
syntari pkg remove <name>     # Remove package
syntari pkg search <query>    # Search packages
```

## Docker
```bash
# Build image
docker build -t syntari:0.4.0 .

# Run container
docker run -it syntari:0.4.0

# With Docker Compose
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose logs -f        # View logs
```

## REPL Commands
```
help       - Show help
version    - Show version
exit       - Exit REPL
quit       - Exit REPL
clear      - Clear screen
vars       - Show variables
```

## Language Syntax

### Variables
```javascript
let x = 42              // Mutable
const y = "hello"       // Immutable
```

### Functions
```javascript
fn add(a, b) {
    return a + b
}

let result = add(5, 3)
```

### Control Flow
```javascript
if (x > 10) {
    print("big")
} else {
    print("small")
}

while (x > 0) {
    x = x - 1
}
```

### Arrays
```javascript
let arr = [1, 2, 3, 4]
print(arr[0])           // 1
```

### Comments
```javascript
// Single line comment

/* Multi-line
   comment */
```

## Built-in Functions
```javascript
print(value)            // Output to console
trace()                 // Print stack trace
exit(code)              // Exit program
env(key)                // Get environment variable
time()                  // Current timestamp
```

## Networking (Web Module)
```javascript
use net

// HTTP GET
let response = net.get("https://api.example.com")

// HTTP POST
let data = {key: "value"}
let response = net.post("https://api.example.com", data)
```

## AI Functions (Stub)
```javascript
use ai

let answer = ai.query("What is 2+2?")
print(answer)
```

## Error Types
- SyntaxError - Code syntax issues
- TypeError - Type mismatches
- NameError - Undefined variables
- RuntimeError - Execution errors
- ImportError - Module import failures

## Performance
- Interpreter: ~50K ops/sec
- Bytecode: ~290K-510K ops/sec
- Speedup: 5-10x via compilation

## File Extensions
- `.syn` - Syntari source code
- `.sbc` - Syntecode bytecode

## Environment Variables
```bash
SYNTARI_ENV=production       # production/development
LOG_LEVEL=INFO               # DEBUG/INFO/WARNING/ERROR
WEB_REPL_PORT=8765           # Web REPL port
```

## Project Structure
```
syntari/
├── src/
│   ├── interpreter/     # Lexer, Parser, Interpreter
│   ├── compiler/        # Bytecode compiler
│   ├── runtime/         # VM runtime
│   ├── core/            # Core modules
│   ├── tools/           # Debugger, LSP, Profiler
│   └── pkg/             # Package manager
├── examples/            # Example programs
├── tests/               # Test suite
└── web/                 # Web REPL
```

## Useful Links
- GitHub: https://github.com/Adahandles/Syntari
- Docs: See README.md and guides/
- Issues: Submit via GitHub Issues
- Security: legal@deuos.io

## Quick Tips
1. Use `--profile` to find bottlenecks
2. Use `--debug` for interactive debugging
3. Check `examples/` for sample code
4. Run `make test` before committing
5. Use Docker for deployment

## Version: 0.4.0
**Status**: Production Ready ✅
**Release**: January 26, 2026
