#!/usr/bin/env python3
"""
Health check script for Syntari deployment verification
"""

import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 8):
        return False, f"Python {version.major}.{version.minor} < 3.8"
    if version > (3, 12):
        return True, f"Python {version.major}.{version.minor} (untested)"
    return True, f"Python {version.major}.{version.minor}"

def check_imports():
    """Check if all required modules can be imported"""
    modules = [
        "src.interpreter.lexer",
        "src.interpreter.parser",
        "src.interpreter.nodes",
        "src.interpreter.interpreter",
        "src.compiler.bytecode_v2",
        "src.runtime.vm_v2",
        "src.core.system",
        "src.core.logging",
        "src.core.errors",
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
        except ImportError as e:
            failed.append((module, str(e)))
    
    if failed:
        return False, f"Failed imports: {', '.join(m for m, _ in failed)}"
    return True, f"{len(modules)} modules imported successfully"

def check_examples():
    """Check if example files exist"""
    examples_dir = Path("examples")
    if not examples_dir.exists():
        return False, "examples/ directory not found"
    
    examples = list(examples_dir.glob("*.syn"))
    if len(examples) < 5:
        return False, f"Only {len(examples)} examples found (expected >= 5)"
    
    return True, f"{len(examples)} example programs found"

def check_tests():
    """Check if tests can be discovered"""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        return False, "tests/ directory not found"
    
    test_files = list(tests_dir.glob("test_*.py"))
    if len(test_files) < 10:
        return False, f"Only {len(test_files)} test files found (expected >= 10)"
    
    return True, f"{len(test_files)} test files found"

def check_version():
    """Check if version command works"""
    try:
        result = subprocess.run(
            ["python3", "main.py", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return False, "Version command failed"
        if "0.4.0" not in result.stdout:
            return False, f"Unexpected version: {result.stdout.strip()}"
        return True, "Version 0.4.0"
    except Exception as e:
        return False, f"Version check failed: {e}"

def check_repl():
    """Check if REPL can start (basic check)"""
    try:
        # Just check if the command accepts the --repl flag
        result = subprocess.run(
            ["python3", "main.py", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "--repl" not in result.stdout:
            return False, "REPL flag not found in help"
        return True, "REPL command available"
    except Exception as e:
        return False, f"REPL check failed: {e}"

def main():
    """Run all health checks"""
    checks = [
        ("Python Version", check_python_version),
        ("Module Imports", check_imports),
        ("Example Files", check_examples),
        ("Test Files", check_tests),
        ("Version Command", check_version),
        ("REPL Availability", check_repl),
    ]
    
    results = []
    all_passed = True
    
    print("=" * 60)
    print("Syntari Health Check")
    print("=" * 60)
    print()
    
    for name, check_func in checks:
        passed, message = check_func()
        results.append({
            "check": name,
            "passed": passed,
            "message": message
        })
        
        status = "✓ PASS" if passed else "✗ FAIL"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{status}{reset} {name}: {message}")
        
        if not passed:
            all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("\033[92m✓ All health checks passed! Syntari is ready.\033[0m")
        return 0
    else:
        print("\033[91m✗ Some health checks failed. Please review.\033[0m")
        return 1

if __name__ == "__main__":
    sys.exit(main())
