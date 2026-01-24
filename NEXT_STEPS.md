# Syntari Development - Next Steps

## Project Status Summary

**Current Version:** v0.3  
**Target Version:** v0.4  
**Last Updated:** 2026-01-23

### What's Working
- ✅ Bytecode compiler (`bytecode.py`) - Compiles basic Syntari expressions to .sbc format
- ✅ VM Runtime (`runtime.py`) - Executes .sbc bytecode files
- ✅ Bytecode format specification (BYTECODE_FORMAT.md)
- ✅ Language grammar specification (Syntari_v0.3_Grammar_Specification.md)
- ✅ Basic example (hello_world.syn)

### What's Missing (Placeholder Files)
- ❌ Lexer implementation (`lexer.py`, `src/interpreter/lexer.py`)
- ❌ Parser implementation (`parser.py`, `src/interpreter/parser.py`)
- ❌ AST Nodes (`nodes.py`, `src/interpreter/nodes.py`)
- ❌ Interpreter (`interpreter.py`, `src/interpreter/interpreter.py`)
- ❌ AI Core module (`src/core/ai.py`)
- ❌ System Core module (`src/core/system.py`)
- ❌ Main entry point (`main.py`, `src/interpreter/main.py`)

---

## Priority 1: Complete v0.3 Foundation

### 1.1 Implement Core Lexer
**File:** `src/interpreter/lexer.py`

**Requirements:**
- Tokenize Syntari source code according to v0.3 grammar
- Support all token types: keywords, identifiers, literals, operators, symbols
- Handle comments (single-line `//` and multi-line `/* */`)
- Proper error reporting with line/column numbers

**Reference:** Syntari_v0.3_Grammar_Specification.md (Section 1)

**Token Types Needed:**
```python
# Keywords
'use', 'type', 'trait', 'impl', 'fn', 'let', 'const', 'if', 'else', 
'while', 'match', 'return', 'true', 'false'

# Literals
INTEGER, FLOAT, STRING, BOOLEAN

# Operators
'+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', '&&', '||', '!', '='

# Delimiters
'(', ')', '{', '}', ',', ';', ':', '->', '.'
```

### 1.2 Implement Parser
**File:** `src/interpreter/parser.py`

**Requirements:**
- Parse token stream into Abstract Syntax Tree (AST)
- Support all grammar constructs from v0.3 specification
- Proper precedence handling for expressions
- Error recovery and reporting

**Grammar Support:**
- [x] Expressions (arithmetic, logical, comparison)
- [x] Variable declarations (`let`, `const`)
- [x] Function declarations (`fn`)
- [x] Control flow (`if`, `while`, `match`)
- [x] Type annotations
- [x] Import statements (`use`)
- [x] Blocks and statements

### 1.3 Implement AST Nodes
**File:** `src/interpreter/nodes.py`

**Requirements:**
- Define node classes for all grammar constructs
- Base `Node` class with visitor pattern support
- Nodes needed (at minimum):
  - `Program`, `Block`, `Statement`
  - `VarDecl`, `VarAssign`, `FuncDecl`
  - `IfStmt`, `WhileStmt`, `MatchStmt`, `ReturnStmt`
  - `BinOp`, `UnaryOp`, `Call`, `Var`
  - `Number`, `String`, `Boolean`
  - Type nodes (`TypeRef`, `TypeDecl`, `TraitDecl`)

**Current Status:** Bytecode compiler already references some nodes (Number, String, Var, VarAssign, Print, BinOp, Block) but these are not implemented.

### 1.4 Implement Tree-Walking Interpreter
**File:** `src/interpreter/interpreter.py`

**Requirements:**
- Execute AST directly for REPL and testing
- Variable scoping (global, function, block)
- Function calls and closures
- Type checking (basic)
- Error handling with stack traces

**Purpose:** Complement the bytecode VM with an interpreter for:
- Interactive REPL development
- Faster iteration during development
- Debugging AST structure
- Testing without bytecode compilation

### 1.5 Implement Core System Module
**File:** `src/core/system.py`

**Requirements:**
- `print(value)` - Output to stdout
- `trace()` - Debug trace current execution state
- `exit(code)` - Exit with status code
- `env(key)` - Get environment variable
- `time()` - Get current timestamp

### 1.6 Implement Core AI Module (Stub)
**File:** `src/core/ai.py`

**Requirements for v0.3:**
- `ai.query(prompt)` - Return stub response (real AI integration in v0.4+)
- `ai.eval(code)` - Return stub response
- `ai.suggest()` - Return stub response
- Proper error messages explaining stub nature

### 1.7 Create Main Entry Point
**File:** `src/interpreter/main.py`

**Requirements:**
- Command-line interface for running .syn files
- REPL mode (interactive)
- Compile mode (generate .sbc)
- Run mode (execute .sbc via VM)
- Help and version information

**Usage Examples:**
```bash
# Run interpreter directly
python -m src.interpreter.main hello_world.syn

# Compile to bytecode
python -m src.interpreter.main --compile hello_world.syn

# Run bytecode
python -m src.interpreter.main --run hello_world.sbc

# Interactive REPL
python -m src.interpreter.main --repl
```

### 1.8 Update Root-Level Files
**Files:** `main.py`, `lexer.py`, `parser.py`, `interpreter.py`, `nodes.py`

**Options:**
1. **Import from src/** - Make these thin wrappers that import from src/interpreter/
2. **Deprecate** - Remove these and only use src/ structure
3. **Symlinks** - Link to src/ versions

**Recommendation:** Option 1 (backwards compatibility wrapper)

---

## Priority 2: Expand Examples and Tests

### 2.1 Create More Example Programs
**Directory:** `examples/`

**Examples Needed:**
- `arithmetic.syn` - Math operations
- `variables.syn` - Variable declarations and assignments
- `functions.syn` - Function definitions and calls
- `control_flow.syn` - if/else/while
- `types.syn` - Type declarations and usage
- `ai_query_demo.syn` - AI integration (stub)

### 2.2 Add Test Suite
**Directory:** `tests/` (new)

**Test Categories:**
- Unit tests for lexer
- Unit tests for parser
- Unit tests for interpreter
- Integration tests for compilation
- Integration tests for VM execution
- Example validation tests

**Framework:** pytest or unittest

---

## Priority 3: v0.4 Features (Next Phase)

### 3.1 Networking Module
**File:** `src/core/net.py`

**Requirements:**
- HTTP client (`net.get()`, `net.post()`)
- WebSocket support (`net.ws()`)
- TCP/UDP sockets (low-level)
- TLS/SSL support
- Timeout and retry logic

### 3.2 Web-Based REPL
**Directory:** `web/` (new)

**Components:**
- Frontend: HTML/CSS/JavaScript REPL interface
- Backend: WebSocket server for code execution
- Monaco Editor or CodeMirror for syntax highlighting
- Output streaming
- Session management

**Technology Stack:**
- Backend: Flask/FastAPI + WebSockets
- Frontend: Vanilla JS or lightweight framework
- Deployment: Docker container

### 3.3 Package Manager
**File:** `src/pkg/manager.py`

**Requirements:**
- Package manifest format (syntari.toml or package.syn)
- Dependency resolution
- Local package cache
- Registry integration (future)
- Version constraints

### 3.4 Enhanced Bytecode Compiler
**Improvements to:** `bytecode.py`

**Enhancements:**
- Optimization passes (constant folding, dead code elimination)
- Control flow instructions (JMP, JMP_IF_FALSE)
- Function calls (CALL, RETURN)
- Better debug information
- Source maps for error reporting

### 3.5 JIT Compilation (Stretch Goal)
**Directory:** `src/jit/` (new)

**Approach:**
- Use LLVM bindings (llvmlite)
- Or PyPy-style tracing JIT
- Profile-guided optimization
- Hotspot detection

---

## Priority 4: Documentation and Tooling

### 4.1 Developer Documentation
**Directory:** `docs/` (new or expand)

**Documents Needed:**
- `CONTRIBUTING.md` - How to contribute
- `ARCHITECTURE.md` - System design overview
- `API_REFERENCE.md` - Core library documentation
- `TUTORIAL.md` - Getting started guide
- `EXAMPLES.md` - Annotated example walkthrough

### 4.2 Build and Development Tools
**Files to Add:**
- `requirements.txt` or `pyproject.toml` - Python dependencies
- `Makefile` or `build.sh` - Build automation
- `.editorconfig` - Code style configuration
- `.pre-commit-hooks` - Git hooks for linting
- `setup.py` - Package installation

### 4.3 CI/CD Pipeline
**File:** `.github/workflows/ci.yml`

**Steps:**
- Lint code (flake8, black, mypy)
- Run test suite
- Build bytecode for examples
- Check documentation
- Security scanning

### 4.4 VS Code Extension (Stretch)
**Directory:** `vscode-syntari/` (new)

**Features:**
- Syntax highlighting
- Code completion
- Error diagnostics
- Integrated debugger
- Run/compile commands

---

## Recommended Development Order

### Phase 1: Core Language (2-3 weeks)
1. ✅ Implement Lexer (3 days)
2. ✅ Implement Parser (5 days)
3. ✅ Implement AST Nodes (2 days)
4. ✅ Implement Interpreter (4 days)
5. ✅ Implement Core Modules (2 days)
6. ✅ Create Main Entry Point (1 day)
7. ✅ Write Examples (2 days)
8. ✅ Basic Tests (2 days)

### Phase 2: Bytecode Enhancement (1 week)
1. ✅ Fix import issues in bytecode.py
2. ✅ Add missing opcodes (JMP, JMP_IF_FALSE, CALL, RETURN)
3. ✅ Enhance compiler with control flow
4. ✅ Test compilation and execution

### Phase 3: Networking (1 week)
1. ✅ Design net module API
2. ✅ Implement HTTP client
3. ✅ Add WebSocket support
4. ✅ Write networking examples
5. ✅ Integration tests

### Phase 4: Web REPL (2 weeks)
1. ✅ Design architecture
2. ✅ Build backend (WebSocket server)
3. ✅ Build frontend (editor + output)
4. ✅ Add authentication (optional)
5. ✅ Deploy and test

### Phase 5: Documentation & Polish (1 week)
1. ✅ Write developer docs
2. ✅ API reference
3. ✅ Tutorial content
4. ✅ CI/CD setup
5. ✅ Release v0.4

---

## Technical Debt to Address

1. **Import Structure:** Current bytecode.py has relative imports that may fail. Standardize on absolute imports from project root.

2. **Code Organization:** Duplicate files at root level and in src/. Consolidate into src/ with proper package structure.

3. **Error Handling:** Add comprehensive error handling throughout lexer, parser, and runtime.

4. **Type Hints:** Add Python type hints for better IDE support and type checking.

5. **Testing:** Zero test coverage currently. Add tests before expanding features.

6. **Documentation:** Code comments are minimal. Add docstrings and inline comments.

7. **Dependencies:** No requirements.txt or package manifest. Document and lock dependencies.

---

## Quick Start for Contributors

### Immediate Next Task
**Start Here:** Implement the Lexer

1. Open `src/interpreter/lexer.py`
2. Implement tokenization according to Syntari_v0.3_Grammar_Specification.md
3. Write tests in `tests/test_lexer.py`
4. Validate with simple input strings

### Running the Project (Current State)
```bash
# The lexer, parser, nodes, and interpreter are currently placeholders
# Only bytecode.py and runtime.py have working implementations

# To test the working VM:
# 1. You need a working parser first (currently placeholder)
# 2. Then compile: python bytecode.py hello_world.syn
# 3. Then run: python runtime.py hello_world.sbc
```

---

## Questions for Project Owner

1. **AI Integration:** What AI service/API should `core.ai` integrate with in v0.4? (OpenAI, Claude, local model?)

2. **Licensing:** Is the commercial license structure final? Any planned open-source components?

3. **Target Users:** Who is the primary audience? (Blockchain devs, AI researchers, general purpose?)

4. **Performance Goals:** What performance benchmarks should we target for v0.4?

5. **Deployment:** How will users install/run Syntari? (pip package, standalone binary, Docker?)

6. **Priority Features:** Which v0.4 features are must-have vs. nice-to-have?

---

## Resources and References

### Internal Documentation
- [Syntari v0.3 Grammar Specification](Syntari_v0.3_Grammar_Specification.md)
- [Bytecode Format](BYTECODE_FORMAT.md)
- [Roadmap](ROADMAP.md)
- [README](README.md)

### External Resources
- [Crafting Interpreters](https://craftinginterpreters.com/) - Excellent guide for language implementation
- [Python AST Module](https://docs.python.org/3/library/ast.html) - Reference for AST design
- [LLVM Tutorial](https://llvm.org/docs/tutorial/) - For future JIT work

---

## Success Metrics

### v0.3 Complete (Foundation)
- ✅ Can parse all Syntari v0.3 grammar constructs
- ✅ Can execute simple programs via interpreter
- ✅ Can compile simple programs to bytecode
- ✅ Can run bytecode via VM
- ✅ Core modules (system, ai stubs) functional
- ✅ 5+ working example programs
- ✅ 80%+ test coverage

### v0.4 Complete (Networking & Web REPL)
- ✅ Networking module with HTTP/WebSocket
- ✅ Web REPL accessible via browser
- ✅ Package manager basic functionality
- ✅ JIT compilation (optional)
- ✅ Comprehensive documentation
- ✅ CI/CD pipeline operational

---

**This document should be updated as priorities shift or features are completed.**
