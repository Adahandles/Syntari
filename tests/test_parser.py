"""
Tests for Syntari Parser
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.interpreter.lexer import tokenize
from src.interpreter.parser import Parser, ParseError, parse
from src.interpreter.nodes import *


class TestLiterals:
    """Test parsing literal values"""
    
    def test_parse_integer(self):
        """Test parsing integer literal"""
        tokens = tokenize('42')
        tree = parse(tokens)
        
        assert isinstance(tree, Program)
        assert len(tree.statements) == 1
        assert isinstance(tree.statements[0], ExprStmt)
        assert isinstance(tree.statements[0].expr, Number)
        assert tree.statements[0].expr.value == 42
    
    def test_parse_float(self):
        """Test parsing float literal"""
        tokens = tokenize('3.14')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, Number)
        assert expr.value == 3.14
    
    def test_parse_string(self):
        """Test parsing string literal"""
        tokens = tokenize('"hello"')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, String)
        assert expr.value == "hello"
    
    def test_parse_boolean_true(self):
        """Test parsing true"""
        tokens = tokenize('true')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, Boolean)
        assert expr.value is True
    
    def test_parse_boolean_false(self):
        """Test parsing false"""
        tokens = tokenize('false')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, Boolean)
        assert expr.value is False


class TestVariables:
    """Test parsing variables"""
    
    def test_parse_identifier(self):
        """Test parsing identifier"""
        tokens = tokenize('x')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, Var)
        assert expr.name == "x"
    
    def test_parse_var_decl_let(self):
        """Test parsing let declaration"""
        tokens = tokenize('let x = 42')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.name == "x"
        assert stmt.is_const is False
        assert isinstance(stmt.value, Number)
        assert stmt.value.value == 42
    
    def test_parse_var_decl_const(self):
        """Test parsing const declaration"""
        tokens = tokenize('const PI = 3.14')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.name == "PI"
        assert stmt.is_const is True
    
    def test_parse_var_decl_with_type(self):
        """Test parsing variable with type annotation"""
        tokens = tokenize('let x: int = 42')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, VarDecl)
        assert stmt.type_ref == "int"
    
    def test_parse_assignment(self):
        """Test parsing assignment"""
        tokens = tokenize('x = 10')
        tree = parse(tokens)
        
        stmt = tree.statements[0].expr
        assert isinstance(stmt, VarAssign)
        assert stmt.name == "x"
        assert isinstance(stmt.value, Number)


class TestBinaryOperations:
    """Test parsing binary operations"""
    
    def test_parse_addition(self):
        """Test parsing addition: 1 + 2"""
        tokens = tokenize('1 + 2')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, BinOp)
        assert expr.op == "+"
        assert isinstance(expr.left, Number)
        assert isinstance(expr.right, Number)
    
    def test_parse_subtraction(self):
        """Test parsing subtraction"""
        tokens = tokenize('5 - 3')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, BinOp)
        assert expr.op == "-"
    
    def test_parse_multiplication(self):
        """Test parsing multiplication"""
        tokens = tokenize('3 * 4')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, BinOp)
        assert expr.op == "*"
    
    def test_parse_division(self):
        """Test parsing division"""
        tokens = tokenize('10 / 2')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, BinOp)
        assert expr.op == "/"
    
    def test_parse_precedence(self):
        """Test operator precedence: 2 + 3 * 4 should be 2 + (3 * 4)"""
        tokens = tokenize('2 + 3 * 4')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        # Should be: (2 + (3 * 4))
        assert isinstance(expr, BinOp)
        assert expr.op == "+"
        assert isinstance(expr.left, Number)
        assert expr.left.value == 2
        assert isinstance(expr.right, BinOp)
        assert expr.right.op == "*"
    
    def test_parse_comparison(self):
        """Test parsing comparison operators"""
        test_cases = [
            ('x < 5', '<'),
            ('x <= 5', '<='),
            ('x > 5', '>'),
            ('x >= 5', '>='),
            ('x == 5', '=='),
            ('x != 5', '!='),
        ]
        
        for source, expected_op in test_cases:
            tokens = tokenize(source)
            tree = parse(tokens)
            expr = tree.statements[0].expr
            assert isinstance(expr, BinOp)
            assert expr.op == expected_op
    
    def test_parse_logical_and(self):
        """Test parsing logical AND"""
        tokens = tokenize('true && false')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, BinOp)
        assert expr.op == "&&"
    
    def test_parse_logical_or(self):
        """Test parsing logical OR"""
        tokens = tokenize('true || false')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, BinOp)
        assert expr.op == "||"


class TestUnaryOperations:
    """Test parsing unary operations"""
    
    def test_parse_negation(self):
        """Test parsing negation: -5"""
        tokens = tokenize('-5')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, UnaryOp)
        assert expr.op == "-"
        assert isinstance(expr.operand, Number)
    
    def test_parse_logical_not(self):
        """Test parsing logical not: !true"""
        tokens = tokenize('!true')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, UnaryOp)
        assert expr.op == "!"


class TestCalls:
    """Test parsing function calls"""
    
    def test_parse_call_no_args(self):
        """Test parsing call with no arguments"""
        tokens = tokenize('foo()')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, Call)
        assert expr.callee == "foo"
        assert len(expr.args) == 0
    
    def test_parse_call_one_arg(self):
        """Test parsing call with one argument"""
        tokens = tokenize('print("hello")')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, Call)
        assert expr.callee == "print"
        assert len(expr.args) == 1
        assert isinstance(expr.args[0], String)
    
    def test_parse_call_multiple_args(self):
        """Test parsing call with multiple arguments"""
        tokens = tokenize('add(1, 2, 3)')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert isinstance(expr, Call)
        assert len(expr.args) == 3


class TestControlFlow:
    """Test parsing control flow statements"""
    
    def test_parse_if_no_else(self):
        """Test parsing if without else"""
        tokens = tokenize('if (x > 5) { print("big") }')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, IfStmt)
        assert isinstance(stmt.condition, BinOp)
        assert isinstance(stmt.then_block, Block)
        assert stmt.else_block is None
    
    def test_parse_if_with_else(self):
        """Test parsing if with else"""
        tokens = tokenize('if (x > 5) { print("big") } else { print("small") }')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, IfStmt)
        assert stmt.else_block is not None
        assert isinstance(stmt.else_block, Block)
    
    def test_parse_while(self):
        """Test parsing while loop"""
        tokens = tokenize('while (i < 10) { i = i + 1 }')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, WhileStmt)
        assert isinstance(stmt.condition, BinOp)
        assert isinstance(stmt.body, Block)
    
    def test_parse_return_with_value(self):
        """Test parsing return with value"""
        tokens = tokenize('return 42')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, ReturnStmt)
        assert isinstance(stmt.value, Number)
    
    def test_parse_return_bare(self):
        """Test parsing bare return"""
        tokens = tokenize('return')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, ReturnStmt)
        assert stmt.value is None


class TestFunctions:
    """Test parsing function declarations"""
    
    def test_parse_func_no_params(self):
        """Test parsing function with no parameters"""
        tokens = tokenize('fn greet() { print("hello") }')
        tree = parse(tokens)
        
        func = tree.statements[0]
        assert isinstance(func, FuncDecl)
        assert func.name == "greet"
        assert len(func.params) == 0
        assert func.return_type is None
        assert isinstance(func.body, Block)
    
    def test_parse_func_with_params(self):
        """Test parsing function with parameters"""
        tokens = tokenize('fn add(a: int, b: int) { return a + b }')
        tree = parse(tokens)
        
        func = tree.statements[0]
        assert isinstance(func, FuncDecl)
        assert func.name == "add"
        assert len(func.params) == 2
        assert func.params[0].name == "a"
        assert func.params[0].type_ref == "int"
    
    def test_parse_func_with_return_type(self):
        """Test parsing function with return type"""
        tokens = tokenize('fn add(a: int, b: int) -> int { return a + b }')
        tree = parse(tokens)
        
        func = tree.statements[0]
        assert func.return_type == "int"


class TestImports:
    """Test parsing import declarations"""
    
    def test_parse_simple_import(self):
        """Test parsing simple import"""
        tokens = tokenize('use core')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, ImportDecl)
        assert stmt.path == ["core"]
    
    def test_parse_nested_import(self):
        """Test parsing nested import"""
        tokens = tokenize('use core.system')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, ImportDecl)
        assert stmt.path == ["core", "system"]


class TestTypes:
    """Test parsing type declarations"""
    
    def test_parse_type_decl(self):
        """Test parsing type declaration"""
        tokens = tokenize('type Point { x: int, y: int }')
        tree = parse(tokens)
        
        stmt = tree.statements[0]
        assert isinstance(stmt, TypeDecl)
        assert stmt.name == "Point"
        assert len(stmt.fields) == 2
        assert stmt.fields[0].name == "x"
        assert stmt.fields[0].type_ref == "int"


class TestComplexPrograms:
    """Test parsing complex programs"""
    
    def test_parse_hello_world(self):
        """Test parsing hello world"""
        tokens = tokenize('print("Hello, world")')
        tree = parse(tokens)
        
        assert isinstance(tree, Program)
        assert len(tree.statements) == 1
        expr = tree.statements[0].expr
        assert isinstance(expr, Call)
        assert expr.callee == "print"
    
    def test_parse_variable_arithmetic(self):
        """Test parsing variable arithmetic"""
        source = '''
        let x = 10
        let y = 20
        let z = x + y
        '''
        tokens = tokenize(source)
        tree = parse(tokens)
        
        assert len(tree.statements) == 3
        assert all(isinstance(s, VarDecl) for s in tree.statements)
    
    def test_parse_function_with_body(self):
        """Test parsing complete function"""
        source = '''
        fn add(a: int, b: int) -> int {
            return a + b
        }
        '''
        tokens = tokenize(source)
        tree = parse(tokens)
        
        func = tree.statements[0]
        assert isinstance(func, FuncDecl)
        assert len(func.body.statements) == 1
        assert isinstance(func.body.statements[0], ReturnStmt)
    
    def test_parse_multiple_statements(self):
        """Test parsing multiple statements"""
        source = '''
        let x = 5
        print(x)
        x = x + 1
        print(x)
        '''
        tokens = tokenize(source)
        tree = parse(tokens)
        
        assert len(tree.statements) == 4


class TestGrouping:
    """Test parsing grouped expressions"""
    
    def test_parse_parenthesized_expr(self):
        """Test parsing parenthesized expression"""
        tokens = tokenize('(1 + 2) * 3')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        # Should be: ((1 + 2) * 3)
        assert isinstance(expr, BinOp)
        assert expr.op == "*"
        assert isinstance(expr.left, BinOp)
        assert expr.left.op == "+"


class TestErrors:
    """Test error handling"""
    
    def test_error_missing_semicolon_ok(self):
        """Test that missing semicolon is okay (optional)"""
        tokens = tokenize('let x = 5')
        tree = parse(tokens)
        assert len(tree.statements) == 1
    
    def test_error_unexpected_token(self):
        """Test error on unexpected token"""
        # Lexer will catch invalid tokens like @
        from src.interpreter.lexer import LexerError
        
        with pytest.raises(LexerError):
            tokens = tokenize('@invalid')
    
    def test_error_missing_paren(self):
        """Test error on missing parenthesis"""
        tokens = tokenize('if x > 5 { print("big") }')
        
        with pytest.raises(ParseError) as exc_info:
            parse(tokens)
        
        assert "Expected '('" in str(exc_info.value)
    
    def test_error_missing_brace(self):
        """Test error on missing brace"""
        tokens = tokenize('if (true) print("hi")')
        
        with pytest.raises(ParseError) as exc_info:
            parse(tokens)
        
        assert "Expected '{'" in str(exc_info.value)


class TestEdgeCases:
    """Test edge cases"""
    
    def test_parse_empty_program(self):
        """Test parsing empty program"""
        tokens = tokenize('')
        tree = parse(tokens)
        
        assert isinstance(tree, Program)
        assert len(tree.statements) == 0
    
    def test_parse_only_whitespace(self):
        """Test parsing program with only whitespace"""
        tokens = tokenize('   \n\t  ')
        tree = parse(tokens)
        
        assert len(tree.statements) == 0
    
    def test_parse_with_comments(self):
        """Test parsing with comments"""
        source = '''
        // This is a comment
        let x = 5
        /* Multi-line
           comment */
        print(x)
        '''
        tokens = tokenize(source)
        tree = parse(tokens)
        
        assert len(tree.statements) == 2


class TestPrecedence:
    """Test operator precedence"""
    
    def test_precedence_multiply_before_add(self):
        """Test that * binds tighter than +"""
        tokens = tokenize('1 + 2 * 3')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert expr.op == "+"
        assert isinstance(expr.right, BinOp)
        assert expr.right.op == "*"
    
    def test_precedence_comparison_before_logical(self):
        """Test that comparison binds tighter than logical ops"""
        tokens = tokenize('x > 5 && y < 10')
        tree = parse(tokens)
        
        expr = tree.statements[0].expr
        assert expr.op == "&&"
        assert isinstance(expr.left, BinOp)
        assert expr.left.op == ">"
        assert isinstance(expr.right, BinOp)
        assert expr.right.op == "<"
