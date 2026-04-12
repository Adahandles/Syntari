# Chain-Of-Record Integration

Syntari includes an optional **execution auditing layer** that emits structured
events at runtime. These events form an immutable, ordered record of every
meaningful action taken during a program run — suitable for feeding into the
[Chain-Of-Record](https://github.com/Adahandles/Chain-Of-Record) audit service
or any custom backend you choose.

---

## Quick Start

Run a Syntari script and save its execution record to a JSON-lines file:

```bash
syntari --record my_script.syn
```

By default the events are written to `execution_record.jsonl` in the current
directory. Specify a custom path with `--record-output`:

```bash
syntari --record --record-output /var/log/syntari/audit.jsonl my_script.syn
```

Enable `--verbose` alongside `--record` to see a summary printed to stderr:

```bash
syntari --record --verbose my_script.syn
# [Syntari] Recording execution events to: execution_record.jsonl
# [Syntari] Wrote 14 events to execution_record.jsonl
```

---

## Output Format

The `.jsonl` file contains one JSON object per line. Each line represents a
single `ExecutionEvent`:

```json
{"event_id": "a3f2...", "session_id": "b1c9...", "event_type": "program_start", "timestamp": 1713000000.12, "payload": {"session_id": "b1c9..."}}
{"event_id": "d4e5...", "session_id": "b1c9...", "event_type": "var_assign",    "timestamp": 1713000000.18, "payload": {"name": "x", "value": "42", "kind": "declaration"}}
{"event_id": "f6a7...", "session_id": "b1c9...", "event_type": "func_call",     "timestamp": 1713000000.20, "payload": {"name": "add", "args": ["3", "4"]}}
{"event_id": "g8b9...", "session_id": "b1c9...", "event_type": "func_return",   "timestamp": 1713000000.21, "payload": {"name": "add", "return_value": "7"}}
{"event_id": "h0c1...", "session_id": "b1c9...", "event_type": "program_end",   "timestamp": 1713000000.25, "payload": {"result": "None", "error": null}}
```

### Event Types

| `event_type`       | When emitted                               | Key payload fields                                  |
|--------------------|--------------------------------------------|-----------------------------------------------------|
| `program_start`    | Before the first statement executes        | `session_id`                                        |
| `program_end`      | After the last statement (or on error)     | `result`, `error`                                   |
| `var_assign`       | On `let` declaration **or** reassignment   | `name`, `value`, `kind` (`declaration`/`assignment`)|
| `func_call`        | When a user-defined function is called     | `name`, `args`                                      |
| `func_return`      | When a user-defined function returns       | `name`, `return_value`                              |
| `exception_raised` | *(reserved for future use)*               |                                                     |

All events share:

| Field        | Type   | Description                                       |
|--------------|--------|---------------------------------------------------|
| `event_id`   | string | Unique UUID4 for this event                       |
| `session_id` | string | UUID4 shared by all events in one interpreter run |
| `timestamp`  | float  | Unix epoch (seconds, floating-point)              |
| `payload`    | object | Event-specific key-value data                     |

---

## Python API

### Using the built-in `FileAdapter`

```python
from src.core.chain_of_record import FileAdapter
from src.interpreter.interpreter import Interpreter
from src.interpreter.lexer import tokenize
from src.interpreter.parser import parse

source = """
fn add(a, b) { return a + b; }
let result = add(3, 4);
"""

tokens = tokenize(source)
tree = parse(tokens)

with FileAdapter("/tmp/my_run.jsonl") as adapter:
    interpreter = Interpreter(recorder=adapter)
    interpreter.interpret(tree)

print(f"Wrote {adapter.events_written} events to /tmp/my_run.jsonl")
```

### Using the convenience `interpret()` function

```python
from src.core.chain_of_record import FileAdapter
from src.interpreter.interpreter import interpret
from src.interpreter.lexer import tokenize
from src.interpreter.parser import parse

adapter = FileAdapter("audit.jsonl")
tokens = tokenize("let x = 42;")
tree = parse(tokens)
interpret(tree, recorder=adapter)
adapter.close()
```

### Writing a custom adapter

Subclass `RecorderAdapter` to forward events to any backend:

```python
from src.core.chain_of_record import RecorderAdapter, ExecutionEvent

class MyAdapter(RecorderAdapter):
    def record(self, event: ExecutionEvent) -> None:
        # Forward to your logging system, message queue, HTTP API, etc.
        print(f"[AUDIT] {event.event_type.value}: {event.payload}")

    def close(self) -> None:
        pass  # flush / teardown here
```

Then pass it to the interpreter:

```python
interpreter = Interpreter(recorder=MyAdapter())
interpreter.interpret(tree)
```

---

## Chain-Of-Record Service Integration

Once the `chain-of-record` Python client is available, install it as an
optional dependency:

```bash
pip install "syntari[chain-of-record]"
```

Then implement a `ChainOfRecordAdapter` that posts events to the service
endpoint, and pass it to the interpreter as shown above. The adapter interface
is intentionally minimal to make this straightforward.

---

## Architecture

```
Syntari interpreter
       │
       │  emits ExecutionEvent objects
       ▼
RecorderAdapter (interface)
       │
       ├── NoOpAdapter      ← default, zero overhead
       ├── FileAdapter      ← writes JSON-lines (built-in)
       └── ChainOfRecord…  ← future: posts to COR service
```

- **`src/core/chain_of_record.py`** — defines `ExecutionEvent`, `EventType`,
  `RecorderAdapter`, `NoOpAdapter`, and `FileAdapter`.
- **`src/interpreter/interpreter.py`** — `Interpreter.__init__` accepts an
  optional `recorder: RecorderAdapter` kwarg; defaults to `NoOpAdapter`.
- **`src/interpreter/main.py`** — CLI wires `--record` / `--record-output`
  to `FileAdapter` and passes it to the interpreter.

---

## Running the Tests

```bash
pytest tests/test_chain_of_record.py -v
```
