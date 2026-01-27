# -*- coding: utf-8 -*-
"""
Bytecode compiler for the Syntari language.
"""

class BytecodeCompiler:
    def __init__(self):
        self.bytecode = []

    def compile(self, source_code):
        # Compile source code into bytecode.
        print("Compiling...")
        # Implementation details go here.

    def save(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.bytecode)

    def clear(self):
        self.bytecode = []
        print("Cleared bytecode.")

    # Additional methods...
    
