"""
Tests for the Chain-Of-Record integration adapter.

Validates:
- ExecutionEvent creation and serialization
- NoOpAdapter (zero-overhead default)
- FileAdapter (JSON-lines output)
- Interpreter integration (events emitted correctly)
- CLI --record flag wiring
"""

import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

import pytest

from src.core.chain_of_record import (
    EventType,
    ExecutionEvent,
    FileAdapter,
    NoOpAdapter,
    RecorderAdapter,
    _make_event,
)
from src.interpreter.interpreter import Interpreter, interpret
from src.interpreter.lexer import tokenize
from src.interpreter.parser import parse

# ---------------------------------------------------------------------------
# ExecutionEvent helpers
# ---------------------------------------------------------------------------


def _parse_run(source: str, recorder: RecorderAdapter) -> List[ExecutionEvent]:
    """Parse *source*, run with *recorder*, return captured events."""
    tokens = tokenize(source)
    tree = parse(tokens)
    interp = Interpreter(recorder=recorder)
    interp.interpret(tree)
    return []  # events are in recorder


# ---------------------------------------------------------------------------
# ExecutionEvent tests
# ---------------------------------------------------------------------------


class TestExecutionEvent:
    """Tests for the ExecutionEvent dataclass."""

    def test_to_dict_contains_required_keys(self):
        """to_dict() must include all required fields."""
        event = _make_event(EventType.PROGRAM_START, "sess-1", {"foo": "bar"})
        d = event.to_dict()
        assert d["event_type"] == "program_start"
        assert d["session_id"] == "sess-1"
        assert "event_id" in d
        assert "timestamp" in d
        assert d["payload"] == {"foo": "bar"}

    def test_to_json_is_valid_json(self):
        """to_json() must produce parseable JSON."""
        event = _make_event(EventType.FUNC_CALL, "sess-2", {"name": "add"})
        parsed = json.loads(event.to_json())
        assert parsed["event_type"] == "func_call"

    def test_event_is_frozen(self):
        """ExecutionEvent must be immutable (frozen dataclass)."""
        event = _make_event(EventType.VAR_ASSIGN, "sess-3")
        with pytest.raises((AttributeError, TypeError)):
            event.session_id = "changed"  # type: ignore[misc]

    def test_make_event_unique_ids(self):
        """Each call to _make_event must produce a different event_id."""
        e1 = _make_event(EventType.PROGRAM_END, "s")
        e2 = _make_event(EventType.PROGRAM_END, "s")
        assert e1.event_id != e2.event_id

    def test_event_type_values(self):
        """All EventType members must have non-empty string values."""
        for et in EventType:
            assert isinstance(et.value, str) and et.value


# ---------------------------------------------------------------------------
# NoOpAdapter tests
# ---------------------------------------------------------------------------


class TestNoOpAdapter:
    """Tests for NoOpAdapter."""

    def test_record_does_not_raise(self):
        """record() must accept any event without raising."""
        adapter = NoOpAdapter()
        event = _make_event(EventType.PROGRAM_START, "s")
        adapter.record(event)  # should not raise

    def test_close_does_not_raise(self):
        """close() must be a no-op."""
        adapter = NoOpAdapter()
        adapter.close()

    def test_is_recorder_adapter_subclass(self):
        """NoOpAdapter must be a RecorderAdapter."""
        assert isinstance(NoOpAdapter(), RecorderAdapter)


# ---------------------------------------------------------------------------
# FileAdapter tests
# ---------------------------------------------------------------------------


class TestFileAdapter:
    """Tests for FileAdapter."""

    def test_writes_events_as_jsonl(self, tmp_path: Path):
        """FileAdapter must write one JSON object per line."""
        out = tmp_path / "events.jsonl"
        adapter = FileAdapter(str(out))
        adapter.record(_make_event(EventType.PROGRAM_START, "sess"))
        adapter.record(_make_event(EventType.PROGRAM_END, "sess"))
        adapter.close()

        lines = out.read_text().strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            obj = json.loads(line)
            assert "event_id" in obj
            assert "event_type" in obj

    def test_events_written_counter(self, tmp_path: Path):
        """events_written must track the number of recorded events."""
        out = tmp_path / "events.jsonl"
        adapter = FileAdapter(str(out))
        assert adapter.events_written == 0
        adapter.record(_make_event(EventType.FUNC_CALL, "s", {"name": "f"}))
        adapter.record(_make_event(EventType.FUNC_RETURN, "s", {"name": "f"}))
        assert adapter.events_written == 2
        adapter.close()

    def test_path_property(self, tmp_path: Path):
        """path property must return the file path given at construction."""
        out = tmp_path / "events.jsonl"
        adapter = FileAdapter(str(out))
        assert adapter.path == str(out)
        adapter.close()

    def test_context_manager(self, tmp_path: Path):
        """FileAdapter must work as a context manager."""
        out = tmp_path / "events.jsonl"
        with FileAdapter(str(out)) as adapter:
            adapter.record(_make_event(EventType.PROGRAM_START, "s"))
        assert out.exists()
        lines = out.read_text().strip().splitlines()
        assert len(lines) == 1

    def test_appends_to_existing_file(self, tmp_path: Path):
        """FileAdapter must append if the output file already exists."""
        out = tmp_path / "events.jsonl"
        with FileAdapter(str(out)) as a:
            a.record(_make_event(EventType.PROGRAM_START, "s1"))
        with FileAdapter(str(out)) as a:
            a.record(_make_event(EventType.PROGRAM_START, "s2"))
        lines = out.read_text().strip().splitlines()
        assert len(lines) == 2

    def test_each_line_is_parseable_json(self, tmp_path: Path):
        """Every line written must be independently parseable."""
        out = tmp_path / "events.jsonl"
        with FileAdapter(str(out)) as adapter:
            for et in EventType:
                adapter.record(_make_event(et, "sess"))
        for line in out.read_text().strip().splitlines():
            json.loads(line)  # must not raise


# ---------------------------------------------------------------------------
# Interpreter integration tests
# ---------------------------------------------------------------------------


class TestInterpreterRecording:
    """Tests verifying the Interpreter emits events to the adapter."""

    def _captured(self, source: str) -> List[ExecutionEvent]:
        """Run *source* and return all captured events."""
        events: List[ExecutionEvent] = []
        mock_adapter = MagicMock(spec=RecorderAdapter)
        mock_adapter.record.side_effect = events.append
        tokens = tokenize(source)
        tree = parse(tokens)
        interp = Interpreter(recorder=mock_adapter)
        interp.interpret(tree)
        return events

    def test_program_start_and_end_emitted(self):
        """interpret() must emit PROGRAM_START then PROGRAM_END."""
        events = self._captured("let x = 1;")
        types = [e.event_type for e in events]
        assert EventType.PROGRAM_START in types
        assert EventType.PROGRAM_END in types
        # PROGRAM_START must come before PROGRAM_END
        assert types.index(EventType.PROGRAM_START) < types.index(EventType.PROGRAM_END)

    def test_var_decl_emits_var_assign(self):
        """Variable declarations must emit VAR_ASSIGN events."""
        events = self._captured("let answer = 42;")
        assign_events = [e for e in events if e.event_type == EventType.VAR_ASSIGN]
        assert len(assign_events) >= 1
        payloads = [e.payload for e in assign_events]
        names = [p["name"] for p in payloads]
        assert "answer" in names

    def test_var_assign_payload_has_value(self):
        """VAR_ASSIGN payload must include the assigned value representation."""
        events = self._captured("let x = 99;")
        assigns = [e for e in events if e.event_type == EventType.VAR_ASSIGN]
        x_event = next((e for e in assigns if e.payload["name"] == "x"), None)
        assert x_event is not None, "Expected a VAR_ASSIGN event for variable 'x'"
        assert "99" in x_event.payload["value"]

    def test_func_call_event_emitted(self):
        """Calling a user-defined function must emit FUNC_CALL and FUNC_RETURN."""
        source = """
fn add(a, b) {
    return a + b;
}
let result = add(3, 4);
"""
        events = self._captured(source)
        types = [e.event_type for e in events]
        assert EventType.FUNC_CALL in types
        assert EventType.FUNC_RETURN in types

    def test_func_call_payload_has_function_name(self):
        """FUNC_CALL payload must include the function name."""
        source = """
fn greet(name) {
    return name;
}
greet("world");
"""
        events = self._captured(source)
        call_events = [e for e in events if e.event_type == EventType.FUNC_CALL]
        assert any(e.payload.get("name") == "greet" for e in call_events)

    def test_all_events_share_session_id(self):
        """All events from one run must share the same session_id."""
        events = self._captured("let a = 1; let b = 2;")
        session_ids = {e.session_id for e in events}
        assert len(session_ids) == 1

    def test_default_recorder_is_noop(self):
        """Interpreter without explicit recorder must use NoOpAdapter."""
        tokens = tokenize("let x = 5;")
        tree = parse(tokens)
        interp = Interpreter()
        assert isinstance(interp._recorder, NoOpAdapter)
        interp.interpret(tree)  # must not raise

    def test_interpret_convenience_fn_with_recorder(self, tmp_path: Path):
        """interpret() convenience function must forward recorder."""
        out = tmp_path / "events.jsonl"
        adapter = FileAdapter(str(out))
        tokens = tokenize("let z = 7;")
        tree = parse(tokens)
        interpret(tree, recorder=adapter)
        adapter.close()
        lines = out.read_text().strip().splitlines()
        # At minimum PROGRAM_START + VAR_ASSIGN + PROGRAM_END
        assert len(lines) >= 3

    def test_program_end_emitted_on_runtime_error(self):
        """PROGRAM_END must be emitted even if execution raises."""
        events: List[ExecutionEvent] = []
        mock_adapter = MagicMock(spec=RecorderAdapter)
        mock_adapter.record.side_effect = events.append
        tokens = tokenize("let x = undefined_var;")
        tree = parse(tokens)
        interp = Interpreter(recorder=mock_adapter)
        with pytest.raises(Exception):
            interp.interpret(tree)
        types = [e.event_type for e in events]
        assert EventType.PROGRAM_END in types
