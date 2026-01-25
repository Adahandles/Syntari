# GitHub Copilot Instructions for Syntari

## Project Overview

Syntari is an AI-integrated, type-safe, functional-first programming language developed by DeuOS, LLC. It combines deterministic computing, adaptive intelligence, and low-level performance into one unified ecosystem.

## Language and Technology Stack

- **Primary Language**: Python 3.8+
- **Project Type**: Programming language implementation (interpreter, compiler, runtime)
- **Testing Framework**: pytest with coverage reporting
- **Code Quality Tools**: Black (formatter), flake8 (linter), mypy (type checker)
- **Build System**: setuptools with pyproject.toml

## Code Style Guidelines

### Python Style
- Follow PEP 8 with **100 character line length**
- Use Black for automatic code formatting
- Type hints are encouraged where appropriate
- Docstrings should follow Google style format

### Naming Conventions
- Classes: `PascalCase` (e.g., `TokenType`, `ASTNode`)
- Functions/methods: `snake_case` (e.g., `parse_expression`, `evaluate_node`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RECURSION_DEPTH`)
- Private members: prefix with `_` (e.g., `_internal_state`)

### Import Organization
```python
# 1. Standard library imports
import os
import sys

# 2. Third-party imports
import pytest

# 3. Local application imports
from src.interpreter.lexer import Lexer
from src.core.types import Type
```

## Project Structure

```
Syntari/
├── src/
│   ├── core/          # Core modules (types, AI integration)
│   └── interpreter/   # Interpreter implementation
├── tests/             # Test files (must mirror src structure)
├── examples/          # Example Syntari programs (.syn files)
├── pyproject.toml     # Project configuration
└── Makefile          # Development commands
```

## Development Best Practices

### Testing
- All new features MUST include tests
- Tests should be placed in `tests/` directory
- Test files must start with `test_` prefix
- Aim for high test coverage (current standard: comprehensive coverage)
- Run tests with: `make test` or `pytest tests/`

### Code Quality Checks
Before committing code:
1. **Format**: `make format` or `black src/ tests/`
2. **Lint**: `make lint` or `flake8 src/ tests/`
3. **Type Check**: `mypy src/ --ignore-missing-imports`
4. **Test**: `make test` or `pytest tests/ -v`

### Security Considerations
- This is a programming language implementation - be mindful of:
  - Input validation in parsers and lexers
  - Proper error handling to prevent crashes
  - Memory safety in runtime operations
  - Sandbox security for code execution
- Never commit credentials or API keys
- Validate all external inputs

## Syntari Language Specifics

### File Extensions
- `.syn` - Syntari source files
- `.sbc` - Syntari bytecode files

### Key Components
- **Lexer**: Tokenizes Syntari source code
- **Parser**: Builds Abstract Syntax Tree (AST)
- **Interpreter**: Executes AST nodes
- **Runtime**: Manages execution environment
- **Bytecode**: Compilation target for JIT execution

### Core Modules
- `core.ai` - AI integration and reasoning
- `core.type` - Type system and type checking
- `core.system` - System operations

## Common Patterns

### Error Handling
```python
# Use custom exception types
class SyntariError(Exception):
    """Base exception for Syntari errors"""
    pass

class ParseError(SyntariError):
    """Raised during parsing"""
    pass

# Provide helpful error messages with context
raise ParseError(f"Unexpected token {token} at line {line}")
```

### AST Node Pattern
```python
from dataclasses import dataclass
from typing import List

@dataclass
class ASTNode:
    """Base class for AST nodes"""
    pass

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
```

### Visitor Pattern for AST Traversal
```python
def visit(node: ASTNode):
    method_name = f'visit_{type(node).__name__}'
    visitor = getattr(self, method_name, self.generic_visit)
    return visitor(node)
```

## Helpful Commands

```bash
# Development
make install          # Install in development mode
make test            # Run all tests
make test-verbose    # Run tests with detailed output
make lint            # Run linters
make format          # Format code with Black
make format-check    # Check if formatting is needed
make clean           # Clean build artifacts
make build           # Build distribution packages

# Running Syntari
python3 main.py <file.syn>     # Run a Syntari program
python3 main.py --repl         # Start interactive REPL
make repl                      # Start REPL
make examples                  # Run all examples
```

## Documentation

- **Getting Started**: [GETTING_STARTED.md](../GETTING_STARTED.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Implementation Guide**: [IMPLEMENTATION_GUIDE.md](../IMPLEMENTATION_GUIDE.md)
- **Language Spec**: [Syntari_v0.3_Grammar_Specification.md](../Syntari_v0.3_Grammar_Specification.md)
- **Roadmap**: [ROADMAP_VISUAL.md](../ROADMAP_VISUAL.md)

## Copilot-Specific Guidance

When generating code suggestions:
1. **Respect the functional-first paradigm** of Syntari
2. **Include type hints** where helpful
3. **Follow the existing patterns** in the codebase
4. **Generate comprehensive tests** for new functionality
5. **Consider edge cases** in parser/interpreter logic
6. **Add docstrings** for public APIs
7. **Keep security in mind** - validate inputs, handle errors gracefully
8. **Maintain backwards compatibility** with existing Syntari v0.3 code

## Priority Areas

Current development focuses:
- Type system implementation and type inference
- JIT compiler optimization
- AI module integration (`core.ai`)
- Package manager functionality
- Security hardening and sandboxing
- Performance optimization

## License Note

Syntari is proprietary software owned by DeuOS, LLC. All contributions must respect the commercial license.
