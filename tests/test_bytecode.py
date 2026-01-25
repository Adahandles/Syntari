"""
Tests for Syntari Bytecode Compiler and VM
"""

import pytest
import os
import tempfile
from src.compiler.bytecode import BytecodeGenerator, compile_file, OPCODES
from src.vm.runtime import SyntariVM, run_vm, VMSecurityError
from src.interpreter.lexer import tokenize
from src.interpreter.parser import Parser
from src.interpreter.nodes import *


class TestBytecodeGeneration:
    """Test bytecode generation from AST"""

    def test_load_const_number(self):
        """Test loading a numeric constant"""
        gen = BytecodeGenerator()
        node = Number(42)
        gen.compile_expr(node)

        assert len(gen.constants) == 1
        assert gen.constants[0] == 42
        assert gen.instructions[0][0] == "LOAD_CONST"

    def test_load_const_string(self):
        """Test loading a string constant"""
        gen = BytecodeGenerator()
        node = String("hello")
        gen.compile_expr(node)

        assert len(gen.constants) == 1
        assert gen.constants[0] == "hello"

    def test_load_const_boolean(self):
        """Test loading a boolean constant"""
        gen = BytecodeGenerator()
        node = Boolean(True)
        gen.compile_expr(node)

        assert len(gen.constants) == 1
        assert gen.constants[0] is True

    def test_binary_operation_add(self):
        """Test compiling addition"""
        gen = BytecodeGenerator()
        node = BinOp(Number(2), "+", Number(3))
        gen.compile_expr(node)

        # Should have two constants (2 and 3)
        assert 2 in gen.constants
        assert 3 in gen.constants

        # Should have LOAD_CONST, LOAD_CONST, ADD instructions
        opcodes = [instr[0] for instr in gen.instructions]
        assert "LOAD_CONST" in opcodes
        assert "ADD" in opcodes

    def test_binary_operation_comparison(self):
        """Test compiling comparison operators"""
        gen = BytecodeGenerator()

        # Test ==
        node = BinOp(Number(5), "==", Number(5))
        gen.compile_expr(node)
        opcodes = [instr[0] for instr in gen.instructions]
        assert "EQ_EQ" in opcodes

    def test_unary_operation_neg(self):
        """Test compiling unary negation"""
        gen = BytecodeGenerator()
        node = UnaryOp("-", Number(42))
        gen.compile_expr(node)

        opcodes = [instr[0] for instr in gen.instructions]
        assert "LOAD_CONST" in opcodes
        assert "NEG" in opcodes

    def test_unary_operation_not(self):
        """Test compiling logical NOT"""
        gen = BytecodeGenerator()
        node = UnaryOp("!", Boolean(True))
        gen.compile_expr(node)

        opcodes = [instr[0] for instr in gen.instructions]
        assert "NOT" in opcodes

    def test_variable_declaration(self):
        """Test compiling variable declaration"""
        gen = BytecodeGenerator()
        node = VarDecl("x", None, Number(10), False)
        gen.compile_node(node)

        opcodes = [instr[0] for instr in gen.instructions]
        assert "LOAD_CONST" in opcodes
        assert "STORE" in opcodes

    def test_variable_load(self):
        """Test compiling variable load"""
        gen = BytecodeGenerator()
        node = Var("x")
        gen.compile_expr(node)

        opcodes = [instr[0] for instr in gen.instructions]
        assert "LOAD" in opcodes

    def test_print_statement(self):
        """Test compiling print statement"""
        gen = BytecodeGenerator()
        node = Print(String("hello"))
        gen.compile_node(node)

        opcodes = [instr[0] for instr in gen.instructions]
        assert "LOAD_CONST" in opcodes
        assert "PRINT" in opcodes

    def test_if_statement(self):
        """Test compiling if statement"""
        gen = BytecodeGenerator()
        condition = BinOp(Number(1), "==", Number(1))
        then_block = Block([Print(String("true"))])
        node = IfStmt(condition, then_block, None)
        gen.compile_node(node)

        opcodes = [instr[0] for instr in gen.instructions]
        assert "EQ_EQ" in opcodes
        assert "JMP_IF_FALSE" in opcodes
        assert "PRINT" in opcodes

    def test_while_statement(self):
        """Test compiling while statement"""
        gen = BytecodeGenerator()
        condition = BinOp(Var("x"), "<", Number(10))
        body = Block([VarAssign("x", BinOp(Var("x"), "+", Number(1)))])
        node = WhileStmt(condition, body)
        gen.compile_node(node)

        opcodes = [instr[0] for instr in gen.instructions]
        assert "JMP_IF_FALSE" in opcodes
        assert "JMP" in opcodes

    def test_label_resolution(self):
        """Test that labels are properly resolved to addresses"""
        gen = BytecodeGenerator()

        # Create a simple if statement
        condition = Boolean(True)
        then_block = Block([Print(String("yes"))])
        node = IfStmt(condition, then_block, None)
        gen.compile_node(node)

        # Resolve labels
        gen.resolve_labels()

        # Check that no LABEL instructions remain
        for instr in gen.instructions:
            assert instr[0] != "LABEL"

        # Check that JMP instructions have numeric addresses
        for instr in gen.instructions:
            if instr[0] in ["JMP", "JMP_IF_FALSE", "JMP_IF_TRUE"]:
                assert isinstance(instr[1][0], int)

    def test_to_bytes(self):
        """Test bytecode serialization"""
        gen = BytecodeGenerator()
        node = Print(String("test"))
        gen.compile_node(node)
        gen.finalize()

        bytecode = gen.to_bytes()

        # Check magic bytes
        assert bytecode.startswith(b"SYNTARI03")

        # Check that it's not empty
        assert len(bytecode) > len(b"SYNTARI03")


class TestVM:
    """Test VM execution"""

    def test_load_const_and_print(self):
        """Test loading a constant and printing it"""
        vm = SyntariVM()

        # Manually construct simple bytecode
        vm.consts = [42]
        vm.code = bytes([0x01, 0, 0, 0, 0, 0x40, 0xFF])  # LOAD_CONST 0, PRINT, HALT
        vm.ninstr = 3

        # Run and capture output
        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        vm.run()
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "42" in output

    def test_arithmetic_operations(self):
        """Test arithmetic operations in VM"""
        vm = SyntariVM()

        # Test 2 + 3
        vm.consts = [2, 3]
        vm.code = bytes(
            [
                0x01,
                0,
                0,
                0,
                0,  # LOAD_CONST 0 (2)
                0x01,
                1,
                0,
                0,
                0,  # LOAD_CONST 1 (3)
                0x04,  # ADD
                0x40,  # PRINT
                0xFF,  # HALT
            ]
        )
        vm.ninstr = 5

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        vm.run()
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "5" in output

    def test_variable_store_and_load(self):
        """Test storing and loading variables"""
        vm = SyntariVM()

        # Store 42 to 'x', then load and print it
        vm.consts = [42]
        vm.code = (
            bytes([0x01, 0, 0, 0, 0])  # LOAD_CONST 0
            + bytes([0x02, 1, 0, 0, 0])  # STORE (name length 1)
            + b"x"  # name
            + bytes([0x03, 1, 0, 0, 0])  # LOAD (name length 1)
            + b"x"  # name
            + bytes([0x40])  # PRINT
            + bytes([0xFF])  # HALT
        )
        vm.ninstr = 5

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        vm.run()
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "42" in output

    def test_comparison_operations(self):
        """Test comparison operations in VM"""
        vm = SyntariVM()

        # Test 5 == 5
        vm.consts = [5, 5]
        vm.code = bytes(
            [
                0x01,
                0,
                0,
                0,
                0,  # LOAD_CONST 0 (5)
                0x01,
                1,
                0,
                0,
                0,  # LOAD_CONST 1 (5)
                0x10,  # EQ_EQ
                0x40,  # PRINT
                0xFF,  # HALT
            ]
        )
        vm.ninstr = 5

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        vm.run()
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "True" in output

    def test_jump_if_false(self):
        """Test conditional jump"""
        vm = SyntariVM()

        # Simple test: load False, jump if false, should skip the print
        vm.consts = [False, "should not print"]
        vm.code = bytes(
            [
                0x01,
                0,
                0,
                0,
                0,  # LOAD_CONST 0 (False) - bytes 0-4
                0x21,
                16,
                0,
                0,
                0,  # JMP_IF_FALSE to byte 16 - bytes 5-9
                # This section should be skipped:
                0x01,
                1,
                0,
                0,
                0,  # LOAD_CONST 1 - bytes 10-14
                0x40,  # PRINT - byte 15
                # Jump target (byte 16):
                0xFF,  # HALT - byte 16
            ]
        )

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        vm.run()
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        # Should not print anything
        assert "should not print" not in output

    def test_security_stack_overflow(self):
        """Test that stack overflow is detected"""
        vm = SyntariVM()
        vm.consts = [1]

        # Try to push too many values
        code = []
        for _ in range(11000):  # Exceeds MAX_STACK_SIZE
            code.extend([0x01, 0, 0, 0, 0])  # LOAD_CONST 0

        code.append(0xFF)  # HALT
        vm.code = bytes(code)
        vm.ninstr = 11001

        with pytest.raises(VMSecurityError, match="Stack overflow"):
            vm.run()

    def test_security_variable_limit(self):
        """Test that variable limit is enforced"""
        vm = SyntariVM()
        vm.consts = [1]

        # Try to create too many variables
        code = []
        for i in range(10001):  # Exceeds MAX_VARS
            code.extend([0x01, 0, 0, 0, 0])  # LOAD_CONST 0
            var_name = f"var{i}".encode("utf-8")
            code.extend([0x02, len(var_name), 0, 0, 0])  # STORE
            code.extend(var_name)

        code.append(0xFF)  # HALT
        vm.code = bytes(code)
        vm.ninstr = 20002

        with pytest.raises(VMSecurityError, match="Variable limit"):
            vm.run()


class TestEndToEnd:
    """Test end-to-end compilation and execution"""

    def test_simple_arithmetic(self):
        """Test compiling and running simple arithmetic"""
        code = "print(2 + 3)"

        tokens = tokenize(code)
        tree = Parser(tokens).parse()

        gen = BytecodeGenerator()
        gen.compile_node(tree)
        gen.finalize()

        # Get bytecode
        bytecode = gen.to_bytes()

        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix=".sbc", delete=False) as f:
            f.write(bytecode)
            temp_file = f.name

        try:
            # Load and run in VM
            vm = SyntariVM()
            vm.load_sbc(temp_file)

            import io
            import sys

            captured = io.StringIO()
            sys.stdout = captured
            vm.run()
            sys.stdout = sys.__stdout__

            output = captured.getvalue()
            assert "5" in output
        finally:
            os.unlink(temp_file)

    def test_variable_declaration_and_use(self):
        """Test variable declaration and usage"""
        code = """
let x = 10
let y = 20
print(x + y)
"""

        tokens = tokenize(code)
        tree = Parser(tokens).parse()

        gen = BytecodeGenerator()
        gen.compile_node(tree)
        gen.finalize()

        bytecode = gen.to_bytes()

        with tempfile.NamedTemporaryFile(suffix=".sbc", delete=False) as f:
            f.write(bytecode)
            temp_file = f.name

        try:
            vm = SyntariVM()
            vm.load_sbc(temp_file)

            import io
            import sys

            captured = io.StringIO()
            sys.stdout = captured
            vm.run()
            sys.stdout = sys.__stdout__

            output = captured.getvalue()
            assert "30" in output
        finally:
            os.unlink(temp_file)

    def test_if_statement(self):
        """Test if statement compilation and execution"""
        code = """
let x = 5
if (x == 5) {
    print("correct")
}
"""

        tokens = tokenize(code)
        tree = Parser(tokens).parse()

        gen = BytecodeGenerator()
        gen.compile_node(tree)
        gen.finalize()

        bytecode = gen.to_bytes()

        with tempfile.NamedTemporaryFile(suffix=".sbc", delete=False) as f:
            f.write(bytecode)
            temp_file = f.name

        try:
            vm = SyntariVM()
            vm.load_sbc(temp_file)

            import io
            import sys

            captured = io.StringIO()
            sys.stdout = captured
            vm.run()
            sys.stdout = sys.__stdout__

            output = captured.getvalue()
            assert "correct" in output
        finally:
            os.unlink(temp_file)

    def test_while_loop(self):
        """Test while loop compilation and execution"""
        code = """
let x = 0
while (x < 3) {
    print(x)
    x = x + 1
}
"""

        tokens = tokenize(code)
        tree = Parser(tokens).parse()

        gen = BytecodeGenerator()
        gen.compile_node(tree)
        gen.finalize()

        bytecode = gen.to_bytes()

        with tempfile.NamedTemporaryFile(suffix=".sbc", delete=False) as f:
            f.write(bytecode)
            temp_file = f.name

        try:
            vm = SyntariVM()
            vm.load_sbc(temp_file)

            import io
            import sys

            captured = io.StringIO()
            sys.stdout = captured
            vm.run()
            sys.stdout = sys.__stdout__

            output = captured.getvalue()
            # Should print 0, 1, 2
            assert "0" in output
            assert "1" in output
            assert "2" in output
        finally:
            os.unlink(temp_file)

    def test_compile_file_function(self):
        """Test the compile_file function"""
        # Create a temporary source file
        code = "let answer = 42\nprint(answer)"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".syn", delete=False) as f:
            f.write(code)
            source_file = f.name

        try:
            # Compile it
            output_file = compile_file(source_file)

            # Verify .sbc file was created
            assert os.path.exists(output_file)
            assert output_file.endswith(".sbc")

            # Run the bytecode
            vm = SyntariVM()
            vm.load_sbc(output_file)

            import io
            import sys

            captured = io.StringIO()
            sys.stdout = captured
            vm.run()
            sys.stdout = sys.__stdout__

            output = captured.getvalue()
            assert "42" in output

            # Clean up
            os.unlink(output_file)
        finally:
            os.unlink(source_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
