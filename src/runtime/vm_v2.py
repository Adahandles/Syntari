"""
Syntari Enhanced VM Runtime v2

Supports v0.4 bytecode with control flow, comparisons, and functions.

Security features:
- Stack depth limits
- Instruction count limits
- Memory allocation limits
- Execution time limits
- Recursion depth tracking
"""

import struct
import sys
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


# Security limits
MAX_STACK_SIZE = 10000
MAX_INSTRUCTIONS = 10_000_000
MAX_VARS = 10000
MAX_STRING_LENGTH = 1_000_000
MAX_EXECUTION_TIME = 30  # seconds
MAX_RECURSION_DEPTH = 1000
MAX_BYTECODE_SIZE = 100 * 1024 * 1024  # 100MB


class VMSecurityError(Exception):
    """Raised when VM security limits are exceeded"""
    pass


class VMRuntimeError(Exception):
    """Raised during VM execution errors"""
    pass


@dataclass
class CallFrame:
    """Represents a function call frame"""
    return_address: int
    local_vars: Dict[str, Any]
    name: str


class SyntariVMV2:
    """Enhanced Syntari Virtual Machine for v0.4 bytecode"""
    
    MAGIC_V2 = b"SYNTARI04"
    
    def __init__(self, debug=False):
        self.stack: List[Any] = []
        self.globals: Dict[str, Any] = {}
        self.constants: List[Any] = []
        self.code: bytes = b""
        self.ip: int = 0  # Instruction pointer
        self.instructions_executed: int = 0
        self.start_time: float = 0
        self.debug = debug
        
        # Call stack for functions
        self.call_stack: List[CallFrame] = []
        self.current_locals: Dict[str, Any] = {}
        
        # Metadata
        self.max_stack_depth: int = 0
        self.instruction_count: int = 0
        self.version: tuple = (0, 0, 0)
    
    def load_bytecode(self, path: str):
        """Load bytecode file"""
        with open(path, 'rb') as f:
            data = f.read()
        
        # Security: Check file size
        if len(data) > MAX_BYTECODE_SIZE:
            raise VMSecurityError(
                f"Bytecode size {len(data)} exceeds maximum {MAX_BYTECODE_SIZE}"
            )
        
        self._parse_bytecode(data)
    
    def _parse_bytecode(self, data: bytes):
        """Parse bytecode format"""
        if not data.startswith(self.MAGIC_V2):
            raise ValueError("Invalid bytecode: wrong magic number")
        
        offset = len(self.MAGIC_V2)
        
        # Version
        self.version = struct.unpack_from("<BBB", data, offset)
        offset += 3
        
        # Metadata
        self.max_stack_depth = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        self.instruction_count = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        
        # Security: Check metadata
        if self.max_stack_depth > MAX_STACK_SIZE:
            raise VMSecurityError(f"Max stack depth {self.max_stack_depth} exceeds limit")
        if self.instruction_count > MAX_INSTRUCTIONS:
            raise VMSecurityError(f"Instruction count {self.instruction_count} exceeds limit")
        
        # Constants pool
        num_constants = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        
        if num_constants > 100000:
            raise VMSecurityError(f"Too many constants: {num_constants}")
        
        self.constants = []
        for _ in range(num_constants):
            const, offset = self._decode_constant(data, offset)
            self.constants.append(const)
        
        # Instructions
        num_instructions = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        
        # Store remaining bytecode as instructions
        self.code = data[offset:]
        self.ip = 0
    
    def _decode_constant(self, data: bytes, offset: int) -> tuple:
        """Decode a constant value"""
        type_byte = data[offset]
        offset += 1
        
        if type_byte == 0x00:  # Null
            return None, offset
        elif type_byte == 0x01:  # Boolean
            value = bool(data[offset])
            return value, offset + 1
        elif type_byte == 0x02:  # Integer
            value = struct.unpack_from("<q", data, offset)[0]
            return value, offset + 8
        elif type_byte == 0x03:  # Float
            value = struct.unpack_from("<d", data, offset)[0]
            return value, offset + 8
        elif type_byte == 0x04:  # String
            length = struct.unpack_from("<I", data, offset)[0]
            offset += 4
            if length > MAX_STRING_LENGTH:
                raise VMSecurityError(f"String length {length} exceeds maximum")
            value = data[offset:offset + length].decode('utf-8')
            return value, offset + length
        else:
            raise ValueError(f"Unknown constant type: {type_byte}")
    
    def run(self):
        """Execute bytecode"""
        self.start_time = time.time()
        self.instructions_executed = 0
        
        while self.ip < len(self.code):
            # Security checks
            self._check_security_limits()
            
            # Fetch and execute
            opcode = self._fetch_u8()
            lineno = self._fetch_u16()
            
            if self.debug:
                self._debug_print(opcode, lineno)
            
            self._execute_opcode(opcode)
            self.instructions_executed += 1
    
    def _check_security_limits(self):
        """Check security limits"""
        # Execution time
        if time.time() - self.start_time > MAX_EXECUTION_TIME:
            raise VMSecurityError(f"Execution time exceeded {MAX_EXECUTION_TIME} seconds")
        
        # Instruction count
        if self.instructions_executed >= MAX_INSTRUCTIONS:
            raise VMSecurityError(f"Instruction limit {MAX_INSTRUCTIONS} exceeded")
        
        # Stack size
        if len(self.stack) > MAX_STACK_SIZE:
            raise VMSecurityError(f"Stack overflow: size {len(self.stack)} exceeds limit")
        
        # Recursion depth
        if len(self.call_stack) > MAX_RECURSION_DEPTH:
            raise VMSecurityError(f"Recursion depth {len(self.call_stack)} exceeds limit")
        
        # Variable count
        total_vars = len(self.globals) + len(self.current_locals)
        if total_vars > MAX_VARS:
            raise VMSecurityError(f"Too many variables: {total_vars}")
    
    def _execute_opcode(self, opcode: int):
        """Execute a single opcode"""
        if opcode == 0x01:  # LOAD_CONST
            idx = self._fetch_u32()
            self.stack.append(self.constants[idx])
        
        elif opcode == 0x02:  # STORE
            name = self._fetch_string()
            value = self.stack.pop()
            if self.current_locals:
                self.current_locals[name] = value
            else:
                self.globals[name] = value
        
        elif opcode == 0x03:  # LOAD
            name = self._fetch_string()
            if name in self.current_locals:
                self.stack.append(self.current_locals[name])
            elif name in self.globals:
                self.stack.append(self.globals[name])
            else:
                raise VMRuntimeError(f"Undefined variable: {name}")
        
        elif opcode == 0x04:  # ADD
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left + right)
        
        elif opcode == 0x05:  # SUB
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left - right)
        
        elif opcode == 0x06:  # MUL
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left * right)
        
        elif opcode == 0x07:  # DIV
            right = self.stack.pop()
            left = self.stack.pop()
            if right == 0:
                raise VMRuntimeError("Division by zero")
            self.stack.append(left / right)
        
        elif opcode == 0x08:  # MOD
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left % right)
        
        elif opcode == 0x09:  # PRINT
            value = self.stack.pop()
            print(value)
        
        elif opcode == 0x10:  # JMP
            target = self._fetch_u32()
            self._jump_to(target)
        
        elif opcode == 0x11:  # JMP_IF_FALSE
            target = self._fetch_u32()
            condition = self.stack.pop()
            if not self._is_truthy(condition):
                self._jump_to(target)
        
        elif opcode == 0x12:  # JMP_IF_TRUE
            target = self._fetch_u32()
            condition = self.stack.pop()
            if self._is_truthy(condition):
                self._jump_to(target)
        
        elif opcode == 0x13:  # COMPARE_EQ
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left == right)
        
        elif opcode == 0x14:  # COMPARE_NE
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left != right)
        
        elif opcode == 0x15:  # COMPARE_LT
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left < right)
        
        elif opcode == 0x16:  # COMPARE_LE
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left <= right)
        
        elif opcode == 0x17:  # COMPARE_GT
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left > right)
        
        elif opcode == 0x18:  # COMPARE_GE
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(left >= right)
        
        elif opcode == 0x30:  # DUP
            self.stack.append(self.stack[-1])
        
        elif opcode == 0x31:  # POP
            self.stack.pop()
        
        elif opcode == 0x32:  # SWAP
            self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
        
        elif opcode == 0x40:  # AND
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._is_truthy(left) and self._is_truthy(right))
        
        elif opcode == 0x41:  # OR
            right = self.stack.pop()
            left = self.stack.pop()
            self.stack.append(self._is_truthy(left) or self._is_truthy(right))
        
        elif opcode == 0x42:  # NOT
            value = self.stack.pop()
            self.stack.append(not self._is_truthy(value))
        
        elif opcode == 0xFF:  # HALT
            raise StopIteration("Program halted normally")
        
        else:
            raise VMRuntimeError(f"Unknown opcode: {opcode:#x}")
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy"""
        if value is None or value is False:
            return False
        if value == 0 or value == "":
            return False
        return True
    
    def _jump_to(self, target: int):
        """Jump to instruction index"""
        # Convert instruction index to byte offset
        # This is simplified - in practice, we'd need instruction boundaries
        self.ip = target
    
    def _fetch_u8(self) -> int:
        """Fetch unsigned byte"""
        value = self.code[self.ip]
        self.ip += 1
        return value
    
    def _fetch_u16(self) -> int:
        """Fetch unsigned 16-bit int"""
        value = struct.unpack_from("<H", self.code, self.ip)[0]
        self.ip += 2
        return value
    
    def _fetch_u32(self) -> int:
        """Fetch unsigned 32-bit int"""
        value = struct.unpack_from("<I", self.code, self.ip)[0]
        self.ip += 4
        return value
    
    def _fetch_string(self) -> str:
        """Fetch string"""
        length = self._fetch_u32()
        if length > MAX_STRING_LENGTH:
            raise VMSecurityError(f"String length {length} exceeds maximum")
        value = self.code[self.ip:self.ip + length].decode('utf-8')
        self.ip += length
        return value
    
    def _debug_print(self, opcode: int, lineno: int):
        """Print debug information"""
        opcode_names = {
            0x01: "LOAD_CONST", 0x02: "STORE", 0x03: "LOAD",
            0x04: "ADD", 0x05: "SUB", 0x06: "MUL", 0x07: "DIV", 0x08: "MOD",
            0x09: "PRINT",
            0x10: "JMP", 0x11: "JMP_IF_FALSE", 0x12: "JMP_IF_TRUE",
            0x13: "COMPARE_EQ", 0x14: "COMPARE_NE", 0x15: "COMPARE_LT",
            0x16: "COMPARE_LE", 0x17: "COMPARE_GT", 0x18: "COMPARE_GE",
            0x30: "DUP", 0x31: "POP", 0x32: "SWAP",
            0x40: "AND", 0x41: "OR", 0x42: "NOT",
            0xFF: "HALT"
        }
        opcode_name = opcode_names.get(opcode, f"UNKNOWN({opcode:#x})")
        print(f"[VM] Line {lineno}: {opcode_name} | Stack: {self.stack[-5:] if len(self.stack) > 0 else '[]'}")


def run_bytecode(path: str, debug: bool = False):
    """Run a bytecode file"""
    vm = SyntariVMV2(debug=debug)
    
    try:
        vm.load_bytecode(path)
        print(f"[Syntari VM v2] Loaded {path}")
        print(f"  Version: {'.'.join(map(str, vm.version))}")
        print(f"  Instructions: {vm.instruction_count}")
        print(f"  Constants: {len(vm.constants)}")
        print(f"  Max stack depth: {vm.max_stack_depth}")
        print()
        
        vm.run()
        
    except StopIteration:
        pass  # Normal termination
    except VMSecurityError as e:
        print(f"[Security Error] {e}", file=sys.stderr)
        sys.exit(1)
    except VMRuntimeError as e:
        print(f"[Runtime Error] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[VM Error] {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n[VM] Executed {vm.instructions_executed} instructions")
    print(f"[VM] Execution time: {time.time() - vm.start_time:.4f}s")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.runtime.vm_v2 <bytecode.sbc> [--debug]")
        sys.exit(1)
    
    bytecode_path = sys.argv[1]
    debug = '--debug' in sys.argv
    
    run_bytecode(bytecode_path, debug=debug)
