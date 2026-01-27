"""
DEPRECATED: This file has been moved to src/vm/runtime.py

This wrapper is provided for backward compatibility.
Please update your imports to use src.vm.runtime instead.
"""

import warnings

warnings.warn(
    "runtime.py is deprecated. Use 'from src.vm.runtime import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.vm import runtime as _runtime

# Re-export public names from src.vm.runtime for backward compatibility
if hasattr(_runtime, "__all__"):
    globals().update({name: getattr(_runtime, name) for name in _runtime.__all__})
else:
    for _name in dir(_runtime):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_runtime, _name)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python runtime.py <file.sbc>")
        sys.exit(1)
    _runtime.run_vm(sys.argv[1])
