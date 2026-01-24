# Syntari Implementation Guide

## Quick Reference for Developers

This guide provides tactical implementation details for building Syntari v0.3 components.

---

## 1. Implementing the Lexer

### Step-by-Step Implementation

**File:** `src/interpreter/lexer.py`

```python
# Basic structure
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    USE = auto()
    TYPE = auto()
    TRAIT = auto()
    IMPL = auto()
    FN = auto()
    LET = auto()
    CONST = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    MATCH = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ_EQ = auto()
    NOT_EQ = auto()
    LT = auto()
    LT_EQ = auto()
    GT = auto()
    GT_EQ = auto()
    AND_AND = auto()
    OR_OR = auto()
    BANG = auto()
    EQ = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    ARROW = auto()
    DOT = auto()
    
    # Special
    IDENTIFIER = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
    
    def _scan_token(self):
        # Implementation here
        pass
    
    def _skip_whitespace_and_comments(self):
        # Skip whitespace and comments
        pass

def tokenize(source: str) -> List[Token]:
    lexer = Lexer(source)
    return lexer.tokenize()
```

### Testing the Lexer

```python
# tests/test_lexer.py
import pytest
from src.interpreter.lexer import tokenize, TokenType

def test_simple_print():
    tokens = tokenize('print("hello")')
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "print"
    assert tokens[1].type == TokenType.LPAREN
    assert tokens[2].type == TokenType.STRING
    assert tokens[2].value == "hello"
    
def test_arithmetic():
    tokens = tokenize('1 + 2 * 3')
    assert len(tokens) == 6  # 1, +, 2, *, 3, EOF
```

---

## 2. Implementing the Parser

### Step-by-Step Implementation

**File:** `src/interpreter/parser.py`

```python
from typing import List
from src.interpreter.lexer import Token, TokenType
from src.interpreter.nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        
    def parse(self) -> Program:
        statements = []
        while not self._is_at_end():
            statements.append(self._parse_statement())
        return Program(statements)
    
    def _parse_statement(self):
        # Dispatch based on token type
        if self._match(TokenType.LET, TokenType.CONST):
            return self._parse_var_decl()
        if self._match(TokenType.FN):
            return self._parse_func_decl()
        if self._match(TokenType.IF):
            return self._parse_if_stmt()
        if self._match(TokenType.WHILE):
            return self._parse_while_stmt()
        if self._match(TokenType.RETURN):
            return self._parse_return_stmt()
        return self._parse_expr_stmt()
    
    def _parse_expression(self):
        return self._parse_logical_or()
    
    def _parse_logical_or(self):
        # Implement precedence climbing
        pass
    
    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False
    
    def _check(self, type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == type
    
    def _advance(self) -> Token:
        if not self._is_at_end():
            self.pos += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        return self.tokens[self.pos]
    
    def _previous(self) -> Token:
        return self.tokens[self.pos - 1]
```

### Precedence Table

```
Highest:
  primary       literals, identifiers, calls, grouping
  unary         !, -
  factor        *, /, %
  term          +, -
  comparison    <, <=, >, >=
  equality      ==, !=
  logical_and   &&
  logical_or    ||
Lowest
```

---

## 3. Implementing AST Nodes

**File:** `src/interpreter/nodes.py`

```python
from dataclasses import dataclass
from typing import List, Optional, Any

# Base class
class Node:
    def accept(self, visitor):
        method_name = f'visit_{self.__class__.__name__}'
        method = getattr(visitor, method_name, None)
        if method:
            return method(self)
        raise NotImplementedError(f"No visitor method {method_name}")

# Program structure
@dataclass
class Program(Node):
    statements: List[Node]

@dataclass
class Block(Node):
    statements: List[Node]

# Literals
@dataclass
class Number(Node):
    value: float

@dataclass
class String(Node):
    value: str

@dataclass
class Boolean(Node):
    value: bool

# Variables
@dataclass
class Var(Node):
    name: str

@dataclass
class VarDecl(Node):
    name: str
    type_ref: Optional[str]
    value: Node
    is_const: bool

@dataclass
class VarAssign(Node):
    name: str
    value: Node

# Expressions
@dataclass
class BinOp(Node):
    left: Node
    op: str
    right: Node

@dataclass
class UnaryOp(Node):
    op: str
    operand: Node

@dataclass
class Call(Node):
    callee: str
    args: List[Node]

# Statements
@dataclass
class Print(Node):
    expr: Node

@dataclass
class IfStmt(Node):
    condition: Node
    then_block: Block
    else_block: Optional[Block]

@dataclass
class WhileStmt(Node):
    condition: Node
    body: Block

@dataclass
class ReturnStmt(Node):
    value: Optional[Node]

@dataclass
class FuncDecl(Node):
    name: str
    params: List[tuple]  # [(name, type), ...]
    return_type: Optional[str]
    body: Block
```

---

## 4. Implementing the Interpreter

**File:** `src/interpreter/interpreter.py`

```python
from src.interpreter.nodes import *
from src.core.system import print as sys_print
from src.core.ai import query as ai_query

class Interpreter:
    def __init__(self):
        self.globals = {}
        self.locals = [{}]  # Stack of scopes
        
    def interpret(self, program: Program):
        for stmt in program.statements:
            self._execute(stmt)
    
    def _execute(self, node: Node):
        return node.accept(self)
    
    def _evaluate(self, node: Node):
        return node.accept(self)
    
    # Visitors
    def visit_Number(self, node: Number):
        return node.value
    
    def visit_String(self, node: String):
        return node.value
    
    def visit_Boolean(self, node: Boolean):
        return node.value
    
    def visit_Var(self, node: Var):
        # Look up in current scope, then outer scopes
        for scope in reversed(self.locals):
            if node.name in scope:
                return scope[node.name]
        if node.name in self.globals:
            return self.globals[node.name]
        raise RuntimeError(f"Undefined variable: {node.name}")
    
    def visit_VarDecl(self, node: VarDecl):
        value = self._evaluate(node.value)
        self.locals[-1][node.name] = value
        return value
    
    def visit_VarAssign(self, node: VarAssign):
        value = self._evaluate(node.value)
        # Update in current scope
        self.locals[-1][node.name] = value
        return value
    
    def visit_BinOp(self, node: BinOp):
        left = self._evaluate(node.left)
        right = self._evaluate(node.right)
        
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left / right
        elif node.op == '%':
            return left % right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            return left < right
        elif node.op == '<=':
            return left <= right
        elif node.op == '>':
            return left > right
        elif node.op == '>=':
            return left >= right
        elif node.op == '&&':
            return left and right
        elif node.op == '||':
            return left or right
        else:
            raise RuntimeError(f"Unknown operator: {node.op}")
    
    def visit_Print(self, node: Print):
        value = self._evaluate(node.expr)
        sys_print(value)
        return None
    
    def visit_Call(self, node: Call):
        # Built-in functions
        if node.callee == "print":
            args = [self._evaluate(arg) for arg in node.args]
            sys_print(*args)
            return None
        
        # User-defined functions
        # ... function call logic ...
        
        raise RuntimeError(f"Unknown function: {node.callee}")
    
    def visit_Block(self, node: Block):
        # Push new scope
        self.locals.append({})
        try:
            for stmt in node.statements:
                self._execute(stmt)
        finally:
            # Pop scope
            self.locals.pop()
```

---

## 5. Implementing Core Modules

### System Module

**File:** `src/core/system.py`

```python
import sys
import time as _time
import os

def print(*args, sep=' ', end='\n'):
    """Print to stdout"""
    output = sep.join(str(arg) for arg in args)
    sys.stdout.write(output + end)
    sys.stdout.flush()

def trace():
    """Print stack trace for debugging"""
    import traceback
    traceback.print_stack()

def exit(code=0):
    """Exit with status code"""
    sys.exit(code)

def env(key):
    """Get environment variable"""
    return os.environ.get(key)

def time():
    """Get current Unix timestamp"""
    return _time.time()
```

### AI Module (Stub)

**File:** `src/core/ai.py`

```python
def query(prompt):
    """
    AI query function (stub implementation for v0.3)
    In v0.4+, this will integrate with actual AI services
    """
    return f"[AI Stub] Received query: {prompt}"

def eval(code):
    """
    AI code evaluation (stub implementation for v0.3)
    """
    return f"[AI Stub] Code evaluation not yet implemented"

def suggest():
    """
    AI suggestion function (stub implementation for v0.3)
    """
    return "[AI Stub] No suggestions available"
```

---

## 6. Main Entry Point

**File:** `src/interpreter/main.py`

```python
#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

from src.interpreter.lexer import tokenize
from src.interpreter.parser import Parser
from src.interpreter.interpreter import Interpreter
from bytecode import compile_file
from runtime import run_vm

def run_file(path: str):
    """Run a Syntari source file"""
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tokens = tokenize(source)
    tree = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(tree)

def compile_and_run(path: str):
    """Compile to bytecode and run"""
    sbc_path = Path(path).with_suffix('.sbc')
    compile_file(path, str(sbc_path))
    run_vm(str(sbc_path))

def repl():
    """Interactive REPL"""
    print("Syntari v0.3 REPL")
    print("Type 'exit' to quit")
    
    interpreter = Interpreter()
    
    while True:
        try:
            line = input(">>> ")
            if line.strip().lower() in ('exit', 'quit'):
                break
            
            tokens = tokenize(line)
            tree = Parser(tokens).parse()
            interpreter.interpret(tree)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Syntari Programming Language')
    parser.add_argument('file', nargs='?', help='Syntari source file to run')
    parser.add_argument('--compile', '-c', action='store_true', 
                       help='Compile to bytecode')
    parser.add_argument('--run', '-r', action='store_true',
                       help='Run bytecode file')
    parser.add_argument('--repl', '-i', action='store_true',
                       help='Start interactive REPL')
    parser.add_argument('--version', '-v', action='version', version='Syntari 0.3')
    
    args = parser.parse_args()
    
    if args.repl:
        repl()
    elif args.file:
        if args.run:
            run_vm(args.file)
        elif args.compile:
            compile_file(args.file)
        else:
            run_file(args.file)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

---

## 7. Fix Bytecode Compiler Imports

**File:** `bytecode.py`

Update the imports at the top:

```python
# Change from relative imports to absolute
from src.interpreter.lexer import tokenize
from src.interpreter.parser import Parser
from src.interpreter.nodes import (
    Number, String, Var, VarAssign, Print, 
    BinOp, Block, Program
)
```

---

## 8. Testing Strategy

### Directory Structure
```
tests/
├── __init__.py
├── test_lexer.py
├── test_parser.py
├── test_interpreter.py
├── test_bytecode.py
├── test_vm.py
├── test_integration.py
└── fixtures/
    ├── simple.syn
    ├── arithmetic.syn
    └── functions.syn
```

### Example Test File

**File:** `tests/test_integration.py`

```python
import pytest
from src.interpreter.lexer import tokenize
from src.interpreter.parser import Parser
from src.interpreter.interpreter import Interpreter

def test_hello_world():
    code = 'print("Hello, world")'
    tokens = tokenize(code)
    tree = Parser(tokens).parse()
    interpreter = Interpreter()
    
    # Capture output
    import io
    import sys
    captured = io.StringIO()
    sys.stdout = captured
    
    interpreter.interpret(tree)
    
    sys.stdout = sys.__stdout__
    assert captured.getvalue() == "Hello, world\n"

def test_arithmetic():
    code = 'let x = 2 + 3 * 4; print(x)'
    tokens = tokenize(code)
    tree = Parser(tokens).parse()
    interpreter = Interpreter()
    interpreter.interpret(tree)
    # Check result is 14
```

---

## 9. Project Setup

### Create requirements.txt

```
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Code quality
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# Optional: JIT compilation
# llvmlite>=0.40.0
```

### Create setup.py

```python
from setuptools import setup, find_packages

setup(
    name="syntari",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'syntari=src.interpreter.main:main',
        ],
    },
    python_requires='>=3.8',
)
```

### Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "syntari"
version = "0.3.0"
description = "AI-integrated programming language"
requires-python = ">=3.8"

[tool.black]
line-length = 100
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

---

## 10. Development Workflow

### Initial Setup
```bash
# Clone repository
git clone https://github.com/Adahandles/Syntari.git
cd Syntari

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_lexer.py

# Run with verbose output
pytest -v
```

### Code Formatting
```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

### Running Syntari
```bash
# Interpret directly
syntari examples/hello_world.syn

# Compile to bytecode
syntari --compile examples/hello_world.syn

# Run bytecode
syntari --run examples/hello_world.sbc

# Start REPL
syntari --repl
```

---

## Common Pitfalls and Solutions

### 1. Import Errors
**Problem:** Relative imports fail when running from different directories

**Solution:** Use absolute imports from project root and add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/Syntari"
```

### 2. Scope Management
**Problem:** Variables leak between scopes

**Solution:** Use scope stack in interpreter, push/pop on block entry/exit

### 3. Operator Precedence
**Problem:** Expressions evaluate incorrectly (e.g., `2 + 3 * 4` gives 20 instead of 14)

**Solution:** Implement precedence climbing correctly in parser

### 4. Token Position Tracking
**Problem:** Error messages don't show where error occurred

**Solution:** Track line/column in lexer, propagate to parser and interpreter

### 5. Memory Leaks in VM
**Problem:** Stack grows indefinitely

**Solution:** Proper stack management, clear on function return

---

## Next Steps After Implementation

1. **Validate with Examples:** Run all examples and verify output
2. **Write Documentation:** Document all public APIs
3. **Performance Testing:** Benchmark interpreter vs VM
4. **Security Review:** Check for injection vulnerabilities
5. **Community Feedback:** Share with early users

---

**For questions or issues, refer to NEXT_STEPS.md or open a GitHub issue.**
