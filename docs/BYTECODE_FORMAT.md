# Syntari Bytecode Format (SBC)

## Overview
Syntari compiles source files (.syn) into bytecode (.sbc) for execution by the Syntari VM.

## Structure
| Section | Description |
|----------|-------------|
| Header | Magic bytes: `SYNTARI` + version |
| Constants | Table of literals and identifiers |
| Code Segment | Instruction sequence |
| Metadata | Function map and debug info |

## Instruction Set (v0.3)
```
LOAD_CONST idx
STORE name
LOAD name
ADD, SUB, MUL, DIV
JMP addr
JMP_IF_FALSE addr
CALL name argc
RETURN
PRINT
HALT
```
