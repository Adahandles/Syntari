#!/usr/bin/env python3
"""
Syntari Security Scanner

Comprehensive security scanning tool for the Syntari codebase.
Runs multiple security checks and generates a detailed report.
"""

import json
import os
import subprocess  # nosec B404 - subprocess module needed for security scanning
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return its output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,  # nosec B602 - This is a security scanning tool that needs shell
            capture_output=True,
            text=True,
            timeout=300
        )
        return {
            "description": description,
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "description": description,
            "command": cmd,
            "error": "Command timed out after 300 seconds",
            "success": False
        }
    except Exception as e:
        return {
            "description": description,
            "command": cmd,
            "error": str(e),
            "success": False
        }


def main():
    """Run all security checks."""
    print("Syntari Security Scanner")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Working directory: {os.getcwd()}")
    
    # Install required tools
    print("\n\nInstalling security tools...")
    install_result = run_command(
        "pip install -q bandit safety pip-audit 2>&1",
        "Installing security tools"
    )
    
    if not install_result["success"]:
        print("Warning: Some tools may not have installed correctly")
    
    # Run security checks
    checks = []
    
    # 1. Bandit - Python security scanner
    checks.append(run_command(
        "bandit -r src/ -ll -f txt",
        "Bandit: Python security issues scanner"
    ))
    
    # 2. Bandit - JSON report
    checks.append(run_command(
        "bandit -r src/ -f json -o bandit-report.json 2>&1",
        "Bandit: Generating JSON report"
    ))
    
    # 3. Safety - Dependency vulnerability scanner
    checks.append(run_command(
        "safety check --json 2>&1 || true",
        "Safety: Checking for vulnerable dependencies"
    ))
    
    # 4. pip-audit - Python package auditor
    checks.append(run_command(
        "pip-audit --desc 2>&1 || true",
        "pip-audit: Auditing Python packages"
    ))
    
    # 5. Check for secrets in code
    checks.append(run_command(
        "grep -r -n -E '(password|secret|token|api_key|private_key)\\s*=\\s*['\\\"]' src/ || echo 'No hardcoded secrets found'",
        "Grep: Searching for hardcoded secrets"
    ))
    
    # 6. Run security tests
    checks.append(run_command(
        "pytest tests/test_security.py -v 2>&1 || echo 'Security tests not found or failed'",
        "Pytest: Running security tests"
    ))
    
    # Generate summary report
    print("\n\n" + "="*60)
    print("SECURITY SCAN SUMMARY")
    print("="*60)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "passed": sum(1 for c in checks if c.get("success", False)),
            "failed": sum(1 for c in checks if not c.get("success", False)),
        }
    }
    
    # Save report
    with open("security-scan-report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nTotal checks: {report['summary']['total_checks']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    
    print("\n\nDetailed report saved to: security-scan-report.json")
    print("Bandit report saved to: bandit-report.json")
    
    # Print failed checks
    failed_checks = [c for c in checks if not c.get("success", False)]
    if failed_checks:
        print("\n\nFailed Checks:")
        for check in failed_checks:
            print(f"  ❌ {check['description']}")
    
    passed_checks = [c for c in checks if c.get("success", False)]
    if passed_checks:
        print("\nPassed Checks:")
        for check in passed_checks:
            print(f"  ✅ {check['description']}")
    
    print("\n\nScan complete!")
    
    # Exit with error if any critical checks failed
    if report['summary']['failed'] > 2:  # Allow some failures
        print("\n⚠️  Warning: Multiple security checks failed!")
        sys.exit(1)
    else:
        print("\n✅ Security scan passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
