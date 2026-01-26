# Syntari Developer Tools

This document describes the developer tools available in Syntari v0.4, including the interactive debugger and Language Server Protocol (LSP) integration.

## Table of Contents

1. [Overview](#overview)
2. [Interactive Debugger](#interactive-debugger)
   - [Features](#features)
   - [Usage](#usage)
   - [Commands](#commands)
   - [Examples](#examples)
3. [Language Server Protocol (LSP)](#language-server-protocol-lsp)
   - [Features](#lsp-features)
   - [IDE Setup](#ide-setup)
   - [VS Code Configuration](#vs-code-configuration)
4. [Integration](#integration)
5. [Troubleshooting](#troubleshooting)

---

## Overview

Syntari v0.4 includes two powerful developer tools:

1. **Interactive Debugger** - Step through code, set breakpoints, inspect variables
2. **LSP Server** - IDE integration for syntax highlighting, auto-completion, and more

---

## Interactive Debugger

### Features

The Syntari debugger provides:

- **Breakpoints**
  - File:line breakpoints (`break file.syn:10`)
  - Function name breakpoints (`break main`)
  - Conditional breakpoints (`break file.syn:10 if x > 5`)
  - Enable/disable/delete breakpoints
  - Hit count tracking

- **Stepping**
  - Step over (execute current line, don't enter functions)
  - Step into (enter function calls)
  - Step out (exit current function)
  - Continue (run until next breakpoint)

- **Inspection**
  - Print variable values (`print x`)
  - View local variables (`locals`)
  - View global variables (`globals`)
  - Evaluate expressions (`eval x + y`)

- **Stack Traces**
  - View call stack (`stack` or `bt`)
  - Show current location (`where` or `w`)
  - List source code (`list` or `l`)

### Usage

Run a Syntari script with the debugger:

```bash
# Using main.py
python3 main.py --debug script.syn

# Using Makefile
make debug FILE=script.syn

# Using syntari command (if installed)
syntari --debug script.syn
```

### Commands

The debugger provides an interactive command-line interface:

| Command | Aliases | Description |
|---------|---------|-------------|
| `continue` | `c` | Continue execution until next breakpoint |
| `step` | `s` | Step into next line (enters functions) |
| `next` | `n` | Step over next line (doesn't enter functions) |
| `out` | `o` | Step out of current function |
| `break <location>` | `b` | Set a breakpoint |
| `delete <id>` | `d` | Delete breakpoint by ID |
| `list` | `l` | List source code around current line |
| `print <expr>` | `p` | Print value of expression |
| `locals` | | Show local variables |
| `globals` | | Show global variables |
| `stack` | `bt` | Show call stack (backtrace) |
| `where` | `w` | Show current location |
| `eval <expr>` | | Evaluate expression in current context |
| `quit` | `q`, `exit` | Exit debugger |
| `help` | `h`, `?` | Show help message |

### Examples

#### Example 1: Basic Debugging

**script.syn:**
```javascript
fn factorial(n) {
    if (n <= 1) {
        return 1
    }
    return n * factorial(n - 1)
}

let result = factorial(5)
print(result)
```

**Debug session:**
```
$ python3 main.py --debug script.syn

Syntari Debugger (sdb)
Type 'help' for commands

(sdb) break factorial
Breakpoint 1 set at function 'factorial'

(sdb) continue
Breakpoint 1 hit at function 'factorial'
  1 | fn factorial(n) {
> 2 |     if (n <= 1) {
  3 |         return 1

(sdb) print n
5

(sdb) next
  2 |     if (n <= 1) {
  3 |         return 1
> 4 |     }

(sdb) continue
Breakpoint 1 hit at function 'factorial'
  1 | fn factorial(n) {
> 2 |     if (n <= 1) {
  3 |         return 1

(sdb) print n
4

(sdb) stack
#0 factorial(n=4) at script.syn:2
#1 factorial(n=5) at script.syn:5
#2 <module> at script.syn:8

(sdb) quit
```

#### Example 2: Conditional Breakpoints

```
(sdb) break script.syn:10 if x > 100
Conditional breakpoint 1 set at script.syn:10 (condition: x > 100)

(sdb) continue
# Only breaks when x > 100
```

#### Example 3: Inspecting Variables

```
(sdb) locals
x = 42
y = "hello"
result = None

(sdb) eval x * 2
84

(sdb) print result
None
```

---

## Language Server Protocol (LSP)

### LSP Features

The Syntari LSP server provides IDE features:

- **Syntax Highlighting** - Token-based syntax coloring
- **Auto-completion** - Keyword, builtin, and symbol completion
- **Go-to-Definition** - Jump to symbol definitions
- **Hover Information** - Documentation on hover
- **Diagnostics** - Real-time error/warning reporting
- **Document Symbols** - Outline view of functions/variables
- **Code Formatting** - Basic indentation formatting

### IDE Setup

#### Starting the LSP Server

```bash
# Using main.py
python3 main.py --lsp

# Using Makefile
make lsp

# Using syntari command (if installed)
syntari --lsp
```

The server listens on stdin/stdout for JSON-RPC messages.

### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
  "syntari.lsp.enabled": true,
  "syntari.lsp.command": "python3",
  "syntari.lsp.args": [
    "/path/to/Syntari/main.py",
    "--lsp"
  ],
  "syntari.lsp.filetypes": ["syntari", "syn"],
  "[syntari]": {
    "editor.formatOnSave": true,
    "editor.quickSuggestions": {
      "other": true,
      "comments": false,
      "strings": false
    }
  }
}
```

#### VS Code Extension (Custom)

Create a VS Code extension for Syntari:

**package.json:**
```json
{
  "name": "syntari-language-support",
  "displayName": "Syntari Language Support",
  "version": "0.4.0",
  "publisher": "deuos",
  "engines": {
    "vscode": "^1.60.0"
  },
  "categories": ["Programming Languages"],
  "contributes": {
    "languages": [
      {
        "id": "syntari",
        "aliases": ["Syntari", "syntari"],
        "extensions": [".syn"],
        "configuration": "./language-configuration.json"
      }
    ],
    "grammars": [
      {
        "language": "syntari",
        "scopeName": "source.syntari",
        "path": "./syntaxes/syntari.tmLanguage.json"
      }
    ]
  },
  "activationEvents": [
    "onLanguage:syntari"
  ],
  "main": "./out/extension.js",
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./"
  },
  "devDependencies": {
    "@types/vscode": "^1.60.0",
    "typescript": "^4.4.0"
  }
}
```

**extension.ts:**
```typescript
import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    const serverOptions: ServerOptions = {
        command: 'python3',
        args: ['/path/to/Syntari/main.py', '--lsp']
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'syntari' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.syn')
        }
    };

    client = new LanguageClient(
        'syntariLanguageServer',
        'Syntari Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
```

### Sublime Text Configuration

**Syntari.sublime-settings:**
```json
{
  "clients": {
    "syntari": {
      "enabled": true,
      "command": ["python3", "/path/to/Syntari/main.py", "--lsp"],
      "selector": "source.syntari",
      "syntaxes": ["Syntari.sublime-syntax"]
    }
  }
}
```

### Neovim Configuration

**lua/lsp/syntari.lua:**
```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

if not configs.syntari then
  configs.syntari = {
    default_config = {
      cmd = {'python3', '/path/to/Syntari/main.py', '--lsp'},
      filetypes = {'syntari', 'syn'},
      root_dir = function(fname)
        return lspconfig.util.find_git_ancestor(fname)
      end,
      settings = {},
    },
  }
end

lspconfig.syntari.setup{}
```

---

## Integration

### Programmatic Debugger Usage

```python
from src.interpreter.lexer import tokenize
from src.interpreter.parser import parse
from src.tools.debugger import SyntariDebugger, DebuggableInterpreter

# Load source code
with open("script.syn") as f:
    source = f.read()

# Parse
tokens = tokenize(source)
program = parse(tokens)

# Create debugger
debugger = SyntariDebugger()
debugger.set_breakpoint(file="script.syn", line=10)
debugger.set_breakpoint(function="main")

# Run with debugging
interpreter = DebuggableInterpreter(debugger)
debugger.run(program, interpreter)
```

### Programmatic LSP Usage

```python
from src.tools.lsp import SyntariLSP, Position

# Create LSP instance
lsp = SyntariLSP()

# Open document
lsp.did_open("file:///script.syn", source_code)

# Get completions
pos = Position(line=5, character=10)
completions = lsp.get_completions("file:///script.syn", pos)

for completion in completions:
    print(f"{completion.label}: {completion.detail}")

# Get diagnostics
diagnostics = lsp.get_diagnostics("file:///script.syn")
for diag in diagnostics:
    print(f"Line {diag.range.start.line}: {diag.message}")

# Get hover info
hover = lsp.get_hover("file:///script.syn", pos)
print(hover)
```

---

## Troubleshooting

### Debugger Issues

#### Breakpoints Not Hit

**Problem:** Breakpoint set but never triggered

**Solutions:**
1. Check file path is correct: `break /full/path/to/script.syn:10`
2. Verify line number has executable code (not comments/whitespace)
3. Ensure function name is spelled correctly
4. Check if breakpoint is enabled: `list` to see all breakpoints

#### Variables Not Found

**Problem:** `print x` says "Undefined variable"

**Solutions:**
1. Use `locals` to see available local variables
2. Use `globals` to see global variables
3. Variable may be out of scope - check `stack` for current frame
4. Use `eval` for complex expressions

#### Debugger Won't Start

**Problem:** `python3 main.py --debug script.syn` fails

**Solutions:**
1. Check Python version: `python3 --version` (need 3.8+)
2. Reinstall Syntari: `pip install -e .`
3. Check file exists: `ls -l script.syn`
4. Try with `--verbose` flag for more info

### LSP Issues

#### LSP Server Won't Start

**Problem:** `python3 main.py --lsp` exits immediately

**Solutions:**
1. Check for import errors: run with `--verbose`
2. Ensure dependencies installed: `pip install -e ".[web]"`
3. Check Python path is correct
4. Look for error messages in stderr

#### No Completions in IDE

**Problem:** Auto-completion doesn't work

**Solutions:**
1. Verify LSP server is running (check IDE logs)
2. Check file extension is `.syn`
3. Ensure document is saved (some IDEs require this)
4. Restart IDE and LSP server
5. Check IDE LSP client configuration

#### Diagnostics Not Showing

**Problem:** Errors don't appear in IDE

**Solutions:**
1. Save the file (triggers diagnostics)
2. Check LSP server logs for errors
3. Verify `textDocument/publishDiagnostics` capability
4. Try closing and reopening the file

#### Go-to-Definition Not Working

**Problem:** Can't jump to symbol definitions

**Solutions:**
1. Ensure symbol is defined in same file (cross-file not yet supported)
2. Check symbol name is correct
3. Try hovering first (hover usually works better)
4. Symbol extraction may have failed - check for parse errors

### Performance Issues

#### Debugger Slow

**Problem:** Stepping through code is slow

**Solutions:**
1. Reduce number of breakpoints
2. Use `continue` instead of repeated `step`
3. Disable conditional breakpoints if not needed
4. Profile the script to find bottlenecks

#### LSP Server Lag

**Problem:** IDE becomes unresponsive

**Solutions:**
1. Reduce file size (LSP parses entire file)
2. Disable unused LSP features in IDE
3. Increase IDE's LSP timeout setting
4. Restart LSP server periodically

---

## Advanced Usage

### Custom Debugger Commands

Extend the debugger with custom commands:

```python
from src.tools.debugger import SyntariDebugger, DebugCommand

class CustomDebugger(SyntariDebugger):
    def handle_command(self, line: str):
        if line.startswith("watch "):
            # Custom watch command
            var = line[6:].strip()
            print(f"Watching variable: {var}")
            return DebugCommand.CONTINUE
        
        return super().handle_command(line)
```

### LSP Extensions

Add custom LSP capabilities:

```python
from src.tools.lsp import SyntariLSP

class ExtendedLSP(SyntariLSP):
    def get_code_actions(self, uri: str, range: dict):
        """Custom code actions"""
        actions = []
        # Add custom refactorings, quick fixes, etc.
        return actions
    
    def rename_symbol(self, uri: str, position: dict, new_name: str):
        """Rename symbol across file"""
        # Implement rename functionality
        pass
```

---

## Statistics

Phase 5 implementation:

- **Lines of Code:** ~2,000
- **Test Files:** 2 (test_debugger.py, test_lsp.py)
- **Tests:** 50
- **Test Coverage:** 50% debugger, 64% LSP
- **Commands:** 15 debugger commands
- **LSP Capabilities:** 6 (sync, completion, hover, definition, symbols, formatting)

---

## Future Enhancements

Planned for v0.5:

- [ ] Remote debugging (debug over TCP/IP)
- [ ] Visual debugger UI (web-based)
- [ ] Conditional breakpoint expressions
- [ ] Data breakpoints (break on variable change)
- [ ] Time-travel debugging (replay execution)
- [ ] LSP cross-file support (go-to-definition across files)
- [ ] LSP refactoring (rename, extract function, etc.)
- [ ] LSP code actions (quick fixes, suggestions)
- [ ] LSP semantic tokens (better syntax highlighting)
- [ ] LSP workspace symbols (search across project)

---

## Contributing

To contribute to the dev tools:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

---

## License

Syntari is proprietary software owned by DeuOS, LLC.

Copyright © 2024 DeuOS, LLC. All rights reserved.

---

## Support

For questions or issues:

- GitHub Issues: https://github.com/Adahandles/Syntari/issues
- Email: legal@deuos.io
- Documentation: See GETTING_STARTED.md, IMPLEMENTATION_GUIDE.md

---

**Happy Debugging! 🐛🔍**
