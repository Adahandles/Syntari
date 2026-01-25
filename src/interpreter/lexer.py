"""
Syntari Lexer - Tokenizes Syntari source code according to v0.3 grammar.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for Syntari v0.3"""

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
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    CLASS = auto()
    NEW = auto()
    THIS = auto()
    SUPER = auto()
    EXTENDS = auto()
    STATIC = auto()

    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()

    # Operators
    PLUS = auto()  # +
    MINUS = auto()  # -
    STAR = auto()  # *
    SLASH = auto()  # /
    PERCENT = auto()  # %
    EQ_EQ = auto()  # ==
    NOT_EQ = auto()  # !=
    LT = auto()  # <
    LT_EQ = auto()  # <=
    GT = auto()  # >
    GT_EQ = auto()  # >=
    AND_AND = auto()  # &&
    OR_OR = auto()  # ||
    BANG = auto()  # !
    EQ = auto()  # =

    # Delimiters
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    COMMA = auto()  # ,
    SEMICOLON = auto()  # ;
    COLON = auto()  # :
    ARROW = auto()  # ->
    DOT = auto()  # .

    # Special
    IDENTIFIER = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a single token in Syntari source code"""

    type: TokenType
    value: any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class LexerError(Exception):
    """Raised when lexer encounters an error"""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")


class Lexer:
    """Tokenizes Syntari source code"""

    # Keywords mapping
    KEYWORDS = {
        "use": TokenType.USE,
        "type": TokenType.TYPE,
        "trait": TokenType.TRAIT,
        "impl": TokenType.IMPL,
        "fn": TokenType.FN,
        "let": TokenType.LET,
        "const": TokenType.CONST,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "match": TokenType.MATCH,
        "return": TokenType.RETURN,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "try": TokenType.TRY,
        "catch": TokenType.CATCH,
        "finally": TokenType.FINALLY,
        "throw": TokenType.THROW,
        "class": TokenType.CLASS,
        "new": TokenType.NEW,
        "this": TokenType.THIS,
        "super": TokenType.SUPER,
        "extends": TokenType.EXTENDS,
        "static": TokenType.STATIC,
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def current_char(self) -> Optional[str]:
        """Get current character without advancing"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at a character"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> Optional[str]:
        """Consume and return current character"""
        if self.pos >= len(self.source):
            return None

        char = self.source[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_char() and self.current_char() in " \t\r\n":
            self.advance()

    def skip_single_line_comment(self):
        """Skip single-line comment starting with //"""
        # Skip //
        self.advance()
        self.advance()

        # Skip until newline or EOF
        while self.current_char() and self.current_char() != "\n":
            self.advance()

    def skip_multi_line_comment(self):
        """Skip multi-line comment /* ... */"""
        start_line = self.line
        start_column = self.column

        # Skip /*
        self.advance()
        self.advance()

        # Skip until */ or EOF
        while self.current_char():
            if self.current_char() == "*" and self.peek_char() == "/":
                self.advance()  # *
                self.advance()  # /
                return
            self.advance()

        raise LexerError("Unterminated multi-line comment", start_line, start_column)

    def read_string(self) -> str:
        """Read string literal"""
        start_line = self.line
        start_column = self.column

        # Skip opening "
        self.advance()

        value = []
        while self.current_char() and self.current_char() != '"':
            char = self.current_char()

            # Handle escape sequences
            if char == "\\":
                self.advance()
                next_char = self.current_char()
                if next_char == "n":
                    value.append("\n")
                elif next_char == "t":
                    value.append("\t")
                elif next_char == "r":
                    value.append("\r")
                elif next_char == "\\":
                    value.append("\\")
                elif next_char == '"':
                    value.append('"')
                else:
                    value.append(next_char if next_char else "")
                self.advance()
            else:
                value.append(char)
                self.advance()

        if not self.current_char():
            raise LexerError("Unterminated string literal", start_line, start_column)

        # Skip closing "
        self.advance()

        return "".join(value)

    def read_number(self) -> Token:
        """Read integer or float literal"""
        start_line = self.line
        start_column = self.column

        value = []
        has_dot = False

        while self.current_char() and (self.current_char().isdigit() or self.current_char() == "."):
            if self.current_char() == ".":
                # Check if this is a decimal point or method call
                if has_dot or (self.peek_char() and not self.peek_char().isdigit()):
                    break
                has_dot = True
            value.append(self.current_char())
            self.advance()

        num_str = "".join(value)

        if has_dot:
            return Token(TokenType.FLOAT, float(num_str), start_line, start_column)
        else:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_column)

    def read_identifier(self) -> Token:
        """Read identifier or keyword"""
        start_line = self.line
        start_column = self.column

        value = []
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == "_"):
            value.append(self.current_char())
            self.advance()

        identifier = "".join(value)

        # Check if it's a keyword
        token_type = self.KEYWORDS.get(identifier, TokenType.IDENTIFIER)

        # For boolean keywords, return boolean value
        if token_type == TokenType.TRUE:
            return Token(token_type, True, start_line, start_column)
        elif token_type == TokenType.FALSE:
            return Token(token_type, False, start_line, start_column)
        else:
            return Token(token_type, identifier, start_line, start_column)

    def scan_token(self) -> Optional[Token]:
        """Scan and return next token"""
        self.skip_whitespace()

        if not self.current_char():
            return None

        char = self.current_char()
        line = self.line
        column = self.column

        # Comments
        if char == "/" and self.peek_char() == "/":
            self.skip_single_line_comment()
            return self.scan_token()  # Continue to next token

        if char == "/" and self.peek_char() == "*":
            self.skip_multi_line_comment()
            return self.scan_token()  # Continue to next token

        # String literals
        if char == '"':
            value = self.read_string()
            return Token(TokenType.STRING, value, line, column)

        # Numbers
        if char.isdigit():
            return self.read_number()

        # Identifiers and keywords
        if char.isalpha() or char == "_":
            return self.read_identifier()

        # Two-character operators
        if char == "=" and self.peek_char() == "=":
            self.advance()
            self.advance()
            return Token(TokenType.EQ_EQ, "==", line, column)

        if char == "!" and self.peek_char() == "=":
            self.advance()
            self.advance()
            return Token(TokenType.NOT_EQ, "!=", line, column)

        if char == "<" and self.peek_char() == "=":
            self.advance()
            self.advance()
            return Token(TokenType.LT_EQ, "<=", line, column)

        if char == ">" and self.peek_char() == "=":
            self.advance()
            self.advance()
            return Token(TokenType.GT_EQ, ">=", line, column)

        if char == "&" and self.peek_char() == "&":
            self.advance()
            self.advance()
            return Token(TokenType.AND_AND, "&&", line, column)

        if char == "|" and self.peek_char() == "|":
            self.advance()
            self.advance()
            return Token(TokenType.OR_OR, "||", line, column)

        if char == "-" and self.peek_char() == ">":
            self.advance()
            self.advance()
            return Token(TokenType.ARROW, "->", line, column)

        # Single-character operators and delimiters
        single_char_tokens = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "!": TokenType.BANG,
            "=": TokenType.EQ,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.COMMA,
            ";": TokenType.SEMICOLON,
            ":": TokenType.COLON,
            ".": TokenType.DOT,
        }

        if char in single_char_tokens:
            token_type = single_char_tokens[char]
            self.advance()
            return Token(token_type, char, line, column)

        # Unknown character
        raise LexerError(f"Unexpected character: {char!r}", line, column)

    def tokenize(self) -> List[Token]:
        """Tokenize entire source code"""
        self.tokens = []

        while self.current_char():
            token = self.scan_token()
            if token:
                self.tokens.append(token)

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))

        return self.tokens


def tokenize(source: str) -> List[Token]:
    """Convenience function to tokenize source code"""
    lexer = Lexer(source)
    return lexer.tokenize()
