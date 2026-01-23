"""
Syntari AST Nodes - Abstract Syntax Tree node definitions for v0.3
"""

from dataclasses import dataclass
from typing import List, Optional, Any


# Base class for all AST nodes
class Node:
    """Base class for all AST nodes with visitor pattern support"""
    
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern"""
        method_name = f'visit_{self.__class__.__name__}'
        method = getattr(visitor, method_name, None)
        if method:
            return method(self)
        raise NotImplementedError(f"No visitor method {method_name}")


# Program structure
@dataclass
class Program(Node):
    """Root node containing all top-level statements"""
    statements: List[Node]
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


@dataclass
class Block(Node):
    """Block of statements enclosed in braces"""
    statements: List[Node]
    
    def __repr__(self):
        return f"Block({len(self.statements)} statements)"


# Literals
@dataclass
class Number(Node):
    """Numeric literal (integer or float)"""
    value: float  # Can hold both int and float
    
    def __repr__(self):
        return f"Number({self.value})"


@dataclass
class String(Node):
    """String literal"""
    value: str
    
    def __repr__(self):
        return f"String({self.value!r})"


@dataclass
class Boolean(Node):
    """Boolean literal (true/false)"""
    value: bool
    
    def __repr__(self):
        return f"Boolean({self.value})"


# Variables
@dataclass
class Var(Node):
    """Variable reference"""
    name: str
    
    def __repr__(self):
        return f"Var({self.name!r})"


@dataclass
class VarDecl(Node):
    """Variable declaration (let/const)"""
    name: str
    type_ref: Optional[str]  # Type annotation
    value: Node  # Initial value
    is_const: bool  # True for const, False for let
    
    def __repr__(self):
        kind = "const" if self.is_const else "let"
        type_str = f": {self.type_ref}" if self.type_ref else ""
        return f"VarDecl({kind} {self.name}{type_str} = ...)"


@dataclass
class VarAssign(Node):
    """Variable assignment"""
    name: str
    value: Node
    
    def __repr__(self):
        return f"VarAssign({self.name} = ...)"


# Expressions
@dataclass
class BinOp(Node):
    """Binary operation (e.g., a + b, x == y)"""
    left: Node
    op: str  # Operator: +, -, *, /, %, ==, !=, <, <=, >, >=, &&, ||
    right: Node
    
    def __repr__(self):
        return f"BinOp(... {self.op} ...)"


@dataclass
class UnaryOp(Node):
    """Unary operation (e.g., -x, !flag)"""
    op: str  # Operator: -, !
    operand: Node
    
    def __repr__(self):
        return f"UnaryOp({self.op}...)"


@dataclass
class Call(Node):
    """Function/method call"""
    callee: str  # Function/method name
    args: List[Node]  # Arguments
    
    def __repr__(self):
        return f"Call({self.callee}, {len(self.args)} args)"


# Statements
@dataclass
class Print(Node):
    """Print statement (built-in)"""
    expr: Node
    
    def __repr__(self):
        return f"Print(...)"


@dataclass
class ExprStmt(Node):
    """Expression statement (expression used as statement)"""
    expr: Node
    
    def __repr__(self):
        return f"ExprStmt(...)"


@dataclass
class IfStmt(Node):
    """If statement with optional else"""
    condition: Node
    then_block: Block
    else_block: Optional[Block]
    
    def __repr__(self):
        has_else = " with else" if self.else_block else ""
        return f"IfStmt({has_else})"


@dataclass
class WhileStmt(Node):
    """While loop"""
    condition: Node
    body: Block
    
    def __repr__(self):
        return f"WhileStmt(...)"


@dataclass
class ReturnStmt(Node):
    """Return statement"""
    value: Optional[Node]  # None for bare return
    
    def __repr__(self):
        has_value = "with value" if self.value else "bare"
        return f"ReturnStmt({has_value})"


@dataclass
class MatchStmt(Node):
    """Match statement (pattern matching)"""
    expr: Node
    cases: List[tuple]  # List of (pattern, block) tuples
    
    def __repr__(self):
        return f"MatchStmt({len(self.cases)} cases)"


# Functions
@dataclass
class Param(Node):
    """Function parameter"""
    name: str
    type_ref: Optional[str]
    
    def __repr__(self):
        type_str = f": {self.type_ref}" if self.type_ref else ""
        return f"Param({self.name}{type_str})"


@dataclass
class FuncDecl(Node):
    """Function declaration"""
    name: str
    params: List[Param]
    return_type: Optional[str]
    body: Block
    
    def __repr__(self):
        ret_str = f" -> {self.return_type}" if self.return_type else ""
        return f"FuncDecl({self.name}({len(self.params)} params){ret_str})"


# Types
@dataclass
class TypeRef(Node):
    """Type reference (for type annotations)"""
    name: str
    generics: List[str]  # Generic type parameters
    
    def __repr__(self):
        gen_str = f"<{', '.join(self.generics)}>" if self.generics else ""
        return f"TypeRef({self.name}{gen_str})"


@dataclass
class FieldDecl(Node):
    """Field declaration in type definition"""
    name: str
    type_ref: str
    
    def __repr__(self):
        return f"FieldDecl({self.name}: {self.type_ref})"


@dataclass
class TypeDecl(Node):
    """Type declaration"""
    name: str
    fields: List[FieldDecl]
    
    def __repr__(self):
        return f"TypeDecl({self.name}, {len(self.fields)} fields)"


@dataclass
class TraitDecl(Node):
    """Trait declaration"""
    name: str
    type_param: Optional[str]  # Generic type parameter
    methods: List['FuncSignature']
    
    def __repr__(self):
        tp_str = f"<{self.type_param}>" if self.type_param else ""
        return f"TraitDecl({self.name}{tp_str}, {len(self.methods)} methods)"


@dataclass
class FuncSignature(Node):
    """Function signature (for trait definitions)"""
    name: str
    params: List[Param]
    return_type: Optional[str]
    
    def __repr__(self):
        ret_str = f" -> {self.return_type}" if self.return_type else ""
        return f"FuncSignature({self.name}({len(self.params)} params){ret_str})"


@dataclass
class ImplDecl(Node):
    """Implementation block (impl Trait for Type)"""
    trait_name: str
    type_param: Optional[str]
    methods: List[FuncDecl]
    
    def __repr__(self):
        tp_str = f"<{self.type_param}>" if self.type_param else ""
        return f"ImplDecl({self.trait_name}{tp_str}, {len(self.methods)} methods)"


# Imports
@dataclass
class ImportDecl(Node):
    """Import declaration (use statement)"""
    path: List[str]  # e.g., ['core', 'system'] for 'use core.system'
    
    def __repr__(self):
        path_str = '.'.join(self.path)
        return f"ImportDecl({path_str})"


# Helper functions for creating nodes
def make_number(value: float) -> Number:
    """Create a Number node"""
    return Number(value)


def make_string(value: str) -> String:
    """Create a String node"""
    return String(value)


def make_boolean(value: bool) -> Boolean:
    """Create a Boolean node"""
    return Boolean(value)


def make_var(name: str) -> Var:
    """Create a Var node"""
    return Var(name)


def make_binop(left: Node, op: str, right: Node) -> BinOp:
    """Create a BinOp node"""
    return BinOp(left, op, right)


def make_call(callee: str, args: List[Node]) -> Call:
    """Create a Call node"""
    return Call(callee, args)


def make_block(statements: List[Node]) -> Block:
    """Create a Block node"""
    return Block(statements)
