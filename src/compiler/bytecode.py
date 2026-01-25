"""
Syntari Bytecode Compiler - Compiles AST to bytecode (.sbc files)
"""

import struct
import sys
import os

MAGIC = b"SYNTARI03"

# Extended opcode set for v0.3
OPCODES = {
    # Stack operations
    "LOAD_CONST": 0x01,  # Load constant from pool
    "STORE": 0x02,  # Store value to variable
    "LOAD": 0x03,  # Load variable value
    # Arithmetic operations
    "ADD": 0x04,
    "SUB": 0x05,
    "MUL": 0x06,
    "DIV": 0x07,
    "MOD": 0x08,  # Modulo operation
    # Comparison operations
    "EQ_EQ": 0x10,  # Equal ==
    "NOT_EQ": 0x11,  # Not equal !=
    "LT": 0x12,  # Less than <
    "LT_EQ": 0x13,  # Less than or equal <=
    "GT": 0x14,  # Greater than >
    "GT_EQ": 0x15,  # Greater than or equal >=
    # Logical operations
    "AND": 0x16,  # Logical AND &&
    "OR": 0x17,  # Logical OR ||
    "NOT": 0x18,  # Logical NOT !
    # Unary operations
    "NEG": 0x19,  # Unary negation -
    # Control flow
    "JMP": 0x20,  # Unconditional jump
    "JMP_IF_FALSE": 0x21,  # Jump if top of stack is false
    "JMP_IF_TRUE": 0x22,  # Jump if top of stack is true
    # Functions
    "CALL": 0x30,  # Call function
    "RETURN": 0x31,  # Return from function
    # I/O
    "PRINT": 0x40,  # Print value
    # Special
    "POP": 0x50,  # Pop value from stack
    "DUP": 0x51,  # Duplicate top of stack
    "HALT": 0xFF,  # Halt execution
}

# Public API exports
__all__ = [
    "MAGIC",
    "OPCODES",
    "BytecodeGenerator",
    "compile_file",
]


class BytecodeGenerator:
    """Generates bytecode from Syntari AST"""

    def __init__(self):
        self.instructions = []
        self.constants = []
        self.label_counter = 0

    def add_const(self, value):
        """Add a constant to the pool and return its index"""
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)

    def emit(self, opcode, *args):
        """Emit an instruction with optional arguments"""
        self.instructions.append((opcode, args))

    def new_label(self):
        """Generate a new unique label"""
        self.label_counter += 1
        return f"__label_{self.label_counter}__"

    def emit_label(self, label):
        """Emit a label marker"""
        self.instructions.append(("LABEL", (label,)))

    def compile_node(self, node):
        """Compile a single AST node"""
        from src.interpreter.nodes import (
            Number,
            String,
            Boolean,
            Var,
            VarDecl,
            VarAssign,
            Print,
            BinOp,
            UnaryOp,
            Block,
            IfStmt,
            WhileStmt,
            ExprStmt,
            FuncDecl,
            Call,
            ReturnStmt,
            Program,
        )

        if isinstance(node, Program):
            for stmt in node.statements:
                self.compile_node(stmt)
            return

        if isinstance(node, Block):
            for stmt in node.statements:
                self.compile_node(stmt)
            return

        if isinstance(node, VarDecl):
            # Compile the initial value expression
            self.compile_expr(node.value)
            # Store to variable
            self.emit("STORE", node.name)
            return

        if isinstance(node, VarAssign):
            # Compile the value expression
            self.compile_expr(node.value)
            # Store to variable
            self.emit("STORE", node.name)
            return

        if isinstance(node, Print):
            # Compile the expression to print
            self.compile_expr(node.expr)
            self.emit("PRINT")
            return

        if isinstance(node, ExprStmt):
            # Check if it's an assignment (which is a statement disguised as expression)
            from src.interpreter.nodes import VarAssign, MemberAssign

            if isinstance(node.expr, VarAssign):
                self.compile_node(node.expr)
            elif isinstance(node.expr, MemberAssign):
                self.compile_node(node.expr)
            else:
                # Compile expression and pop result (side effects only)
                self.compile_expr(node.expr)
                self.emit("POP")
            return

        if isinstance(node, IfStmt):
            # Compile condition
            self.compile_expr(node.condition)

            # Jump to else block if condition is false
            else_label = self.new_label()
            end_label = self.new_label()

            self.emit("JMP_IF_FALSE", else_label)

            # Compile then block
            self.compile_node(node.then_block)
            self.emit("JMP", end_label)

            # Else block
            self.emit_label(else_label)
            if node.else_block:
                self.compile_node(node.else_block)

            self.emit_label(end_label)
            return

        if isinstance(node, WhileStmt):
            # Loop structure:
            # start:
            #   condition
            #   JMP_IF_FALSE end
            #   body
            #   JMP start
            # end:

            start_label = self.new_label()
            end_label = self.new_label()

            self.emit_label(start_label)

            # Compile condition
            self.compile_expr(node.condition)
            self.emit("JMP_IF_FALSE", end_label)

            # Compile body
            self.compile_node(node.body)

            # Jump back to start
            self.emit("JMP", start_label)

            self.emit_label(end_label)
            return

        if isinstance(node, FuncDecl):
            # For now, skip function declarations in bytecode
            # TODO: Implement proper function compilation
            return

        if isinstance(node, ReturnStmt):
            if node.value:
                self.compile_expr(node.value)
            else:
                # Return None/null
                idx = self.add_const(None)
                self.emit("LOAD_CONST", idx)
            self.emit("RETURN")
            return

        # Default: try to compile as expression
        self.compile_expr(node)

    def compile_expr(self, node):
        """Compile an expression node (leaves result on stack)"""
        from src.interpreter.nodes import (
            Number,
            String,
            Boolean,
            Var,
            BinOp,
            UnaryOp,
            Call,
        )

        if isinstance(node, Number):
            idx = self.add_const(node.value)
            self.emit("LOAD_CONST", idx)
            return

        if isinstance(node, String):
            idx = self.add_const(node.value)
            self.emit("LOAD_CONST", idx)
            return

        if isinstance(node, Boolean):
            idx = self.add_const(node.value)
            self.emit("LOAD_CONST", idx)
            return

        if isinstance(node, Var):
            self.emit("LOAD", node.name)
            return

        if isinstance(node, BinOp):
            # Compile left and right operands
            self.compile_expr(node.left)
            self.compile_expr(node.right)

            # Emit appropriate operator
            op_map = {
                "+": "ADD",
                "-": "SUB",
                "*": "MUL",
                "/": "DIV",
                "%": "MOD",
                "==": "EQ_EQ",
                "!=": "NOT_EQ",
                "<": "LT",
                "<=": "LT_EQ",
                ">": "GT",
                ">=": "GT_EQ",
                "&&": "AND",
                "||": "OR",
            }

            if node.op in op_map:
                self.emit(op_map[node.op])
            else:
                raise ValueError(f"Unknown binary operator: {node.op}")
            return

        if isinstance(node, UnaryOp):
            # Compile operand
            self.compile_expr(node.operand)

            # Emit appropriate operator
            if node.op == "-":
                self.emit("NEG")
            elif node.op == "!":
                self.emit("NOT")
            else:
                raise ValueError(f"Unknown unary operator: {node.op}")
            return

        if isinstance(node, Call):
            # Compile arguments
            for arg in node.args:
                self.compile_expr(arg)

            # Emit call with function name and arg count
            self.emit("CALL", node.callee, len(node.args))
            return

        raise ValueError(f"Cannot compile expression node: {type(node).__name__}")

    def finalize(self):
        """Finalize bytecode generation"""
        self.emit("HALT")

    def resolve_labels(self):
        """Resolve label references to byte addresses in code"""
        # First pass: calculate byte offsets for each instruction and map labels
        label_map = {}
        byte_offset = 0

        for item in self.instructions:
            if item[0] == "LABEL":
                # Map label to current byte offset
                label_map[item[1][0]] = byte_offset
            else:
                # Calculate size of this instruction in bytes
                opcode, args = item
                byte_offset += 1  # opcode byte

                for arg in args:
                    if isinstance(arg, int):
                        byte_offset += 4  # 32-bit integer
                    elif isinstance(arg, str):
                        # Check if it's a label reference (will be converted to int)
                        if arg.startswith("__label_"):
                            byte_offset += 4  # Will become 32-bit integer
                        else:
                            # String: 4 bytes for length + string bytes
                            byte_offset += 4 + len(arg.encode("utf-8"))

        # Second pass: replace label references with byte addresses
        resolved = []
        for item in self.instructions:
            if item[0] == "LABEL":
                continue  # Skip label markers

            opcode, args = item
            new_args = []
            for arg in args:
                if isinstance(arg, str) and arg.startswith("__label_"):
                    # Replace label with its byte address
                    if arg not in label_map:
                        raise ValueError(f"Undefined label: {arg}")
                    new_args.append(label_map[arg])
                else:
                    new_args.append(arg)

            resolved.append((opcode, tuple(new_args)))

        self.instructions = resolved

    def to_bytes(self):
        """Convert bytecode to binary format"""
        # Resolve labels before serialization
        self.resolve_labels()

        data = bytearray()
        data.extend(MAGIC)

        # Write constants pool
        data.extend(struct.pack("<I", len(self.constants)))
        for c in self.constants:
            bs = str(c).encode("utf-8")
            data.extend(struct.pack("<I", len(bs)))
            data.extend(bs)

        # Write instruction count
        data.extend(struct.pack("<I", len(self.instructions)))

        # Write instructions
        for op, args in self.instructions:
            data.append(OPCODES[op])

            for a in args:
                if isinstance(a, int):
                    data.extend(struct.pack("<I", a))
                elif isinstance(a, str):
                    b = a.encode("utf-8")
                    data.extend(struct.pack("<I", len(b)))
                    data.extend(b)
                else:
                    raise TypeError(f"Unsupported arg type for {op}: {type(a)}")

        return bytes(data)

    def save(self, filename, verbose=True):
        """Save bytecode to file"""
        self.finalize()
        blob = self.to_bytes()
        with open(filename, "wb") as f:
            f.write(blob)
        if verbose:
            print(f"[Syntari Compiler] Wrote bytecode → {filename}")


def compile_file(source_path, output_path=None, verbose=True):
    """Compile a Syntari source file to bytecode"""
    from src.interpreter.lexer import tokenize
    from src.interpreter.parser import Parser

    with open(source_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Tokenize and parse
    tokens = tokenize(code)
    tree = Parser(tokens).parse()

    # Generate bytecode
    gen = BytecodeGenerator()
    gen.compile_node(tree)

    # Determine output path
    if not output_path:
        base, _ = os.path.splitext(source_path)
        output_path = base + ".sbc"

    gen.save(output_path, verbose=verbose)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.compiler.bytecode <source.syn> [output.sbc]")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    compile_file(src, out)
