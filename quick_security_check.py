#!/usr/bin/env python3
"""
Quick Security Check for Syntari

Runs a fast security check to verify the repository is secure.
Suitable for pre-commit or quick validation.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_command_available(cmd):
    """Check if a command is available."""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_check(name, cmd, success_msg, fail_msg):
    """Run a security check."""
    print(f"\n🔍 {name}...", end=" ", flush=True)
    try:
        result = subprocess.run(
            cmd,
            shell=True,  # nosec B602 - This is a security scanning tool that needs shell
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {success_msg}")
            return True
        else:
            print(f"⚠️  {fail_msg}")
            if result.stderr:
                print(f"   {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run quick security checks."""
    print("="*60)
    print("🔒 Syntari Quick Security Check")
    print("="*60)
    
    os.chdir(Path(__file__).parent)
    
    checks_passed = 0
    checks_failed = 0
    
    # Check 1: No .env file committed
    if not os.path.exists(".env"):
        print("\n🔍 Environment files...", end=" ")
        print("✅ No .env file found (good!)")
        checks_passed += 1
    else:
        print("\n🔍 Environment files...", end=" ")
        print("⚠️  .env file exists (should be in .gitignore)")
        checks_failed += 1
    
    # Check 2: No private keys
    has_keys = any(Path(".").rglob("*.pem")) or any(Path(".").rglob("*.key"))
    if not has_keys:
        print("🔍 Private keys...", end=" ")
        print("✅ No private keys found")
        checks_passed += 1
    else:
        print("🔍 Private keys...", end=" ")
        print("⚠️  Private keys detected")
        checks_failed += 1
    
    # Check 3: Bandit (if available)
    if check_command_available("bandit"):
        if run_check(
            "Bandit scan",
            "bandit -r src/ -ll -q",
            "No security issues",
            "Security issues found"
        ):
            checks_passed += 1
        else:
            checks_failed += 1
    else:
        print("\n🔍 Bandit scan... ⏭️  Skipped (not installed)")
    
    # Check 4: Git status for sensitive files
    result = subprocess.run(
        "git status --porcelain | grep -E '\\.env$|\\.pem$|\\.key$' || true",
        shell=True,  # nosec B602 - Safe grep command for security checking
        capture_output=True,
        text=True
    )
    if not result.stdout.strip():
        print("🔍 Git staged files...", end=" ")
        print("✅ No sensitive files staged")
        checks_passed += 1
    else:
        print("🔍 Git staged files...", end=" ")
        print("⚠️  Sensitive files in staging:")
        print(f"   {result.stdout.strip()}")
        checks_failed += 1
    
    # Check 5: .gitignore exists and has security patterns
    if os.path.exists(".gitignore"):
        with open(".gitignore") as f:
            content = f.read()
            has_env = ".env" in content
            has_keys = "*.key" in content or "*.pem" in content
            
            if has_env and has_keys:
                print("🔍 .gitignore...", end=" ")
                print("✅ Security patterns present")
                checks_passed += 1
            else:
                print("🔍 .gitignore...", end=" ")
                print("⚠️  Missing security patterns")
                checks_failed += 1
    else:
        print("🔍 .gitignore...", end=" ")
        print("❌ .gitignore missing!")
        checks_failed += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 Results: {checks_passed} passed, {checks_failed} warnings")
    print("="*60)
    
    if checks_failed > 0:
        print("\n⚠️  Some security checks have warnings.")
        print("   Run './security_scan.py' for detailed analysis.")
        sys.exit(1)
    else:
        print("\n✅ All security checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
