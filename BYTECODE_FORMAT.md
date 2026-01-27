# Syntari Bytecode Format (SBC)

## Overview
Syntari compiles source files (.syn) into bytecode (.sbc) for execution by the Syntari VM.

## Structure
| Section | Description |
|----------|-------------|
| Header | Magic bytes: `SYNTARI03` (9 bytes) |
| Constants | Table of literals and identifiers |
| Code Segment | Instruction sequence |

## File Format Details

### Header
- Magic bytes: `SYNTARI03` (ASCII, 9 bytes)
- Identifies the file as Syntari bytecode version 0.3

### Constants Pool
- Count: 32-bit unsigned integer (little-endian)
- For each constant:
  - Length: 32-bit unsigned integer (constant data length in bytes, **including type tag bytes**)
  - Data:
    - First byte(s): **type tag**, encoded as ASCII:
      - `S`   : string constant
      - `I`   : integer constant
      - `F`   : float constant
      - `B0`  : boolean `False` (`B` followed by `0`)
      - `B1`  : boolean `True`  (`B` followed by `1`)
      - `N`   : `None` constant
    - Remaining bytes (if any): type-specific payload
      - For tagged strings (`S`), this is the raw UTF-8-encoded string bytes.
      - For simple booleans (`B0`/`B1`) and `None` (`N`), there is typically **no payload**; the tag alone identifies both type (and value, for booleans).
      - Integer constants (`I`) are encoded as the UTF-8/ASCII decimal string representation of the value (e.g., `I42`); float constants (`F`) are encoded as the UTF-8/ASCII decimal string representation of the value (e.g., `F3.14`).
  - After decoding tags, constants are interpreted as: boolean (`True`/`False`), `None`, integer, float, or string.
  - This explicit type-tag scheme ensures, for example, that the string `"True"` (`S` + UTF-8 `"True"`) is distinct from the boolean `True` (`B1`), eliminating earlier ambiguity in the constants pool encoding.

### Instruction Count
- Count: 32-bit unsigned integer (number of instructions in source)
- Note: This is informational; actual execution may execute more instructions due to loops

### Code Segment
- Sequence of instructions, each consisting of:
  - Opcode: 1 byte
  - Arguments: variable length depending on opcode

## Instruction Set (v0.3)

### Stack Operations (0x01-0x0F)
```
0x01  LOAD_CONST idx      Load constant from pool onto stack
                           Args: idx (u32)

0x02  STORE name          Store top of stack to variable
                           Args: name (string: length u32 + bytes)

0x03  LOAD name           Load variable value onto stack
                           Args: name (string: length u32 + bytes)
```

### Arithmetic Operations (0x04-0x08)
```
0x04  ADD                 Pop two values, push sum
0x05  SUB                 Pop two values, push difference (a - b)
0x06  MUL                 Pop two values, push product
0x07  DIV                 Pop two values, push quotient (a / b)
0x08  MOD                 Pop two values, push remainder (a % b)
```

### Comparison Operations (0x10-0x15)
```
0x10  EQ_EQ               Pop two values, push (a == b)
0x11  NOT_EQ              Pop two values, push (a != b)
0x12  LT                  Pop two values, push (a < b)
0x13  LT_EQ               Pop two values, push (a <= b)
0x14  GT                  Pop two values, push (a > b)
0x15  GT_EQ               Pop two values, push (a >= b)
```

### Logical Operations (0x16-0x19)
```
0x16  AND                 Pop two values, push logical AND
0x17  OR                  Pop two values, push logical OR
0x18  NOT                 Pop one value, push logical NOT
0x19  NEG                 Pop one value, push arithmetic negation
```

### Control Flow (0x20-0x22)
```
0x20  JMP addr            Unconditional jump to byte address
                           Args: addr (u32)

0x21  JMP_IF_FALSE addr   Jump if top of stack is falsy
                           Args: addr (u32)
                           Note: Pops the condition value

0x22  JMP_IF_TRUE addr    Jump if top of stack is truthy
                           Args: addr (u32)
                           Note: Pops the condition value
```

### Function Operations (0x30-0x31)
```
0x30  CALL name argc      Call function with arguments
                           Args: name (string), argc (u32)
                           Note: Arguments are popped from stack
                           Built-in functions: print

0x31  RETURN              Return from function
                           Note: Return value should be on stack
```

### I/O Operations (0x40)
```
0x40  PRINT               Print top of stack to stdout
                           Note: Pops the value
```

### Stack Manipulation (0x50-0x51)
```
0x50  POP                 Pop and discard top of stack
0x51  DUP                 Duplicate top of stack
```

### Special (0xFF)
```
0xFF  HALT                Stop execution
```

## Truthiness
Values are considered falsy if they are:
- `False` (boolean)
- `None`
- `0` (integer or float)
- `""` (empty string)
- `[]` (empty list)

All other values are truthy.

## Jump Addresses
Jump addresses are byte offsets within the code segment (relative to the start of the code section, not the file).

## Security Limits
The VM enforces the following limits:
- Maximum stack size: 10,000 entries
- Maximum variables: 10,000
- Maximum instructions executed: 1,000,000
- Maximum string length: 1 MB
- Maximum call depth: 1,000
- Maximum bytecode file size: 100 MB
- Maximum constants: 100,000

## Example
A simple program:
```syntari
let x = 42
print(x)
```

Compiles to approximately:
```
LOAD_CONST 0        ; Load 42
STORE "x"           ; Store to x
LOAD "x"            ; Load x
CALL "print" 1      ; Call print(x)
POP                 ; Discard return value
HALT                ; End
```
