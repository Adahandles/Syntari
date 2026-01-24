"""
Syntari AST Nodes - Backwards compatibility wrapper
Import from src.interpreter.nodes for actual implementation
"""

from src.interpreter.nodes import (
    # Base
    Node,
    
    # Program structure
    Program,
    Block,
    
    # Literals
    Number,
    String,
    Boolean,
    
    # Variables
    Var,
    VarDecl,
    VarAssign,
    
    # Expressions
    BinOp,
    UnaryOp,
    Call,
    
    # Statements
    Print,
    ExprStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    MatchStmt,
    
    # Functions
    Param,
    FuncDecl,
    FuncSignature,
    
    # Types
    TypeRef,
    FieldDecl,
    TypeDecl,
    TraitDecl,
    ImplDecl,
    
    # Imports
    ImportDecl,
    
    # Helpers
    make_number,
    make_string,
    make_boolean,
    make_var,
    make_binop,
    make_call,
    make_block,
)

__all__ = [
    'Node', 'Program', 'Block',
    'Number', 'String', 'Boolean',
    'Var', 'VarDecl', 'VarAssign',
    'BinOp', 'UnaryOp', 'Call',
    'Print', 'ExprStmt', 'IfStmt', 'WhileStmt', 'ReturnStmt', 'MatchStmt',
    'Param', 'FuncDecl', 'FuncSignature',
    'TypeRef', 'FieldDecl', 'TypeDecl', 'TraitDecl', 'ImplDecl',
    'ImportDecl',
    'make_number', 'make_string', 'make_boolean', 'make_var', 'make_binop', 'make_call', 'make_block',
]

