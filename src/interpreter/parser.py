from dataclasses import dataclass
from typing import List
import re


@dataclass
class Token:
    """
    Represents a single token produced by the Parser.
    
    Note: This is a simplified Token class used by the Parser for basic tokenization.
    It differs from lexer.Token which includes line/column tracking for detailed
    error reporting. Use lexer.Token for full lexical analysis.

    Attributes:
        type: A string describing the token type (e.g. 'NUMBER', 'IDENT', 'SYMBOL').
        value: The original string value of the token.
        position: The zero-based character index in the source string.
    """
    type: str
    value: str
    position: int


class Parser:
    """
    A minimal, generic parser that tokenizes an input string.

    This implementation splits the input into:
      - NUMBER tokens: sequences of digits (optionally with a decimal point),
      - IDENT tokens: sequences of alphabetic/underscore characters and digits
        (starting with a letter or underscore),
      - SYMBOL tokens: any single non-whitespace character not matched above.
    """

    _number_pattern = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")
    _ident_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def parse(self, source: str) -> List[Token]:
        """
        Tokenize the given source string into a list of Token objects.

        Args:
            source: The input string to tokenize.

        Returns:
            A list of Token instances in the order they appear in the source.
        """
        tokens: List[Token] = []

        length = len(source)
        i = 0

        # Simple hand-written scanner that distinguishes numbers, identifiers,
        # string literals, and symbols/operators. This avoids treating an entire
        # non-whitespace run (e.g. "a==b") as a single token.
        while i < length:
            ch = source[i]

            # Skip whitespace
            if ch.isspace():
                i += 1
                continue

            start = i

            # Number literal: digits, optionally with a single decimal point.
            if ch.isdigit() or (ch == "." and i + 1 < length and source[i + 1].isdigit()):
                i += 1
                dot_seen = (ch == ".")
                while i < length:
                    c = source[i]
                    if c.isdigit():
                        i += 1
                        continue
                    if c == "." and not dot_seen:
                        dot_seen = True
                        i += 1
                        continue
                    break
                text = source[start:i]
                token_type = self._classify_token(text)
                tokens.append(Token(type=token_type, value=text, position=start))
                continue

            # Identifier: letter or underscore followed by letters, digits, or underscores.
            if ch.isalpha() or ch == "_":
                i += 1
                while i < length and (source[i].isalnum() or source[i] == "_"):
                    i += 1
                text = source[start:i]
                token_type = self._classify_token(text)
                tokens.append(Token(type=token_type, value=text, position=start))
                continue

            # String literal: text enclosed in single or double quotes, with simple escape handling.
            if ch == '"' or ch == "'":
                quote_char = ch
                i += 1
                escaped = False
                while i < length:
                    c = source[i]
                    if escaped:
                        escaped = False
                    elif c == "\\":
                        escaped = True
                    elif c == quote_char:
                        i += 1
                        break
                    i += 1
                text = source[start:i]
                token_type = self._classify_token(text)
                tokens.append(Token(type=token_type, value=text, position=start))
                continue

            # Symbols / operators. Recognize a few common two-character operators,
            # otherwise fall back to single-character symbols.
            two_char_ops = ("==", "!=", ">=", "<=")
            if i + 1 < length and source[i:i + 2] in two_char_ops:
                i += 2
            else:
                i += 1
            text = source[start:i]
            token_type = self._classify_token(text)
            tokens.append(Token(type=token_type, value=text, position=start))
        return tokens

    def _classify_token(self, text: str) -> str:
        """
        Determine the type of a token string.

        Args:
            text: The token string to classify.

        Returns:
            'NUMBER', 'IDENT', or 'SYMBOL'.
        """
        if self._number_pattern.match(text):
            return "NUMBER"
        if self._ident_pattern.match(text):
            return "IDENT"
        return "SYMBOL"
