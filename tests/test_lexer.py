"""
Tests for Syntari Lexer
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.interpreter.lexer import tokenize, Lexer, TokenType, Token, LexerError


class TestBasicTokens:
    """Test basic token recognition"""
    
    def test_keywords(self):
        """Test all keywords are recognized"""
        keywords = [
            'use', 'type', 'trait', 'impl', 'fn', 'let', 'const',
            'if', 'else', 'while', 'match', 'return', 'true', 'false'
        ]
        
        for keyword in keywords:
            tokens = tokenize(keyword)
            assert len(tokens) == 2  # keyword + EOF
            assert tokens[0].value == keyword or isinstance(tokens[0].value, bool)
            assert tokens[1].type == TokenType.EOF
    
    def test_identifiers(self):
        """Test identifier recognition"""
        identifiers = ['x', 'foo', 'bar123', '_private', 'camelCase', 'snake_case']
        
        for ident in identifiers:
            tokens = tokenize(ident)
            assert tokens[0].type == TokenType.IDENTIFIER
            assert tokens[0].value == ident
    
    def test_integers(self):
        """Test integer literal recognition"""
        test_cases = [
            ('0', 0),
            ('42', 42),
            ('123', 123),
            ('999999', 999999),
        ]
        
        for source, expected in test_cases:
            tokens = tokenize(source)
            assert tokens[0].type == TokenType.INTEGER
            assert tokens[0].value == expected
    
    def test_floats(self):
        """Test float literal recognition"""
        test_cases = [
            ('3.14', 3.14),
            ('0.5', 0.5),
            ('123.456', 123.456),
        ]
        
        for source, expected in test_cases:
            tokens = tokenize(source)
            assert tokens[0].type == TokenType.FLOAT
            assert tokens[0].value == expected
    
    def test_strings(self):
        """Test string literal recognition"""
        test_cases = [
            ('"hello"', 'hello'),
            ('"Hello, world!"', 'Hello, world!'),
            ('""', ''),
            ('"with spaces"', 'with spaces'),
        ]
        
        for source, expected in test_cases:
            tokens = tokenize(source)
            assert tokens[0].type == TokenType.STRING
            assert tokens[0].value == expected
    
    def test_string_escapes(self):
        """Test string escape sequences"""
        test_cases = [
            (r'"line1\nline2"', 'line1\nline2'),
            (r'"tab\there"', 'tab\there'),
            (r'"quote:\""', 'quote:"'),
            (r'"backslash:\\"', 'backslash:\\'),
        ]
        
        for source, expected in test_cases:
            tokens = tokenize(source)
            assert tokens[0].type == TokenType.STRING
            assert tokens[0].value == expected
    
    def test_booleans(self):
        """Test boolean literals"""
        tokens = tokenize('true false')
        assert tokens[0].type == TokenType.TRUE
        assert tokens[0].value is True
        assert tokens[1].type == TokenType.FALSE
        assert tokens[1].value is False


class TestOperators:
    """Test operator recognition"""
    
    def test_arithmetic_operators(self):
        """Test arithmetic operators"""
        source = '+ - * / %'
        tokens = tokenize(source)
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
            TokenType.SLASH, TokenType.PERCENT, TokenType.EOF
        ]
        
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type
    
    def test_comparison_operators(self):
        """Test comparison operators"""
        source = '< <= > >= == !='
        tokens = tokenize(source)
        
        expected_types = [
            TokenType.LT, TokenType.LT_EQ, TokenType.GT,
            TokenType.GT_EQ, TokenType.EQ_EQ, TokenType.NOT_EQ, TokenType.EOF
        ]
        
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type
    
    def test_logical_operators(self):
        """Test logical operators"""
        source = '&& || !'
        tokens = tokenize(source)
        
        assert tokens[0].type == TokenType.AND_AND
        assert tokens[1].type == TokenType.OR_OR
        assert tokens[2].type == TokenType.BANG
    
    def test_assignment(self):
        """Test assignment operator"""
        tokens = tokenize('=')
        assert tokens[0].type == TokenType.EQ


class TestDelimiters:
    """Test delimiter recognition"""
    
    def test_parentheses(self):
        """Test parentheses"""
        tokens = tokenize('()')
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN
    
    def test_braces(self):
        """Test braces"""
        tokens = tokenize('{}')
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.RBRACE
    
    def test_punctuation(self):
        """Test other punctuation"""
        source = ', ; : . ->'
        tokens = tokenize(source)
        
        expected_types = [
            TokenType.COMMA, TokenType.SEMICOLON, TokenType.COLON,
            TokenType.DOT, TokenType.ARROW, TokenType.EOF
        ]
        
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type


class TestComments:
    """Test comment handling"""
    
    def test_single_line_comment(self):
        """Test single-line comments are ignored"""
        source = '''
        let x = 5  // this is a comment
        let y = 10
        '''
        tokens = tokenize(source)
        
        # Should get: let, x, =, 5, let, y, =, 10, EOF
        assert len(tokens) == 9
        assert tokens[0].type == TokenType.LET
        assert tokens[1].value == 'x'
    
    def test_multi_line_comment(self):
        """Test multi-line comments are ignored"""
        source = '''
        let x = 5
        /* This is a
           multi-line comment */
        let y = 10
        '''
        tokens = tokenize(source)
        
        # Should get: let, x, =, 5, let, y, =, 10, EOF
        assert len(tokens) == 9
        assert tokens[0].type == TokenType.LET
    
    def test_comment_at_end_of_file(self):
        """Test comment at end of file"""
        source = 'let x = 5 // comment at end'
        tokens = tokenize(source)
        
        assert len(tokens) == 5  # let, x, =, 5, EOF
        assert tokens[-1].type == TokenType.EOF


class TestComplexExpressions:
    """Test tokenizing complex expressions"""
    
    def test_simple_print(self):
        """Test: print("hello")"""
        tokens = tokenize('print("hello")')
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'print'
        assert tokens[1].type == TokenType.LPAREN
        assert tokens[2].type == TokenType.STRING
        assert tokens[2].value == 'hello'
        assert tokens[3].type == TokenType.RPAREN
        assert tokens[4].type == TokenType.EOF
    
    def test_variable_declaration(self):
        """Test: let x = 42"""
        tokens = tokenize('let x = 42')
        
        assert tokens[0].type == TokenType.LET
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == 'x'
        assert tokens[2].type == TokenType.EQ
        assert tokens[3].type == TokenType.INTEGER
        assert tokens[3].value == 42
    
    def test_arithmetic_expression(self):
        """Test: 2 + 3 * 4"""
        tokens = tokenize('2 + 3 * 4')
        
        expected_types = [
            TokenType.INTEGER, TokenType.PLUS, TokenType.INTEGER,
            TokenType.STAR, TokenType.INTEGER, TokenType.EOF
        ]
        
        for i, expected_type in enumerate(expected_types):
            assert tokens[i].type == expected_type
    
    def test_function_declaration(self):
        """Test: fn add(a: int, b: int) -> int"""
        tokens = tokenize('fn add(a: int, b: int) -> int')
        
        assert tokens[0].type == TokenType.FN
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == 'add'
        assert tokens[2].type == TokenType.LPAREN
        # a
        assert tokens[3].type == TokenType.IDENTIFIER
        assert tokens[4].type == TokenType.COLON
        # int
        assert tokens[5].type == TokenType.IDENTIFIER
        assert tokens[6].type == TokenType.COMMA
        # More params...
    
    def test_if_statement(self):
        """Test: if (x > 5)"""
        tokens = tokenize('if (x > 5)')
        
        assert tokens[0].type == TokenType.IF
        assert tokens[1].type == TokenType.LPAREN
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[3].type == TokenType.GT
        assert tokens[4].type == TokenType.INTEGER
        assert tokens[5].type == TokenType.RPAREN
    
    def test_method_call(self):
        """Test: obj.method()"""
        tokens = tokenize('obj.method()')
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == 'obj'
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == 'method'
        assert tokens[3].type == TokenType.LPAREN
        assert tokens[4].type == TokenType.RPAREN


class TestLineAndColumn:
    """Test line and column tracking"""
    
    def test_single_line_positions(self):
        """Test column tracking on single line"""
        tokens = tokenize('let x = 5')
        
        assert tokens[0].line == 1
        assert tokens[0].column == 1  # 'let'
        assert tokens[1].column == 5  # 'x'
        assert tokens[2].column == 7  # '='
        assert tokens[3].column == 9  # '5'
    
    def test_multi_line_positions(self):
        """Test line and column tracking across lines"""
        source = '''let x = 5
let y = 10'''
        tokens = tokenize(source)
        
        # First line
        assert tokens[0].line == 1  # 'let'
        
        # Second line
        assert tokens[4].line == 2  # 'let'
        assert tokens[4].column == 1


class TestErrors:
    """Test error handling"""
    
    def test_unterminated_string(self):
        """Test error on unterminated string"""
        with pytest.raises(LexerError) as exc_info:
            tokenize('"unterminated')
        
        assert 'Unterminated string' in str(exc_info.value)
    
    def test_unterminated_multi_line_comment(self):
        """Test error on unterminated multi-line comment"""
        with pytest.raises(LexerError) as exc_info:
            tokenize('/* unterminated comment')
        
        assert 'Unterminated multi-line comment' in str(exc_info.value)
    
    def test_unexpected_character(self):
        """Test error on unexpected character"""
        with pytest.raises(LexerError) as exc_info:
            tokenize('let x = @')
        
        assert 'Unexpected character' in str(exc_info.value)


class TestWhitespace:
    """Test whitespace handling"""
    
    def test_spaces(self):
        """Test spaces are handled correctly"""
        tokens = tokenize('let    x    =    5')
        assert len(tokens) == 5  # let, x, =, 5, EOF
    
    def test_tabs_and_newlines(self):
        """Test tabs and newlines"""
        source = 'let\tx\n=\r\n5'
        tokens = tokenize(source)
        assert len(tokens) == 5  # let, x, =, 5, EOF
    
    def test_empty_source(self):
        """Test empty source"""
        tokens = tokenize('')
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_only_whitespace(self):
        """Test source with only whitespace"""
        tokens = tokenize('   \n\t\r\n  ')
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF


class TestRealWorldExamples:
    """Test with real Syntari code examples"""
    
    def test_hello_world(self):
        """Test hello world program"""
        source = 'print("Hello, world")'
        tokens = tokenize(source)
        
        assert len(tokens) == 5  # print, (, "Hello, world", ), EOF
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[2].type == TokenType.STRING
        assert tokens[2].value == 'Hello, world'
    
    def test_variable_arithmetic(self):
        """Test arithmetic with variables"""
        source = '''
        let x = 10
        let y = 20
        let z = x + y
        '''
        tokens = tokenize(source)
        
        # Should tokenize without errors
        assert tokens[-1].type == TokenType.EOF
        assert any(t.value == 'x' for t in tokens)
        assert any(t.value == 'y' for t in tokens)
        assert any(t.value == 'z' for t in tokens)
    
    def test_function_with_body(self):
        """Test function definition"""
        source = '''
        fn add(a: int, b: int) -> int {
            return a + b
        }
        '''
        tokens = tokenize(source)
        
        # Should have fn, identifier, params, arrow, return type, braces, etc.
        assert tokens[0].type == TokenType.FN
        assert any(t.type == TokenType.RETURN for t in tokens)
        assert any(t.type == TokenType.LBRACE for t in tokens)
        assert any(t.type == TokenType.RBRACE for t in tokens)
    
    def test_control_flow(self):
        """Test if/while statements"""
        source = '''
        if (x > 5) {
            print("big")
        } else {
            print("small")
        }
        
        while (x > 0) {
            x = x - 1
        }
        '''
        tokens = tokenize(source)
        
        assert any(t.type == TokenType.IF for t in tokens)
        assert any(t.type == TokenType.ELSE for t in tokens)
        assert any(t.type == TokenType.WHILE for t in tokens)
