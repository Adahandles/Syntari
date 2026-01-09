import struct
import sys

MAGIC = b"SYNTARI03"

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

        if not data.startswith(MAGIC):
            raise ValueError("Invalid bytecode: bad magic")

        off = len(MAGIC)

        nconst = self._u32(data, off); off += 4
        consts = []
        for _ in range(nconst):
            slen = self._u32(data, off); off += 4
            s = data[off:off+slen].decode("utf-8"); off += slen
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

        self.ninstr = self._u32(data, off); off += 4
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
        s = self.code[self.ip:self.ip+ln].decode("utf-8")
        self.ip += ln
        return s

    def run(self):
        executed = 0
        while executed < self.ninstr and self.ip < len(self.code):
            op = self._fetch_u8()
            executed += 1

            if op == 0x01:  # LOAD_CONST idx
                idx = self._fetch_u32()
                self.stack.append(self.consts[idx])

            elif op == 0x02:  # STORE name
                name = self._fetch_str()
                val = self.stack.pop() if self.stack else None
                self.vars[name] = val

            elif op == 0x03:  # LOAD name
                name = self._fetch_str()
                if name not in self.vars:
                    raise RuntimeError(f"Undefined variable '{name}'")
                self.stack.append(self.vars[name])

            elif op in (0x04, 0x05, 0x06, 0x07):  # arithmetic
                b = self.stack.pop()
                a = self.stack.pop()
                if op == 0x04:
                    self.stack.append(a + b)
                elif op == 0x05:
                    self.stack.append(a - b)
                elif op == 0x06:
                    self.stack.append(a * b)
                elif op == 0x07:
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
