"""
Tests for ``syntari.api`` – the public embedding API used by Chain-Of-Record.

Covers:
- validate(): syntax-valid and syntax-invalid source
- execute(): basic execution, input injection, decision/score extraction,
             stdout capture, error handling, trace, limits, edge-cases
"""

import syntari.api as api


# ---------------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------------


class TestValidate:
    """Tests for syntari.api.validate()."""

    def test_valid_simple_declaration(self):
        result = api.validate("let x = 1;")
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_empty_source(self):
        result = api.validate("")
        assert result["valid"] is True

    def test_valid_function_declaration(self):
        source = "fn add(a, b) { return a + b; }"
        result = api.validate(source)
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_multiline(self):
        source = """
let x = 10;
let y = 20;
let z = x + y;
"""
        result = api.validate(source)
        assert result["valid"] is True

    def test_invalid_unexpected_character(self):
        result = api.validate("let @@@ = 1;")
        assert result["valid"] is False
        assert result["error"] is not None
        assert isinstance(result["error"], str)

    def test_invalid_syntax(self):
        result = api.validate("fn ( {")
        assert result["valid"] is False
        assert result["error"] is not None

    def test_non_string_source_returns_invalid(self):
        result = api.validate(None)  # type: ignore[arg-type]
        assert result["valid"] is False
        assert "string" in result["error"].lower()

    def test_returns_dict_with_required_keys(self):
        result = api.validate("let x = 1;")
        assert "valid" in result
        assert "error" in result

    def test_valid_result_has_none_error(self):
        result = api.validate("let a = true;")
        assert result["valid"] is True
        assert result["error"] is None

    def test_invalid_result_has_string_error(self):
        result = api.validate("$$$$")
        assert result["valid"] is False
        assert isinstance(result["error"], str)
        assert len(result["error"]) > 0


# ---------------------------------------------------------------------------
# execute()
# ---------------------------------------------------------------------------


class TestExecute:
    """Tests for syntari.api.execute()."""

    # --- Return structure ---

    def test_returns_required_keys(self):
        result = api.execute("let x = 1;", {})
        for key in ("decision", "score", "outputs", "trace", "error", "stdout", "duration_ms"):
            assert key in result, f"Missing key: {key}"

    def test_error_is_none_on_success(self):
        result = api.execute("let x = 1;", {})
        assert result["error"] is None

    def test_outputs_is_dict(self):
        result = api.execute("let x = 42;", {})
        assert isinstance(result["outputs"], dict)

    def test_duration_ms_is_non_negative(self):
        result = api.execute("let x = 1;", {})
        assert result["duration_ms"] >= 0

    # --- Variable injection (inputs) ---

    def test_inputs_injected_as_variables(self):
        result = api.execute("let y = x + 1;", {"x": 5})
        assert result["error"] is None
        assert result["outputs"].get("y") == 6

    def test_multiple_inputs(self):
        result = api.execute("let total = a + b;", {"a": 10, "b": 20})
        assert result["error"] is None
        assert result["outputs"].get("total") == 30

    def test_string_input(self):
        result = api.execute("let greeting = name;", {"name": "Chain-Of-Record"})
        assert result["outputs"].get("greeting") == "Chain-Of-Record"

    # --- decision and score extraction ---

    def test_decision_extracted_when_set(self):
        result = api.execute('let decision = "approve";', {})
        assert result["decision"] == "approve"

    def test_decision_none_when_not_set(self):
        result = api.execute("let x = 1;", {})
        assert result["decision"] is None

    def test_score_extracted_when_set_as_int(self):
        result = api.execute("let score = 95;", {})
        assert result["score"] == 95
        assert isinstance(result["score"], int)

    def test_score_none_when_not_set(self):
        result = api.execute("let x = 1;", {})
        assert result["score"] is None

    def test_decision_and_score_together(self):
        source = 'let decision = "deny"; let score = 10;'
        result = api.execute(source, {})
        assert result["decision"] == "deny"
        assert result["score"] == 10

    def test_score_from_input(self):
        result = api.execute("let score = base_score;", {"base_score": 77})
        assert result["score"] == 77

    # --- stdout capture ---

    def test_stdout_captured(self):
        result = api.execute('print("hello world");', {})
        assert "hello world" in result["stdout"]

    def test_stdout_empty_when_no_print(self):
        result = api.execute("let x = 1;", {})
        assert result["stdout"] == ""

    # --- Error handling ---

    def test_syntax_error_returns_error_field(self):
        result = api.execute("@@@invalid", {})
        assert result["error"] is not None
        assert result["decision"] is None
        assert result["score"] is None
        assert result["outputs"] == {}

    def test_runtime_error_returns_error_field(self):
        result = api.execute("let x = undefined_var;", {})
        assert result["error"] is not None
        assert isinstance(result["error"], str)

    def test_error_field_is_none_on_clean_execution(self):
        result = api.execute("let x = 1 + 2;", {})
        assert result["error"] is None

    # --- Trace ---

    def test_trace_none_by_default(self):
        result = api.execute("let x = 1;", {})
        assert result["trace"] is None

    def test_trace_returned_when_enabled(self):
        result = api.execute("let x = 1;", {}, enable_trace=True)
        assert result["trace"] is not None
        assert "events" in result["trace"]
        assert "event_count" in result["trace"]

    def test_trace_has_at_least_program_start_and_end(self):
        result = api.execute("let x = 1;", {}, enable_trace=True)
        event_types = [e["event_type"] for e in result["trace"]["events"]]
        assert "program_start" in event_types
        assert "program_end" in event_types

    def test_trace_event_count_matches_events_list(self):
        result = api.execute("let a = 1; let b = 2;", {}, enable_trace=True)
        assert result["trace"]["event_count"] == len(result["trace"]["events"])

    # --- Limits ---

    def test_custom_max_output_bytes(self):
        # Source that produces output; cap at 10 bytes
        result = api.execute('print("0123456789ABCDEFGHIJ");', {}, limits={"max_output_bytes": 10})
        # The stdout must be capped: truncated content + truncation marker
        assert "[output truncated]" in result["stdout"]
        assert "0123456789" in result["stdout"]  # initial bytes preserved

    def test_empty_inputs(self):
        result = api.execute("let x = 42;", {})
        assert result["error"] is None
        assert result["outputs"]["x"] == 42

    # --- Arithmetic and control flow ---

    def test_arithmetic(self):
        result = api.execute("let result = 3 * 7;", {})
        assert result["outputs"]["result"] == 21

    def test_boolean_logic(self):
        result = api.execute("let ok = true;", {})
        assert result["outputs"]["ok"] is True

    def test_conditional(self):
        source = """
let x = 10;
let decision = "deny";
if (x > 5) {
    let decision = "approve";
}
"""
        result = api.execute(source, {})
        assert result["error"] is None

    def test_function_call(self):
        source = """
fn double(n) {
    return n * 2;
}
let result = double(21);
"""
        result = api.execute(source, {})
        assert result["error"] is None
        assert result["outputs"]["result"] == 42

    # --- JSON-serialisability ---

    def test_outputs_are_json_serialisable(self):
        import json

        source = 'let x = 1; let label = "ok";'
        result = api.execute(source, {})
        # Should not raise
        json.dumps(result)

    def test_result_with_trace_is_json_serialisable(self):
        import json

        result = api.execute("let x = 1;", {}, enable_trace=True)
        json.dumps(result)
