"""
Tests for Syntari VM runtime (src/vm/runtime.py) - covers opcode execution,
security limits, constant parsing and load_sbc error paths.
"""

import io
import os
import struct
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vm.runtime import (
    MAGIC,
    MAX_CALL_DEPTH,
    MAX_INSTRUCTIONS,
    MAX_STACK_SIZE,
    MAX_STRING_LENGTH,
    MAX_VARS,
    OP,
    CallFrame,
    SyntariVM,
    VMSecurityError,
    run_vm,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _pack_u32(n: int) -> bytes:
    return struct.pack("<I", n)


def _pack_str(s: str) -> bytes:
    b = s.encode("utf-8")
    return _pack_u32(len(b)) + b


def _encode_const(value) -> bytes:
    """Encode a constant value with its type tag."""
    if value is None:
        s = "N"
    elif isinstance(value, bool):
        s = f"B{'1' if value else '0'}"
    elif isinstance(value, int):
        s = f"I{value}"
    elif isinstance(value, float):
        s = f"F{value}"
    else:
        s = f"S{value}"
    return _pack_str(s)


def _make_sbc(consts, code_bytes: bytes, ninstr: int = 0) -> bytes:
    """Build a complete SBC bytecode blob."""
    data = MAGIC
    data += _pack_u32(len(consts))
    for c in consts:
        data += _encode_const(c)
    data += _pack_u32(ninstr)
    data += code_bytes
    return data


def _write_sbc(consts, code_bytes: bytes, ninstr: int = 0) -> str:
    """Write SBC bytecode to a temp file and return the path."""
    data = _make_sbc(consts, code_bytes, ninstr)
    f = tempfile.NamedTemporaryFile(suffix=".sbc", delete=False)
    f.write(data)
    f.close()
    return f.name


def _run_vm_direct(vm: SyntariVM, consts, code_bytes: bytes):
    """Set consts/code directly and run, capturing stdout."""
    vm.consts = list(consts)
    vm.code = code_bytes
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        vm.run(verbose=False)
    finally:
        sys.stdout = old_stdout
    return captured.getvalue()


def _run(consts, code_bytes: bytes) -> str:
    """Convenience: create a VM, run code, return stdout."""
    vm = SyntariVM()
    return _run_vm_direct(vm, consts, code_bytes)


def _lc(idx: int) -> bytes:
    """LOAD_CONST <idx>"""
    return bytes([0x01]) + _pack_u32(idx)


def _store(name: str) -> bytes:
    """STORE <name>"""
    return bytes([0x02]) + _pack_str(name)


def _load(name: str) -> bytes:
    """LOAD <name>"""
    return bytes([0x03]) + _pack_str(name)


def _jmp(addr: int) -> bytes:
    return bytes([0x20]) + _pack_u32(addr)


def _jmp_if_false(addr: int) -> bytes:
    return bytes([0x21]) + _pack_u32(addr)


def _jmp_if_true(addr: int) -> bytes:
    return bytes([0x22]) + _pack_u32(addr)


def _call(name: str, argc: int) -> bytes:
    return bytes([0x30]) + _pack_str(name) + _pack_u32(argc)


HALT = bytes([0xFF])
PRINT = bytes([0x40])
POP = bytes([0x50])
DUP = bytes([0x51])
ADD = bytes([0x04])
SUB = bytes([0x05])
MUL = bytes([0x06])
DIV = bytes([0x07])
MOD = bytes([0x08])
EQ_EQ = bytes([0x10])
NOT_EQ = bytes([0x11])
LT = bytes([0x12])
LT_EQ = bytes([0x13])
GT = bytes([0x14])
GT_EQ = bytes([0x15])
AND = bytes([0x16])
OR = bytes([0x17])
NOT = bytes([0x18])
NEG = bytes([0x19])
RETURN = bytes([0x31])


# ---------------------------------------------------------------------------
# CallFrame
# ---------------------------------------------------------------------------


class TestCallFrame:
    def test_default_locals(self):
        frame = CallFrame(return_ip=10)
        assert frame.return_ip == 10
        assert frame.local_vars == {}

    def test_custom_locals(self):
        frame = CallFrame(return_ip=5, local_vars={"x": 42})
        assert frame.local_vars == {"x": 42}


# ---------------------------------------------------------------------------
# VM internals
# ---------------------------------------------------------------------------


class TestVMInternals:
    def test_is_truthy_none(self):
        vm = SyntariVM()
        assert vm._is_truthy(None) is False

    def test_is_truthy_false(self):
        vm = SyntariVM()
        assert vm._is_truthy(False) is False

    def test_is_truthy_zero(self):
        vm = SyntariVM()
        assert vm._is_truthy(0) is False

    def test_is_truthy_empty_string(self):
        vm = SyntariVM()
        assert vm._is_truthy("") is False

    def test_is_truthy_empty_list(self):
        vm = SyntariVM()
        assert vm._is_truthy([]) is False

    def test_is_truthy_truthy_values(self):
        vm = SyntariVM()
        assert vm._is_truthy(1) is True
        assert vm._is_truthy("hello") is True
        assert vm._is_truthy(True) is True
        assert vm._is_truthy([1]) is True

    def test_push_pop(self):
        vm = SyntariVM()
        vm._push(42)
        assert vm._pop() == 42

    def test_stack_underflow_raises(self):
        vm = SyntariVM()
        with pytest.raises(RuntimeError, match="Stack underflow"):
            vm._pop()

    def test_fetch_u8(self):
        vm = SyntariVM()
        vm.code = bytes([0xAB, 0xCD])
        vm.ip = 0
        assert vm._fetch_u8() == 0xAB
        assert vm.ip == 1

    def test_fetch_u32(self):
        vm = SyntariVM()
        vm.code = struct.pack("<I", 12345) + b"\x00"
        vm.ip = 0
        assert vm._fetch_u32() == 12345
        assert vm.ip == 4

    def test_fetch_str(self):
        vm = SyntariVM()
        name = "hello"
        vm.code = _pack_str(name)
        vm.ip = 0
        assert vm._fetch_str() == name

    def test_fetch_str_too_long_raises(self):
        vm = SyntariVM()
        # Write a length that exceeds MAX_STRING_LENGTH
        vm.code = _pack_u32(MAX_STRING_LENGTH + 1) + b"\x00"
        vm.ip = 0
        with pytest.raises(VMSecurityError, match="String length"):
            vm._fetch_str()


# ---------------------------------------------------------------------------
# Arithmetic opcodes
# ---------------------------------------------------------------------------


class TestArithmeticOpcodes:
    def test_sub(self):
        code = _lc(0) + _lc(1) + SUB + PRINT + HALT
        out = _run([10, 3], code)
        assert "7" in out

    def test_mul(self):
        code = _lc(0) + _lc(1) + MUL + PRINT + HALT
        out = _run([4, 5], code)
        assert "20" in out

    def test_div(self):
        code = _lc(0) + _lc(1) + DIV + PRINT + HALT
        out = _run([10, 2], code)
        assert "5.0" in out

    def test_div_by_zero_raises(self):
        vm = SyntariVM()
        vm.consts = [10, 0]
        vm.code = _lc(0) + _lc(1) + DIV + HALT
        with pytest.raises(RuntimeError, match="Division by zero"):
            vm.run(verbose=False)

    def test_mod(self):
        code = _lc(0) + _lc(1) + MOD + PRINT + HALT
        out = _run([10, 3], code)
        assert "1" in out

    def test_mod_by_zero_raises(self):
        vm = SyntariVM()
        vm.consts = [10, 0]
        vm.code = _lc(0) + _lc(1) + MOD + HALT
        with pytest.raises(RuntimeError, match="Modulo by zero"):
            vm.run(verbose=False)

    def test_neg(self):
        code = _lc(0) + NEG + PRINT + HALT
        out = _run([5], code)
        assert "-5" in out


# ---------------------------------------------------------------------------
# Comparison opcodes
# ---------------------------------------------------------------------------


class TestComparisonOpcodes:
    def test_not_eq_true(self):
        code = _lc(0) + _lc(1) + NOT_EQ + PRINT + HALT
        out = _run([5, 3], code)
        assert "True" in out

    def test_not_eq_false(self):
        code = _lc(0) + _lc(1) + NOT_EQ + PRINT + HALT
        out = _run([5, 5], code)
        assert "False" in out

    def test_lt(self):
        code = _lc(0) + _lc(1) + LT + PRINT + HALT
        out = _run([3, 5], code)
        assert "True" in out

    def test_lt_false(self):
        code = _lc(0) + _lc(1) + LT + PRINT + HALT
        out = _run([5, 3], code)
        assert "False" in out

    def test_lt_eq_equal(self):
        code = _lc(0) + _lc(1) + LT_EQ + PRINT + HALT
        out = _run([5, 5], code)
        assert "True" in out

    def test_lt_eq_less(self):
        code = _lc(0) + _lc(1) + LT_EQ + PRINT + HALT
        out = _run([3, 5], code)
        assert "True" in out

    def test_lt_eq_greater(self):
        code = _lc(0) + _lc(1) + LT_EQ + PRINT + HALT
        out = _run([5, 3], code)
        assert "False" in out

    def test_gt(self):
        code = _lc(0) + _lc(1) + GT + PRINT + HALT
        out = _run([5, 3], code)
        assert "True" in out

    def test_gt_false(self):
        code = _lc(0) + _lc(1) + GT + PRINT + HALT
        out = _run([3, 5], code)
        assert "False" in out

    def test_gt_eq_equal(self):
        code = _lc(0) + _lc(1) + GT_EQ + PRINT + HALT
        out = _run([5, 5], code)
        assert "True" in out

    def test_gt_eq_greater(self):
        code = _lc(0) + _lc(1) + GT_EQ + PRINT + HALT
        out = _run([5, 3], code)
        assert "True" in out

    def test_gt_eq_less(self):
        code = _lc(0) + _lc(1) + GT_EQ + PRINT + HALT
        out = _run([3, 5], code)
        assert "False" in out


# ---------------------------------------------------------------------------
# Logical opcodes
# ---------------------------------------------------------------------------


class TestLogicalOpcodes:
    def test_and_true(self):
        code = _lc(0) + _lc(1) + AND + PRINT + HALT
        out = _run([True, True], code)
        assert "True" in out

    def test_and_false(self):
        code = _lc(0) + _lc(1) + AND + PRINT + HALT
        out = _run([True, False], code)
        assert "False" in out

    def test_or_true(self):
        code = _lc(0) + _lc(1) + OR + PRINT + HALT
        out = _run([False, True], code)
        assert "True" in out

    def test_or_false(self):
        code = _lc(0) + _lc(1) + OR + PRINT + HALT
        out = _run([False, False], code)
        assert "False" in out

    def test_not_true(self):
        code = _lc(0) + NOT + PRINT + HALT
        out = _run([True], code)
        assert "False" in out

    def test_not_false(self):
        code = _lc(0) + NOT + PRINT + HALT
        out = _run([False], code)
        assert "True" in out


# ---------------------------------------------------------------------------
# Control flow opcodes
# ---------------------------------------------------------------------------


class TestControlFlowOpcodes:
    def test_jmp_unconditional(self):
        # JMP past a PRINT, so nothing is printed; then HALT
        code = (
            _lc(0)  # bytes 0-4: LOAD_CONST 0 ("skip")
            + _jmp(16)  # bytes 5-9: JMP to byte 16
            + _lc(0)  # bytes 10-14: LOAD_CONST 0 (skipped)
            + PRINT  # byte 15: PRINT (skipped)
            + HALT  # byte 16: HALT
        )
        out = _run(["skip"], code)
        assert "skip" not in out

    def test_jmp_if_false_taken(self):
        # condition=False → jump past the print
        code = (
            _lc(0)  # bytes 0-4: LOAD_CONST 0 (False)
            + _jmp_if_false(16)  # bytes 5-9: JMP_IF_FALSE → 16
            + _lc(1)  # bytes 10-14: LOAD_CONST 1 ("nope") - skipped
            + PRINT  # byte 15: PRINT - skipped
            + HALT  # byte 16
        )
        out = _run([False, "nope"], code)
        assert "nope" not in out

    def test_jmp_if_false_not_taken(self):
        # condition=True → do NOT jump, print the value
        code = (
            _lc(0)  # bytes 0-4: LOAD_CONST 0 (True)
            + _jmp_if_false(16)  # bytes 5-9: JMP_IF_FALSE (not taken)
            + _lc(1)  # bytes 10-14: LOAD_CONST 1 ("yes")
            + PRINT  # byte 15
            + HALT  # byte 16
        )
        out = _run([True, "yes"], code)
        assert "yes" in out

    def test_jmp_if_true_taken(self):
        # condition=True → jump
        code = (
            _lc(0)  # bytes 0-4: LOAD_CONST 0 (True)
            + _jmp_if_true(16)  # bytes 5-9: JMP_IF_TRUE → 16
            + _lc(1)  # bytes 10-14: LOAD_CONST 1 (skipped)
            + PRINT  # byte 15 (skipped)
            + HALT  # byte 16
        )
        out = _run([True, "skipped"], code)
        assert "skipped" not in out

    def test_jmp_if_true_not_taken(self):
        # condition=False → do NOT jump
        code = (
            _lc(0)  # bytes 0-4: LOAD_CONST 0 (False)
            + _jmp_if_true(16)  # bytes 5-9: JMP_IF_TRUE (not taken)
            + _lc(1)  # bytes 10-14: LOAD_CONST 1 ("yes")
            + PRINT  # byte 15
            + HALT  # byte 16
        )
        out = _run([False, "yes"], code)
        assert "yes" in out

    def test_invalid_jmp_address_raises(self):
        vm = SyntariVM()
        vm.consts = []
        # JMP to an address beyond end of code
        vm.code = _jmp(9999) + HALT
        with pytest.raises(RuntimeError, match="Invalid jump address"):
            vm.run(verbose=False)

    def test_invalid_jmp_if_false_address_raises(self):
        vm = SyntariVM()
        vm.consts = [False]
        vm.code = _lc(0) + _jmp_if_false(9999) + HALT
        with pytest.raises(RuntimeError, match="Invalid jump address"):
            vm.run(verbose=False)

    def test_invalid_jmp_if_true_address_raises(self):
        vm = SyntariVM()
        vm.consts = [True]
        vm.code = _lc(0) + _jmp_if_true(9999) + HALT
        with pytest.raises(RuntimeError, match="Invalid jump address"):
            vm.run(verbose=False)

    def test_return_from_main_halts(self):
        """RETURN with empty call stack should halt execution."""
        code = RETURN + _lc(0) + PRINT + HALT
        out = _run(["never"], code)
        assert "never" not in out


# ---------------------------------------------------------------------------
# Stack opcodes
# ---------------------------------------------------------------------------


class TestStackOpcodes:
    def test_pop(self):
        code = _lc(0) + POP + HALT
        out = _run([42], code)
        # Just verify no crash; nothing printed
        assert out == ""

    def test_dup(self):
        # DUP then print twice
        code = _lc(0) + DUP + PRINT + PRINT + HALT
        out = _run(["hi"], code)
        assert out.count("hi") == 2


# ---------------------------------------------------------------------------
# I/O and CALL opcodes
# ---------------------------------------------------------------------------


class TestIOAndCallOpcodes:
    def test_print_opcode(self, capsys):
        code = _lc(0) + PRINT + HALT
        _run(["hello"], code)
        # Already captured in _run via StringIO; just verify no exception

    def test_call_print_builtin(self):
        # CALL print with 1 argument
        code = _lc(0) + _call("print", 1) + POP + HALT
        out = _run(["world"], code)
        assert "world" in out

    def test_call_print_multiple_args(self):
        # CALL print with 2 arguments
        code = _lc(0) + _lc(1) + _call("print", 2) + POP + HALT
        out = _run(["hello", "world"], code)
        assert "hello" in out
        assert "world" in out

    def test_call_undefined_function_raises(self):
        vm = SyntariVM()
        vm.consts = []
        vm.code = _call("undefined_func", 0) + HALT
        with pytest.raises(NotImplementedError, match="undefined_func"):
            vm.run(verbose=False)


# ---------------------------------------------------------------------------
# Variable opcodes
# ---------------------------------------------------------------------------


class TestVariableOpcodes:
    def test_store_and_load(self):
        code = _lc(0) + _store("x") + _load("x") + PRINT + HALT
        out = _run([99], code)
        assert "99" in out

    def test_load_undefined_raises(self):
        vm = SyntariVM()
        vm.consts = []
        vm.code = _load("undefined_var") + HALT
        with pytest.raises(RuntimeError, match="Undefined variable"):
            vm.run(verbose=False)

    def test_load_const_invalid_index_raises(self):
        vm = SyntariVM()
        vm.consts = [1]
        vm.code = _lc(99) + HALT  # index 99 out of range
        with pytest.raises(RuntimeError, match="Invalid constant index"):
            vm.run(verbose=False)


# ---------------------------------------------------------------------------
# Unknown opcode
# ---------------------------------------------------------------------------


class TestUnknownOpcode:
    def test_unknown_opcode_raises(self):
        vm = SyntariVM()
        vm.consts = []
        vm.code = bytes([0xEE, 0xFF])  # 0xEE is not a known opcode
        with pytest.raises(RuntimeError, match="Unknown opcode"):
            vm.run(verbose=False)


# ---------------------------------------------------------------------------
# Verbose run
# ---------------------------------------------------------------------------


class TestVerboseRun:
    def test_verbose_output(self, capsys):
        vm = SyntariVM()
        vm.consts = []
        vm.code = HALT
        vm.run(verbose=True)
        captured = capsys.readouterr()
        assert "Execution complete" in captured.out


# ---------------------------------------------------------------------------
# Security limits
# ---------------------------------------------------------------------------


class TestSecurityLimits:
    def test_instruction_limit_exceeded(self):
        """Executing more than MAX_INSTRUCTIONS instructions raises VMSecurityError."""
        vm = SyntariVM()
        vm.consts = [1]
        # Build a tight loop by loading and popping constantly
        # but make it finite enough to not run forever in the test
        # We'll set executed artificially near the limit
        vm.consts = [1]
        # Build code that has a backward jump (infinite loop)
        # JMP 0 → forever
        vm.code = _jmp(0) + HALT
        with pytest.raises(VMSecurityError, match="Instruction limit"):
            vm.run(verbose=False)

    def test_call_depth_limit_exceeded(self):
        """Calling a user-defined function when call stack is at max depth raises error."""
        vm = SyntariVM()
        vm.consts = []
        # Fill the call stack manually beyond the limit
        for i in range(MAX_CALL_DEPTH + 1):
            vm.call_stack.append(CallFrame(return_ip=0))
        vm.code = _call("some_func", 0) + HALT
        with pytest.raises(VMSecurityError, match="Call depth"):
            vm.run(verbose=False)


# ---------------------------------------------------------------------------
# load_sbc – constant parsing
# ---------------------------------------------------------------------------


class TestLoadSBCConstantParsing:
    def _load_from_bytes(self, data: bytes) -> SyntariVM:
        f = tempfile.NamedTemporaryFile(suffix=".sbc", delete=False)
        f.write(data)
        f.close()
        vm = SyntariVM()
        try:
            vm.load_sbc(f.name)
        finally:
            os.unlink(f.name)
        return vm

    def test_string_constant(self):
        path = _write_sbc(["hello"], HALT)
        vm = SyntariVM()
        vm.load_sbc(path)
        os.unlink(path)
        assert vm.consts == ["hello"]

    def test_integer_constant(self):
        path = _write_sbc([42], HALT)
        vm = SyntariVM()
        vm.load_sbc(path)
        os.unlink(path)
        assert vm.consts == [42]

    def test_float_constant(self):
        path = _write_sbc([3.14], HALT)
        vm = SyntariVM()
        vm.load_sbc(path)
        os.unlink(path)
        assert vm.consts == [3.14]

    def test_bool_true_constant(self):
        path = _write_sbc([True], HALT)
        vm = SyntariVM()
        vm.load_sbc(path)
        os.unlink(path)
        assert vm.consts == [True]

    def test_bool_false_constant(self):
        path = _write_sbc([False], HALT)
        vm = SyntariVM()
        vm.load_sbc(path)
        os.unlink(path)
        assert vm.consts == [False]

    def test_none_constant(self):
        path = _write_sbc([None], HALT)
        vm = SyntariVM()
        vm.load_sbc(path)
        os.unlink(path)
        assert vm.consts == [None]

    def test_legacy_true_constant(self):
        """Legacy bytecode that uses 'True' string directly (starts with 'T', not a type tag)."""
        data = MAGIC + _pack_u32(1) + _pack_str("True") + _pack_u32(1) + HALT
        vm = self._load_from_bytes(data)
        assert vm.consts == [True]

    def test_legacy_integer_constant(self):
        data = MAGIC + _pack_u32(1) + _pack_str("42") + _pack_u32(1) + HALT
        vm = self._load_from_bytes(data)
        assert vm.consts == [42]

    def test_legacy_float_constant(self):
        data = MAGIC + _pack_u32(1) + _pack_str("3.14") + _pack_u32(1) + HALT
        vm = self._load_from_bytes(data)
        assert vm.consts == [3.14]

    def test_legacy_string_constant(self):
        data = MAGIC + _pack_u32(1) + _pack_str("hello world") + _pack_u32(1) + HALT
        vm = self._load_from_bytes(data)
        assert vm.consts == ["hello world"]


# ---------------------------------------------------------------------------
# load_sbc – error paths
# ---------------------------------------------------------------------------


class TestLoadSBCErrors:
    def _write(self, data: bytes) -> str:
        f = tempfile.NamedTemporaryFile(suffix=".sbc", delete=False)
        f.write(data)
        f.close()
        return f.name

    def test_bad_magic(self):
        path = self._write(b"BADMAGIC!!" + b"\x00" * 20)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="bad magic"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_file_too_large_raises(self, tmp_path):
        """Simulate an oversized file by patching open."""
        from unittest.mock import patch, MagicMock

        big_data = b"X" * (101 * 1024 * 1024)  # > 100MB
        path = str(tmp_path / "big.sbc")

        m = MagicMock()
        m.__enter__ = MagicMock(return_value=MagicMock(read=MagicMock(return_value=big_data)))
        m.__exit__ = MagicMock(return_value=False)

        vm = SyntariVM()
        with patch("builtins.open", return_value=m):
            with pytest.raises(VMSecurityError, match="Bytecode file size"):
                vm.load_sbc(path)

    def test_truncated_after_magic(self):
        path = self._write(MAGIC + b"\x01")  # nconst needs 4 bytes, only 1 provided
        vm = SyntariVM()
        try:
            with pytest.raises((ValueError, struct.error)):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_truncated_constant_data(self):
        # Claim 1 constant with length 100, but provide only 5 bytes
        data = MAGIC + _pack_u32(1) + _pack_u32(100) + b"hello"
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="Truncated bytecode"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_empty_constant_raises(self):
        # Constant of length 0 → empty string is invalid
        data = MAGIC + _pack_u32(1) + _pack_u32(0) + _pack_u32(1) + HALT
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="empty constant"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_invalid_integer_constant(self):
        # 'I' tag with non-numeric payload
        data = MAGIC + _pack_u32(1) + _pack_str("Inot_a_number") + _pack_u32(1) + HALT
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="Invalid integer constant"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_invalid_float_constant(self):
        data = MAGIC + _pack_u32(1) + _pack_str("Fnot_a_float") + _pack_u32(1) + HALT
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="Invalid float constant"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_invalid_bool_constant(self):
        data = MAGIC + _pack_u32(1) + _pack_str("B2") + _pack_u32(1) + HALT
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="Invalid boolean constant"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_invalid_none_constant_has_payload(self):
        data = MAGIC + _pack_u32(1) + _pack_str("Nextra") + _pack_u32(1) + HALT
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="Invalid None constant"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_truncated_before_ninstr(self):
        # Valid consts section but no ninstr bytes
        data = MAGIC + _pack_u32(0)  # nconst=0, no ninstr
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(ValueError, match="Truncated bytecode"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)

    def test_too_many_instructions_raises(self):
        # ninstr > MAX_INSTRUCTIONS
        data = MAGIC + _pack_u32(0) + _pack_u32(MAX_INSTRUCTIONS + 1) + HALT
        path = self._write(data)
        vm = SyntariVM()
        try:
            with pytest.raises(VMSecurityError, match="Too many instructions"):
                vm.load_sbc(path)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# run_vm function
# ---------------------------------------------------------------------------


class TestRunVM:
    def test_run_vm_function(self, capsys):
        path = _write_sbc(["hello!"], _lc(0) + PRINT + HALT, ninstr=3)
        try:
            run_vm(path, verbose=False)
            captured = capsys.readouterr()
            assert "hello!" in captured.out
        finally:
            os.unlink(path)

    def test_run_vm_verbose(self, capsys):
        path = _write_sbc([], HALT, ninstr=1)
        try:
            run_vm(path, verbose=True)
            captured = capsys.readouterr()
            assert "Execution complete" in captured.out
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# OP mapping / module constants
# ---------------------------------------------------------------------------


class TestModuleConstants:
    def test_op_mapping_complete(self):
        assert 0x01 in OP
        assert 0xFF in OP
        assert OP[0xFF] == "HALT"

    def test_security_limit_constants(self):
        assert MAX_STACK_SIZE == 10000
        assert MAX_INSTRUCTIONS == 1000000
        assert MAX_VARS == 10000
        assert MAX_CALL_DEPTH == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
