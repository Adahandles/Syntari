import struct
import sys
import os

from ..interpreter.lexer import tokenize
from ..interpreter.parser import Parser

MAGIC = b"SYNTARI03"
OPCODES = {
    "LOAD_CONST": 0x01,
    "STORE": 0x02,
    "LOAD": 0x03,
    "ADD": 0x04,
    "SUB": 0x05,
    "MUL": 0x06,
    "DIV": 0x07,
    "PRINT": 0x08,
    "HALT": 0xFF,
}


class BytecodeGenerator:
    def __init__(self):
        self.instructions = []
        self.constants = []

    def add_const(self, value):
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)

    def emit(self, opcode, *args):
        self.instructions.append((opcode, args))

    def compile_node(self, node):
        from ..interpreter.nodes import Number, String, Var, VarAssign, Print, BinOp, Block

        if isinstance(node, Block):
            for stmt in node.statements:
                self.compile_node(stmt)
            return

        if isinstance(node, VarAssign):
            idx = self.compile_expr(node.value)
            self.emit("LOAD_CONST", idx)
            self.emit("STORE", node.name)
            return

        if isinstance(node, Print):
            idx = self.compile_expr(node.expr)
            self.emit("LOAD_CONST", idx)
            self.emit("PRINT")
            return

        self.compile_expr(node)

    def compile_expr(self, node):
        from ..interpreter.nodes import Number, String, Var, BinOp

        if isinstance(node, Number):
            return self.add_const(node.value)
        if isinstance(node, String):
            return self.add_const(node.value)
        if isinstance(node, Var):
            self.emit("LOAD", node.name)
            return self.add_const(f"__RUNTIME_VAR__:{node.name}")
        if isinstance(node, BinOp):
            l_idx = self.compile_expr(node.left)
            r_idx = self.compile_expr(node.right)
            self.emit("LOAD_CONST", l_idx)
            self.emit("LOAD_CONST", r_idx)
            if node.op == "+":
                self.emit("ADD")
            elif node.op == "-":
                self.emit("SUB")
            elif node.op == "*":
                self.emit("MUL")
            elif node.op == "/":
                self.emit("DIV")
            return self.add_const("__STACK_TOP__")
        return self.add_const("__UNSUPPORTED_EXPR__")

    def finalize(self):
        self.emit("HALT")

    def to_bytes(self):
        data = bytearray()
        data.extend(MAGIC)

        data.extend(struct.pack("<I", len(self.constants)))
        for c in self.constants:
            bs = str(c).encode("utf-8")
            data.extend(struct.pack("<I", len(bs)))
            data.extend(bs)

        data.extend(struct.pack("<I", len(self.instructions)))
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

    def save(self, filename):
        self.finalize()
        blob = self.to_bytes()
        with open(filename, "wb") as f:
            f.write(blob)
        print(f"[Syntari Compiler] Wrote bytecode → {filename}")


def compile_file(source_path, output_path=None):
    with open(source_path, "r", encoding="utf-8") as f:
        code = f.read()

    tokens = tokenize(code)
    tree = Parser(tokens).parse()

    gen = BytecodeGenerator()
    gen.compile_node(tree)
    gen.finalize()

    if not output_path:
        base, _ = os.path.splitext(source_path)
        output_path = base + ".sbc"

    gen.save(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/compiler/bytecode.py <source.syn> [output.sbc]")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    compile_file(src, out)
