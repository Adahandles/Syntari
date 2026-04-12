"""
Chain-Of-Record Integration Adapter for Syntari

Provides a lightweight, optional auditing/recording layer that emits structured
execution events from the Syntari interpreter. Events can be consumed by:
- The Chain-Of-Record service (when installed via the ``chain-of-record`` extra)
- A local JSON-lines file (built-in ``FileAdapter``)
- Any custom adapter that implements ``RecorderAdapter``

Design principles:
- **Zero-overhead when disabled**: the default ``NoOpAdapter`` is a no-op and
  adds no measurable overhead to normal execution.
- **Adapter pattern**: Syntari does *not* depend on the Chain-Of-Record package
  at runtime. The adapter interface is defined here so third-party adapters can
  be dropped in without modifying Syntari itself.
- **Immutable events**: ``ExecutionEvent`` is a frozen dataclass; adapters
  receive read-only snapshots.

Usage::

    from src.core.chain_of_record import FileAdapter
    from src.interpreter.interpreter import Interpreter

    adapter = FileAdapter("execution_record.jsonl")
    interpreter = Interpreter(recorder=adapter)
    interpreter.interpret(program)
    adapter.close()

Or via the CLI::

    syntari --record --record-output execution_record.jsonl script.syn
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Enumeration of all execution event types emitted by the interpreter."""

    PROGRAM_START = "program_start"
    PROGRAM_END = "program_end"
    FUNC_CALL = "func_call"
    FUNC_RETURN = "func_return"
    VAR_ASSIGN = "var_assign"
    EXCEPTION_RAISED = "exception_raised"


@dataclass(frozen=True)
class ExecutionEvent:
    """
    Immutable record of a single Syntari runtime event.

    Attributes:
        event_id: Unique identifier for this event (UUID4).
        session_id: Identifier grouping all events from one interpreter run.
        event_type: The kind of event (see ``EventType``).
        timestamp: Unix epoch timestamp (seconds) when the event occurred.
        payload: Arbitrary key-value data specific to this event type.
    """

    event_id: str
    session_id: str
    event_type: EventType
    timestamp: float
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation suitable for serialization."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        return data

    def to_json(self) -> str:
        """Return a compact JSON string for this event."""
        return json.dumps(self.to_dict(), default=str)


def _make_event(
    event_type: EventType,
    session_id: str,
    payload: Optional[Dict[str, Any]] = None,
) -> ExecutionEvent:
    """Factory helper that stamps an event with a fresh UUID and current time."""
    return ExecutionEvent(
        event_id=str(uuid.uuid4()),
        session_id=session_id,
        event_type=event_type,
        timestamp=time.time(),
        payload=payload or {},
    )


class RecorderAdapter:
    """
    Abstract base class for Chain-Of-Record adapters.

    Subclass this to forward Syntari execution events to any backend
    (file, HTTP endpoint, message queue, the Chain-Of-Record service, etc.).

    Adapters are expected to be reentrant-safe when used from a single thread
    (the interpreter is single-threaded).
    """

    def record(self, event: ExecutionEvent) -> None:
        """
        Persist or forward a single execution event.

        Args:
            event: The immutable event to record. Implementations must *not*
                mutate the event object.
        """
        raise NotImplementedError

    def close(self) -> None:
        """
        Flush and release any resources held by the adapter.

        Called automatically by the interpreter at program end (if the adapter
        is the ``FileAdapter``) but callers should invoke this explicitly when
        managing adapters outside the interpreter lifecycle.
        """


class NoOpAdapter(RecorderAdapter):
    """
    Default no-operation adapter.

    Used when recording is disabled. All calls are discarded without any
    I/O or computation, keeping interpreter overhead at zero.
    """

    def record(self, event: ExecutionEvent) -> None:
        """Discard the event silently."""

    def close(self) -> None:
        """Nothing to flush or release."""


class FileAdapter(RecorderAdapter):
    """
    Writes execution events to a JSON-lines (``.jsonl``) file.

    Each line in the output file is a self-contained JSON object representing
    one ``ExecutionEvent``. The file can be replayed, audited, or forwarded to
    the Chain-Of-Record service with the ``cor import`` command (once that CLI
    is installed).

    Args:
        path: Destination file path. The file is created (or appended to) when
            this adapter is instantiated.

    Example::

        adapter = FileAdapter("/tmp/my_run.jsonl")
        # ... run interpreter ...
        adapter.close()  # flush and close
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._file = open(path, "a", encoding="utf-8")  # noqa: WPS515
        self._events_written = 0

    @property
    def path(self) -> str:
        """Path to the output file."""
        return self._path

    @property
    def events_written(self) -> int:
        """Number of events written so far."""
        return self._events_written

    def record(self, event: ExecutionEvent) -> None:
        """
        Append the event as a JSON line to the output file.

        Args:
            event: The execution event to persist.
        """
        self._file.write(event.to_json() + "\n")
        self._events_written += 1

    def close(self) -> None:
        """Flush and close the underlying file handle."""
        if not self._file.closed:
            self._file.flush()
            self._file.close()

    def __enter__(self) -> "FileAdapter":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
