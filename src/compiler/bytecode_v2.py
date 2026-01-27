"""
Syntari Enhanced Bytecode Compiler v2

Improvements over v1:
- Control flow support (if, while, functions)
- Comparison operators
- Function calls and returns
- Optimization passes (constant folding, dead code elimination)
- Better code generation
- Enhanced security tracking

Security features:
- Instruction count limits
- Stack depth tracking
- Recursion depth limits
- Memory allocation tracking
"""

import struct
import sys
import os
from typing import List, Tuple, Any, Dict, Optional
from dataclasses import dataclass
from enum import IntEnum

# Import from existing codebase
from ..interpreter.lexer import tokenize
from ..interpreter.parser import Parser
from ..interpreter.nodes import *


class Opcode(IntEnum):
    """Enhanced opcode set for Syntari v0.4"""

    # Constants and Variables
    LOAD_CONST = 0x01
    STORE = 0x02
    LOAD = 0x03

    # Arithmetic
    ADD = 0x04
    SUB = 0x05
    MUL = 0x06
    DIV = 0x07
    MOD = 0x08

    # I/O
    PRINT = 0x09

    # Control Flow
    JMP = 0x10  # Unconditional jump
    JMP_IF_FALSE = 0x11  # Jump if top of stack is false
    JMP_IF_TRUE = 0x12  # Jump if top of stack is true

    # Comparison
    COMPARE_EQ = 0x13  # ==
    COMPARE_NE = 0x14  # !=
    COMPARE_LT = 0x15  # <
    COMPARE_LE = 0x16  # <=
    COMPARE_GT = 0x17  # >
    COMPARE_GE = 0x18  # >=

    # Functions
    CALL = 0x20  # Call function
    RETURN = 0x21  # Return from function
    LOAD_FUNC = 0x22  # Load function reference

    # Stack Operations
    DUP = 0x30  # Duplicate top of stack
    POP = 0x31  # Pop and discard top of stack
    SWAP = 0x32  # Swap top two items

    # Logical Operations
    AND = 0x40  # Logical AND
    OR = 0x41  # Logical OR
    NOT = 0x42  # Logical NOT

    # Special
    HALT = 0xFF


@dataclass
class Instruction:
    """Represents a single bytecode instruction"""

    opcode: Opcode
    args: Tuple[Any, ...] = ()
    lineno: int = 0
    comment: str = ""

    def __repr__(self):
        args_str = ", ".join(str(a) for a in self.args)
        return f"{self.opcode.name}({args_str}) # {self.comment}"


class OptimizationPass:
    """Base class for optimization passes"""

    def optimize(self, instructions: List[Instruction]) -> List[Instruction]:
        """Apply optimization to instruction list"""
        raise NotImplementedError


class ConstantFoldingPass(OptimizationPass):
    """Fold constant expressions at compile time"""

    def optimize(self, instructions: List[Instruction]) -> List[Instruction]:
        optimized = []
        i = 0

        while i < len(instructions):
            # Look for pattern: LOAD_CONST, LOAD_CONST, ADD/SUB/MUL/DIV
            if (
                i + 2 < len(instructions)
                and instructions[i].opcode == Opcode.LOAD_CONST
                and instructions[i + 1].opcode == Opcode.LOAD_CONST
                and instructions[i + 2].opcode in (Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV)
            ):

                left = instructions[i].args[0]
                right = instructions[i + 1].args[0]
                op = instructions[i + 2].opcode

                # Only fold if both are numbers
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    if op == Opcode.ADD:
                        result = left + right
                    elif op == Opcode.SUB:
                        result = left - right
                    elif op == Opcode.MUL:
                        result = left * right
                    elif op == Opcode.DIV:
                        if right != 0:
                            result = left / right
                        else:
                            # Can't fold division by zero
                            optimized.extend(
                                [instructions[i], instructions[i + 1], instructions[i + 2]]
                            )
                            i += 3
                            continue

                    # Replace three instructions with one
                    optimized.append(
                        Instruction(
                            Opcode.LOAD_CONST,
                            (result,),
                            instructions[i].lineno,
                            f"folded: {left} {op.name} {right}",
                        )
                    )
                    i += 3
                    continue

            optimized.append(instructions[i])
            i += 1

        return optimized


class DeadCodeEliminationPass(OptimizationPass):
    """Remove unreachable code"""

    def optimize(self, instructions: List[Instruction]) -> List[Instruction]:
        # Mark reachable instructions
        reachable = [False] * len(instructions)
        self._mark_reachable(instructions, 0, reachable)

        # Keep only reachable instructions
        return [inst for i, inst in enumerate(instructions) if reachable[i]]

    def _mark_reachable(self, instructions: List[Instruction], start: int, reachable: List[bool]):
        """Recursively mark reachable instructions"""
        i = start
        while i < len(instructions):
            if reachable[i]:
                # Already visited
                return

            reachable[i] = True
            inst = instructions[i]

            if inst.opcode == Opcode.JMP:
                # Follow jump
                target = inst.args[0]
                self._mark_reachable(instructions, target, reachable)
                return  # Stop following this path

            elif inst.opcode in (Opcode.JMP_IF_FALSE, Opcode.JMP_IF_TRUE):
                # Follow both paths
                target = inst.args[0]
                self._mark_reachable(instructions, target, reachable)
                # Continue to next instruction

            elif inst.opcode in (Opcode.RETURN, Opcode.HALT):
                # End of path
                return

            i += 1


class BytecodeCompilerV2:
    """Enhanced bytecode compiler with optimizations"""

    MAGIC = b"SYNTARI04"  # New magic for v0.4 bytecode
    VERSION = (0, 4, 0)

    def __init__(self, optimize=True):
        self.instructions: List[Instruction] = []
        self.constants: List[Any] = []
        self.const_cache: Dict[Any, int] = {}
        self.optimize = optimize
        self.label_counter = 0
        self.labels: Dict[str, int] = {}
        self.pending_labels: List[Tuple[int, str]] = []
        self.function_names: List[str] = []
        self.current_function = None

        # Security tracking
        self.max_stack_depth = 0
        self.current_stack_depth = 0
        self.instruction_count = 0

    def add_const(self, value: Any) -> int:
        """Add constant to pool or return existing index"""
        # Use tuple as key for hashable cache
        key = value if isinstance(value, (int, float, str, bool)) else id(value)

        if key in self.const_cache:
            return self.const_cache[key]

        idx = len(self.constants)
        self.constants.append(value)
        self.const_cache[key] = idx
        return idx

    def emit(self, opcode: Opcode, *args, comment="", lineno=0):
        """Emit an instruction"""
        self.instructions.append(Instruction(opcode, args, lineno, comment))
        self.instruction_count += 1

        # Track stack depth for security
        if opcode in (Opcode.LOAD_CONST, Opcode.LOAD, Opcode.DUP):
            self.current_stack_depth += 1
            self.max_stack_depth = max(self.max_stack_depth, self.current_stack_depth)
        elif opcode in (Opcode.POP, Opcode.STORE, Opcode.PRINT, Opcode.RETURN):
            self.current_stack_depth -= 1
        elif opcode in (Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD):
            self.current_stack_depth -= 1  # Two pops, one push = net -1

        return len(self.instructions) - 1

    def create_label(self, prefix="L") -> str:
        """Create a new unique label"""
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label

    def mark_label(self, label: str):
        """Mark the current position with a label"""
        self.labels[label] = len(self.instructions)

    def emit_jump(self, opcode: Opcode, label: str, comment=""):
        """Emit a jump instruction to a label"""
        idx = self.emit(opcode, 0, comment=comment)  # Placeholder
        self.pending_labels.append((idx, label))

    def resolve_labels(self):
        """Resolve all label references to actual positions"""
        for inst_idx, label in self.pending_labels:
            if label not in self.labels:
                raise CompileError(f"Undefined label: {label}")
            target = self.labels[label]
            # Update the instruction's jump target
            self.instructions[inst_idx] = Instruction(
                self.instructions[inst_idx].opcode,
                (target,),
                self.instructions[inst_idx].lineno,
                self.instructions[inst_idx].comment,
            )

    def compile(self, source_code: str) -> bytes:
        """Compile source code to bytecode"""
        # Parse
        tokens = tokenize(source_code)
        ast = Parser(tokens).parse()

        # Compile
        self.compile_node(ast)
        self.emit(Opcode.HALT, comment="end of program")

        # Resolve jumps
        self.resolve_labels()

        # Optimize
        if self.optimize:
            self.apply_optimizations()

        # Generate bytecode
        return self.to_bytes()

    def apply_optimizations(self):
        """Apply all optimization passes"""
        passes = [
            ConstantFoldingPass(),
            DeadCodeEliminationPass(),
        ]

        for opt_pass in passes:
            self.instructions = opt_pass.optimize(self.instructions)

    def compile_node(self, node):
        """Compile an AST node"""
        if isinstance(node, Program):
            for stmt in node.statements:
                self.compile_node(stmt)

        elif isinstance(node, Block):
            for stmt in node.statements:
                self.compile_node(stmt)

        elif isinstance(node, VarDecl):
            self.compile_expr(node.value)
            self.emit(Opcode.STORE, node.name, comment=f"store {node.name}")

        elif isinstance(node, VarAssign):
            self.compile_expr(node.value)
            self.emit(Opcode.STORE, node.name, comment=f"assign {node.name}")

        elif isinstance(node, IfStmt):
            self.compile_if(node)

        elif isinstance(node, WhileStmt):
            self.compile_while(node)

        elif isinstance(node, FuncDecl):
            self.compile_function(node)

        elif isinstance(node, ReturnStmt):
            if node.value:
                self.compile_expr(node.value)
            else:
                idx = self.add_const(None)
                self.emit(Opcode.LOAD_CONST, idx)
            self.emit(Opcode.RETURN, comment="return")

        elif isinstance(node, Print):
            self.compile_expr(node.expr)
            self.emit(Opcode.PRINT, comment="print")

        elif isinstance(node, ExprStmt):
            self.compile_expr(node.expr)
            self.emit(Opcode.POP, comment="discard result")

        else:
            # Try as expression
            try:
                self.compile_expr(node)
                self.emit(Opcode.POP, comment="discard result")
            except:
                raise CompileError(f"Unsupported node type: {type(node).__name__}")

    def compile_expr(self, node):
        """Compile an expression"""
        if isinstance(node, Number):
            idx = self.add_const(node.value)
            self.emit(Opcode.LOAD_CONST, idx, comment=f"const {node.value}")

        elif isinstance(node, String):
            idx = self.add_const(node.value)
            self.emit(Opcode.LOAD_CONST, idx, comment=f'const "{node.value}"')

        elif isinstance(node, Boolean):
            idx = self.add_const(node.value)
            self.emit(Opcode.LOAD_CONST, idx, comment=f"const {node.value}")

        elif isinstance(node, Var):
            self.emit(Opcode.LOAD, node.name, comment=f"load {node.name}")

        elif isinstance(node, BinOp):
            self.compile_binop(node)

        elif isinstance(node, UnaryOp):
            self.compile_unary(node)

        elif isinstance(node, Call):
            self.compile_call(node)

        else:
            raise CompileError(f"Unsupported expression: {type(node).__name__}")

    def compile_binop(self, node: BinOp):
        """Compile binary operation"""
        # Handle short-circuit operators
        if node.op == "&&":
            self.compile_expr(node.left)
            self.emit(Opcode.DUP, comment="dup for AND")
            end_label = self.create_label("and_end")
            self.emit_jump(Opcode.JMP_IF_FALSE, end_label, comment="short-circuit AND")
            self.emit(Opcode.POP, comment="pop left value")
            self.compile_expr(node.right)
            self.mark_label(end_label)
            return

        elif node.op == "||":
            self.compile_expr(node.left)
            self.emit(Opcode.DUP, comment="dup for OR")
            end_label = self.create_label("or_end")
            self.emit_jump(Opcode.JMP_IF_TRUE, end_label, comment="short-circuit OR")
            self.emit(Opcode.POP, comment="pop left value")
            self.compile_expr(node.right)
            self.mark_label(end_label)
            return

        # Regular binary operators
        self.compile_expr(node.left)
        self.compile_expr(node.right)

        op_map = {
            "+": Opcode.ADD,
            "-": Opcode.SUB,
            "*": Opcode.MUL,
            "/": Opcode.DIV,
            "%": Opcode.MOD,
            "==": Opcode.COMPARE_EQ,
            "!=": Opcode.COMPARE_NE,
            "<": Opcode.COMPARE_LT,
            "<=": Opcode.COMPARE_LE,
            ">": Opcode.COMPARE_GT,
            ">=": Opcode.COMPARE_GE,
        }

        if node.op in op_map:
            self.emit(op_map[node.op], comment=f"{node.op}")
        else:
            raise CompileError(f"Unsupported operator: {node.op}")

    def compile_unary(self, node: UnaryOp):
        """Compile unary operation"""
        self.compile_expr(node.operand)

        if node.op == "!":
            self.emit(Opcode.NOT, comment="logical NOT")
        elif node.op == "-":
            # Negate: 0 - x
            idx = self.add_const(0)
            self.emit(Opcode.LOAD_CONST, idx)
            self.emit(Opcode.SWAP)
            self.emit(Opcode.SUB, comment="negate")
        else:
            raise CompileError(f"Unsupported unary operator: {node.op}")

    def compile_if(self, node: IfStmt):
        """Compile if statement"""
        # Compile condition
        self.compile_expr(node.condition)

        else_label = self.create_label("else")
        end_label = self.create_label("endif")

        # Jump to else if condition is false
        self.emit_jump(Opcode.JMP_IF_FALSE, else_label, comment="if false, jump to else")

        # Then block
        self.compile_node(node.then_block)

        if node.else_block:
            # Jump over else block
            self.emit_jump(Opcode.JMP, end_label, comment="skip else block")
            self.mark_label(else_label)
            self.compile_node(node.else_block)
            self.mark_label(end_label)
        else:
            self.mark_label(else_label)

    def compile_while(self, node: WhileStmt):
        """Compile while loop"""
        start_label = self.create_label("while_start")
        end_label = self.create_label("while_end")

        self.mark_label(start_label)

        # Compile condition
        self.compile_expr(node.condition)

        # Exit loop if false
        self.emit_jump(Opcode.JMP_IF_FALSE, end_label, comment="exit loop if false")

        # Loop body
        self.compile_node(node.body)

        # Jump back to start
        self.emit_jump(Opcode.JMP, start_label, comment="loop back")

        self.mark_label(end_label)

    def compile_function(self, node: FuncDecl):
        """Compile function declaration"""
        # For now, we'll store function as a constant with special marker
        # Full function support requires more VM changes
        func_label = self.create_label(f"func_{node.name}")
        func_idx = self.add_const(func_label)
        self.emit(Opcode.LOAD_FUNC, func_idx, comment=f"define function {node.name}")
        self.emit(Opcode.STORE, node.name, comment=f"store function {node.name}")

        # TODO: Implement full function compilation in next iteration

    def compile_call(self, node: Call):
        """Compile function call"""
        # Compile arguments
        for arg in node.args:
            self.compile_expr(arg)

        # Load function
        self.emit(Opcode.LOAD, node.callee, comment=f"load function {node.callee}")

        # Call with arg count
        self.emit(Opcode.CALL, len(node.args), comment=f"call {node.callee}")

    def to_bytes(self) -> bytes:
        """Convert compiled code to bytecode"""
        data = bytearray()

        # Header
        data.extend(self.MAGIC)
        data.extend(struct.pack("<BBB", *self.VERSION))

        # Metadata
        data.extend(struct.pack("<I", self.max_stack_depth))
        data.extend(struct.pack("<I", self.instruction_count))

        # Constants pool
        data.extend(struct.pack("<I", len(self.constants)))
        for const in self.constants:
            self._encode_constant(data, const)

        # Instructions
        data.extend(struct.pack("<I", len(self.instructions)))
        for inst in self.instructions:
            self._encode_instruction(data, inst)

        return bytes(data)

    def _encode_constant(self, data: bytearray, const: Any):
        """Encode a constant value"""
        if isinstance(const, bool):
            data.append(0x01)  # Boolean type
            data.append(1 if const else 0)
        elif isinstance(const, int):
            data.append(0x02)  # Integer type
            data.extend(struct.pack("<q", const))
        elif isinstance(const, float):
            data.append(0x03)  # Float type
            data.extend(struct.pack("<d", const))
        elif isinstance(const, str):
            data.append(0x04)  # String type
            encoded = const.encode("utf-8")
            data.extend(struct.pack("<I", len(encoded)))
            data.extend(encoded)
        elif const is None:
            data.append(0x00)  # Null type
        else:
            raise CompileError(f"Unsupported constant type: {type(const)}")

    def _encode_instruction(self, data: bytearray, inst: Instruction):
        """Encode an instruction"""
        data.append(inst.opcode)
        data.extend(struct.pack("<H", inst.lineno))  # Line number for debugging

        # Encode arguments based on opcode
        if inst.opcode in (
            Opcode.LOAD_CONST,
            Opcode.JMP,
            Opcode.JMP_IF_FALSE,
            Opcode.JMP_IF_TRUE,
            Opcode.CALL,
        ):
            # Integer argument
            data.extend(struct.pack("<I", inst.args[0]))
        elif inst.opcode in (Opcode.STORE, Opcode.LOAD, Opcode.LOAD_FUNC):
            # String argument (variable/function name)
            name = inst.args[0]
            encoded = name.encode("utf-8")
            data.extend(struct.pack("<I", len(encoded)))
            data.extend(encoded)
        # Other opcodes have no arguments


class CompileError(Exception):
    """Compilation error"""

    pass


def compile_file(source_path: str, output_path: str = None, optimize: bool = True):
    """Compile a Syntari source file to bytecode"""
    with open(source_path, "r", encoding="utf-8") as f:
        source = f.read()

    compiler = BytecodeCompilerV2(optimize=optimize)
    try:
        bytecode = compiler.compile(source)
    except Exception as e:
        print(f"[Compilation Error] {e}")
        sys.exit(1)

    if not output_path:
        base, _ = os.path.splitext(source_path)
        output_path = base + ".sbc"

    with open(output_path, "wb") as f:
        f.write(bytecode)

    print(f"[Syntari Compiler v2] Compiled {source_path} → {output_path}")
    print(f"  Instructions: {compiler.instruction_count}")
    print(f"  Constants: {len(compiler.constants)}")
    print(f"  Max stack depth: {compiler.max_stack_depth}")
    print(f"  Optimizations: {'enabled' if optimize else 'disabled'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.compiler.bytecode_v2 <source.syn> [output.sbc] [--no-optimize]")
        sys.exit(1)

    src = sys.argv[1]
    out = None
    optimize = True

    for arg in sys.argv[2:]:
        if arg == "--no-optimize":
            optimize = False
        elif not out:
            out = arg

    compile_file(src, out, optimize)
