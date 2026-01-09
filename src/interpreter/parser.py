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
        position = 0

        buffer = []
        buffer_start = 0

        def flush_buffer() -> None:
            nonlocal buffer, buffer_start
            if not buffer:
                return
            text = "".join(buffer)
            token_type = self._classify_token(text)
            tokens.append(Token(type=token_type, value=text, position=buffer_start))
            buffer.clear()

        for idx, char in enumerate(source):
            if char.isspace():
                flush_buffer()
                buffer_start = idx + 1
            else:
                if not buffer:
                    buffer_start = idx
                buffer.append(char)

        flush_buffer()
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
