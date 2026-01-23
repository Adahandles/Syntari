"""
Tests for Syntari AST Nodes
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.interpreter.nodes import *


class TestLiterals:
    """Test literal node creation"""
    
    def test_number_node(self):
        """Test Number node"""
        node = Number(42)
        assert node.value == 42
        assert isinstance(node, Node)
        assert "Number(42)" in repr(node)
    
    def test_float_number(self):
        """Test Number node with float"""
        node = Number(3.14)
        assert node.value == 3.14
    
    def test_string_node(self):
        """Test String node"""
        node = String("hello")
        assert node.value == "hello"
        assert isinstance(node, Node)
    
    def test_boolean_node(self):
        """Test Boolean node"""
        node_true = Boolean(True)
        node_false = Boolean(False)
        assert node_true.value is True
        assert node_false.value is False


class TestVariables:
    """Test variable-related nodes"""
    
    def test_var_node(self):
        """Test Var (variable reference) node"""
        node = Var("x")
        assert node.name == "x"
    
    def test_var_decl_let(self):
        """Test variable declaration with let"""
        node = VarDecl("x", None, Number(42), is_const=False)
        assert node.name == "x"
        assert node.type_ref is None
        assert isinstance(node.value, Number)
        assert node.is_const is False
    
    def test_var_decl_const(self):
        """Test variable declaration with const"""
        node = VarDecl("PI", "float", Number(3.14), is_const=True)
        assert node.name == "PI"
        assert node.type_ref == "float"
        assert node.is_const is True
    
    def test_var_assign(self):
        """Test variable assignment"""
        node = VarAssign("x", Number(10))
        assert node.name == "x"
        assert isinstance(node.value, Number)


class TestExpressions:
    """Test expression nodes"""
    
    def test_binop_addition(self):
        """Test binary operation - addition"""
        left = Number(2)
        right = Number(3)
        node = BinOp(left, "+", right)
        
        assert node.op == "+"
        assert isinstance(node.left, Number)
        assert isinstance(node.right, Number)
    
    def test_binop_comparison(self):
        """Test binary operation - comparison"""
        left = Var("x")
        right = Number(10)
        node = BinOp(left, ">", right)
        
        assert node.op == ">"
        assert isinstance(node.left, Var)
        assert isinstance(node.right, Number)
    
    def test_unary_op_negation(self):
        """Test unary operation - negation"""
        node = UnaryOp("-", Number(5))
        assert node.op == "-"
        assert isinstance(node.operand, Number)
    
    def test_unary_op_not(self):
        """Test unary operation - logical not"""
        node = UnaryOp("!", Boolean(True))
        assert node.op == "!"
    
    def test_call_no_args(self):
        """Test function call with no arguments"""
        node = Call("foo", [])
        assert node.callee == "foo"
        assert len(node.args) == 0
    
    def test_call_with_args(self):
        """Test function call with arguments"""
        args = [Number(1), String("test"), Var("x")]
        node = Call("print", args)
        assert node.callee == "print"
        assert len(node.args) == 3


class TestStatements:
    """Test statement nodes"""
    
    def test_print_stmt(self):
        """Test Print statement"""
        node = Print(String("hello"))
        assert isinstance(node.expr, String)
    
    def test_expr_stmt(self):
        """Test expression statement"""
        call = Call("foo", [])
        node = ExprStmt(call)
        assert isinstance(node.expr, Call)
    
    def test_if_stmt_no_else(self):
        """Test if statement without else"""
        condition = BinOp(Var("x"), ">", Number(5))
        then_block = Block([Print(String("big"))])
        node = IfStmt(condition, then_block, None)
        
        assert isinstance(node.condition, BinOp)
        assert isinstance(node.then_block, Block)
        assert node.else_block is None
    
    def test_if_stmt_with_else(self):
        """Test if statement with else"""
        condition = Boolean(True)
        then_block = Block([Print(String("yes"))])
        else_block = Block([Print(String("no"))])
        node = IfStmt(condition, then_block, else_block)
        
        assert node.else_block is not None
        assert isinstance(node.else_block, Block)
    
    def test_while_stmt(self):
        """Test while loop"""
        condition = BinOp(Var("i"), "<", Number(10))
        body = Block([Print(Var("i"))])
        node = WhileStmt(condition, body)
        
        assert isinstance(node.condition, BinOp)
        assert isinstance(node.body, Block)
    
    def test_return_stmt_with_value(self):
        """Test return statement with value"""
        node = ReturnStmt(Number(42))
        assert isinstance(node.value, Number)
    
    def test_return_stmt_bare(self):
        """Test bare return statement"""
        node = ReturnStmt(None)
        assert node.value is None
    
    def test_match_stmt(self):
        """Test match statement"""
        expr = Var("x")
        cases = [
            (Number(1), Block([Print(String("one"))])),
            (Number(2), Block([Print(String("two"))])),
        ]
        node = MatchStmt(expr, cases)
        
        assert isinstance(node.expr, Var)
        assert len(node.cases) == 2


class TestFunctions:
    """Test function-related nodes"""
    
    def test_param_no_type(self):
        """Test parameter without type annotation"""
        node = Param("x", None)
        assert node.name == "x"
        assert node.type_ref is None
    
    def test_param_with_type(self):
        """Test parameter with type annotation"""
        node = Param("x", "int")
        assert node.name == "x"
        assert node.type_ref == "int"
    
    def test_func_decl_no_params(self):
        """Test function declaration without parameters"""
        body = Block([Print(String("hello"))])
        node = FuncDecl("greet", [], None, body)
        
        assert node.name == "greet"
        assert len(node.params) == 0
        assert node.return_type is None
        assert isinstance(node.body, Block)
    
    def test_func_decl_with_params(self):
        """Test function declaration with parameters"""
        params = [Param("a", "int"), Param("b", "int")]
        body = Block([ReturnStmt(BinOp(Var("a"), "+", Var("b")))])
        node = FuncDecl("add", params, "int", body)
        
        assert node.name == "add"
        assert len(node.params) == 2
        assert node.return_type == "int"
    
    def test_func_signature(self):
        """Test function signature (for traits)"""
        params = [Param("x", "int")]
        node = FuncSignature("foo", params, "bool")
        
        assert node.name == "foo"
        assert len(node.params) == 1
        assert node.return_type == "bool"


class TestTypes:
    """Test type-related nodes"""
    
    def test_type_ref_simple(self):
        """Test simple type reference"""
        node = TypeRef("int", [])
        assert node.name == "int"
        assert len(node.generics) == 0
    
    def test_type_ref_generic(self):
        """Test generic type reference"""
        node = TypeRef("List", ["int"])
        assert node.name == "List"
        assert node.generics == ["int"]
    
    def test_field_decl(self):
        """Test field declaration"""
        node = FieldDecl("name", "string")
        assert node.name == "name"
        assert node.type_ref == "string"
    
    def test_type_decl(self):
        """Test type declaration"""
        fields = [
            FieldDecl("x", "int"),
            FieldDecl("y", "int"),
        ]
        node = TypeDecl("Point", fields)
        
        assert node.name == "Point"
        assert len(node.fields) == 2
    
    def test_trait_decl(self):
        """Test trait declaration"""
        methods = [
            FuncSignature("foo", [], None),
            FuncSignature("bar", [Param("x", "int")], "bool"),
        ]
        node = TraitDecl("MyTrait", None, methods)
        
        assert node.name == "MyTrait"
        assert node.type_param is None
        assert len(node.methods) == 2
    
    def test_trait_decl_with_type_param(self):
        """Test trait declaration with type parameter"""
        node = TraitDecl("Container", "T", [])
        assert node.type_param == "T"
    
    def test_impl_decl(self):
        """Test implementation block"""
        methods = [
            FuncDecl("foo", [], None, Block([])),
        ]
        node = ImplDecl("MyTrait", None, methods)
        
        assert node.trait_name == "MyTrait"
        assert len(node.methods) == 1


class TestStructure:
    """Test structural nodes"""
    
    def test_block_empty(self):
        """Test empty block"""
        node = Block([])
        assert len(node.statements) == 0
    
    def test_block_with_statements(self):
        """Test block with statements"""
        stmts = [
            VarDecl("x", None, Number(1), False),
            Print(Var("x")),
        ]
        node = Block(stmts)
        
        assert len(node.statements) == 2
        assert isinstance(node.statements[0], VarDecl)
        assert isinstance(node.statements[1], Print)
    
    def test_program(self):
        """Test program node"""
        stmts = [
            ImportDecl(["core", "system"]),
            FuncDecl("main", [], None, Block([])),
        ]
        node = Program(stmts)
        
        assert len(node.statements) == 2
        assert isinstance(node.statements[0], ImportDecl)
        assert isinstance(node.statements[1], FuncDecl)


class TestImports:
    """Test import-related nodes"""
    
    def test_import_decl_simple(self):
        """Test simple import"""
        node = ImportDecl(["core"])
        assert node.path == ["core"]
    
    def test_import_decl_nested(self):
        """Test nested import"""
        node = ImportDecl(["core", "system"])
        assert node.path == ["core", "system"]


class TestHelpers:
    """Test helper functions"""
    
    def test_make_number(self):
        """Test make_number helper"""
        node = make_number(42)
        assert isinstance(node, Number)
        assert node.value == 42
    
    def test_make_string(self):
        """Test make_string helper"""
        node = make_string("test")
        assert isinstance(node, String)
        assert node.value == "test"
    
    def test_make_boolean(self):
        """Test make_boolean helper"""
        node = make_boolean(True)
        assert isinstance(node, Boolean)
        assert node.value is True
    
    def test_make_var(self):
        """Test make_var helper"""
        node = make_var("x")
        assert isinstance(node, Var)
        assert node.name == "x"
    
    def test_make_binop(self):
        """Test make_binop helper"""
        left = Number(2)
        right = Number(3)
        node = make_binop(left, "+", right)
        
        assert isinstance(node, BinOp)
        assert node.op == "+"
    
    def test_make_call(self):
        """Test make_call helper"""
        args = [Number(1), Number(2)]
        node = make_call("add", args)
        
        assert isinstance(node, Call)
        assert node.callee == "add"
        assert len(node.args) == 2
    
    def test_make_block(self):
        """Test make_block helper"""
        stmts = [Print(String("hi"))]
        node = make_block(stmts)
        
        assert isinstance(node, Block)
        assert len(node.statements) == 1


class TestVisitorPattern:
    """Test visitor pattern support"""
    
    def test_visitor_method_called(self):
        """Test that accept() calls the correct visitor method"""
        
        class TestVisitor:
            def visit_Number(self, node):
                return f"visited {node.value}"
        
        node = Number(42)
        visitor = TestVisitor()
        result = node.accept(visitor)
        
        assert result == "visited 42"
    
    def test_visitor_not_implemented(self):
        """Test that missing visitor method raises error"""
        
        class TestVisitor:
            pass
        
        node = Number(42)
        visitor = TestVisitor()
        
        with pytest.raises(NotImplementedError):
            node.accept(visitor)


class TestComplexTrees:
    """Test building complex AST structures"""
    
    def test_arithmetic_tree(self):
        """Test building arithmetic expression tree: 2 + 3 * 4"""
        # Should be: 2 + (3 * 4)
        mul = BinOp(Number(3), "*", Number(4))
        add = BinOp(Number(2), "+", mul)
        
        assert isinstance(add, BinOp)
        assert add.op == "+"
        assert isinstance(add.right, BinOp)
        assert add.right.op == "*"
    
    def test_function_with_body(self):
        """Test complete function declaration"""
        # fn add(a: int, b: int) -> int { return a + b }
        params = [Param("a", "int"), Param("b", "int")]
        return_expr = BinOp(Var("a"), "+", Var("b"))
        body = Block([ReturnStmt(return_expr)])
        func = FuncDecl("add", params, "int", body)
        
        assert func.name == "add"
        assert len(func.params) == 2
        assert len(func.body.statements) == 1
        assert isinstance(func.body.statements[0], ReturnStmt)
    
    def test_if_else_tree(self):
        """Test if-else statement tree"""
        # if (x > 5) { print("big") } else { print("small") }
        condition = BinOp(Var("x"), ">", Number(5))
        then_block = Block([Print(String("big"))])
        else_block = Block([Print(String("small"))])
        if_stmt = IfStmt(condition, then_block, else_block)
        
        assert isinstance(if_stmt.condition, BinOp)
        assert len(if_stmt.then_block.statements) == 1
        assert len(if_stmt.else_block.statements) == 1
