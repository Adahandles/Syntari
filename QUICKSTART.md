# Syntari Quick Start Guide

**Get up and running with Syntari in 5 minutes!**

---

## Installation (1 minute)

```bash
# Clone the repository
git clone https://github.com/Adahandles/Syntari.git
cd Syntari

# Install dependencies (if needed)
pip install -r requirements.txt

# Or use the setup script
./setup.sh
```

---

## Your First Program (1 minute)

Create `hello.syn`:

```javascript
fn main() {
    print("Hello, Syntari!")
    
    let x = 42
    let y = x * 2
    print("The answer is:", y)
}

main()
```

Run it:

```bash
python3 main.py hello.syn
```

Output:
```
Hello, Syntari!
The answer is: 84
```

---

## Interactive REPL (1 minute)

```bash
python3 main.py --repl
```

Try these commands:

```javascript
>>> let x = 10
>>> let y = 20
>>> print(x + y)
30
>>> fn greet(name) { print("Hello,", name) }
>>> greet("World")
Hello, World
>>> exit
```

---

## Running Examples (1 minute)

```bash
# Try the provided examples
python3 main.py examples/functions.syn
python3 main.py examples/control_flow.syn
python3 main.py examples/arithmetic.syn

# Or run all examples
for f in examples/*.syn; do
    echo "Running $f..."
    python3 main.py "$f"
    echo ""
done
```

---

## Testing & Development (1 minute)

```bash
# Run tests
make test

# Run benchmarks
make benchmark

# Check code quality
make lint
make format-check

# Run security checks
make security
```

---

## Key Commands

| Command | Description |
|---------|-------------|
| `python3 main.py <file.syn>` | Run a Syntari program |
| `python3 main.py --repl` | Start interactive REPL |
| `python3 main.py --profile <file>` | Profile performance |
| `python3 main.py --debug <file>` | Debug with breakpoints |
| `make test` | Run all tests |
| `make benchmark` | Run performance benchmarks |
| `make help` | Show all available commands |

---

## Language Basics

### Variables

```javascript
let x = 42           // Mutable variable
const PI = 3.14159   // Immutable constant
let name = "Alice"   // Strings
let flag = true      // Booleans
```

### Functions

```javascript
fn add(a, b) {
    return a + b
}

let result = add(10, 20)
print(result)  // 30
```

### Control Flow

```javascript
// If statement
if (x > 10) {
    print("x is large")
} else {
    print("x is small")
}

// While loop
let i = 0
while (i < 5) {
    print(i)
    i = i + 1
}
```

### Built-in Functions

```javascript
print("Hello")           // Print to stdout
trace()                  // Print stack trace (debugging)
exit(0)                  // Exit program
time()                   // Get current Unix timestamp
```

---

## Next Steps

1. **Read the docs:** [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Explore examples:** Check out `examples/` directory
3. **Learn the syntax:** [Syntari_v0.3_Grammar_Specification.md](Syntari_v0.3_Grammar_Specification.md)
4. **Deploy to production:** [DEPLOYMENT.md](DEPLOYMENT.md)
5. **Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Common Issues

### Import Error: No module named 'src'

```bash
# Make sure you're in the project root
cd /path/to/Syntari

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Tests Not Running

```bash
# Install pytest
pip install pytest pytest-cov

# Run from project root
python3 -m pytest tests/
```

### Examples Don't Work

```bash
# Check Python version (need 3.8+)
python3 --version

# Verify installation
python3 -c "from src.interpreter.lexer import tokenize; print('OK')"
```

---

## Getting Help

- **Documentation:** See [README.md](README.md) for complete guide
- **Issues:** https://github.com/Adahandles/Syntari/issues
- **Email:** legal@deuos.io

---

## Example Programs

### Fibonacci

```javascript
fn fib(n) {
    if (n <= 1) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

print("Fibonacci(10) =", fib(10))
```

### Factorial

```javascript
fn factorial(n) {
    if (n <= 1) {
        return 1
    }
    return n * factorial(n - 1)
}

print("5! =", factorial(5))
```

### Greeting System

```javascript
fn greet(name, lang) {
    if (lang == "en") {
        print("Hello,", name)
    } else if (lang == "es") {
        print("Hola,", name)
    } else if (lang == "fr") {
        print("Bonjour,", name)
    } else {
        print("Hi,", name)
    }
}

greet("Alice", "en")
greet("Bob", "es")
greet("Charlie", "fr")
```

---

**You're ready to start coding in Syntari!** 🚀

For more detailed information, see [GETTING_STARTED.md](GETTING_STARTED.md) and [CURRENT_STATUS.md](CURRENT_STATUS.md).

---

**Copyright © 2024-2026 DeuOS, LLC**
