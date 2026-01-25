"""
Syntari Interpreter - Executes Abstract Syntax Tree for v0.3
"""

from typing import Any, Dict, List, Optional
from src.interpreter.nodes import *
from src.core import system, ai, net


class RuntimeError(Exception):
    """Raised when interpreter encounters a runtime error"""

    def __init__(self, message: str, node: Optional[Node] = None):
        self.message = message
        self.node = node
        super().__init__(f"Runtime error: {message}")


class SyntariException(Exception):
    """User-thrown exception in Syntari code"""

    def __init__(self, value: Any, exception_type: str = "Exception"):
        self.value = value
        self.exception_type = exception_type
        super().__init__(f"{exception_type}: {value}")


class ReturnValue(Exception):
    """Exception used to implement return statements"""

    def __init__(self, value: Any):
        self.value = value


class SyntariClass:
    """Represents a class definition"""

    def __init__(self, class_node: "ClassDecl", enclosing_env: "Environment"):
        self.class_node = class_node
        self.enclosing_env = enclosing_env

    def __repr__(self):
        return f"<class {self.class_node.name}>"


class ClassInstance:
    """Represents an instance of a class"""

    def __init__(self, class_def: SyntariClass):
        self.class_def = class_def
        self.properties: Dict[str, Any] = {}

        # Initialize properties with default values
        for prop in class_def.class_node.properties:
            if prop.initializer:
                # We'll evaluate initializers when they're accessed
                self.properties[prop.name] = None
            else:
                self.properties[prop.name] = None

    def __repr__(self):
        return f"<{self.class_def.class_node.name} instance>"


class BoundMethod:
    """Represents a method bound to an instance"""

    def __init__(self, instance: ClassInstance, method: "MethodDecl", interpreter: "Interpreter"):
        self.instance = instance
        self.method = method
        self.interpreter = interpreter

    def __call__(self, *args):
        """Call the bound method"""
        return self.interpreter._call_method(self.instance, self.method, list(args))

    def __repr__(self):
        return f"<bound method {self.method.name}>"


class Environment:
    """Variable environment with scope support"""

    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}

    def define(self, name: str, value: Any):
        """Define a new variable in current scope"""
        self.variables[name] = value

    def get(self, name: str) -> Any:
        """Get variable value, searching up scope chain"""
        if name in self.variables:
            return self.variables[name]

        if self.parent:
            return self.parent.get(name)

        raise RuntimeError(f"Undefined variable: {name}")

    def set(self, name: str, value: Any):
        """Set variable value, searching up scope chain"""
        if name in self.variables:
            self.variables[name] = value
            return

        if self.parent:
            self.parent.set(name, value)
            return

        raise RuntimeError(f"Undefined variable: {name}")

    def exists(self, name: str) -> bool:
        """Check if variable exists in scope chain"""
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False


class Interpreter:
    """Interprets and executes Syntari AST"""

    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.functions: Dict[str, FuncDecl] = {}

        # Register built-in functions
        self._register_builtins()

    def _register_builtins(self):
        """Register built-in functions and modules"""
        # Built-ins are handled specially in visit_Call
        pass

    def interpret(self, program: Program) -> Any:
        """Interpret a program"""
        result = None
        for statement in program.statements:
            result = self._execute(statement)
        return result

    def _execute(self, node: Node) -> Any:
        """Execute a statement or declaration"""
        return node.accept(self)

    def _evaluate(self, node: Node) -> Any:
        """Evaluate an expression"""
        return node.accept(self)

    # === Visitor Methods ===

    # Program structure
    def visit_Program(self, node: Program) -> Any:
        """Visit program node"""
        result = None
        for statement in node.statements:
            result = self._execute(statement)
        return result

    def visit_Block(self, node: Block) -> Any:
        """Visit block - creates new scope"""
        # Create new environment for block scope
        previous = self.environment
        self.environment = Environment(previous)

        try:
            result = None
            for statement in node.statements:
                result = self._execute(statement)
            return result
        finally:
            # Restore previous environment
            self.environment = previous

    # Literals
    def visit_Number(self, node: Number) -> float:
        """Visit number literal"""
        return node.value

    def visit_String(self, node: String) -> str:
        """Visit string literal"""
        return node.value

    def visit_Boolean(self, node: Boolean) -> bool:
        """Visit boolean literal"""
        return node.value

    # Variables
    def visit_Var(self, node: Var) -> Any:
        """Visit variable reference"""
        return self.environment.get(node.name)

    def visit_VarDecl(self, node: VarDecl) -> None:
        """Visit variable declaration"""
        value = self._evaluate(node.value)
        self.environment.define(node.name, value)
        return None

    def visit_VarAssign(self, node: VarAssign) -> Any:
        """Visit variable assignment"""
        value = self._evaluate(node.value)
        self.environment.set(node.name, value)
        return value

    # Expressions
    def visit_BinOp(self, node: BinOp) -> Any:
        """Visit binary operation"""
        left = self._evaluate(node.left)
        right = self._evaluate(node.right)

        # Arithmetic
        if node.op == "+":
            return left + right
        elif node.op == "-":
            return left - right
        elif node.op == "*":
            return left * right
        elif node.op == "/":
            if right == 0:
                raise RuntimeError("Division by zero", node)
            return left / right
        elif node.op == "%":
            return left % right

        # Comparison
        elif node.op == "==":
            return left == right
        elif node.op == "!=":
            return left != right
        elif node.op == "<":
            return left < right
        elif node.op == "<=":
            return left <= right
        elif node.op == ">":
            return left > right
        elif node.op == ">=":
            return left >= right

        # Logical
        elif node.op == "&&":
            return left and right
        elif node.op == "||":
            return left or right

        else:
            raise RuntimeError(f"Unknown binary operator: {node.op}", node)

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        """Visit unary operation"""
        operand = self._evaluate(node.operand)

        if node.op == "-":
            return -operand
        elif node.op == "!":
            return not operand
        else:
            raise RuntimeError(f"Unknown unary operator: {node.op}", node)

    def visit_Call(self, node: Call) -> Any:
        """Visit function call"""
        # Evaluate arguments
        args = [self._evaluate(arg) for arg in node.args]

        # Handle string callees (simple function names)
        if isinstance(node.callee, str):
            # Built-in functions
            if node.callee == "print":
                system.print(*args)
                return None
            elif node.callee == "input":
                prompt = args[0] if args else ""
                return system.input(prompt)
            elif node.callee == "time":
                return system.time()
            elif node.callee == "exit":
                code = args[0] if args else 0
                system.exit(code)
            elif node.callee == "trace":
                system.trace()
                return None

            # AI module functions
            elif node.callee == "ai.query":
                prompt = args[0] if args else ""
                return ai.query(prompt)
            elif node.callee == "ai.eval":
                code = args[0] if args else ""
                return ai.eval(code)
            elif node.callee == "ai.suggest":
                return ai.suggest()

            # Networking module functions
            elif node.callee == "net.get":
                url = args[0] if args else ""
                return net.net_get(url)
            elif node.callee == "net.post":
                url = args[0] if args else ""
                data = args[1] if len(args) > 1 else {}
                return net.net_post(url, data)
            elif node.callee == "net.put":
                url = args[0] if args else ""
                data = args[1] if len(args) > 1 else {}
                return net.net_put(url, data)
            elif node.callee == "net.delete":
                url = args[0] if args else ""
                return net.net_delete(url)
            elif node.callee == "net.ws":
                url = args[0] if args else ""
                return net.net_ws(url)

            # User-defined functions
            elif node.callee in self.functions:
                func = self.functions[node.callee]
                return self._call_function(func, args)

            else:
                raise RuntimeError(f"Undefined function: {node.callee}", node)

        # Handle node callees (e.g., MemberAccess for method calls)
        else:
            # Check if it's a MemberAccess for module functions
            if isinstance(node.callee, MemberAccess):
                obj = node.callee.object
                member = node.callee.member

                # Handle module.function calls
                if isinstance(obj, Var):
                    module_name = obj.name

                    # AI module
                    if module_name == "ai":
                        if member == "query":
                            prompt = args[0] if args else ""
                            return ai.query(prompt)
                        elif member == "eval":
                            code = args[0] if args else ""
                            return ai.eval(code)
                        elif member == "suggest":
                            return ai.suggest()

                    # Networking module
                    elif module_name == "net":
                        if member == "get":
                            url = args[0] if args else ""
                            return net.net_get(url)
                        elif member == "post":
                            url = args[0] if args else ""
                            data = args[1] if len(args) > 1 else {}
                            return net.net_post(url, data)
                        elif member == "put":
                            url = args[0] if args else ""
                            data = args[1] if len(args) > 1 else {}
                            return net.net_put(url, data)
                        elif member == "delete":
                            url = args[0] if args else ""
                            return net.net_delete(url)
                        elif member == "ws":
                            url = args[0] if args else ""
                            return net.net_ws(url)

            # Try to evaluate the callee
            callee = self._evaluate(node.callee)

            # If it's a bound method, call it
            if isinstance(callee, BoundMethod):
                return callee(*args)

            raise RuntimeError(f"Cannot call non-callable value", node)

    def _call_function(self, func: FuncDecl, args: List[Any]) -> Any:
        """Call a user-defined function"""
        # Check argument count
        if len(args) != len(func.params):
            raise RuntimeError(
                f"Function {func.name} expects {len(func.params)} arguments, got {len(args)}"
            )

        # Create new environment for function
        previous = self.environment
        self.environment = Environment(self.globals)

        try:
            # Bind parameters
            for param, arg in zip(func.params, args):
                self.environment.define(param.name, arg)

            # Execute function body
            try:
                self._execute(func.body)
                return None  # Implicit return None
            except ReturnValue as ret:
                return ret.value
        finally:
            # Restore environment
            self.environment = previous

    # Statements
    def visit_Print(self, node: Print) -> None:
        """Visit print statement (deprecated - use print() function)"""
        value = self._evaluate(node.expr)
        system.print(value)
        return None

    def visit_ExprStmt(self, node: ExprStmt) -> Any:
        """Visit expression statement"""
        return self._evaluate(node.expr)

    def visit_IfStmt(self, node: IfStmt) -> Any:
        """Visit if statement"""
        condition = self._evaluate(node.condition)

        if self._is_truthy(condition):
            return self._execute(node.then_block)
        elif node.else_block:
            return self._execute(node.else_block)

        return None

    def visit_WhileStmt(self, node: WhileStmt) -> None:
        """Visit while loop"""
        while self._is_truthy(self._evaluate(node.condition)):
            self._execute(node.body)
        return None

    def visit_ReturnStmt(self, node: ReturnStmt) -> None:
        """Visit return statement"""
        value = None
        if node.value:
            value = self._evaluate(node.value)
        raise ReturnValue(value)

    def visit_MatchStmt(self, node: MatchStmt) -> Any:
        """Visit match statement"""
        expr_value = self._evaluate(node.expr)

        for pattern, case_block in node.cases:
            # Simple pattern matching - just value equality
            if pattern == "_" or pattern == expr_value:
                return self._execute(case_block)

        return None

    # Error Handling
    def visit_TryStmt(self, node: TryStmt) -> Any:
        """Visit try-catch-finally statement"""
        exception_caught = False
        result = None

        try:
            # Execute try block
            result = self._execute(node.try_block)
        except SyntariException as e:
            # Check each catch clause
            for catch_clause in node.catch_clauses:
                # Check if exception type matches (if specified)
                if (
                    catch_clause.exception_type is None
                    or catch_clause.exception_type == e.exception_type
                ):
                    # Bind exception to variable if specified
                    if catch_clause.exception_var:
                        # Create new scope for catch block
                        catch_env = Environment(self.environment)
                        catch_env.define(catch_clause.exception_var, e.value)
                        self.environment = catch_env

                    try:
                        result = self._execute(catch_clause.block)
                        exception_caught = True
                    finally:
                        # Restore environment
                        if catch_clause.exception_var:
                            self.environment = self.environment.parent

                    break  # Stop after first matching catch

            # Re-raise if not caught
            if not exception_caught:
                raise
        except RuntimeError as e:
            # Handle runtime errors in catch blocks
            for catch_clause in node.catch_clauses:
                if (
                    catch_clause.exception_type is None
                    or catch_clause.exception_type == "RuntimeError"
                ):
                    if catch_clause.exception_var:
                        catch_env = Environment(self.environment)
                        catch_env.define(catch_clause.exception_var, e.message)
                        self.environment = catch_env

                    try:
                        result = self._execute(catch_clause.block)
                        exception_caught = True
                    finally:
                        if catch_clause.exception_var:
                            self.environment = self.environment.parent

                    break

            if not exception_caught:
                raise
        finally:
            # Always execute finally block if present
            if node.finally_block:
                self._execute(node.finally_block)

        return result

    def visit_CatchClause(self, node: CatchClause) -> Any:
        """Visit catch clause - should not be visited directly"""
        raise RuntimeError("CatchClause should not be visited directly")

    def visit_ThrowStmt(self, node: ThrowStmt) -> None:
        """Visit throw statement"""
        value = self._evaluate(node.expr)
        # Determine exception type from value
        exception_type = "Exception"
        if isinstance(value, str):
            exception_type = "Exception"
        raise SyntariException(value, exception_type)

    # Functions
    def visit_FuncDecl(self, node: FuncDecl) -> None:
        """Visit function declaration"""
        self.functions[node.name] = node
        return None

    # Classes and OOP
    def visit_ClassDecl(self, node: "ClassDecl") -> None:
        """Visit class declaration"""
        # Store class definition
        self.environment.define(node.name, SyntariClass(node, self.environment))
        return None

    def visit_NewExpr(self, node: "NewExpr") -> Any:
        """Visit new expression - create instance"""
        # Get class definition
        try:
            class_def = self.environment.get(node.class_name)
        except RuntimeError:
            raise RuntimeError(f"Undefined class: {node.class_name}")

        if not isinstance(class_def, SyntariClass):
            raise RuntimeError(f"{node.class_name} is not a class")

        # Create instance
        instance = ClassInstance(class_def)

        # Initialize properties with their default values
        for prop in class_def.class_node.properties:
            if prop.initializer:
                # Evaluate the initializer expression
                value = self._evaluate(prop.initializer)
                instance.properties[prop.name] = value

        # Call constructor if it exists
        if class_def.class_node.constructor:
            # Evaluate constructor arguments
            args = [self._evaluate(arg) for arg in node.args]

            # Call constructor method
            constructor = class_def.class_node.constructor
            self._call_method(instance, constructor, args)

        return instance

    def visit_ThisExpr(self, node: "ThisExpr") -> Any:
        """Visit this expression"""
        # Get 'this' from environment
        try:
            return self.environment.get("this")
        except RuntimeError:
            raise RuntimeError("'this' used outside of class context")

    def visit_SuperExpr(self, node: "SuperExpr") -> Any:
        """Visit super expression"""
        # Get super class from environment
        try:
            return self.environment.get("super")
        except RuntimeError:
            raise RuntimeError("'super' used outside of class context")

    def visit_MemberAccess(self, node: "MemberAccess") -> Any:
        """Visit member access"""
        obj = self._evaluate(node.object)

        # Handle dictionaries (for networking responses, etc.)
        if isinstance(obj, dict):
            if node.member in obj:
                return obj[node.member]
            else:
                raise RuntimeError(f"Dictionary has no key: {node.member}")

        # Handle class instances
        if not isinstance(obj, ClassInstance):
            raise RuntimeError(f"Cannot access member '{node.member}' on non-object")

        # Get property value
        if node.member in obj.properties:
            return obj.properties[node.member]

        # Get method (bound to instance)
        for method in obj.class_def.class_node.methods:
            if method.name == node.member:
                # Return a bound method (closure that remembers 'this')
                return BoundMethod(obj, method, self)

        raise RuntimeError(f"Undefined property or method: {node.member}")

    def visit_MemberAssign(self, node: "MemberAssign") -> Any:
        """Visit member assignment"""
        obj = self._evaluate(node.object)

        if not isinstance(obj, ClassInstance):
            raise RuntimeError(f"Cannot assign to member '{node.member}' on non-object")

        value = self._evaluate(node.value)
        obj.properties[node.member] = value
        return value

    def _call_method(self, instance: "ClassInstance", method: "MethodDecl", args: List[Any]) -> Any:
        """Call a method on an instance"""
        # Create new environment for method
        method_env = Environment(instance.class_def.enclosing_env)

        # Bind 'this' to the instance
        method_env.define("this", instance)

        # Bind parameters
        for i, param in enumerate(method.params):
            if i < len(args):
                method_env.define(param.name, args[i])
            else:
                method_env.define(param.name, None)

        # Execute method body
        previous_env = self.environment
        self.environment = method_env

        try:
            self._execute(method.body)
            return None
        except ReturnValue as ret:
            return ret.value
        finally:
            self.environment = previous_env

    # Imports
    def visit_ImportDecl(self, node: ImportDecl) -> None:
        """Visit import declaration"""
        # For now, imports are no-ops since we pre-register modules
        # In v0.4+, this will actually load modules
        return None

    # Types (not evaluated at runtime in v0.3)
    def visit_TypeDecl(self, node: TypeDecl) -> None:
        """Visit type declaration (no-op for now)"""
        return None

    def visit_TraitDecl(self, node: TraitDecl) -> None:
        """Visit trait declaration (no-op for now)"""
        return None

    def visit_ImplDecl(self, node: ImplDecl) -> None:
        """Visit implementation declaration (no-op for now)"""
        return None

    # Helper methods
    def _is_truthy(self, value: Any) -> bool:
        """Determine if value is truthy"""
        if value is None or value is False:
            return False
        if value == 0 or value == "":
            return False
        return True


def interpret(program: Program) -> Any:
    """Convenience function to interpret a program"""
    interpreter = Interpreter()
    return interpreter.interpret(program)
