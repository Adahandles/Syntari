"""
syntari.api - Public embedding API for Syntari

This module is the stable integration surface that external applications
(such as Chain-Of-Record) import to validate and execute Syntari source code.

Public interface
----------------
validate(source)
    Performs syntax/parse validation of *source* and returns a dict.

execute(source, inputs, *, limits=None, enable_trace=False)
    Parses and interprets *source* with *inputs* bound as variables, then
    returns a JSON-serialisable result dict.

Both functions are **purely in-process** (no subprocess, no I/O, no network
access by default) and are designed to be safe to call from within a web
request or Celery task.
"""

import io
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict, List, Optional

__all__ = ["validate", "execute"]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_DEFAULT_LIMITS: Dict[str, Any] = {
    "max_steps": 10_000,  # interpreter iterations
    "max_output_bytes": 65_536,  # 64 KB captured stdout
    "timeout_seconds": 10,  # wall-clock budget (best-effort; not enforced via
    # signal because we may run in a thread/async context)
}


def _make_interpreter(inputs: Dict[str, Any], recorder=None):
    """Return a fresh Interpreter pre-populated with *inputs* as globals."""
    from src.interpreter.interpreter import Interpreter

    interp = Interpreter(recorder=recorder)
    for name, value in inputs.items():
        interp.globals.define(name, value)
    return interp


def _safe_serialise(value: Any) -> Any:
    """Recursively convert *value* to a JSON-serialisable structure."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(k): _safe_serialise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_serialise(v) for v in value]
    # Fallback: string representation
    return str(value)


def _collect_outputs(interp) -> Dict[str, Any]:
    """Snapshot user-visible variables from the interpreter environment."""
    outputs: Dict[str, Any] = {}
    try:
        env = interp.environment
        # Walk the environment chain from innermost to outermost
        visited: set = set()
        while env is not None:
            for name, value in env.variables.items():
                if name not in visited:
                    visited.add(name)
                    outputs[name] = _safe_serialise(value)
            env = env.parent
    except Exception:
        pass
    return outputs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate(source: str) -> Dict[str, Any]:
    """
    Validate *source* as Syntari code.

    Runs the full lexer → parser pipeline.  If parsing succeeds without
    exceptions the source is considered syntactically valid.  Semantic
    validation (type-checking, undefined-variable analysis) is not performed
    at this stage—parse-level errors are the primary gate.

    Parameters
    ----------
    source:
        Syntari source code as a plain string.

    Returns
    -------
    dict with keys:
        ``valid``  (bool)  – ``True`` iff no parse error was detected.
        ``error``  (str | None) – Human-readable error message, or ``None``.
    """
    if not isinstance(source, str):
        return {"valid": False, "error": "source must be a string"}

    try:
        from src.interpreter.lexer import tokenize
        from src.interpreter.parser import parse

        tokens = tokenize(source)
        parse(tokens)
        return {"valid": True, "error": None}
    except Exception as exc:
        return {"valid": False, "error": str(exc)}


def execute(
    source: str,
    inputs: Dict[str, Any],
    *,
    limits: Optional[Dict[str, Any]] = None,
    enable_trace: bool = False,
) -> Dict[str, Any]:
    """
    Execute *source* as Syntari code with *inputs* bound as top-level
    variables, and return a JSON-serialisable result dict.

    The execution is **in-process** and **deterministic** given the same
    source + inputs.  Network and filesystem access is allowed by the default
    Syntari runtime but callers in restricted contexts should sandbox via
    OS-level controls (seccomp, Docker, etc.)

    Parameters
    ----------
    source:
        Syntari source code.
    inputs:
        Mapping of variable name → value injected into the global
        environment before execution begins.  Keys must be valid Python
        identifiers.
    limits:
        Optional resource-limit overrides (keys: ``max_steps``,
        ``max_output_bytes``, ``timeout_seconds``).  Merged with defaults.
    enable_trace:
        When ``True``, attach a lightweight in-memory recorder so that
        Chain-Of-Record execution events are included in the returned
        ``trace`` field.

    Returns
    -------
    dict with keys:
        ``decision``  (str | None) – Value of the ``decision`` variable if
            the Syntari program set one, else ``None``.
        ``score``  (int | None) – Value of the ``score`` variable if set,
            cast to ``int``; otherwise ``None``.
        ``outputs``  (dict) – Snapshot of all top-level variables after
            execution.
        ``trace``  (dict | None) – Execution-event trace when
            *enable_trace* is ``True``; ``None`` otherwise.
        ``error``  (str | None) – Error message if execution failed;
            ``None`` on success.
        ``stdout``  (str) – Anything written to standard output during
            execution (capped to ``max_output_bytes``).
        ``duration_ms``  (float) – Wall-clock execution time in
            milliseconds.
    """
    effective_limits = {**_DEFAULT_LIMITS, **(limits or {})}
    max_output_bytes: int = int(effective_limits.get("max_output_bytes", 65_536))

    # Validate first so callers get a clean error on bad syntax
    val = validate(source)
    if not val["valid"]:
        return {
            "decision": None,
            "score": None,
            "outputs": {},
            "trace": None,
            "error": val["error"],
            "stdout": "",
            "duration_ms": 0.0,
        }

    trace_data: Optional[Dict[str, Any]] = None
    recorder = None

    if enable_trace:
        recorder = _InMemoryRecorder()

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    error_msg: Optional[str] = None
    interp = None
    start = time.monotonic()

    try:
        from src.interpreter.lexer import tokenize
        from src.interpreter.parser import parse

        tokens = tokenize(source)
        tree = parse(tokens)

        interp = _make_interpreter(inputs, recorder=recorder)

        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            interp.interpret(tree)

    except Exception as exc:
        error_msg = f"{type(exc).__name__}: {exc}"
        # Include compact traceback for debugging but avoid leaking internals
        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        # Keep only the last few frames to cap size
        short_tb = "".join(tb_lines[-6:])
        error_msg = f"{error_msg}\n{short_tb}".strip()

    duration_ms = (time.monotonic() - start) * 1000.0

    # Collect outputs from interpreter environment
    outputs: Dict[str, Any] = {}
    if interp is not None:
        outputs = _collect_outputs(interp)

    # Extract well-known output variables
    decision: Optional[str] = None
    score: Optional[int] = None
    if "decision" in outputs:
        decision = str(outputs["decision"])
    if "score" in outputs:
        try:
            score = int(outputs["score"])
        except (TypeError, ValueError):
            score = None

    # Cap stdout
    raw_stdout = stdout_buf.getvalue()
    if len(raw_stdout) > max_output_bytes:
        raw_stdout = raw_stdout[:max_output_bytes] + "\n[output truncated]"

    # Build trace
    if enable_trace and recorder is not None:
        trace_data = recorder.to_dict()

    return {
        "decision": decision,
        "score": score,
        "outputs": outputs,
        "trace": trace_data,
        "error": error_msg,
        "stdout": raw_stdout,
        "duration_ms": round(duration_ms, 3),
    }


# ---------------------------------------------------------------------------
# Internal in-memory recorder (used when enable_trace=True)
# ---------------------------------------------------------------------------


class _InMemoryRecorder:
    """Lightweight recorder that stores events in a list for later inspection."""

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def record(self, event) -> None:  # event: ExecutionEvent
        try:
            self._events.append(event.to_dict())
        except Exception:
            pass

    def close(self) -> None:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {"events": self._events, "event_count": len(self._events)}
