"""
Tests for Syntari main entry point (src/interpreter/main.py)
"""

import io
import os
import sys
import struct
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interpreter.main import (
    _validate_file_path,
    _validate_output_path,
    run_file,
    compile_file,
    run_bytecode,
    print_help,
    main,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_syn_file(source: str, suffix: str = ".syn") -> str:
    """Write source to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(source)
    f.close()
    return f.name


def _make_sbc_file() -> str:
    """Build a minimal valid SBC bytecode file and return its path."""
    # SYNTARI03 magic + 0 constants + 0 instructions + HALT opcode
    MAGIC = b"SYNTARI03"
    data = MAGIC
    data += struct.pack("<I", 0)  # nconst = 0
    data += struct.pack("<I", 1)  # ninstr = 1
    data += bytes([0xFF])  # HALT

    f = tempfile.NamedTemporaryFile(suffix=".sbc", delete=False)
    f.write(data)
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# _validate_file_path
# ---------------------------------------------------------------------------


class TestValidateFilePath:
    def test_valid_file_no_extension_check(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        result = _validate_file_path(str(f))
        assert result == str(f.resolve())

    def test_valid_file_with_correct_extension(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        result = _validate_file_path(str(f), allowed_extensions={".syn"})
        assert result == str(f.resolve())

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(ValueError, match="does not exist"):
            _validate_file_path(str(tmp_path / "missing.syn"))

    def test_directory_raises(self, tmp_path):
        with pytest.raises(ValueError, match="not a file"):
            _validate_file_path(str(tmp_path))

    def test_wrong_extension_raises(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        with pytest.raises(ValueError, match="Invalid file extension"):
            _validate_file_path(str(f), allowed_extensions={".syn"})


# ---------------------------------------------------------------------------
# _validate_output_path
# ---------------------------------------------------------------------------


class TestValidateOutputPath:
    def test_valid_output_path(self, tmp_path):
        out = tmp_path / "output.sbc"
        result = _validate_output_path(str(out))
        assert result == str(out.resolve())

    def test_valid_output_with_extension_check(self, tmp_path):
        out = tmp_path / "output.sbc"
        result = _validate_output_path(str(out), allowed_extensions={".sbc"})
        assert result == str(out.resolve())

    def test_nonexistent_parent_raises(self):
        with pytest.raises(ValueError, match="Parent directory"):
            _validate_output_path("/nonexistent/path/output.sbc")

    def test_wrong_extension_raises(self, tmp_path):
        out = tmp_path / "output.txt"
        with pytest.raises(ValueError, match="Invalid file extension"):
            _validate_output_path(str(out), allowed_extensions={".sbc"})


# ---------------------------------------------------------------------------
# run_file
# ---------------------------------------------------------------------------


class TestRunFile:
    def test_success_simple_program(self, capsys):
        path = _make_syn_file('print("hello")')
        try:
            code = run_file(path)
            assert code == 0
        finally:
            os.unlink(path)

    def test_success_verbose(self, capsys):
        path = _make_syn_file("let x = 42")
        try:
            code = run_file(path, verbose=True)
            assert code == 0
            captured = capsys.readouterr()
            assert "[Syntari]" in captured.out
        finally:
            os.unlink(path)

    def test_wrong_extension_returns_1(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("let x = 1")
        code = run_file(str(f))
        assert code == 1

    def test_file_not_found_returns_1(self):
        code = run_file("/nonexistent/path/test.syn")
        assert code == 1

    def test_lexer_error_returns_1(self):
        path = _make_syn_file("let $invalid = 1")
        try:
            code = run_file(path)
            assert code == 1
        finally:
            os.unlink(path)

    def test_parse_error_returns_1(self):
        path = _make_syn_file("let x =")  # incomplete expression
        try:
            code = run_file(path)
            assert code == 1
        finally:
            os.unlink(path)

    def test_runtime_error_returns_1(self):
        # Division by zero triggers RuntimeError
        path = _make_syn_file("let x = 1 / 0")
        try:
            code = run_file(path)
            assert code == 1
        finally:
            os.unlink(path)

    def test_keyboard_interrupt_returns_130(self):
        path = _make_syn_file("let x = 1")
        try:
            with patch("src.interpreter.main.interpret", side_effect=KeyboardInterrupt):
                code = run_file(path)
            assert code == 130
        finally:
            os.unlink(path)

    def test_unexpected_exception_returns_1(self):
        path = _make_syn_file("let x = 1")
        try:
            with patch("src.interpreter.main.interpret", side_effect=Exception("oops")):
                code = run_file(path)
            assert code == 1
        finally:
            os.unlink(path)

    def test_unexpected_exception_verbose(self, capsys):
        path = _make_syn_file("let x = 1")
        try:
            with patch("src.interpreter.main.interpret", side_effect=Exception("oops")):
                code = run_file(path, verbose=True)
            assert code == 1
        finally:
            os.unlink(path)

    def test_record_mode(self, tmp_path):
        path = _make_syn_file("let x = 42")
        record_path = str(tmp_path / "events.jsonl")
        try:
            code = run_file(path, record_path=record_path)
            assert code == 0
            assert Path(record_path).exists()
        finally:
            os.unlink(path)

    def test_record_mode_verbose(self, tmp_path, capsys):
        path = _make_syn_file("let x = 42")
        record_path = str(tmp_path / "events.jsonl")
        try:
            code = run_file(path, verbose=True, record_path=record_path)
            assert code == 0
            captured = capsys.readouterr()
            assert "Recording" in captured.out
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# compile_file
# ---------------------------------------------------------------------------


class TestCompileFile:
    def test_success_with_mock(self, tmp_path):
        src = tmp_path / "test.syn"
        src.write_text("let x = 1")
        out = str(tmp_path / "test.sbc")

        with patch("src.interpreter.main.compile_file") as mock_cf:
            mock_cf.return_value = 0
            # Test directly mocking bc_compile inside the function
            with patch.dict("sys.modules", {"bytecode": MagicMock()}):
                import importlib
                import sys as _sys

                fake_bc = MagicMock()
                fake_bc.compile_file = MagicMock(return_value=None)
                _sys.modules["bytecode"] = fake_bc
                result = compile_file(str(src), out, verbose=False)
                assert result == 0

    def test_file_not_found_returns_1(self):
        result = compile_file("/nonexistent/test.syn")
        assert result == 1

    def test_wrong_extension_returns_1(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        result = compile_file(str(f))
        assert result == 1

    def test_wrong_output_extension_returns_1(self, tmp_path):
        src = tmp_path / "test.syn"
        src.write_text("let x = 1")
        result = compile_file(str(src), str(tmp_path / "out.txt"))
        assert result == 1

    def test_compile_exception_returns_1(self, tmp_path):
        src = tmp_path / "test.syn"
        src.write_text("let x = 1")

        fake_bc = MagicMock()
        fake_bc.compile_file = MagicMock(side_effect=Exception("fail"))
        with patch.dict("sys.modules", {"bytecode": fake_bc}):
            result = compile_file(str(src), verbose=False)
            assert result == 1

    def test_compile_verbose_success(self, tmp_path):
        src = tmp_path / "test.syn"
        src.write_text("let x = 1")

        fake_bc = MagicMock()
        fake_bc.compile_file = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"bytecode": fake_bc}):
            result = compile_file(str(src), verbose=True)
            assert result == 0

    def test_auto_output_path(self, tmp_path):
        src = tmp_path / "test.syn"
        src.write_text("let x = 1")

        fake_bc = MagicMock()
        fake_bc.compile_file = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"bytecode": fake_bc}):
            result = compile_file(str(src))
            assert result == 0


# ---------------------------------------------------------------------------
# run_bytecode
# ---------------------------------------------------------------------------


class TestRunBytecode:
    def test_file_not_found_returns_1(self):
        result = run_bytecode("/nonexistent/test.sbc")
        assert result == 1

    def test_wrong_extension_returns_1(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"garbage")
        result = run_bytecode(str(f))
        assert result == 1

    def test_success_with_mock(self, tmp_path):
        sbc = tmp_path / "test.sbc"
        sbc.write_bytes(b"SYNTARI03" + b"\x00" * 8 + b"\xff")

        fake_runtime = MagicMock()
        fake_runtime.run_vm = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"runtime": fake_runtime}):
            result = run_bytecode(str(sbc), verbose=False)
            assert result == 0

    def test_success_verbose(self, tmp_path, capsys):
        sbc = tmp_path / "test.sbc"
        sbc.write_bytes(b"SYNTARI03" + b"\x00" * 8 + b"\xff")

        fake_runtime = MagicMock()
        fake_runtime.run_vm = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"runtime": fake_runtime}):
            result = run_bytecode(str(sbc), verbose=True)
            assert result == 0

    def test_vm_exception_returns_1(self, tmp_path):
        sbc = tmp_path / "test.sbc"
        sbc.write_bytes(b"SYNTARI03" + b"\x00" * 8 + b"\xff")

        fake_runtime = MagicMock()
        fake_runtime.run_vm = MagicMock(side_effect=Exception("VM crash"))
        with patch.dict("sys.modules", {"runtime": fake_runtime}):
            result = run_bytecode(str(sbc))
            assert result == 1


# ---------------------------------------------------------------------------
# print_help
# ---------------------------------------------------------------------------


class TestPrintHelp:
    def test_prints_help(self, capsys):
        print_help()
        captured = capsys.readouterr()
        assert "Syntari" in captured.out
        assert "exit" in captured.out


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def _run_main(self, argv):
        """Run main() with given argv list (excluding program name)."""
        with patch("sys.argv", ["syntari"] + argv):
            return main()

    def test_no_args_prints_help_returns_1(self, capsys):
        result = self._run_main([])
        assert result == 1

    def test_run_valid_file(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        result = self._run_main([str(f)])
        assert result == 0

    def test_run_missing_file(self):
        result = self._run_main(["/nonexistent/test.syn"])
        assert result == 1

    def test_verbose_flag(self, tmp_path, capsys):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        result = self._run_main(["--verbose", str(f)])
        assert result == 0
        captured = capsys.readouterr()
        assert "[Syntari]" in captured.out

    def test_compile_mode(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        fake_bc = MagicMock()
        fake_bc.compile_file = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"bytecode": fake_bc}):
            result = self._run_main(["--compile", str(f)])
            assert result == 0

    def test_compile_mode_with_output(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        out = str(tmp_path / "out.sbc")
        fake_bc = MagicMock()
        fake_bc.compile_file = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"bytecode": fake_bc}):
            result = self._run_main(["--compile", "-o", out, str(f)])
            assert result == 0

    def test_run_bytecode_mode(self, tmp_path):
        sbc = tmp_path / "test.sbc"
        sbc.write_bytes(b"SYNTARI03" + b"\x00" * 8 + b"\xff")
        fake_runtime = MagicMock()
        fake_runtime.run_vm = MagicMock(return_value=None)
        with patch.dict("sys.modules", {"runtime": fake_runtime}):
            result = self._run_main(["--run", str(sbc)])
            assert result == 0

    def test_repl_exits_on_eof(self):
        # Simulate REPL mode with immediate EOF
        with patch("builtins.input", side_effect=EOFError):
            result = self._run_main(["--repl"])
            assert result == 0

    def test_lsp_mode_error(self):
        # LSP server start() blocks; test that an error from it is handled
        with patch("src.tools.lsp.LSPServer") as MockLSP:
            MockLSP.return_value.start.side_effect = Exception("LSP failed")
            result = self._run_main(["--lsp"])
            assert result == 1

    def test_lsp_mode_success(self):
        with patch("src.tools.lsp.LSPServer") as MockLSP:
            MockLSP.return_value.start.return_value = None
            result = self._run_main(["--lsp"])
            assert result == 0

    def test_debug_mode(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        with patch("src.tools.debugger.SyntariDebugger") as MockDbg:
            mock_dbg = MagicMock()
            MockDbg.return_value = mock_dbg
            with patch("src.tools.debugger.DebuggableInterpreter"):
                result = self._run_main(["--debug", str(f)])
                assert result == 0

    def test_debug_mode_error(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        with patch("src.interpreter.main.parse", side_effect=Exception("oops")):
            result = self._run_main(["--debug", str(f)])
            assert result == 1

    def test_debug_mode_missing_file(self):
        result = self._run_main(["--debug", "/nonexistent/test.syn"])
        assert result == 1

    def test_profile_mode(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        with patch("src.tools.profiler.profile_interpreter", return_value=None):
            result = self._run_main(["--profile", str(f)])
            assert result == 0

    def test_profile_mode_error(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        with patch("src.tools.profiler.profile_interpreter", side_effect=Exception("oops")):
            result = self._run_main(["--profile", str(f)])
            assert result == 1

    def test_record_mode(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        result = self._run_main(["--record", str(f)])
        assert result == 0

    def test_record_mode_custom_output(self, tmp_path):
        f = tmp_path / "test.syn"
        f.write_text("let x = 1")
        out = str(tmp_path / "audit.jsonl")
        result = self._run_main(["--record", "--record-output", out, str(f)])
        assert result == 0


# ---------------------------------------------------------------------------
# REPL internals
# ---------------------------------------------------------------------------


class TestReplInternals:
    """Test individual REPL behaviors via the REPL input path."""

    def _run_repl_with_inputs(self, inputs):
        """Run REPL with a sequence of inputs then EOF."""
        input_iter = iter(inputs)

        def fake_input(prompt=""):
            try:
                return next(input_iter)
            except StopIteration:
                raise EOFError

        from src.interpreter.main import run_repl

        with patch("builtins.input", side_effect=fake_input):
            return run_repl()

    def test_exit_command(self):
        result = self._run_repl_with_inputs(["exit"])
        assert result == 0

    def test_quit_command(self):
        result = self._run_repl_with_inputs(["quit"])
        assert result == 0

    def test_help_command(self, capsys):
        result = self._run_repl_with_inputs(["help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Syntari" in captured.out

    def test_version_command(self, capsys):
        result = self._run_repl_with_inputs(["version"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Syntari" in captured.out

    def test_empty_line_ignored(self):
        result = self._run_repl_with_inputs(["", "exit"])
        assert result == 0

    def test_valid_expression(self, capsys):
        result = self._run_repl_with_inputs(["let x = 42", "exit"])
        assert result == 0

    def test_lexer_error_handled(self, capsys):
        result = self._run_repl_with_inputs(["let $bad = 1", "exit"])
        assert result == 0
        captured = capsys.readouterr()
        assert "error" in captured.out.lower()

    def test_parse_error_handled(self, capsys):
        result = self._run_repl_with_inputs(["let x =", "exit"])
        assert result == 0
        captured = capsys.readouterr()
        assert "error" in captured.out.lower()

    def test_runtime_error_handled(self, capsys):
        result = self._run_repl_with_inputs(["1 / 0", "exit"])
        assert result == 0
        captured = capsys.readouterr()
        assert "error" in captured.out.lower()

    def test_expression_result_printed(self, capsys):
        result = self._run_repl_with_inputs(["42", "exit"])
        assert result == 0
        captured = capsys.readouterr()
        assert "42" in captured.out

    def test_keyboard_interrupt_continues(self):
        inputs = [KeyboardInterrupt, "exit"]
        input_idx = [0]

        def fake_input(prompt=""):
            val = inputs[input_idx[0]]
            input_idx[0] += 1
            if isinstance(val, type) and issubclass(val, BaseException):
                raise val()
            return val

        from src.interpreter.main import run_repl

        with patch("builtins.input", side_effect=fake_input):
            result = run_repl()
        assert result == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
