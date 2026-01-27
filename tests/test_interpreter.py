"""
Tests for Syntari Interpreter
"""

import pytest
import sys
import os
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interpreter.lexer import tokenize
from src.interpreter.parser import parse
from src.interpreter.interpreter import Interpreter, RuntimeError as SyntariRuntimeError, interpret
from src.interpreter.nodes import *


def run_code(source: str) -> any:
    """Helper to run code and return result"""
    tokens = tokenize(source)
    tree = parse(tokens)
    return interpret(tree)


def capture_output(source: str) -> str:
    """Helper to capture stdout from running code"""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        run_code(source)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    return output


class TestLiterals:
    """Test evaluating literals"""

    def test_number(self):
        """Test number literal"""
        result = run_code("42")
        assert result == 42

    def test_float(self):
        """Test float literal"""
        result = run_code("3.14")
        assert result == 3.14

    def test_string(self):
        """Test string literal"""
        result = run_code('"hello"')
        assert result == "hello"

    def test_boolean_true(self):
        """Test true literal"""
        result = run_code("true")
        assert result is True

    def test_boolean_false(self):
        """Test false literal"""
        result = run_code("false")
        assert result is False


class TestArithmetic:
    """Test arithmetic operations"""

    def test_addition(self):
        """Test addition"""
        result = run_code("2 + 3")
        assert result == 5

    def test_subtraction(self):
        """Test subtraction"""
        result = run_code("10 - 3")
        assert result == 7

    def test_multiplication(self):
        """Test multiplication"""
        result = run_code("4 * 5")
        assert result == 20

    def test_division(self):
        """Test division"""
        result = run_code("10 / 2")
        assert result == 5.0

    def test_modulo(self):
        """Test modulo"""
        result = run_code("10 % 3")
        assert result == 1

    def test_precedence(self):
        """Test operator precedence: 2 + 3 * 4 = 14"""
        result = run_code("2 + 3 * 4")
        assert result == 14

    def test_parentheses(self):
        """Test parentheses: (2 + 3) * 4 = 20"""
        result = run_code("(2 + 3) * 4")
        assert result == 20

    def test_division_by_zero(self):
        """Test division by zero raises error"""
        with pytest.raises(SyntariRuntimeError):
            run_code("10 / 0")


class TestComparison:
    """Test comparison operations"""

    def test_equal(self):
        """Test equality"""
        assert run_code("5 == 5") is True
        assert run_code("5 == 3") is False

    def test_not_equal(self):
        """Test inequality"""
        assert run_code("5 != 3") is True
        assert run_code("5 != 5") is False

    def test_less_than(self):
        """Test less than"""
        assert run_code("3 < 5") is True
        assert run_code("5 < 3") is False

    def test_less_equal(self):
        """Test less than or equal"""
        assert run_code("3 <= 5") is True
        assert run_code("5 <= 5") is True
        assert run_code("7 <= 5") is False

    def test_greater_than(self):
        """Test greater than"""
        assert run_code("5 > 3") is True
        assert run_code("3 > 5") is False

    def test_greater_equal(self):
        """Test greater than or equal"""
        assert run_code("5 >= 3") is True
        assert run_code("5 >= 5") is True
        assert run_code("3 >= 5") is False


class TestLogical:
    """Test logical operations"""

    def test_and_true(self):
        """Test logical AND with true values"""
        assert run_code("true && true") is True

    def test_and_false(self):
        """Test logical AND with false"""
        assert run_code("true && false") is False
        assert run_code("false && true") is False

    def test_or_true(self):
        """Test logical OR with true"""
        assert run_code("true || false") is True
        assert run_code("false || true") is True

    def test_or_false(self):
        """Test logical OR with false values"""
        assert run_code("false || false") is False

    def test_not(self):
        """Test logical NOT"""
        assert run_code("!true") is False
        assert run_code("!false") is True


class TestUnary:
    """Test unary operations"""

    def test_negation(self):
        """Test negation"""
        result = run_code("-5")
        assert result == -5

    def test_double_negation(self):
        """Test double negation"""
        result = run_code("--5")
        assert result == 5


class TestVariables:
    """Test variable operations"""

    def test_var_decl_and_use(self):
        """Test variable declaration and use"""
        source = """
        let x = 42
        x
        """
        result = run_code(source)
        assert result == 42

    def test_const_decl(self):
        """Test const declaration"""
        source = """
        const PI = 3.14
        PI
        """
        result = run_code(source)
        assert result == 3.14

    def test_assignment(self):
        """Test variable assignment"""
        source = """
        let x = 5
        x = 10
        x
        """
        result = run_code(source)
        assert result == 10

    def test_undefined_variable(self):
        """Test undefined variable raises error"""
        with pytest.raises(SyntariRuntimeError):
            run_code("undefined_var")

    def test_variable_in_expression(self):
        """Test variable in expression"""
        source = """
        let x = 10
        let y = 20
        x + y
        """
        result = run_code(source)
        assert result == 30


class TestPrint:
    """Test print function"""

    def test_print_number(self):
        """Test printing number"""
        output = capture_output("print(42)")
        assert output.strip() == "42"

    def test_print_string(self):
        """Test printing string"""
        output = capture_output('print("hello")')
        assert output.strip() == "hello"

    def test_print_multiple_args(self):
        """Test printing multiple arguments"""
        output = capture_output("print(1, 2, 3)")
        assert output.strip() == "1 2 3"


class TestControlFlow:
    """Test control flow statements"""

    def test_if_true(self):
        """Test if with true condition"""
        source = """
        let x = 0
        if (true) {
            x = 10
        }
        x
        """
        result = run_code(source)
        assert result == 10

    def test_if_false(self):
        """Test if with false condition"""
        source = """
        let x = 0
        if (false) {
            x = 10
        }
        x
        """
        result = run_code(source)
        assert result == 0

    def test_if_else_true(self):
        """Test if-else with true condition"""
        source = """
        let x = 0
        if (true) {
            x = 10
        } else {
            x = 20
        }
        x
        """
        result = run_code(source)
        assert result == 10

    def test_if_else_false(self):
        """Test if-else with false condition"""
        source = """
        let x = 0
        if (false) {
            x = 10
        } else {
            x = 20
        }
        x
        """
        result = run_code(source)
        assert result == 20

    def test_while_loop(self):
        """Test while loop"""
        source = """
        let i = 0
        let sum = 0
        while (i < 5) {
            sum = sum + i
            i = i + 1
        }
        sum
        """
        result = run_code(source)
        assert result == 0 + 1 + 2 + 3 + 4  # 10


class TestFunctions:
    """Test function definitions and calls"""

    def test_function_no_params(self):
        """Test function with no parameters"""
        source = """
        fn greet() {
            return "hello"
        }
        greet()
        """
        result = run_code(source)
        assert result == "hello"

    def test_function_with_params(self):
        """Test function with parameters"""
        source = """
        fn add(a, b) {
            return a + b
        }
        add(3, 4)
        """
        result = run_code(source)
        assert result == 7

    def test_function_multiple_statements(self):
        """Test function with multiple statements"""
        source = """
        fn compute(x) {
            let y = x * 2
            let z = y + 10
            return z
        }
        compute(5)
        """
        result = run_code(source)
        assert result == 20

    def test_function_no_return(self):
        """Test function without explicit return"""
        source = """
        fn foo() {
            let x = 5
        }
        foo()
        """
        result = run_code(source)
        assert result is None

    def test_recursive_function(self):
        """Test recursive function"""
        source = """
        fn factorial(n) {
            if (n <= 1) {
                return 1
            } else {
                return n * factorial(n - 1)
            }
        }
        factorial(5)
        """
        result = run_code(source)
        assert result == 120


class TestScope:
    """Test variable scoping"""

    def test_block_scope(self):
        """Test block creates new scope"""
        source = """
        let x = 10
        if (true) {
            let x = 20
        }
        x
        """
        result = run_code(source)
        assert result == 10

    def test_nested_scope(self):
        """Test nested scopes"""
        source = """
        let x = 1
        if (true) {
            let y = 2
            if (true) {
                let z = 3
                x + y + z
            }
        }
        """
        result = run_code(source)
        assert result == 6


class TestComplexPrograms:
    """Test complete programs"""

    def test_hello_world(self):
        """Test hello world"""
        output = capture_output('print("Hello, world")')
        assert "Hello, world" in output

    def test_fibonacci(self):
        """Test Fibonacci calculation"""
        source = """
        fn fib(n) {
            if (n <= 1) {
                return n
            } else {
                return fib(n - 1) + fib(n - 2)
            }
        }
        fib(10)
        """
        result = run_code(source)
        assert result == 55

    def test_sum_loop(self):
        """Test sum with loop"""
        source = """
        let sum = 0
        let i = 1
        while (i <= 10) {
            sum = sum + i
            i = i + 1
        }
        sum
        """
        result = run_code(source)
        assert result == 55

    def test_conditional_logic(self):
        """Test complex conditional logic"""
        source = """
        fn max(a, b) {
            if (a > b) {
                return a
            } else {
                return b
            }
        }
        max(10, 20)
        """
        result = run_code(source)
        assert result == 20


class TestBuiltins:
    """Test built-in functions"""

    def test_time(self):
        """Test time() function"""
        result = run_code("time()")
        assert isinstance(result, float)
        assert result > 0


class TestEdgeCases:
    """Test edge cases"""

    def test_empty_program(self):
        """Test empty program"""
        result = run_code("")
        assert result is None

    def test_expression_only(self):
        """Test expression-only program"""
        result = run_code("42")
        assert result == 42

    def test_multiple_statements(self):
        """Test multiple statements"""
        source = """
        let a = 1
        let b = 2
        let c = 3
        a + b + c
        """
        result = run_code(source)
        assert result == 6

    def test_nested_arithmetic(self):
        """Test nested arithmetic expressions"""
        result = run_code("((2 + 3) * 4) - (10 / 2)")
        assert result == 15.0

    def test_mixed_types(self):
        """Test mixed integer and float"""
        result = run_code("10 + 3.5")
        assert result == 13.5

    def test_string_variable(self):
        """Test string variables"""
        source = """let msg = "Hello"
msg"""
        result = run_code(source)
        assert result == "Hello"

    def test_modulo_operation(self):
        """Test modulo operator"""
        result = run_code("10 % 3")
        assert result == 1

    def test_function_with_default_return(self):
        """Test function with no explicit return"""
        source = """
        fn test() {
            let x = 1
        }
        test()
        """
        result = run_code(source)
        assert result is None

    def test_function_multiple_params(self):
        """Test function with multiple parameters"""
        source = """
        fn sum(a, b, c) {
            return a + b + c
        }
        sum(1, 2, 3)
        """
        result = run_code(source)
        assert result == 6

    def test_nested_function_calls(self):
        """Test nested function calls"""
        source = """
        fn double(x) { return x * 2 }
        fn triple(x) { return x * 3 }
        double(triple(5))
        """
        result = run_code(source)
        assert result == 30

    def test_return_early(self):
        """Test early return from function"""
        source = """
        fn check(x) {
            if (x < 0) {
                return "negative"
            }
            return "non-negative"
        }
        check(-5)
        """
        result = run_code(source)
        assert result == "negative"

    def test_empty_function(self):
        """Test empty function body"""
        source = """
        fn noop() {}
        noop()
        """
        result = run_code(source)
        assert result is None

    def test_complex_expression(self):
        """Test complex nested expression"""
        result = run_code("(2 + 3) * (4 - 1)")
        assert result == 15

    def test_chained_assignment(self):
        """Test variable reassignment"""
        source = """
        let x = 5
        x = 10
        x = 15
        x
        """
        result = run_code(source)
        assert result == 15
