# Syntari Development - Immediate Action Items

## Priority Tasks for Next 2 Weeks

This document outlines the most critical tasks to complete v0.3 and prepare for v0.4.

---

## Week 1: Core Language Implementation

### Day 1-2: Lexer Implementation ⚡ HIGHEST PRIORITY
**File:** `src/interpreter/lexer.py`

**Status:** ❌ Placeholder only

**Tasks:**
- [ ] Define TokenType enum (all keywords, operators, literals)
- [ ] Create Token dataclass with type, value, line, column
- [ ] Implement Lexer class with source scanning
- [ ] Handle single-line comments (`//`)
- [ ] Handle multi-line comments (`/* */`)
- [ ] Tokenize integers, floats, strings, booleans
- [ ] Tokenize identifiers and keywords
- [ ] Tokenize all operators (arithmetic, logical, comparison)
- [ ] Track line and column numbers for errors
- [ ] Write unit tests (15+ test cases)

**Success Criteria:**
```python
tokens = tokenize('let x = 42 + 3.14; print(x)')
# Should produce: LET, IDENTIFIER("x"), EQ, INTEGER(42), PLUS, FLOAT(3.14), SEMICOLON, ...
```

**Estimated Time:** 8-12 hours

---

### Day 3-5: Parser Implementation ⚡ HIGH PRIORITY
**File:** `src/interpreter/parser.py`

**Status:** ❌ Placeholder only

**Dependencies:** Lexer must be complete

**Tasks:**
- [ ] Implement Parser class with token stream handling
- [ ] Recursive descent parser structure
- [ ] Parse expressions with correct precedence:
  - [ ] Logical OR (`||`)
  - [ ] Logical AND (`&&`)
  - [ ] Equality (`==`, `!=`)
  - [ ] Comparison (`<`, `<=`, `>`, `>=`)
  - [ ] Addition/Subtraction (`+`, `-`)
  - [ ] Multiplication/Division (`*`, `/`, `%`)
  - [ ] Unary (`!`, `-`)
  - [ ] Primary (literals, identifiers, calls, groups)
- [ ] Parse statements:
  - [ ] Variable declarations (`let`, `const`)
  - [ ] Assignments
  - [ ] If statements
  - [ ] While loops
  - [ ] Return statements
  - [ ] Function declarations
  - [ ] Expression statements
- [ ] Parse blocks (`{ ... }`)
- [ ] Error recovery and reporting
- [ ] Write unit tests (20+ test cases)

**Success Criteria:**
```python
tokens = tokenize('let x = 2 + 3; print(x)')
tree = Parser(tokens).parse()
# Should produce valid AST with VarDecl, BinOp, Print nodes
```

**Estimated Time:** 16-20 hours

---

### Day 3-4 (Parallel): AST Nodes ⚡ HIGH PRIORITY
**File:** `src/interpreter/nodes.py`

**Status:** ❌ Placeholder only

**Dependencies:** None (can start immediately)

**Tasks:**
- [ ] Define base Node class with visitor pattern
- [ ] Define all expression nodes:
  - [ ] Number, String, Boolean literals
  - [ ] Var (variable reference)
  - [ ] BinOp (binary operators)
  - [ ] UnaryOp (unary operators)
  - [ ] Call (function calls)
- [ ] Define all statement nodes:
  - [ ] VarDecl, VarAssign
  - [ ] IfStmt, WhileStmt, MatchStmt
  - [ ] ReturnStmt
  - [ ] FuncDecl
  - [ ] Print
- [ ] Define structural nodes:
  - [ ] Program, Block
- [ ] Add type annotations for all nodes
- [ ] Add `__repr__` methods for debugging
- [ ] Write unit tests

**Success Criteria:**
```python
node = BinOp(Number(2), '+', Number(3))
assert node.left.value == 2
assert node.op == '+'
```

**Estimated Time:** 6-8 hours

---

### Day 6-7: Interpreter Implementation ⚡ HIGH PRIORITY
**File:** `src/interpreter/interpreter.py`

**Status:** ❌ Placeholder only

**Dependencies:** Lexer, Parser, Nodes must be complete

**Tasks:**
- [ ] Implement Interpreter class with visitor pattern
- [ ] Environment/scope management (stack of scopes)
- [ ] Evaluate expressions:
  - [ ] Literals return their values
  - [ ] Variables look up in scope stack
  - [ ] Binary operations compute results
  - [ ] Unary operations compute results
- [ ] Execute statements:
  - [ ] Variable declarations add to scope
  - [ ] Assignments update variables
  - [ ] If statements evaluate condition and branch
  - [ ] While loops evaluate condition and iterate
  - [ ] Print outputs to stdout
- [ ] Function calls (basic - no closures yet)
- [ ] Error handling with meaningful messages
- [ ] Write integration tests (10+ test cases)

**Success Criteria:**
```python
code = 'let x = 10; let y = 20; print(x + y)'
tokens = tokenize(code)
tree = Parser(tokens).parse()
interpreter = Interpreter()
interpreter.interpret(tree)
# Should output: 30
```

**Estimated Time:** 12-16 hours

---

### Day 6-7 (Parallel): Core Modules 🔧 MEDIUM PRIORITY
**Files:** `src/core/system.py`, `src/core/ai.py`

**Status:** ❌ Placeholder only

**Tasks:**

#### System Module (`src/core/system.py`)
- [ ] Implement `print(*args)` - output to stdout
- [ ] Implement `trace()` - print stack trace
- [ ] Implement `exit(code)` - exit program
- [ ] Implement `env(key)` - get environment variable
- [ ] Implement `time()` - get current timestamp
- [ ] Write unit tests

#### AI Module (`src/core/ai.py`)
- [ ] Implement `query(prompt)` - stub with placeholder response
- [ ] Implement `eval(code)` - stub with placeholder response
- [ ] Implement `suggest()` - stub with placeholder response
- [ ] Add docstrings explaining stub nature
- [ ] Write unit tests

**Success Criteria:**
```python
from src.core.system import print, time
from src.core.ai import query

print("Hello")  # Outputs: Hello
t = time()  # Returns float timestamp
result = query("test")  # Returns stub message
```

**Estimated Time:** 4-6 hours

---

## Week 2: Integration, Testing, and Examples

### Day 8-9: Main Entry Point and Integration 🔧 MEDIUM PRIORITY
**File:** `src/interpreter/main.py`

**Status:** ❌ Placeholder only

**Dependencies:** All core components must be working

**Tasks:**
- [ ] Implement command-line argument parsing
- [ ] File execution mode: `syntari file.syn`
- [ ] REPL mode: `syntari --repl`
- [ ] Compile mode: `syntari --compile file.syn`
- [ ] Run bytecode mode: `syntari --run file.sbc`
- [ ] Version and help output
- [ ] Proper error handling and user-friendly messages
- [ ] Write integration tests

**Success Criteria:**
```bash
$ syntari hello_world.syn
Hello, world

$ syntari --repl
>>> print(2 + 2)
4
>>> exit

$ syntari --compile hello_world.syn
# Creates hello_world.sbc
```

**Estimated Time:** 8-10 hours

---

### Day 9-10: Fix Bytecode Compiler 🔧 MEDIUM PRIORITY
**File:** `bytecode.py`

**Status:** ⚠️ Partially implemented but has import issues

**Tasks:**
- [ ] Fix imports to use absolute paths from src/
- [ ] Test compilation with new lexer/parser
- [ ] Verify bytecode output format
- [ ] Test VM execution of compiled bytecode
- [ ] Add missing opcodes if needed (JMP, JMP_IF_FALSE, CALL, RETURN)
- [ ] Update bytecode compiler to handle control flow
- [ ] Write integration tests

**Success Criteria:**
```bash
$ python bytecode.py hello_world.syn
# Creates hello_world.sbc

$ python runtime.py hello_world.sbc
Hello, world
[Syntari VM] Execution complete.
```

**Estimated Time:** 6-8 hours

---

### Day 10-11: Comprehensive Example Programs 📝 LOW PRIORITY
**Directory:** `examples/`

**Status:** ❌ Only hello_world.syn exists

**Tasks:**
- [ ] Create `examples/arithmetic.syn` - Basic math operations
- [ ] Create `examples/variables.syn` - Variable declarations and assignments
- [ ] Create `examples/functions.syn` - Function definitions and calls
- [ ] Create `examples/control_flow.syn` - if/else/while
- [ ] Create `examples/recursion.syn` - Recursive functions (factorial, fibonacci)
- [ ] Create `examples/ai_query_demo.syn` - AI integration stub
- [ ] Create `examples/README.md` - Explain each example
- [ ] Verify all examples run correctly

**Example Content:**

**arithmetic.syn:**
```syntari
// Basic arithmetic operations
let a = 10
let b = 5

print(a + b)  // 15
print(a - b)  // 5
print(a * b)  // 50
print(a / b)  // 2
print(a % b)  // 0

let x = 2 + 3 * 4  // Should be 14 (not 20)
print(x)
```

**Estimated Time:** 6-8 hours

---

### Day 11-12: Test Suite 🧪 MEDIUM PRIORITY
**Directory:** `tests/`

**Status:** ❌ No tests exist

**Tasks:**
- [ ] Create test directory structure
- [ ] Write `tests/test_lexer.py` (15+ tests)
- [ ] Write `tests/test_parser.py` (20+ tests)
- [ ] Write `tests/test_interpreter.py` (15+ tests)
- [ ] Write `tests/test_bytecode.py` (10+ tests)
- [ ] Write `tests/test_vm.py` (10+ tests)
- [ ] Write `tests/test_integration.py` (10+ tests)
- [ ] Set up pytest configuration
- [ ] Run full test suite and fix failures
- [ ] Measure code coverage (target: 80%+)

**Key Test Categories:**
- Unit tests for each component
- Integration tests for end-to-end flows
- Edge cases and error conditions
- Performance tests (optional)

**Success Criteria:**
```bash
$ pytest
======================== test session starts =========================
collected 90 items

tests/test_lexer.py ................               [ 17%]
tests/test_parser.py ....................          [ 40%]
tests/test_interpreter.py ...............          [ 56%]
tests/test_bytecode.py ..........                  [ 67%]
tests/test_vm.py ..........                        [ 78%]
tests/test_integration.py ..........               [100%]

========================= 90 passed in 2.34s =========================
```

**Estimated Time:** 12-16 hours

---

### Day 13: Documentation and Polish 📚 LOW PRIORITY
**Files:** Various documentation updates

**Tasks:**
- [ ] Update README.md with installation instructions
- [ ] Add usage examples to README.md
- [ ] Create `CONTRIBUTING.md` for contributors
- [ ] Update code with docstrings and comments
- [ ] Run code formatter (black)
- [ ] Run linter (flake8)
- [ ] Add type hints (mypy)
- [ ] Create changelog for v0.3

**Estimated Time:** 6-8 hours

---

### Day 14: Root-Level File Updates 🔧 LOW PRIORITY
**Files:** `main.py`, `lexer.py`, `parser.py`, `interpreter.py`, `nodes.py`

**Current Status:** ⚠️ All are placeholders

**Decision Required:** Choose one approach:

**Option A: Import Wrappers (Recommended)**
```python
# lexer.py
from src.interpreter.lexer import *

# This allows: import lexer; lexer.tokenize(...)
# Maintains backwards compatibility
```

**Option B: Deprecation Notice**
```python
# lexer.py
import warnings
warnings.warn("lexer.py is deprecated, use src.interpreter.lexer", DeprecationWarning)
from src.interpreter.lexer import *
```

**Option C: Remove Entirely**
- Delete root-level files
- Update all imports to use src.interpreter.*
- Update documentation

**Tasks:**
- [ ] Choose approach (consult with project owner)
- [ ] Implement chosen approach
- [ ] Update imports in bytecode.py and runtime.py
- [ ] Update documentation
- [ ] Test all import paths work

**Estimated Time:** 2-4 hours

---

## Post-Week 2: Stretch Goals

### If Time Permits

1. **Enhanced REPL** (4-6 hours)
   - Syntax highlighting
   - Multi-line input
   - History and completion
   - Use `prompt_toolkit` library

2. **Basic Type Checking** (8-10 hours)
   - Type annotations enforcement
   - Type inference for literals
   - Type error messages
   - Add type checker pass before execution

3. **Better Error Messages** (4-6 hours)
   - Show source code context
   - Highlight error location with ^
   - Suggest fixes for common errors
   - Stack traces with line numbers

4. **Performance Benchmarks** (4-6 hours)
   - Create benchmark suite
   - Compare interpreter vs bytecode VM
   - Profile hot paths
   - Document performance characteristics

---

## Blockers and Dependencies

### Critical Path
```
Lexer → Parser → Interpreter → Main Entry Point
  ↓       ↓          ↓
Nodes ←───┴──────────┘
  ↓
Bytecode Compiler (update imports)
```

### Parallel Tracks
```
Track 1: Lexer → Parser → Interpreter (Week 1, Days 1-7)
Track 2: Nodes implementation (Week 1, Days 3-4)
Track 3: Core Modules (Week 1, Days 6-7)
Track 4: Examples + Tests (Week 2, Days 10-12)
```

---

## Success Metrics

### Week 1 Complete When:
- ✅ Can tokenize any valid Syntari v0.3 code
- ✅ Can parse any valid Syntari v0.3 code
- ✅ Can interpret basic programs (arithmetic, variables, control flow)
- ✅ Core modules (system, ai) are functional
- ✅ Basic manual testing shows correct behavior

### Week 2 Complete When:
- ✅ Main entry point works (run files, REPL, compile)
- ✅ Bytecode compilation and VM execution works
- ✅ 7+ example programs run correctly
- ✅ 80+ unit and integration tests passing
- ✅ Documentation is updated
- ✅ Code is formatted and linted

### v0.3 Complete When:
- ✅ All above criteria met
- ✅ Can demonstrate full pipeline: .syn → tokens → AST → execution
- ✅ Can demonstrate bytecode pipeline: .syn → .sbc → VM execution
- ✅ No critical bugs
- ✅ Ready to begin v0.4 development

---

## Risk Management

### High Risk Items

1. **Parser Complexity**
   - Risk: Incorrect precedence leads to wrong evaluation
   - Mitigation: Test extensively with arithmetic expressions, use proven precedence climbing

2. **Scope Management**
   - Risk: Variable leakage between scopes
   - Mitigation: Use explicit scope stack, test nested scopes thoroughly

3. **Bytecode Import Issues**
   - Risk: Import errors prevent compilation
   - Mitigation: Fix imports first, use absolute paths, test in clean environment

4. **Time Estimation**
   - Risk: Tasks take longer than estimated
   - Mitigation: Focus on critical path first, defer stretch goals, ask for help

### Medium Risk Items

1. **Test Coverage Gaps**
   - Mitigation: Write tests as you code, not after

2. **Documentation Lag**
   - Mitigation: Add docstrings immediately, update docs incrementally

3. **Performance Issues**
   - Mitigation: Profile early if slow, optimize hot paths only

---

## Daily Checklist Template

Use this checklist each day:

```markdown
## Day X - [Date]

### Goals for Today
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Completed
- [x] ...
- [x] ...

### Blockers
- Issue 1: ...
- Issue 2: ...

### Notes
- ...
- ...

### Tomorrow
- ...
```

---

## Getting Help

### If Stuck:
1. Review IMPLEMENTATION_GUIDE.md for code examples
2. Check Syntari_v0.3_Grammar_Specification.md
3. Look at "Crafting Interpreters" book (free online)
4. Ask in project Discord/Slack
5. Open GitHub issue with specific question

### Resources:
- [Crafting Interpreters](https://craftinginterpreters.com/)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)

---

**Last Updated:** 2026-01-23  
**Next Review:** After Week 1 completion

**Let's build Syntari! 🚀**
