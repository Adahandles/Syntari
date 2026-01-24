# Syntari Examples

This directory contains example Syntari programs demonstrating various language features.

## Running Examples

Run any example with:
```bash
python3 main.py examples/<filename>.syn
```

Or with verbose output:
```bash
python3 main.py --verbose examples/<filename>.syn
```

## Examples

### hello_world.syn
Basic "Hello, world!" program.
```bash
python3 main.py hello_world.syn
```

### arithmetic.syn
Demonstrates arithmetic operations:
- Addition, subtraction, multiplication, division, modulo
- Operator precedence
- Parentheses for grouping

### variables.syn
Variable declarations and assignments:
- `let` declarations
- `const` declarations
- Variable assignment
- Expression evaluation

### functions.syn
Function definitions and calls:
- Simple functions
- Functions with parameters
- Recursive functions (factorial, Fibonacci)
- Return values

### control_flow.syn
Control flow structures:
- `if` statements
- `if-else` statements
- `while` loops
- Conditional logic

### error_handling.syn (v0.4)
Exception handling and error management:
- `try-catch-finally` blocks
- `throw` statements
- Custom exceptions
- Error propagation
- Nested error handling

### classes.syn (v0.4)
Object-oriented programming:
- Class definitions
- Constructors
- Properties and methods
- `this` keyword
- Object instantiation with `new`
- Multiple instances

### networking.syn (v0.4)
HTTP client and networking:
- HTTP GET, POST, PUT, DELETE requests
- Response handling with status codes
- Error handling for network failures
- WebSocket stub (full support in future release)
- Module.function syntax (net.get, net.post, etc.)

## Interactive REPL

Start the interactive REPL:
```bash
python3 main.py --repl
```

Try these commands in the REPL:
```
let x = 42
print(x)
fn double(n) { return n * 2 }
double(21)
help
exit
```

## Language Features Demonstrated

### v0.3 Features
- **Variables**: `let` and `const` declarations
- **Data Types**: Numbers (int/float), strings, booleans
- **Operators**: Arithmetic (+, -, *, /, %), comparison (<, <=, >, >=, ==, !=), logical (&&, ||, !)
- **Functions**: Declaration, parameters, return values, recursion
- **Control Flow**: if/else, while loops
- **Built-in Functions**: print(), time(), input(), trace(), exit()
- **Comments**: Single-line (//) and multi-line (/* */)

### v0.4 Features
- **Error Handling**: try-catch-finally blocks, throw statements, custom exceptions
- **Classes/OOP**: Class definitions, constructors, methods, properties, `new`, `this`
- **Networking**: HTTP client (net.get, net.post, net.put, net.delete), response handling
- **Module Functions**: Module.function syntax (ai.query, net.get, etc.)
- **Dictionary Access**: Member access on dictionaries (response.ok, response.status)

## Next Steps

Check out the documentation for more:
- `DEVELOPMENT_SUMMARY.md` - Project overview
- `Syntari_v0.3_Grammar_Specification.md` - Complete language specification
- `IMPLEMENTATION_GUIDE.md` - Implementation details
