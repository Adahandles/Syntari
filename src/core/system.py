"""
Syntari Core System Module - System utilities and I/O
"""

import sys
import time as _time
import os


def print(*args, sep=" ", end="\n", file=None):
    """Print to stdout or file"""
    if file is None:
        file = sys.stdout

    output = sep.join(str(arg) for arg in args)
    file.write(output + end)
    file.flush()


def trace():
    """Print stack trace for debugging"""
    import traceback

    traceback.print_stack()


def exit(code=0):
    """Exit with status code"""
    sys.exit(code)


def env(key):
    """Get environment variable"""
    return os.environ.get(key)


def time():
    """Get current Unix timestamp"""
    return _time.time()


def input(prompt=""):
    """Read line from stdin with size limit"""
    # Security: limit input length to prevent memory exhaustion
    MAX_INPUT_LENGTH = 100000  # 100KB
    try:
        line = sys.stdin.readline(MAX_INPUT_LENGTH)
        if len(line) >= MAX_INPUT_LENGTH:
            raise ValueError(f"Input exceeds maximum allowed length of {MAX_INPUT_LENGTH} bytes")
        return line.rstrip("\n")
    except Exception as e:
        raise RuntimeError(f"Input error: {e}")
