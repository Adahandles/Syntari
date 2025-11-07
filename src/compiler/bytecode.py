class BytecodeGenerator:
    def __init__(self):
        self.instructions = []
        self.constants = []

    def emit(self, opcode, *args):
        self.instructions.append((opcode, args))

    def add_const(self, value):
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)

    def compile(self, ast):
        print("[Compiler] Translating AST to bytecode...")
        self.emit("HALT")
        return self.instructions

    def save(self, filename):
        with open(filename, "w") as f:
            f.write("SYNTARI03\n")
            f.write(str(self.constants) + "\n")
            f.write(str(self.instructions))
