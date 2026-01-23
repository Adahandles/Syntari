"""
Syntari Interpreter - Executes Abstract Syntax Tree for v0.3
"""

from typing import Any, Dict, List, Optional
from src.interpreter.nodes import *
from src.core import system, ai


class RuntimeError(Exception):
    """Raised when interpreter encounters a runtime error"""
    def __init__(self, message: str, node: Optional[Node] = None):
        self.message = message
        self.node = node
        super().__init__(f"Runtime error: {message}")


class ReturnValue(Exception):
    """Exception used to implement return statements"""
    def __init__(self, value: Any):
        self.value = value


class Environment:
    """Variable environment with scope support"""
    
    def __init__(self, parent: Optional['Environment'] = None):
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
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            if right == 0:
                raise RuntimeError("Division by zero", node)
            return left / right
        elif node.op == '%':
            return left % right
        
        # Comparison
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            return left < right
        elif node.op == '<=':
            return left <= right
        elif node.op == '>':
            return left > right
        elif node.op == '>=':
            return left >= right
        
        # Logical
        elif node.op == '&&':
            return left and right
        elif node.op == '||':
            return left or right
        
        else:
            raise RuntimeError(f"Unknown binary operator: {node.op}", node)
    
    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        """Visit unary operation"""
        operand = self._evaluate(node.operand)
        
        if node.op == '-':
            return -operand
        elif node.op == '!':
            return not operand
        else:
            raise RuntimeError(f"Unknown unary operator: {node.op}", node)
    
    def visit_Call(self, node: Call) -> Any:
        """Visit function call"""
        # Evaluate arguments
        args = [self._evaluate(arg) for arg in node.args]
        
        # Built-in functions
        if node.callee == 'print':
            system.print(*args)
            return None
        elif node.callee == 'input':
            prompt = args[0] if args else ''
            return system.input(prompt)
        elif node.callee == 'time':
            return system.time()
        elif node.callee == 'exit':
            code = args[0] if args else 0
            system.exit(code)
        elif node.callee == 'trace':
            system.trace()
            return None
        
        # AI module functions
        elif node.callee == 'ai.query':
            prompt = args[0] if args else ''
            return ai.query(prompt)
        elif node.callee == 'ai.eval':
            code = args[0] if args else ''
            return ai.eval(code)
        elif node.callee == 'ai.suggest':
            return ai.suggest()
        
        # User-defined functions
        elif node.callee in self.functions:
            func = self.functions[node.callee]
            return self._call_function(func, args)
        
        else:
            raise RuntimeError(f"Undefined function: {node.callee}", node)
    
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
            if pattern == '_' or pattern == expr_value:
                return self._execute(case_block)
        
        return None
    
    # Functions
    def visit_FuncDecl(self, node: FuncDecl) -> None:
        """Visit function declaration"""
        self.functions[node.name] = node
        return None
    
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
        if value == 0 or value == '':
            return False
        return True


def interpret(program: Program) -> Any:
    """Convenience function to interpret a program"""
    interpreter = Interpreter()
    return interpreter.interpret(program)
