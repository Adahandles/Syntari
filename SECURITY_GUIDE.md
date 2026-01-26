# Syntari Security Guide

## 🔒 Security Overview

Syntari takes security seriously. This document outlines security practices, configurations, and guidelines for maintaining a secure codebase.

## 🛡️ Security Features

### 1. Network Security (v0.4+)
- **SSRF Protection**: Blocks access to private IP ranges
- **URL Validation**: Enforces safe URL schemes (http/https only)
- **Request Size Limits**: Prevents DoS attacks
- **Timeout Configuration**: Prevents hanging requests

### 2. Code Security
- **Input Validation**: All user inputs are sanitized
- **Path Traversal Protection**: File operations use safe paths
- **Recursion Limits**: Prevents stack overflow
- **Memory Limits**: Prevents resource exhaustion

### 3. Dependency Security
- **Pinned Versions**: All dependencies have version constraints
- **Regular Audits**: Weekly automated security scans
- **Vulnerability Monitoring**: GitHub Dependabot enabled
- **Supply Chain Security**: SLSA compliance

## 🚨 Security Scanning

### Automated Scans

```bash
# Run all security checks
make security

# Run comprehensive scan with reports
./security_scan.py

# Run specific tools
bandit -r src/ -ll              # Security linting
safety check                     # Dependency vulnerabilities
pip-audit                        # Package audit
```

### GitHub Actions

Security scans run automatically on:
- Every push to main/develop
- Every pull request
- Weekly schedule (Mondays at 9 AM UTC)

See [.github/workflows/security-audit.yml](.github/workflows/security-audit.yml)

### Pre-commit Hooks

Install pre-commit hooks to catch security issues before commit:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## 🔐 Security Configuration

### Environment Variables

Never commit sensitive data. Use environment variables:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Fill in your secrets in `.env` (this file is gitignored)

3. Access in code:
   ```python
   import os
   api_key = os.environ.get('AI_API_KEY')
   ```

### Gitignore

The following sensitive files are automatically ignored:
- `.env`, `.env.local`, `.env.*.local`
- `*.pem`, `*.key`, `*.crt` (certificates and keys)
- `secrets/`, `credentials/` (sensitive directories)
- `security-*.json` (security scan reports)
- `*.log` (log files that may contain sensitive data)

See [.gitignore](.gitignore) for complete list.

## 📋 Security Checklist

Before each release, complete the [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md):

- [ ] No hardcoded credentials
- [ ] All inputs validated
- [ ] Dependencies updated
- [ ] Security tests passing
- [ ] Bandit scan clean
- [ ] Safety check clean
- [ ] No secrets in code
- [ ] Documentation updated

## 🐛 Vulnerability Reporting

### How to Report

**DO NOT** open a public issue for security vulnerabilities.

Instead:
1. Email: **legal@deuos.io**
2. Subject: `[SECURITY] Brief description`
3. Include:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (optional)

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Based on severity
  - Critical: Within days
  - High: Within 2 weeks
  - Medium: Within 30 days
  - Low: Next release

### CVE Process

For significant vulnerabilities:
1. Private patch development
2. CVE assignment
3. Coordinated disclosure
4. Public advisory
5. Patch release

See [SECURITY.md](SECURITY.md) for full policy.

## 🔧 Security Tools

### Required Tools

Install security tools:

```bash
pip install bandit safety pip-audit pre-commit
```

### Tool Configuration

- **Bandit**: Configured in `.bandit` (if exists) or via CLI args
- **Pre-commit**: See [.pre-commit-config.yaml](.pre-commit-config.yaml)
- **GitHub Actions**: See [.github/workflows/](.github/workflows/)

## 📚 Security Best Practices

### For Developers

1. **Never commit secrets**
   - Use environment variables
   - Check with `git secrets --scan`
   - Pre-commit hooks will catch most cases

2. **Validate all inputs**
   ```python
   # Bad
   user_file = request.get('file')
   with open(user_file) as f:
       content = f.read()
   
   # Good
   user_file = validate_path(request.get('file'))
   if not user_file.is_relative_to(SAFE_DIR):
       raise ValueError("Invalid path")
   with open(user_file) as f:
       content = f.read()
   ```

3. **Use type hints**
   - Helps catch bugs early
   - Makes code more maintainable
   - Required for mypy checks

4. **Write security tests**
   - Test input validation
   - Test error handling
   - Test resource limits
   - See `tests/test_security.py`

5. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

### For Users

1. **Keep Syntari updated**
   ```bash
   pip install --upgrade syntari
   ```

2. **Review code you run**
   - Syntari code execution is powerful
   - Review untrusted `.syn` files
   - Use sandboxing when possible

3. **Report security issues**
   - See vulnerability reporting above
   - Help keep Syntari secure

## 🏗️ Secure Development Workflow

### Before Committing

```bash
# 1. Format code
make format

# 2. Run linters
make lint

# 3. Run tests
make test

# 4. Security check
make security

# 5. Stage changes
git add .

# 6. Pre-commit hooks run automatically
git commit -m "Your message"
```

### Before Releasing

```bash
# 1. Run comprehensive security scan
./security_scan.py

# 2. Review checklist
cat SECURITY_CHECKLIST.md

# 3. Update version
# Edit pyproject.toml

# 4. Tag release
git tag -a v0.3.x -m "Release v0.3.x"

# 5. Build and publish
make build
```

## 🔗 Additional Resources

- [SECURITY.md](SECURITY.md) - Full security policy
- [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) - Pre-release checklist
- [SECURITY_FIXES.md](SECURITY_FIXES.md) - Known fixes and patches
- [.github/COPILOT_SECURITY_SETUP.md](.github/COPILOT_SECURITY_SETUP.md) - Copilot security

## 📞 Contact

**Security Team**: legal@deuos.io  
**GitHub Security Advisories**: https://github.com/Adahandles/Syntari/security/advisories  
**General Issues**: https://github.com/Adahandles/Syntari/issues

---

**Last Updated**: January 26, 2026  
**Security Policy Version**: 1.0
