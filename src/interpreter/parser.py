"""
Syntari Parser - Builds Abstract Syntax Tree from token stream for v0.3
"""

from typing import List, Optional
from src.interpreter.lexer import Token, TokenType
from src.interpreter.nodes import *


class ParseError(Exception):
    """Raised when parser encounters an error"""

    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at {token.line}:{token.column}: {message}")


class Parser:
    """Recursive descent parser for Syntari v0.3"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # === Core Parser Methods ===

    def parse(self) -> Program:
        """Parse entire program"""
        statements = []
        while not self._is_at_end():
            stmt = self._parse_top_level()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def _parse_top_level(self) -> Optional[Node]:
        """Parse top-level declaration or statement"""
        # Skip semicolons
        if self._match(TokenType.SEMICOLON):
            return None

        # Import declarations
        if self._check(TokenType.USE):
            return self._parse_import()

        # Type declarations
        if self._check(TokenType.TYPE):
            return self._parse_type_decl()

        # Trait declarations
        if self._check(TokenType.TRAIT):
            return self._parse_trait_decl()

        # Implementation blocks
        if self._check(TokenType.IMPL):
            return self._parse_impl_decl()

        # Class declarations
        if self._check(TokenType.CLASS):
            return self._parse_class_decl()

        # Function declarations
        if self._check(TokenType.FN):
            return self._parse_func_decl()

        # Regular statements
        return self._parse_statement()

    def _parse_statement(self) -> Node:
        """Parse statement"""
        # Variable declarations
        if self._match(TokenType.LET, TokenType.CONST):
            return self._parse_var_decl()

        # Control flow
        if self._match(TokenType.IF):
            return self._parse_if_stmt()

        if self._match(TokenType.WHILE):
            return self._parse_while_stmt()

        if self._match(TokenType.MATCH):
            return self._parse_match_stmt()

        if self._match(TokenType.RETURN):
            return self._parse_return_stmt()

        # Error handling
        if self._match(TokenType.TRY):
            return self._parse_try_stmt()

        if self._match(TokenType.THROW):
            return self._parse_throw_stmt()

        # Expression statement
        return self._parse_expr_stmt()

    # === Declarations ===

    def _parse_import(self) -> ImportDecl:
        """Parse import declaration: use core.system"""
        self._consume(TokenType.USE, "Expected 'use'")

        path = []
        path.append(self._consume(TokenType.IDENTIFIER, "Expected module name").value)

        while self._match(TokenType.DOT):
            path.append(self._consume(TokenType.IDENTIFIER, "Expected module name").value)

        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return ImportDecl(path)

    def _parse_type_decl(self) -> TypeDecl:
        """Parse type declaration: type Point { x: int, y: int }"""
        self._consume(TokenType.TYPE, "Expected 'type'")
        name = self._consume(TokenType.IDENTIFIER, "Expected type name").value

        self._consume(TokenType.LBRACE, "Expected '{'")

        fields = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            field_name = self._consume(TokenType.IDENTIFIER, "Expected field name").value
            self._consume(TokenType.COLON, "Expected ':'")
            field_type = self._consume(TokenType.IDENTIFIER, "Expected type").value

            fields.append(FieldDecl(field_name, field_type))

            if not self._match(TokenType.COMMA):
                break

        self._consume(TokenType.RBRACE, "Expected '}'")
        return TypeDecl(name, fields)

    def _parse_trait_decl(self) -> TraitDecl:
        """Parse trait declaration: trait Printable { fn print() }"""
        self._consume(TokenType.TRAIT, "Expected 'trait'")
        name = self._consume(TokenType.IDENTIFIER, "Expected trait name").value

        # Optional type parameter
        type_param = None
        if self._match(TokenType.LT):
            type_param = self._consume(TokenType.IDENTIFIER, "Expected type parameter").value
            self._consume(TokenType.GT, "Expected '>'")

        self._consume(TokenType.LBRACE, "Expected '{'")

        methods = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            self._consume(TokenType.FN, "Expected 'fn'")
            method = self._parse_func_signature()
            methods.append(method)

        self._consume(TokenType.RBRACE, "Expected '}'")
        return TraitDecl(name, type_param, methods)

    def _parse_func_signature(self) -> FuncSignature:
        """Parse function signature: fn foo(x: int) -> bool"""
        name = self._consume(TokenType.IDENTIFIER, "Expected function name").value

        self._consume(TokenType.LPAREN, "Expected '('")
        params = self._parse_param_list()
        self._consume(TokenType.RPAREN, "Expected ')'")

        # Optional return type
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._consume(TokenType.IDENTIFIER, "Expected return type").value

        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return FuncSignature(name, params, return_type)

    def _parse_impl_decl(self) -> ImplDecl:
        """Parse implementation block: impl MyTrait { ... }"""
        self._consume(TokenType.IMPL, "Expected 'impl'")
        trait_name = self._consume(TokenType.IDENTIFIER, "Expected trait name").value

        # Optional type parameter
        type_param = None
        if self._match(TokenType.LT):
            type_param = self._consume(TokenType.IDENTIFIER, "Expected type parameter").value
            self._consume(TokenType.GT, "Expected '>'")

        self._consume(TokenType.LBRACE, "Expected '{'")

        methods = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._check(TokenType.FN):
                methods.append(self._parse_func_decl())
            else:
                break

        self._consume(TokenType.RBRACE, "Expected '}'")
        return ImplDecl(trait_name, type_param, methods)

    def _parse_func_decl(self) -> FuncDecl:
        """Parse function declaration: fn add(a: int, b: int) -> int { ... }"""
        self._consume(TokenType.FN, "Expected 'fn'")
        name = self._consume(TokenType.IDENTIFIER, "Expected function name").value

        self._consume(TokenType.LPAREN, "Expected '('")
        params = self._parse_param_list()
        self._consume(TokenType.RPAREN, "Expected ')'")

        # Optional return type
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._consume(TokenType.IDENTIFIER, "Expected return type").value

        body = self._parse_block()
        return FuncDecl(name, params, return_type, body)

    def _parse_class_decl(self) -> "ClassDecl":
        """Parse class declaration: class MyClass extends BaseClass { ... }"""
        self._consume(TokenType.CLASS, "Expected 'class'")
        name = self._consume(TokenType.IDENTIFIER, "Expected class name").value

        # Optional extends clause
        super_class = None
        if self._match(TokenType.EXTENDS):
            super_class = self._consume(TokenType.IDENTIFIER, "Expected parent class name").value

        self._consume(TokenType.LBRACE, "Expected '{' after class declaration")

        methods = []
        properties = []
        constructor = None

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            is_static = False
            if self._match(TokenType.STATIC):
                is_static = True

            # Check if it's a method (has fn keyword) or property
            if self._check(TokenType.FN):
                method = self._parse_method_decl(is_static)
                if method.name == "constructor":
                    constructor = method
                else:
                    methods.append(method)
            elif self._check(TokenType.IDENTIFIER):
                prop = self._parse_property_decl(is_static)
                properties.append(prop)
            else:
                raise ParseError("Expected method or property declaration", self._peek())

        self._consume(TokenType.RBRACE, "Expected '}' after class body")
        return ClassDecl(name, super_class, methods, properties, constructor)

    def _parse_method_decl(self, is_static: bool = False) -> "MethodDecl":
        """Parse method declaration within a class"""
        self._consume(TokenType.FN, "Expected 'fn'")
        name = self._consume(TokenType.IDENTIFIER, "Expected method name").value

        self._consume(TokenType.LPAREN, "Expected '('")
        params = self._parse_param_list()
        self._consume(TokenType.RPAREN, "Expected ')'")

        # Optional return type
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._consume(TokenType.IDENTIFIER, "Expected return type").value

        body = self._parse_block()
        return MethodDecl(name, params, return_type, body, is_static)

    def _parse_property_decl(self, is_static: bool = False) -> "PropertyDecl":
        """Parse property declaration within a class"""
        name = self._consume(TokenType.IDENTIFIER, "Expected property name").value

        # Optional type annotation
        type_ref = None
        if self._match(TokenType.COLON):
            type_ref = self._consume(TokenType.IDENTIFIER, "Expected type").value

        # Optional initializer
        initializer = None
        if self._match(TokenType.EQ):
            initializer = self._parse_expression()

        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return PropertyDecl(name, type_ref, initializer, is_static)

    def _parse_param_list(self) -> List[Param]:
        """Parse parameter list: a: int, b: int"""
        params = []

        if self._check(TokenType.RPAREN):
            return params

        # First parameter
        param_name = self._consume(TokenType.IDENTIFIER, "Expected parameter name").value
        param_type = None
        if self._match(TokenType.COLON):
            param_type = self._consume(TokenType.IDENTIFIER, "Expected parameter type").value
        params.append(Param(param_name, param_type))

        # Additional parameters
        while self._match(TokenType.COMMA):
            param_name = self._consume(TokenType.IDENTIFIER, "Expected parameter name").value
            param_type = None
            if self._match(TokenType.COLON):
                param_type = self._consume(TokenType.IDENTIFIER, "Expected parameter type").value
            params.append(Param(param_name, param_type))

        return params

    def _parse_var_decl(self) -> VarDecl:
        """Parse variable declaration: let x = 5 or const PI = 3.14"""
        is_const = self._previous().type == TokenType.CONST

        name = self._consume(TokenType.IDENTIFIER, "Expected variable name").value

        # Optional type annotation
        type_ref = None
        if self._match(TokenType.COLON):
            type_ref = self._consume(TokenType.IDENTIFIER, "Expected type").value

        # Initializer
        self._consume(TokenType.EQ, "Expected '='")
        value = self._parse_expression()

        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return VarDecl(name, type_ref, value, is_const)

    # === Statements ===

    def _parse_block(self) -> Block:
        """Parse block: { ... }"""
        self._consume(TokenType.LBRACE, "Expected '{'")

        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._consume(TokenType.RBRACE, "Expected '}'")
        return Block(statements)

    def _parse_if_stmt(self) -> IfStmt:
        """Parse if statement: if (condition) { ... } else { ... }"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after condition")

        then_block = self._parse_block()

        else_block = None
        if self._match(TokenType.ELSE):
            if self._check(TokenType.IF):
                # else if -> convert to nested if
                else_if = self._parse_if_stmt()
                else_block = Block([else_if])
            else:
                else_block = self._parse_block()

        return IfStmt(condition, then_block, else_block)

    def _parse_while_stmt(self) -> WhileStmt:
        """Parse while loop: while (condition) { ... }"""
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after condition")

        body = self._parse_block()
        return WhileStmt(condition, body)

    def _parse_match_stmt(self) -> MatchStmt:
        """Parse match statement: match expr { pattern -> expr, ... }"""
        expr = self._parse_expression()

        self._consume(TokenType.LBRACE, "Expected '{' after match expression")

        cases = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            # Parse pattern (simplified - just numbers and identifiers for now)
            if self._check(TokenType.INTEGER):
                pattern = self._advance().value
            elif self._check(TokenType.IDENTIFIER):
                pattern = self._advance().value
            else:
                raise ParseError("Expected pattern", self._peek())

            self._consume(TokenType.ARROW, "Expected '->' after pattern")

            # Parse expression or block
            if self._check(TokenType.LBRACE):
                case_block = self._parse_block()
            else:
                case_expr = self._parse_expression()
                case_block = Block([ExprStmt(case_expr)])

            cases.append((pattern, case_block))

            if not self._match(TokenType.COMMA):
                break

        self._consume(TokenType.RBRACE, "Expected '}'")
        return MatchStmt(expr, cases)

    def _parse_return_stmt(self) -> ReturnStmt:
        """Parse return statement: return expr"""
        value = None
        if (
            not self._check(TokenType.SEMICOLON)
            and not self._check(TokenType.RBRACE)
            and not self._is_at_end()
        ):
            value = self._parse_expression()

        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return ReturnStmt(value)

    def _parse_try_stmt(self) -> "TryStmt":
        """Parse try-catch-finally statement"""
        # Parse try block
        try_block = self._parse_block()

        # Parse catch clauses
        catch_clauses = []
        while self._match(TokenType.CATCH):
            exception_var = None
            exception_type = None

            # Parse optional (var: Type) or (var) or just {}
            if self._match(TokenType.LPAREN):
                if self._check(TokenType.IDENTIFIER):
                    exception_var = self._advance().value

                    # Check for type annotation
                    if self._match(TokenType.COLON):
                        if self._check(TokenType.IDENTIFIER):
                            exception_type = self._advance().value

                self._consume(TokenType.RPAREN, "Expected ')' after catch parameter")

            # Parse catch block
            catch_block = self._parse_block()

            catch_clauses.append(CatchClause(exception_var, exception_type, catch_block))

        # Parse optional finally block
        finally_block = None
        if self._match(TokenType.FINALLY):
            finally_block = self._parse_block()

        # Must have at least one catch or finally
        if not catch_clauses and not finally_block:
            raise ParseError(
                "Try statement must have at least one catch or finally block", self._previous()
            )

        return TryStmt(try_block, catch_clauses, finally_block)

    def _parse_throw_stmt(self) -> "ThrowStmt":
        """Parse throw statement: throw expr"""
        expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return ThrowStmt(expr)

    def _parse_expr_stmt(self) -> ExprStmt:
        """Parse expression statement"""
        expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return ExprStmt(expr)

    # === Expressions (Precedence Climbing) ===

    def _parse_expression(self) -> Node:
        """Parse expression (lowest precedence)"""
        return self._parse_assignment()

    def _parse_assignment(self) -> Node:
        """Parse assignment: x = expr or obj.member = expr"""
        expr = self._parse_logical_or()

        if self._match(TokenType.EQ):
            value = self._parse_assignment()

            if isinstance(expr, Var):
                return VarAssign(expr.name, value)
            elif isinstance(expr, MemberAccess):
                return MemberAssign(expr.object, expr.member, value)
            else:
                raise ParseError("Invalid assignment target", self._previous())

        return expr

    def _parse_logical_or(self) -> Node:
        """Parse logical OR: expr || expr"""
        left = self._parse_logical_and()

        while self._match(TokenType.OR_OR):
            op = self._previous().value
            right = self._parse_logical_and()
            left = BinOp(left, op, right)

        return left

    def _parse_logical_and(self) -> Node:
        """Parse logical AND: expr && expr"""
        left = self._parse_equality()

        while self._match(TokenType.AND_AND):
            op = self._previous().value
            right = self._parse_equality()
            left = BinOp(left, op, right)

        return left

    def _parse_equality(self) -> Node:
        """Parse equality: expr == expr, expr != expr"""
        left = self._parse_comparison()

        while self._match(TokenType.EQ_EQ, TokenType.NOT_EQ):
            op = self._previous().value
            right = self._parse_comparison()
            left = BinOp(left, op, right)

        return left

    def _parse_comparison(self) -> Node:
        """Parse comparison: expr < expr, expr <= expr, etc."""
        left = self._parse_term()

        while self._match(TokenType.LT, TokenType.LT_EQ, TokenType.GT, TokenType.GT_EQ):
            op = self._previous().value
            right = self._parse_term()
            left = BinOp(left, op, right)

        return left

    def _parse_term(self) -> Node:
        """Parse addition/subtraction: expr + expr, expr - expr"""
        left = self._parse_factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().value
            right = self._parse_factor()
            left = BinOp(left, op, right)

        return left

    def _parse_factor(self) -> Node:
        """Parse multiplication/division: expr * expr, expr / expr, expr % expr"""
        left = self._parse_unary()

        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous().value
            right = self._parse_unary()
            left = BinOp(left, op, right)

        return left

    def _parse_unary(self) -> Node:
        """Parse unary: -expr, !expr"""
        if self._match(TokenType.MINUS, TokenType.BANG):
            op = self._previous().value
            operand = self._parse_unary()
            return UnaryOp(op, operand)

        return self._parse_call()

    def _parse_call(self) -> Node:
        """Parse function call and member access: func(args) or obj.member or obj.method(args)"""
        expr = self._parse_primary()

        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                # Member access or method call
                member_name = self._consume(
                    TokenType.IDENTIFIER, "Expected member name after '.'"
                ).value

                if self._match(TokenType.LPAREN):
                    # Method call: obj.method(args)
                    args = self._parse_arg_list()
                    self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                    # Create member access for the method, then call it
                    member_expr = MemberAccess(expr, member_name)
                    expr = Call(member_expr, args)
                else:
                    # Property access: obj.property
                    expr = MemberAccess(expr, member_name)
            else:
                break

        return expr

    def _finish_call(self, callee: Node) -> Call:
        """Finish parsing function call"""
        # Allow calling identifiers, member access expressions, etc.
        args = self._parse_arg_list()
        self._consume(TokenType.RPAREN, "Expected ')' after arguments")

        # For simple identifiers, extract the name
        if isinstance(callee, Var):
            return Call(callee.name, args)
        # For member access or other expressions, pass the node directly
        return Call(callee, args)

    def _parse_arg_list(self) -> List[Node]:
        """Parse argument list"""
        args = []

        if self._check(TokenType.RPAREN):
            return args

        args.append(self._parse_expression())

        while self._match(TokenType.COMMA):
            args.append(self._parse_expression())

        return args

    def _parse_primary(self) -> Node:
        """Parse primary expression: literals, identifiers, grouping"""
        # Boolean literals
        if self._match(TokenType.TRUE):
            return Boolean(True)

        if self._match(TokenType.FALSE):
            return Boolean(False)

        # Numeric literals
        if self._match(TokenType.INTEGER, TokenType.FLOAT):
            return Number(self._previous().value)

        # String literals
        if self._match(TokenType.STRING):
            return String(self._previous().value)

        # New expression
        if self._match(TokenType.NEW):
            return self._parse_new_expr()

        # This expression
        if self._match(TokenType.THIS):
            return ThisExpr()

        # Super expression - needs method name
        if self._match(TokenType.SUPER):
            self._consume(TokenType.DOT, "Expected '.' after 'super'")
            method_name = self._consume(TokenType.IDENTIFIER, "Expected method name").value
            return SuperExpr(method_name)

        # Identifiers
        if self._match(TokenType.IDENTIFIER):
            return Var(self._previous().value)

        # Grouping
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        raise ParseError(f"Unexpected token: {self._peek().type.name}", self._peek())

    def _parse_new_expr(self) -> "NewExpr":
        """Parse new expression: new ClassName(args)"""
        class_name = self._consume(TokenType.IDENTIFIER, "Expected class name after 'new'").value

        self._consume(TokenType.LPAREN, "Expected '(' after class name")
        args = []

        if not self._check(TokenType.RPAREN):
            args.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                args.append(self._parse_expression())

        self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        return NewExpr(class_name, args)

    # === Helper Methods ===

    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types and advance if so"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        """Consume and return current token"""
        if not self._is_at_end():
            self.pos += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        """Check if at end of token stream"""
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """Return current token without advancing"""
        return self.tokens[self.pos]

    def _previous(self) -> Token:
        """Return previous token"""
        return self.tokens[self.pos - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of given type or raise error"""
        if self._check(token_type):
            return self._advance()

        raise ParseError(message, self._peek())


def parse(tokens: List[Token]) -> Program:
    """Convenience function to parse token stream"""
    parser = Parser(tokens)
    return parser.parse()
