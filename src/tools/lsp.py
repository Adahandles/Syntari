"""
Syntari Language Server Protocol (LSP) Implementation

Provides IDE features:
- Syntax highlighting
- Auto-completion
- Go to definition
- Hover information
- Diagnostics (errors, warnings)
- Document symbols
- Formatting
"""

import json
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from src.interpreter.lexer import tokenize, LexerError
from src.interpreter.parser import Parser, ParseError
from src.interpreter.nodes import Node, Program, FuncDecl, VarDecl


@dataclass
class Position:
    """LSP Position (line, character)"""

    line: int
    character: int

    def to_dict(self):
        return {"line": self.line, "character": self.character}


@dataclass
class Range:
    """LSP Range (start, end)"""

    start: Position
    end: Position

    def to_dict(self):
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class Location:
    """LSP Location (uri, range)"""

    uri: str
    range: Range

    def to_dict(self):
        return {"uri": self.uri, "range": self.range.to_dict()}


@dataclass
class Diagnostic:
    """LSP Diagnostic (error, warning, info)"""

    range: Range
    severity: int  # 1=Error, 2=Warning, 3=Info, 4=Hint
    message: str
    source: str = "syntari"

    def to_dict(self):
        return {
            "range": self.range.to_dict(),
            "severity": self.severity,
            "message": self.message,
            "source": self.source,
        }


@dataclass
class CompletionItem:
    """LSP Completion Item"""

    label: str
    kind: int  # 1-25 (function, variable, etc.)
    detail: Optional[str] = None
    documentation: Optional[str] = None
    insert_text: Optional[str] = None

    def to_dict(self):
        result = {"label": self.label, "kind": self.kind}
        if self.detail:
            result["detail"] = self.detail
        if self.documentation:
            result["documentation"] = self.documentation
        if self.insert_text:
            result["insertText"] = self.insert_text
        return result


@dataclass
class SymbolInformation:
    """LSP Symbol Information"""

    name: str
    kind: int  # 1-26 (File, Module, Namespace, Package, Class, Method, etc.)
    location: Location
    container_name: Optional[str] = None

    def to_dict(self):
        result = {
            "name": self.name,
            "kind": self.kind,
            "location": self.location.to_dict(),
        }
        if self.container_name:
            result["containerName"] = self.container_name
        return result


class SyntariLSP:
    """
    Language Server Protocol implementation for Syntari

    Provides IDE features through LSP protocol
    """

    # LSP Symbol Kinds
    SYMBOL_FILE = 1
    SYMBOL_MODULE = 2
    SYMBOL_NAMESPACE = 3
    SYMBOL_PACKAGE = 4
    SYMBOL_CLASS = 5
    SYMBOL_METHOD = 6
    SYMBOL_PROPERTY = 7
    SYMBOL_FIELD = 8
    SYMBOL_CONSTRUCTOR = 9
    SYMBOL_ENUM = 10
    SYMBOL_INTERFACE = 11
    SYMBOL_FUNCTION = 12
    SYMBOL_VARIABLE = 13
    SYMBOL_CONSTANT = 14
    SYMBOL_STRING = 15
    SYMBOL_NUMBER = 16
    SYMBOL_BOOLEAN = 17
    SYMBOL_ARRAY = 18

    # Completion Item Kinds
    COMPLETION_TEXT = 1
    COMPLETION_METHOD = 2
    COMPLETION_FUNCTION = 3
    COMPLETION_CONSTRUCTOR = 4
    COMPLETION_FIELD = 5
    COMPLETION_VARIABLE = 6
    COMPLETION_CLASS = 7
    COMPLETION_INTERFACE = 8
    COMPLETION_MODULE = 9
    COMPLETION_PROPERTY = 10
    COMPLETION_UNIT = 11
    COMPLETION_VALUE = 12
    COMPLETION_ENUM = 13
    COMPLETION_KEYWORD = 14
    COMPLETION_SNIPPET = 15

    # Diagnostic Severities
    SEVERITY_ERROR = 1
    SEVERITY_WARNING = 2
    SEVERITY_INFO = 3
    SEVERITY_HINT = 4

    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.diagnostics: Dict[str, List[Diagnostic]] = {}
        self.symbols: Dict[str, List[SymbolInformation]] = {}
        self.keywords = [
            "use",
            "type",
            "trait",
            "impl",
            "fn",
            "let",
            "const",
            "if",
            "else",
            "while",
            "match",
            "return",
            "true",
            "false",
        ]
        self.builtins = [
            "print",
            "trace",
            "exit",
            "env",
            "time",
            "ai.query",
            "ai.eval",
            "ai.suggest",
        ]

    def did_open(self, uri: str, text: str):
        """Handle document open"""
        self.documents[uri] = text
        self._analyze_document(uri)

    def did_change(self, uri: str, text: str):
        """Handle document change"""
        self.documents[uri] = text
        self._analyze_document(uri)

    def did_close(self, uri: str):
        """Handle document close"""
        if uri in self.documents:
            del self.documents[uri]
        if uri in self.diagnostics:
            del self.diagnostics[uri]
        if uri in self.symbols:
            del self.symbols[uri]

    def _analyze_document(self, uri: str):
        """Analyze document for diagnostics and symbols"""
        text = self.documents.get(uri, "")

        # Clear previous diagnostics and symbols
        self.diagnostics[uri] = []
        self.symbols[uri] = []

        try:
            # Tokenize
            tokens = tokenize(text)

            # Parse
            parser = Parser(tokens)
            tree = parser.parse()

            # Extract symbols
            self._extract_symbols(uri, tree)

        except LexerError as e:
            # Add lexer error as diagnostic
            diagnostic = Diagnostic(
                range=Range(
                    start=Position(line=getattr(e, "line", 0), character=0),
                    end=Position(line=getattr(e, "line", 0), character=100),
                ),
                severity=self.SEVERITY_ERROR,
                message=f"Lexer error: {str(e)}",
            )
            self.diagnostics[uri].append(diagnostic)

        except ParseError as e:
            # Add parse error as diagnostic
            diagnostic = Diagnostic(
                range=Range(
                    start=Position(line=getattr(e, "line", 0), character=0),
                    end=Position(line=getattr(e, "line", 0), character=100),
                ),
                severity=self.SEVERITY_ERROR,
                message=f"Parse error: {str(e)}",
            )
            self.diagnostics[uri].append(diagnostic)

        except Exception as e:
            # Add generic error
            diagnostic = Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=100),
                ),
                severity=self.SEVERITY_ERROR,
                message=f"Analysis error: {str(e)}",
            )
            self.diagnostics[uri].append(diagnostic)

    def _extract_symbols(self, uri: str, tree: Program):
        """Extract symbols from AST"""
        for stmt in tree.statements:
            self._extract_symbol_from_node(uri, stmt)

    def _extract_symbol_from_node(self, uri: str, node: Node, container: Optional[str] = None):
        """Extract symbol information from node"""
        if isinstance(node, FuncDecl):
            # Function symbol
            symbol = SymbolInformation(
                name=node.name,
                kind=self.SYMBOL_FUNCTION,
                location=Location(
                    uri=uri,
                    range=Range(
                        start=Position(line=getattr(node, "line", 0), character=0),
                        end=Position(line=getattr(node, "line", 0), character=100),
                    ),
                ),
                container_name=container,
            )
            self.symbols[uri].append(symbol)

        elif isinstance(node, VarDecl):
            # Variable symbol
            kind = self.SYMBOL_CONSTANT if node.is_const else self.SYMBOL_VARIABLE
            symbol = SymbolInformation(
                name=node.name,
                kind=kind,
                location=Location(
                    uri=uri,
                    range=Range(
                        start=Position(line=getattr(node, "line", 0), character=0),
                        end=Position(line=getattr(node, "line", 0), character=100),
                    ),
                ),
                container_name=container,
            )
            self.symbols[uri].append(symbol)

    def get_diagnostics(self, uri: str) -> List[Diagnostic]:
        """Get diagnostics for document"""
        return self.diagnostics.get(uri, [])

    def get_completions(self, uri: str, position: Position) -> List[CompletionItem]:
        """Get completion items at position"""
        completions = []

        # Add keywords
        for keyword in self.keywords:
            completions.append(
                CompletionItem(
                    label=keyword,
                    kind=self.COMPLETION_KEYWORD,
                    detail="keyword",
                )
            )

        # Add builtins
        for builtin in self.builtins:
            completions.append(
                CompletionItem(
                    label=builtin,
                    kind=self.COMPLETION_FUNCTION,
                    detail="built-in function",
                )
            )

        # Add symbols from current document
        if uri in self.symbols:
            for symbol in self.symbols[uri]:
                kind = (
                    self.COMPLETION_FUNCTION
                    if symbol.kind == self.SYMBOL_FUNCTION
                    else self.COMPLETION_VARIABLE
                )
                completions.append(
                    CompletionItem(
                        label=symbol.name,
                        kind=kind,
                        detail=f"defined in {symbol.container_name or 'global scope'}",
                    )
                )

        return completions

    def get_hover(self, uri: str, position: Position) -> Optional[str]:
        """Get hover information at position"""
        # Get word at position
        text = self.documents.get(uri, "")
        lines = text.split("\n")

        if position.line >= len(lines):
            return None

        line = lines[position.line]
        if position.character >= len(line):
            return None

        # Extract word
        word = self._get_word_at_position(line, position.character)
        if not word:
            return None

        # Check if it's a keyword
        if word in self.keywords:
            return self._get_keyword_doc(word)

        # Check if it's a builtin
        if word in self.builtins:
            return self._get_builtin_doc(word)

        # Check if it's a symbol
        if uri in self.symbols:
            for symbol in self.symbols[uri]:
                if symbol.name == word:
                    kind_name = "function" if symbol.kind == self.SYMBOL_FUNCTION else "variable"
                    return f"{kind_name} {symbol.name}"

        return None

    def _get_word_at_position(self, line: str, character: int) -> Optional[str]:
        """Extract word at character position"""
        if character >= len(line):
            return None

        # Find word boundaries
        start = character
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] in "_."):
            start -= 1

        end = character
        while end < len(line) and (line[end].isalnum() or line[end] in "_."):
            end += 1

        word = line[start:end]
        return word if word else None

    def _get_keyword_doc(self, keyword: str) -> str:
        """Get documentation for keyword"""
        docs = {
            "use": "Import a module",
            "type": "Define a new type",
            "trait": "Define a trait",
            "impl": "Implement a trait",
            "fn": "Define a function",
            "let": "Declare a variable",
            "const": "Declare a constant",
            "if": "Conditional statement",
            "else": "Alternative branch",
            "while": "Loop statement",
            "match": "Pattern matching",
            "return": "Return from function",
            "true": "Boolean true",
            "false": "Boolean false",
        }
        return docs.get(keyword, keyword)

    def _get_builtin_doc(self, builtin: str) -> str:
        """Get documentation for builtin"""
        docs = {
            "print": "Print values to stdout",
            "trace": "Print stack trace",
            "exit": "Exit with status code",
            "env": "Get environment variable",
            "time": "Get current timestamp",
            "ai.query": "Query AI with prompt",
            "ai.eval": "Evaluate code with AI",
            "ai.suggest": "Get AI suggestions",
        }
        return docs.get(builtin, builtin)

    def goto_definition(self, uri: str, position: Position) -> Optional[Location]:
        """Find definition of symbol at position"""
        # Get word at position
        text = self.documents.get(uri, "")
        lines = text.split("\n")

        if position.line >= len(lines):
            return None

        line = lines[position.line]
        word = self._get_word_at_position(line, position.character)

        if not word:
            return None

        # Find symbol definition
        if uri in self.symbols:
            for symbol in self.symbols[uri]:
                if symbol.name == word:
                    return symbol.location

        return None

    def get_document_symbols(self, uri: str) -> List[SymbolInformation]:
        """Get all symbols in document"""
        return self.symbols.get(uri, [])

    def format_document(self, uri: str) -> Optional[str]:
        """Format document (basic formatting)"""
        text = self.documents.get(uri, "")

        # Basic formatting
        lines = text.split("\n")
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Decrease indent for closing braces
            if stripped.startswith("}"):
                indent_level = max(0, indent_level - 1)

            # Add line with proper indentation
            if stripped:
                formatted_lines.append("    " * indent_level + stripped)
            else:
                formatted_lines.append("")

            # Increase indent for opening braces
            if stripped.endswith("{"):
                indent_level += 1

        return "\n".join(formatted_lines)


class LSPServer:
    """
    JSON-RPC based LSP server

    Communicates via stdin/stdout using JSON-RPC protocol
    """

    def __init__(self):
        self.lsp = SyntariLSP()
        self.running = False

    def start(self):
        """Start LSP server"""
        self.running = True

        while self.running:
            try:
                # Read Content-Length header
                header = sys.stdin.readline().strip()
                if not header:
                    break

                if not header.startswith("Content-Length:"):
                    continue

                content_length = int(header.split(":")[1].strip())

                # Read blank line
                sys.stdin.readline()

                # Read content
                content = sys.stdin.read(content_length)
                message = json.loads(content)

                # Process message
                response = self.handle_message(message)

                if response:
                    self.send_response(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.send_error(-1, f"Server error: {e}")

    def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle JSON-RPC message"""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")

        if method == "initialize":
            return {
                "id": msg_id,
                "result": {
                    "capabilities": {
                        "textDocumentSync": 1,  # Full sync
                        "completionProvider": {"triggerCharacters": ["."]},
                        "hoverProvider": True,
                        "definitionProvider": True,
                        "documentSymbolProvider": True,
                        "documentFormattingProvider": True,
                    }
                },
            }

        elif method == "textDocument/didOpen":
            uri = params["textDocument"]["uri"]
            text = params["textDocument"]["text"]
            self.lsp.did_open(uri, text)
            self.publish_diagnostics(uri)
            return None

        elif method == "textDocument/didChange":
            uri = params["textDocument"]["uri"]
            text = params["contentChanges"][0]["text"]
            self.lsp.did_change(uri, text)
            self.publish_diagnostics(uri)
            return None

        elif method == "textDocument/completion":
            uri = params["textDocument"]["uri"]
            pos = params["position"]
            position = Position(line=pos["line"], character=pos["character"])
            completions = self.lsp.get_completions(uri, position)
            return {"id": msg_id, "result": [c.to_dict() for c in completions]}

        elif method == "textDocument/hover":
            uri = params["textDocument"]["uri"]
            pos = params["position"]
            position = Position(line=pos["line"], character=pos["character"])
            hover = self.lsp.get_hover(uri, position)
            return {"id": msg_id, "result": {"contents": hover} if hover else None}

        elif method == "textDocument/definition":
            uri = params["textDocument"]["uri"]
            pos = params["position"]
            position = Position(line=pos["line"], character=pos["character"])
            location = self.lsp.goto_definition(uri, position)
            return {"id": msg_id, "result": location.to_dict() if location else None}

        elif method == "textDocument/documentSymbol":
            uri = params["textDocument"]["uri"]
            symbols = self.lsp.get_document_symbols(uri)
            return {"id": msg_id, "result": [s.to_dict() for s in symbols]}

        elif method == "textDocument/formatting":
            uri = params["textDocument"]["uri"]
            formatted = self.lsp.format_document(uri)
            if formatted:
                # Return text edit
                return {
                    "id": msg_id,
                    "result": [
                        {
                            "range": {
                                "start": {"line": 0, "character": 0},
                                "end": {"line": 999999, "character": 0},
                            },
                            "newText": formatted,
                        }
                    ],
                }
            return {"id": msg_id, "result": None}

        elif method == "shutdown":
            self.running = False
            return {"id": msg_id, "result": None}

        return None

    def publish_diagnostics(self, uri: str):
        """Publish diagnostics notification"""
        diagnostics = self.lsp.get_diagnostics(uri)
        notification = {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {"uri": uri, "diagnostics": [d.to_dict() for d in diagnostics]},
        }
        self.send_response(notification)

    def send_response(self, response: Dict[str, Any]):
        """Send JSON-RPC response"""
        content = json.dumps(response)
        message = f"Content-Length: {len(content)}\r\n\r\n{content}"
        sys.stdout.write(message)
        sys.stdout.flush()

    def send_error(self, code: int, message: str):
        """Send error response"""
        response = {"jsonrpc": "2.0", "error": {"code": code, "message": message}}
        self.send_response(response)


if __name__ == "__main__":
    # Start LSP server
    server = LSPServer()
    server.start()
