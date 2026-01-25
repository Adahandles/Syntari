import struct
import sys

MAGIC = b"SYNTARI03"

# Security limits for VM execution
MAX_STACK_SIZE = 10000  # Maximum stack depth
MAX_INSTRUCTIONS = 1000000  # Maximum instructions to execute
MAX_VARS = 10000  # Maximum number of variables
MAX_STRING_LENGTH = 1000000  # Maximum string length (1MB)

OP = {
    0x01: "LOAD_CONST",
    0x02: "STORE",
    0x03: "LOAD",
    0x04: "ADD",
    0x05: "SUB",
    0x06: "MUL",
    0x07: "DIV",
    0x08: "PRINT",
    0xFF: "HALT",
}


class VMSecurityError(Exception):
    """Raised when VM security limits are exceeded"""

    pass


class SyntariVM:
    def __init__(self):
        self.stack = []
        self.vars = {}
        self.consts = []
        self.code = b""
        self.ip = 0
        self.ninstr = 0

    def _u32(self, buf, off):
        return struct.unpack_from("<I", buf, off)[0]

    def load_sbc(self, path):
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
            # try numeric cast
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
        b = self.code[self.ip]
        self.ip += 1
        return b

    def _fetch_u32(self):
        v = struct.unpack_from("<I", self.code, self.ip)[0]
        self.ip += 4
        return v

    def _fetch_str(self):
        ln = self._fetch_u32()
        # Security check: prevent excessive string length
        if ln > MAX_STRING_LENGTH:
            raise VMSecurityError(
                f"String length {ln} exceeds maximum allowed length {MAX_STRING_LENGTH}"
            )
        s = self.code[self.ip : self.ip + ln].decode("utf-8")
        self.ip += ln
        return s

    def run(self):
        executed = 0
        while executed < self.ninstr and self.ip < len(self.code):
            # Security check: prevent infinite loops
            if executed >= MAX_INSTRUCTIONS:
                raise VMSecurityError(
                    f"Instruction limit {MAX_INSTRUCTIONS} exceeded. Possible infinite loop."
                )

            op = self._fetch_u8()
            executed += 1

            if op == 0x01:  # LOAD_CONST idx
                # Security check: stack size limit
                if len(self.stack) >= MAX_STACK_SIZE:
                    raise VMSecurityError(f"Stack overflow: exceeded maximum size {MAX_STACK_SIZE}")

                idx = self._fetch_u32()
                self.stack.append(self.consts[idx])

            elif op == 0x02:  # STORE name
                name = self._fetch_str()
                # Security check: variable limit
                if len(self.vars) >= MAX_VARS and name not in self.vars:
                    raise VMSecurityError(
                        f"Variable limit {MAX_VARS} exceeded. Too many variables defined."
                    )

                val = self.stack.pop() if self.stack else None
                self.vars[name] = val

            elif op == 0x03:  # LOAD name
                name = self._fetch_str()
                if name not in self.vars:
                    raise RuntimeError(f"Undefined variable '{name}'")

                # Security check: stack size limit
                if len(self.stack) >= MAX_STACK_SIZE:
                    raise VMSecurityError(f"Stack overflow: exceeded maximum size {MAX_STACK_SIZE}")

                self.stack.append(self.vars[name])

            elif op in (0x04, 0x05, 0x06, 0x07):  # arithmetic
                if len(self.stack) < 2:
                    raise RuntimeError("Stack underflow in arithmetic operation")

                b = self.stack.pop()
                a = self.stack.pop()
                if op == 0x04:
                    self.stack.append(a + b)
                elif op == 0x05:
                    self.stack.append(a - b)
                elif op == 0x06:
                    self.stack.append(a * b)
                elif op == 0x07:
                    if b == 0:
                        raise RuntimeError("Division by zero")
                    self.stack.append(a / b)

            elif op == 0x08:  # PRINT
                val = self.stack.pop() if self.stack else None
                print(val)

            elif op == 0xFF:  # HALT
                break

            else:
                raise RuntimeError(f"Unknown opcode 0x{op:02X}")

        print("[Syntari VM] Execution complete.")


def run_vm(path):
    vm = SyntariVM()
    vm.load_sbc(path)
    vm.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/vm/runtime.py <file.sbc>")
        sys.exit(1)
    run_vm(sys.argv[1])
