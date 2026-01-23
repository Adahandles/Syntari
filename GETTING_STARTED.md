# Getting Started with Syntari

This guide provides the **most logical order** for understanding, using, and extending the Syntari programming language.

## Quick Start (5 minutes)

### 1. Run Your First Program
```bash
# Hello World
python3 main.py hello_world.syn

# Try the REPL
python3 main.py --repl
```

### 2. Explore Examples
```bash
python3 main.py examples/functions.syn
python3 main.py examples/arithmetic.syn
python3 main.py examples/control_flow.syn
```

### 3. Write Your Own Program
Create `my_program.syn`:
```javascript
fn greet(name) {
    print("Hello,", name)
}

greet("World")

let x = 42
print("The answer is", x)
```

Run it:
```bash
python3 main.py my_program.syn
```

---

## Understanding the Codebase (30 minutes)

### Logical Reading Order

**For Users:**
1. `examples/README.md` - See what Syntari can do
2. `DEVELOPMENT_SUMMARY.md` - Understand the project
3. Run examples and REPL to get hands-on experience

**For Contributors:**
1. `DEVELOPMENT_SUMMARY.md` - Project overview (10 min)
2. `Syntari_v0.3_Grammar_Specification.md` - Language syntax
3. Follow the **Pipeline Flow** below (20 min)
4. `IMPLEMENTATION_GUIDE.md` - Deep dive into each component

### Pipeline Flow (How Code Executes)

Follow this order to understand how Syntari works:

```
Source Code (.syn) 
    ↓
1. LEXER (src/interpreter/lexer.py)
    - Converts text into tokens
    - Example: "let x = 5" → [LET, IDENTIFIER, EQUALS, NUMBER, EOF]
    ↓
2. PARSER (src/interpreter/parser.py)  
    - Converts tokens into Abstract Syntax Tree (AST)
    - Uses nodes from src/interpreter/nodes.py
    - Example: Tokens → VarDecl(name='x', value=Number(5))
    ↓
3. INTERPRETER (src/interpreter/interpreter.py)
    - Walks the AST and executes it
    - Uses visitor pattern
    - Manages variables, functions, scope
    ↓
4. OUTPUT
```

**Step-by-step walkthrough:**

1. **Start with Lexer** (`src/interpreter/lexer.py`)
   - Read `tokenize()` function
   - See how it handles keywords, operators, literals
   - Check tests: `tests/test_lexer.py`

2. **Then Parser** (`src/interpreter/parser.py`)
   - Read `parse()` function
   - Understand recursive descent parsing
   - See operator precedence handling
   - Check tests: `tests/test_parser.py`

3. **Review AST Nodes** (`src/interpreter/nodes.py`)
   - Understand the node hierarchy
   - See visitor pattern implementation
   - Check tests: `tests/test_nodes.py`

4. **Finally Interpreter** (`src/interpreter/interpreter.py`)
   - Read `interpret()` function
   - Follow visitor methods (visit_BinOp, visit_Call, etc.)
   - Understand Environment and scope management
   - Check tests: `tests/test_interpreter.py`

5. **CLI/REPL** (`src/interpreter/main.py`)
   - See how everything ties together
   - Understand different execution modes

---

## Development Order (For New Features)

### Adding Language Features

Follow this order when adding new syntax or features:

1. **Plan** - Document in NEXT_STEPS.md or ACTION_ITEMS.md
2. **Grammar** - Update Syntari_v0.3_Grammar_Specification.md
3. **Lexer** - Add new tokens if needed
4. **AST Nodes** - Create node classes for new constructs
5. **Parser** - Add parsing rules
6. **Interpreter** - Implement visitor methods
7. **Tests** - Write tests for each layer
8. **Examples** - Create example programs

### Example: Adding a `for` loop

```
1. Grammar: for (init; cond; update) { body }
2. Lexer: Add FOR token
3. Nodes: Create ForStmt class
4. Parser: Add _parse_for_stmt() method
5. Interpreter: Add visit_ForStmt() method
6. Tests: Add tests at each layer
7. Examples: Create for_loop.syn example
```

---

## Testing Order

### Running Tests

```bash
# All tests
python3 -m pytest tests/

# Individual components (in dependency order)
python3 -m pytest tests/test_lexer.py       # 1. Lexer
python3 -m pytest tests/test_nodes.py       # 2. AST Nodes  
python3 -m pytest tests/test_parser.py      # 3. Parser
python3 -m pytest tests/test_interpreter.py # 4. Interpreter

# Verbose mode
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ --cov=src
```

### Writing Tests

Order of test creation:
1. **Lexer tests** - Token generation
2. **Node tests** - AST construction
3. **Parser tests** - Parsing correctness
4. **Interpreter tests** - Execution behavior

---

## Project Structure (Logical Organization)

```
Syntari/
│
├── Documentation (Read First)
│   ├── README.md                          # Start here
│   ├── GETTING_STARTED.md                 # This file
│   ├── DEVELOPMENT_SUMMARY.md             # 10-min overview
│   ├── Syntari_v0.3_Grammar_Specification.md
│   └── ROADMAP.md                         # Vision
│
├── Planning Documents (For Development)
│   ├── ACTION_ITEMS.md                    # Task breakdown
│   ├── IMPLEMENTATION_GUIDE.md            # How to implement
│   ├── NEXT_STEPS.md                      # Future planning
│   └── ROADMAP_VISUAL.md                  # Visual roadmap
│
├── Core Implementation (Read in Order)
│   ├── src/interpreter/
│   │   ├── lexer.py         # 1. Tokenization
│   │   ├── nodes.py         # 2. AST definitions
│   │   ├── parser.py        # 3. Parsing
│   │   ├── interpreter.py   # 4. Execution
│   │   └── main.py          # 5. CLI/REPL
│   │
│   ├── src/core/
│   │   ├── system.py        # Built-in functions
│   │   └── ai.py            # AI module stubs
│   │
│   └── Root-level wrappers (Backwards compatibility)
│       ├── lexer.py
│       ├── nodes.py
│       ├── parser.py
│       ├── interpreter.py
│       └── main.py
│
├── Tests (Mirror Implementation Order)
│   ├── tests/test_lexer.py
│   ├── tests/test_nodes.py
│   ├── tests/test_parser.py
│   └── tests/test_interpreter.py
│
├── Examples (User-facing)
│   ├── examples/README.md
│   ├── examples/hello_world.syn
│   ├── examples/arithmetic.syn
│   ├── examples/variables.syn
│   ├── examples/functions.syn
│   └── examples/control_flow.syn
│
└── Legacy Systems (Not for v0.3)
    ├── bytecode/            # Bytecode compiler
    ├── runtime/             # VM runtime
    └── vm/                  # Virtual machine
```

---

## Learning Paths

### Path 1: Just Want to Use Syntari
1. Read `examples/README.md`
2. Try running examples
3. Play with REPL
4. Write your own programs
5. Check grammar spec when needed

### Path 2: Understanding How It Works
1. Read `DEVELOPMENT_SUMMARY.md`
2. Follow **Pipeline Flow** above
3. Read source in order: lexer → nodes → parser → interpreter
4. Run tests to see behavior
5. Read `IMPLEMENTATION_GUIDE.md` for details

### Path 3: Contributing/Extending
1. Complete Path 2
2. Read `NEXT_STEPS.md` for planned features
3. Read `ACTION_ITEMS.md` for task structure
4. Follow **Development Order** above
5. Submit PRs with tests

### Path 4: Research/Academic Study
1. Read `Syntari_v0.3_Grammar_Specification.md`
2. Study `src/interpreter/parser.py` (recursive descent)
3. Study `src/interpreter/interpreter.py` (tree-walking, visitor pattern)
4. Read tests to understand edge cases
5. Compare with other interpreters (Python, Ruby, Lua)

---

## Common Workflows

### Debugging a Program

```bash
# Run with verbose output
python3 main.py --verbose my_program.syn

# Use REPL to test expressions
python3 main.py --repl
>>> let x = 5
>>> print(x)
>>> exit
```

### Adding a Built-in Function

1. Add function to `src/core/system.py` or `src/core/ai.py`
2. Handle in `Interpreter.visit_Call()` in `src/interpreter/interpreter.py`
3. Add tests in `tests/test_interpreter.py`
4. Document in examples

### Fixing a Bug

1. **Identify the layer** - Lexer? Parser? Interpreter?
2. **Write a failing test** - Add to appropriate test file
3. **Fix the bug** - Modify appropriate source file
4. **Verify** - Run tests, check examples still work
5. **Document** - Update docs if behavior changes

---

## Version Navigation

### v0.3 (Current - Complete)
- Interpreter pipeline
- Basic language features
- CLI and REPL
- **Status:** Production ready

### v0.4 (Planned)
See `NEXT_STEPS.md` for:
- Networking module
- Web-based REPL
- Package manager
- JIT compilation
- Advanced features

---

## Key Concepts

### Execution Models

Syntari has **two execution paths**:

1. **Interpreter Path** (v0.3 - Current)
   - Source → Lexer → Parser → Interpreter → Output
   - Direct AST execution
   - Good for: Development, scripting, REPL

2. **Bytecode Path** (Legacy, pre-v0.3)
   - Source → Compiler → Bytecode → VM → Output
   - Compile once, run many times
   - Good for: Production, distribution

### Design Patterns

- **Visitor Pattern** - AST traversal (see `nodes.py` and `interpreter.py`)
- **Recursive Descent** - Parsing (see `parser.py`)
- **Environment Chain** - Scoping (see `Environment` in `interpreter.py`)

---

## Troubleshooting

### Tests Not Running
```bash
# Install pytest
pip install --user pytest

# Verify installation
python3 -m pytest --version
```

### Import Errors
```bash
# Make sure you're in the project root
cd /path/to/Syntari

# Run with python3 -m
python3 -m pytest tests/
```

### Examples Not Working
```bash
# Check Python version (need 3.7+)
python3 --version

# Run with full path
python3 /path/to/Syntari/main.py hello_world.syn
```

---

## Resources

- **Quick Reference**: `examples/README.md`
- **Language Spec**: `Syntari_v0.3_Grammar_Specification.md`
- **Architecture**: `DEVELOPMENT_SUMMARY.md`
- **Implementation**: `IMPLEMENTATION_GUIDE.md`
- **Future Plans**: `NEXT_STEPS.md`
- **Tasks**: `ACTION_ITEMS.md`

---

## Summary: Most Logical Order

**To Use Syntari:**
examples → REPL → write programs

**To Understand Syntari:**
DEVELOPMENT_SUMMARY → Pipeline Flow → Source code (lexer → parser → interpreter)

**To Extend Syntari:**
Understand path → NEXT_STEPS → Development Order → Tests → PR

**To Review Code:**
Tests first (see behavior) → Source code (see implementation) → Examples (see usage)

---

## Next Steps

Now that you understand the logical order, choose your path:

- **Want to code?** → Write a .syn program
- **Want to learn?** → Read DEVELOPMENT_SUMMARY.md
- **Want to contribute?** → Read IMPLEMENTATION_GUIDE.md
- **Want to plan v0.4?** → Read NEXT_STEPS.md

Welcome to Syntari! 🚀
