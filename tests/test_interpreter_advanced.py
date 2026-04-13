"""
Advanced interpreter tests covering classes, match, try/catch/throw, imports,
member access, and other features not exercised by the basic test suite.
"""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interpreter.interpreter import (
    Interpreter,
    RuntimeError as SyntariRuntimeError,
    SyntariException,
    SyntariClass,
    ClassInstance,
    BoundMethod,
    Environment,
    interpret,
)
from src.interpreter.lexer import tokenize
from src.interpreter.nodes import (
    Block,
    Call,
    ExprStmt,
    MemberAccess,
    Number,
    String,
    SuperExpr,
    ThisExpr,
    Var,
    MatchStmt,
    CatchClause,
)
from src.interpreter.parser import parse


def run_code(source: str):
    tokens = tokenize(source)
    tree = parse(tokens)
    return interpret(tree)


def capture_output(source: str) -> str:
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        run_code(source)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


class TestEnvironment:
    def test_define_and_get(self):
        env = Environment()
        env.define("x", 42)
        assert env.get("x") == 42

    def test_get_from_parent(self):
        parent = Environment()
        parent.define("x", 10)
        child = Environment(parent)
        assert child.get("x") == 10

    def test_get_undefined_raises(self):
        env = Environment()
        with pytest.raises(SyntariRuntimeError, match="Undefined variable"):
            env.get("missing")

    def test_set_in_current_scope(self):
        env = Environment()
        env.define("x", 1)
        env.set("x", 99)
        assert env.get("x") == 99

    def test_set_in_parent_scope(self):
        parent = Environment()
        parent.define("x", 1)
        child = Environment(parent)
        child.set("x", 99)
        assert parent.get("x") == 99

    def test_set_undefined_raises(self):
        env = Environment()
        with pytest.raises(SyntariRuntimeError, match="Undefined variable"):
            env.set("missing", 42)

    def test_exists_true(self):
        env = Environment()
        env.define("x", 1)
        assert env.exists("x") is True

    def test_exists_in_parent(self):
        parent = Environment()
        parent.define("x", 1)
        child = Environment(parent)
        assert child.exists("x") is True

    def test_exists_false(self):
        env = Environment()
        assert env.exists("missing") is False


# ---------------------------------------------------------------------------
# Classes – declaration, instantiation, properties, methods
# ---------------------------------------------------------------------------


class TestClasses:
    def test_class_declaration(self):
        """Declaring a class stores a SyntariClass in the environment.
        Class properties use 'name = value;' syntax (no 'let').
        """
        interp = Interpreter()
        # Use the same property syntax as examples/classes.syn: name = value;
        tokens = tokenize("class Point {\n    x = 0;\n    y = 0;\n}")
        tree = parse(tokens)
        interp.interpret(tree)
        result = interp.environment.get("Point")
        assert isinstance(result, SyntariClass)

    def test_class_repr(self):
        interp = Interpreter()
        tokens = tokenize("class Foo {}")
        tree = parse(tokens)
        interp.interpret(tree)
        cls = interp.environment.get("Foo")
        assert "Foo" in repr(cls)

    def test_new_instance(self):
        interp = Interpreter()
        tokens = tokenize("class Point {\n    x = 0;\n    y = 0;\n}\nnew Point()")
        tree = parse(tokens)
        result = interp.interpret(tree)
        assert isinstance(result, ClassInstance)

    def test_instance_repr(self):
        interp = Interpreter()
        tokens = tokenize("class Foo {}\nnew Foo()")
        tree = parse(tokens)
        result = interp.interpret(tree)
        assert "Foo" in repr(result)

    def test_property_initializer(self):
        interp = Interpreter()
        tokens = tokenize("class Point {\n    x = 10;\n}\nlet p = new Point()\np.x")
        tree = parse(tokens)
        result = interp.interpret(tree)
        assert result == 10

    def test_member_assignment(self):
        interp = Interpreter()
        tokens = tokenize("class Box {\n    value = 0;\n}\nlet b = new Box()\nb.value = 42\nb.value")
        tree = parse(tokens)
        result = interp.interpret(tree)
        assert result == 42

    def test_method_call(self):
        code = "class Counter {\n    count = 0;\n    fn get_count() {\n        return this.count\n    }\n}\nlet c = new Counter()\nc.count = 5\nc.get_count()"
        result = run_code(code)
        assert result == 5

    def test_bound_method_repr(self):
        code = "class Foo {\n    fn bar() { return 1 }\n}\nlet f = new Foo()\nf.bar"
        result = run_code(code)
        assert isinstance(result, BoundMethod)
        assert "bar" in repr(result)

    def test_undefined_class_raises(self):
        with pytest.raises(SyntariRuntimeError, match="Undefined class"):
            run_code("new NotAClass()")

    def test_non_class_new_raises(self):
        with pytest.raises(SyntariRuntimeError, match="not a class"):
            run_code("let x = 42\nnew x()")

    def test_member_access_on_non_object_raises(self):
        with pytest.raises(SyntariRuntimeError, match="Cannot access member"):
            run_code("let x = 42\nx.foo")

    def test_undefined_property_raises(self):
        with pytest.raises(SyntariRuntimeError, match="Undefined property or method"):
            run_code("class Foo {}\nlet f = new Foo()\nf.nonexistent")

    def test_member_assign_on_non_object_raises(self):
        with pytest.raises(SyntariRuntimeError, match="Cannot assign to member"):
            run_code("let x = 42\nx.foo = 1")

    def test_member_access_on_dict(self):
        """MemberAccess on a dict (e.g. network response) returns the key."""
        interp = Interpreter()
        interp.environment.define("data", {"status": 200})
        node = MemberAccess(object=Var("data"), member="status")
        result = interp._evaluate(node)
        assert result == 200

    def test_member_access_missing_dict_key_raises(self):
        interp = Interpreter()
        interp.environment.define("data", {"status": 200})
        node = MemberAccess(object=Var("data"), member="missing")
        with pytest.raises(SyntariRuntimeError, match="no key"):
            interp._evaluate(node)

    def test_this_outside_class_raises(self):
        """visit_ThisExpr raises when 'this' is not in scope."""
        interp = Interpreter()
        with pytest.raises(SyntariRuntimeError, match="'this'"):
            interp._evaluate(ThisExpr())

    def test_super_outside_class_raises(self):
        """visit_SuperExpr raises when 'super' is not in scope."""
        interp = Interpreter()
        with pytest.raises(SyntariRuntimeError, match="'super'"):
            interp._evaluate(SuperExpr(method_name="init"))

    def test_call_non_callable_raises(self):
        """Calling a non-BoundMethod value (via MemberAccess) raises 'Cannot call'."""
        interp = Interpreter()
        # data.status = 200 (an int) - calling it should raise
        interp.environment.define("data", {"status": 200})
        call_node = Call(
            callee=MemberAccess(object=Var("data"), member="status"),
            args=[],
        )
        with pytest.raises(SyntariRuntimeError, match="Cannot call"):
            interp._evaluate(call_node)


# ---------------------------------------------------------------------------
# Match statements (via interpreter nodes - avoids parser syntax issues)
# ---------------------------------------------------------------------------


class TestMatchStatements:
    def _match(self, subject, cases):
        """Run a match statement directly through the interpreter."""
        interp = Interpreter()
        interp.environment.define("x", subject)

        node = MatchStmt(
            expr=Var("x"),
            cases=[(pat, Block([ExprStmt(String(result))])) for pat, result in cases],
        )
        return interp._execute(node)

    def test_match_exact_value(self):
        result = self._match(2, [(1, "one"), (2, "two"), (3, "three")])
        assert result == "two"

    def test_match_wildcard(self):
        result = self._match(99, [(1, "one"), ("_", "other")])
        assert result == "other"

    def test_match_no_match_returns_none(self):
        result = self._match(99, [(1, "one"), (2, "two")])
        assert result is None

    def test_match_string_subject(self):
        interp = Interpreter()
        interp.environment.define("s", "hello")
        node = MatchStmt(
            expr=Var("s"),
            cases=[
                ("hello", Block([ExprStmt(String("greeting"))])),
                ("_", Block([ExprStmt(String("unknown"))])),
            ],
        )
        result = interp._execute(node)
        assert result == "greeting"

    def test_match_via_source_code(self):
        """Test match via actual source (integer patterns only in parser)."""
        code = "let x = 2\nmatch x { 1 -> { 100 }, 2 -> { 200 } }"
        result = run_code(code)
        assert result == 200


# ---------------------------------------------------------------------------
# Try/Catch/Finally/Throw
# ---------------------------------------------------------------------------


class TestTryCatchFinally:
    def test_try_no_exception(self):
        code = "let x = 0\ntry { x = 42 } catch { x = -1 }\nx"
        result = run_code(code)
        assert result == 42

    def test_throw_caught(self):
        code = 'let result = "none"\ntry { throw "error happened" } catch { result = "caught" }\nresult'
        result = run_code(code)
        assert result == "caught"

    def test_throw_with_exception_var(self):
        code = 'let msg = ""\ntry { throw "test error" } catch (e) { msg = e }\nmsg'
        result = run_code(code)
        assert result == "test error"

    def test_finally_always_runs(self):
        code = "let ran = false\ntry { let x = 1 } finally { ran = true }\nran"
        result = run_code(code)
        assert result is True

    def test_finally_runs_after_throw(self):
        code = "let ran = false\ntry { try { throw \"err\" } finally { ran = true } } catch { let dummy = 0 }\nran"
        result = run_code(code)
        assert result is True

    def test_uncaught_exception_propagates(self):
        with pytest.raises(SyntariException):
            run_code("throw 42")

    def test_runtime_error_caught(self):
        code = 'let result = "none"\ntry { let x = 1 / 0 } catch { result = "caught_runtime" }\nresult'
        result = run_code(code)
        assert result == "caught_runtime"

    def test_runtime_error_with_var(self):
        code = 'let msg = ""\ntry { let x = 1 / 0 } catch (e) { msg = e }\nmsg'
        result = run_code(code)
        assert isinstance(result, str)

    def test_uncaught_runtime_error_raises(self):
        """A typed catch (e: SomeName) with non-RuntimeError type lets it propagate."""
        # Use interpreter nodes directly to avoid parser syntax issues
        from src.interpreter.nodes import TryStmt, Block, ExprStmt, BinOp, Number

        interp = Interpreter()
        # try { 1/0 } catch (e: TypeError) { ... }
        # exception_type = "TypeError" != "RuntimeError" → not caught
        catch = CatchClause(
            exception_var="e",
            exception_type="SomeOtherType",
            block=Block([]),
        )
        node = TryStmt(
            try_block=Block([ExprStmt(BinOp(Number(1), "/", Number(0)))]),
            catch_clauses=[catch],
            finally_block=None,
        )
        with pytest.raises(SyntariRuntimeError):
            interp._execute(node)

    def test_catch_clause_not_visited_directly(self):
        """visit_CatchClause should not be called directly."""
        interp = Interpreter()
        node = CatchClause(exception_var=None, exception_type=None, block=Block([]))
        with pytest.raises(SyntariRuntimeError, match="CatchClause"):
            interp._execute(node)


# ---------------------------------------------------------------------------
# Import declarations
# ---------------------------------------------------------------------------


class TestImports:
    def test_import_is_noop(self):
        # ImportDecl is a no-op in v0.3
        code = "use some.module\nlet x = 42\nx"
        result = run_code(code)
        assert result == 42


# ---------------------------------------------------------------------------
# Type/Trait/Impl declarations (no-ops at runtime)
# ---------------------------------------------------------------------------


class TestTypeDeclarations:
    def test_type_decl_is_noop(self):
        # type uses struct syntax: type Name { field: Type }
        code = "type Vector { x: int, y: int }\nlet v = 1\nv"
        result = run_code(code)
        assert result == 1

    def test_trait_decl_is_noop(self):
        # trait syntax: trait Name { fn method() }
        code = "trait Printable { fn display() }\nlet x = 2\nx"
        result = run_code(code)
        assert result == 2


# ---------------------------------------------------------------------------
# Function edge cases
# ---------------------------------------------------------------------------


class TestFunctionEdgeCases:
    def test_function_wrong_arg_count_raises(self):
        with pytest.raises(SyntariRuntimeError, match="expects"):
            run_code("fn add(a, b) { return a + b }\nadd(1)")

    def test_undefined_function_raises(self):
        with pytest.raises(SyntariRuntimeError, match="Undefined function"):
            run_code("notdefined()")

    def test_return_no_value(self):
        code = "fn nothing() { return }\nnothing()"
        result = run_code(code)
        assert result is None

    def test_nested_function_calls(self):
        code = "fn double(x) { return x * 2 }\nfn quad(x) { return double(double(x)) }\nquad(3)"
        result = run_code(code)
        assert result == 12


# ---------------------------------------------------------------------------
# is_truthy edge cases in interpreter
# ---------------------------------------------------------------------------


class TestIsTruthy:
    def _truthy(self, val) -> bool:
        interp = Interpreter()
        return interp._is_truthy(val)

    def test_none_falsy(self):
        assert self._truthy(None) is False

    def test_false_falsy(self):
        assert self._truthy(False) is False

    def test_zero_falsy(self):
        assert self._truthy(0) is False

    def test_empty_string_falsy(self):
        assert self._truthy("") is False

    def test_truthy_values(self):
        assert self._truthy(1) is True
        assert self._truthy("a") is True
        assert self._truthy(True) is True


# ---------------------------------------------------------------------------
# RuntimeError and SyntariException classes
# ---------------------------------------------------------------------------


class TestRuntimeError:
    def test_runtime_error_with_node(self):
        err = SyntariRuntimeError("test error", node=Number(1))
        assert "test error" in str(err)
        assert err.node is not None

    def test_runtime_error_message(self):
        err = SyntariRuntimeError("something bad")
        assert err.message == "something bad"

    def test_syntari_exception(self):
        exc = SyntariException("test value", "MyError")
        assert exc.value == "test value"
        assert exc.exception_type == "MyError"
        assert "MyError" in str(exc)


# ---------------------------------------------------------------------------
# Interpreter with recorder
# ---------------------------------------------------------------------------


class TestInterpreterRecorder:
    def test_interpreter_with_noop_recorder(self):
        """The default NoOpAdapter recorder doesn't crash."""
        tokens = tokenize("let x = 42")
        tree = parse(tokens)
        result = interpret(tree)
        assert result is None

    def test_interpret_multiple_statements(self):
        tokens = tokenize("let x = 1\nlet y = 2\nx + y")
        tree = parse(tokens)
        result = interpret(tree)
        assert result == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
