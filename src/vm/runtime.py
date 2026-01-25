"""
Syntari VM Runtime - Executes bytecode (.sbc files)
"""

import struct
import sys

MAGIC = b"SYNTARI03"

# Security limits for VM execution
MAX_STACK_SIZE = 10000  # Maximum stack depth
MAX_INSTRUCTIONS = 1000000  # Maximum instructions to execute
MAX_VARS = 10000  # Maximum number of variables
MAX_STRING_LENGTH = 1000000  # Maximum string length (1MB)
MAX_CALL_DEPTH = 1000  # Maximum function call depth

# Opcode mapping
OP = {
    0x01: "LOAD_CONST",
    0x02: "STORE",
    0x03: "LOAD",
    0x04: "ADD",
    0x05: "SUB",
    0x06: "MUL",
    0x07: "DIV",
    0x08: "MOD",
    0x10: "EQ_EQ",
    0x11: "NOT_EQ",
    0x12: "LT",
    0x13: "LT_EQ",
    0x14: "GT",
    0x15: "GT_EQ",
    0x16: "AND",
    0x17: "OR",
    0x18: "NOT",
    0x19: "NEG",
    0x20: "JMP",
    0x21: "JMP_IF_FALSE",
    0x22: "JMP_IF_TRUE",
    0x30: "CALL",
    0x31: "RETURN",
    0x40: "PRINT",
    0x50: "POP",
    0x51: "DUP",
    0xFF: "HALT",
}


class VMSecurityError(Exception):
    """Raised when VM security limits are exceeded"""

    pass


class CallFrame:
    """Represents a function call frame"""

    def __init__(self, return_ip, local_vars=None):
        self.return_ip = return_ip
        self.local_vars = local_vars if local_vars else {}


class SyntariVM:
    """Virtual Machine for executing Syntari bytecode"""

    def __init__(self):
        self.stack = []
        self.vars = {}
        self.consts = []
        self.code = b""
        self.ip = 0
        self.ninstr = 0
        self.call_stack = []
        self.executed = 0

    def _u32(self, buf, off):
        """Unpack a 32-bit unsigned integer"""
        return struct.unpack_from("<I", buf, off)[0]

    def load_sbc(self, path):
        """Load bytecode from .sbc file"""
        with open(path, "rb") as f:
            data = f.read()

        # Security check: validate bytecode file size
        MAX_BYTECODE_SIZE = 100 * 1024 * 1024  # 100MB
        if len(data) > MAX_BYTECODE_SIZE:
            raise VMSecurityError(
                f"Bytecode file size {len(data)} exceeds maximum {MAX_BYTECODE_SIZE}"
            )

        if not data.startswith(MAGIC):
            raise ValueError("Invalid bytecode: bad magic")

        off = len(MAGIC)

        # Read constants pool
        nconst = self._u32(data, off)
        off += 4

        # Security check: validate constant pool size
        MAX_CONSTANTS = 100000
        if nconst > MAX_CONSTANTS:
            raise VMSecurityError(f"Too many constants: {nconst} exceeds maximum {MAX_CONSTANTS}")

        consts = []
        for _ in range(nconst):
            if off + 4 > len(data):
                raise ValueError("Truncated bytecode: cannot read constant length")

            slen = self._u32(data, off)
            off += 4

            # Security check: validate string length
            if slen > MAX_STRING_LENGTH:
                raise VMSecurityError(
                    f"Constant string length {slen} exceeds maximum {MAX_STRING_LENGTH}"
                )

            if off + slen > len(data):
                raise ValueError("Truncated bytecode: cannot read constant data")

            s = data[off : off + slen].decode("utf-8")
            off += slen

            # Try to parse as number or boolean
            if s == "True":
                val = True
            elif s == "False":
                val = False
            elif s == "None":
                val = None
            else:
                try:
                    if "." in s:
                        val = float(s)
                    else:
                        val = int(s)
                except Exception:
                    val = s

            consts.append(val)

        self.consts = consts

        if off + 4 > len(data):
            raise ValueError("Truncated bytecode: cannot read instruction count")

        self.ninstr = self._u32(data, off)
        off += 4

        # Security check: validate instruction count
        if self.ninstr > MAX_INSTRUCTIONS:
            raise VMSecurityError(
                f"Too many instructions: {self.ninstr} exceeds maximum {MAX_INSTRUCTIONS}"
            )

        self.code = data[off:]
        self.ip = 0

    def _fetch_u8(self):
        """Fetch a single byte from code"""
        b = self.code[self.ip]
        self.ip += 1
        return b

    def _fetch_u32(self):
        """Fetch a 32-bit unsigned integer from code"""
        v = struct.unpack_from("<I", self.code, self.ip)[0]
        self.ip += 4
        return v

    def _fetch_str(self):
        """Fetch a string from code"""
        ln = self._fetch_u32()
        # Security check: prevent excessive string length
        if ln > MAX_STRING_LENGTH:
            raise VMSecurityError(
                f"String length {ln} exceeds maximum allowed length {MAX_STRING_LENGTH}"
            )
        s = self.code[self.ip : self.ip + ln].decode("utf-8")
        self.ip += ln
        return s

    def _push(self, value):
        """Push a value onto the stack"""
        if len(self.stack) >= MAX_STACK_SIZE:
            raise VMSecurityError(f"Stack overflow: exceeded maximum size {MAX_STACK_SIZE}")
        self.stack.append(value)

    def _pop(self):
        """Pop a value from the stack"""
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def _is_truthy(self, value):
        """Determine if a value is truthy"""
        if value is None or value is False:
            return False
        if value == 0 or value == "" or value == []:
            return False
        return True

    def run(self, verbose=True):
        """Execute the loaded bytecode"""
        while self.ip < len(self.code):
            # Security check: prevent infinite loops
            if self.executed >= MAX_INSTRUCTIONS:
                raise VMSecurityError(
                    f"Instruction limit {MAX_INSTRUCTIONS} exceeded. Possible infinite loop."
                )

            op = self._fetch_u8()
            self.executed += 1

            # LOAD_CONST idx
            if op == 0x01:
                idx = self._fetch_u32()
                self._push(self.consts[idx])

            # STORE name
            elif op == 0x02:
                name = self._fetch_str()
                # Security check: variable limit
                if len(self.vars) >= MAX_VARS and name not in self.vars:
                    raise VMSecurityError(
                        f"Variable limit {MAX_VARS} exceeded. Too many variables defined."
                    )
                val = self._pop()
                self.vars[name] = val

            # LOAD name
            elif op == 0x03:
                name = self._fetch_str()
                if name not in self.vars:
                    raise RuntimeError(f"Undefined variable '{name}'")
                self._push(self.vars[name])

            # Arithmetic operations
            elif op == 0x04:  # ADD
                b = self._pop()
                a = self._pop()
                self._push(a + b)

            elif op == 0x05:  # SUB
                b = self._pop()
                a = self._pop()
                self._push(a - b)

            elif op == 0x06:  # MUL
                b = self._pop()
                a = self._pop()
                self._push(a * b)

            elif op == 0x07:  # DIV
                b = self._pop()
                a = self._pop()
                if b == 0:
                    raise RuntimeError("Division by zero")
                self._push(a / b)

            elif op == 0x08:  # MOD
                b = self._pop()
                a = self._pop()
                if b == 0:
                    raise RuntimeError("Modulo by zero")
                self._push(a % b)

            # Comparison operations
            elif op == 0x10:  # EQ_EQ
                b = self._pop()
                a = self._pop()
                self._push(a == b)

            elif op == 0x11:  # NOT_EQ
                b = self._pop()
                a = self._pop()
                self._push(a != b)

            elif op == 0x12:  # LT
                b = self._pop()
                a = self._pop()
                self._push(a < b)

            elif op == 0x13:  # LT_EQ
                b = self._pop()
                a = self._pop()
                self._push(a <= b)

            elif op == 0x14:  # GT
                b = self._pop()
                a = self._pop()
                self._push(a > b)

            elif op == 0x15:  # GT_EQ
                b = self._pop()
                a = self._pop()
                self._push(a >= b)

            # Logical operations
            elif op == 0x16:  # AND
                b = self._pop()
                a = self._pop()
                self._push(self._is_truthy(a) and self._is_truthy(b))

            elif op == 0x17:  # OR
                b = self._pop()
                a = self._pop()
                self._push(self._is_truthy(a) or self._is_truthy(b))

            elif op == 0x18:  # NOT
                a = self._pop()
                self._push(not self._is_truthy(a))

            elif op == 0x19:  # NEG
                a = self._pop()
                self._push(-a)

            # Control flow
            elif op == 0x20:  # JMP
                addr = self._fetch_u32()
                self.ip = addr

            elif op == 0x21:  # JMP_IF_FALSE
                addr = self._fetch_u32()
                condition = self._pop()
                if not self._is_truthy(condition):
                    self.ip = addr

            elif op == 0x22:  # JMP_IF_TRUE
                addr = self._fetch_u32()
                condition = self._pop()
                if self._is_truthy(condition):
                    self.ip = addr

            # Function calls
            elif op == 0x30:  # CALL
                func_name = self._fetch_str()
                argc = self._fetch_u32()

                # Pop arguments from stack
                args = []
                for _ in range(argc):
                    args.insert(0, self._pop())

                # Handle built-in functions
                if func_name == "print":
                    # Print all arguments separated by space
                    print(*args)
                    # Push None as return value
                    self._push(None)
                else:
                    # Check call depth
                    if len(self.call_stack) >= MAX_CALL_DEPTH:
                        raise VMSecurityError(
                            f"Call depth {len(self.call_stack)} exceeds maximum {MAX_CALL_DEPTH}"
                        )

                    # For now, user-defined functions are not implemented
                    raise NotImplementedError(f"User-defined function calls not yet implemented: {func_name}")

            elif op == 0x31:  # RETURN
                if not self.call_stack:
                    # Return from main, halt execution
                    break
                # Pop call frame and restore state
                frame = self.call_stack.pop()
                self.ip = frame.return_ip
                # Note: return value is already on stack

            # I/O
            elif op == 0x40:  # PRINT
                val = self._pop()
                print(val)

            # Stack operations
            elif op == 0x50:  # POP
                self._pop()

            elif op == 0x51:  # DUP
                val = self._pop()
                self._push(val)
                self._push(val)

            # HALT
            elif op == 0xFF:
                break

            else:
                raise RuntimeError(f"Unknown opcode 0x{op:02X}")

        if verbose:
            print("[Syntari VM] Execution complete.")


def run_vm(path, verbose=True):
    """Load and run a bytecode file"""
    vm = SyntariVM()
    vm.load_sbc(path)
    vm.run(verbose=verbose)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.vm.runtime <file.sbc>")
        sys.exit(1)
    run_vm(sys.argv[1])
