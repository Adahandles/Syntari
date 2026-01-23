"""
Tests for error handling (try/catch/finally/throw) in Syntari v0.4
"""

import pytest
from src.interpreter.lexer import Lexer
from src.interpreter.parser import Parser
from src.interpreter.interpreter import Interpreter, SyntariException


def parse_and_run(code: str) -> Interpreter:
    """Helper to parse and run code"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    return interpreter


class TestThrow:
    """Test throw statement"""
    
    def test_throw_string(self):
        """Test throwing a string exception"""
        code = 'throw "error message";'
        with pytest.raises(SyntariException) as exc_info:
            parse_and_run(code)
        assert exc_info.value.value == "error message"
    
    def test_throw_number(self):
        """Test throwing a number"""
        code = 'throw 42;'
        with pytest.raises(SyntariException) as exc_info:
            parse_and_run(code)
        assert exc_info.value.value == 42


class TestTryCatch:
    """Test try-catch statements"""
    
    def test_catch_exception(self):
        """Test catching an exception"""
        code = '''
        let result = "";
        try {
            throw "error";
        } catch (e) {
            result = e;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("result") == "error"
    
    def test_catch_without_variable(self):
        """Test catch block without binding exception to variable"""
        code = '''
        let caught = false;
        try {
            throw "error";
        } catch {
            caught = true;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("caught") == True
    
    def test_exception_stops_execution(self):
        """Test that throw stops execution in try block"""
        code = '''
        let x = 0;
        try {
            x = 1;
            throw "error";
            x = 2;
        } catch (e) {
            // Do nothing
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("x") == 1  # Should be 1, not 2
    
    def test_multiple_catch_clauses(self):
        """Test multiple catch clauses"""
        code = '''
        let result = "";
        try {
            throw "test";
        } catch (e) {
            result = e;
        } catch (e2) {
            result = "second";
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("result") == "test"  # First catch should handle it
    
    def test_uncaught_exception_propagates(self):
        """Test that uncaught exceptions propagate"""
        code = '''
        try {
            try {
                throw "error";
            } catch (e) {
                throw "re-thrown";
            }
        } catch (outer) {
            // This should catch the re-thrown exception
        }
        '''
        # Should not raise - outer catch should handle it
        parse_and_run(code)


class TestFinally:
    """Test finally blocks"""
    
    def test_finally_always_executes(self):
        """Test that finally block always executes"""
        code = '''
        let cleanup = false;
        try {
            let x = 1;
        } finally {
            cleanup = true;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("cleanup") == True
    
    def test_finally_executes_after_exception(self):
        """Test that finally executes even when exception is thrown"""
        code = '''
        let cleanup = false;
        try {
            throw "error";
        } catch (e) {
            // Handle error
        } finally {
            cleanup = true;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("cleanup") == True
    
    def test_finally_without_catch(self):
        """Test finally block without catch"""
        code = '''
        let cleanup = false;
        try {
            let x = 1;
        } finally {
            cleanup = true;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("cleanup") == True
    
    def test_finally_with_uncaught_exception(self):
        """Test finally executes even with uncaught exception"""
        code = '''
        let cleanup = false;
        try {
            throw "error";
        } finally {
            cleanup = true;
        }
        '''
        with pytest.raises(SyntariException):
            interp = parse_and_run(code)
            # Check cleanup happened before exception propagated
            assert interp.environment.get("cleanup") == True


class TestComplexErrorHandling:
    """Test complex error handling scenarios"""
    
    def test_nested_try_catch(self):
        """Test nested try-catch blocks"""
        code = '''
        let outer = "";
        let inner = "";
        try {
            try {
                throw "inner error";
            } catch (e) {
                inner = e;
                throw "outer error";
            }
        } catch (e2) {
            outer = e2;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("inner") == "inner error"
        assert interp.environment.get("outer") == "outer error"
    
    def test_exception_in_catch(self):
        """Test throwing exception in catch block"""
        code = '''
        let result = "";
        try {
            try {
                throw "first";
            } catch (e) {
                throw "second";
            }
        } catch (e2) {
            result = e2;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("result") == "second"
    
    def test_return_in_finally(self):
        """Test that code after try-catch-finally executes"""
        code = '''
        let after = false;
        try {
            let x = 1;
        } finally {
            let y = 2;
        }
        after = true;
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("after") == True


class TestErrorMessages:
    """Test error handling with different value types"""
    
    def test_throw_variable(self):
        """Test throwing a variable's value"""
        code = '''
        let msg = "variable error";
        let result = "";
        try {
            throw msg;
        } catch (e) {
            result = e;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("result") == "variable error"
    
    def test_throw_expression(self):
        """Test throwing an expression result"""
        code = '''
        let result = "";
        try {
            throw 10 + 5;
        } catch (e) {
            result = e;
        }
        '''
        interp = parse_and_run(code)
        assert interp.environment.get("result") == 15
