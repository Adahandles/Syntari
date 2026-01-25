# Quick Reference: Security & Development Setup

## 🚀 Quick Start for Developers

### Before Committing
```bash
# 1. Format code
make format

# 2. Run linters
make lint

# 3. Run tests
make test

# 4. Security check (optional but recommended)
pip install bandit safety
bandit -r src/
safety check
```

### GitHub Copilot Setup

GitHub Copilot is now configured with Syntari-specific instructions!

**What you get:**
- Context-aware code suggestions
- Syntari coding patterns and conventions
- Security-aware recommendations
- Consistent style across the codebase

**No action needed** - Copilot will automatically use `.github/copilot-instructions.md`

## 🔒 Security Features

### Automated Scans

All PRs automatically run:
- ✓ CodeQL security analysis
- ✓ Bandit Python security linter
- ✓ Safety dependency vulnerability check
- ✓ Code formatting and linting

### Dependency Updates

Dependabot will automatically:
- Create PRs for security updates (immediate)
- Update dependencies weekly (grouped for dev tools)
- Check for vulnerable packages

**Action required:** Review and merge Dependabot PRs weekly

### Security Reporting

**Found a vulnerability?**
- 🔴 **Sensitive/Exploitable**: Email `legal@deuos.io` (DO NOT create public issue)
- 🟡 **Non-sensitive**: Use the Security issue template
- See `SECURITY.md` for full details

## 📝 PR Checklist

When creating a PR, ensure:
- [ ] PR template is filled out completely
- [ ] Tests added/updated for changes
- [ ] Code formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Security considerations addressed
- [ ] Documentation updated if needed

## 🛠️ Common Commands

```bash
# Development
make install          # Install in dev mode
make test            # Run tests
make lint            # Run linters
make format          # Format with Black

# Running Syntari
python3 main.py file.syn    # Run a program
make repl                   # Start REPL

# Security checks (manual)
bandit -r src/              # Python security
safety check                # Dependency vulnerabilities
```

## 📊 Monitoring

Check these regularly:
1. **Security tab** - CodeQL alerts and vulnerabilities
2. **Dependabot PRs** - Dependency updates
3. **Actions tab** - Workflow results and security reports
4. **OpenSSF Scorecard** - Security posture metrics

## 🔗 Quick Links

- [Copilot Instructions](.github/copilot-instructions.md)
- [Security Policy](../SECURITY.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Full Setup Documentation](.github/COPILOT_SECURITY_SETUP.md)

## 💡 Tips

1. **Use Copilot effectively**: Provide clear comments describing what you want
2. **Review suggestions**: Always review and test Copilot suggestions
3. **Security first**: Consider security implications of all code changes
4. **Ask for help**: Use issue templates or discussions for questions

## 🚨 Important Notes

- Never commit secrets, API keys, or credentials
- Always validate user input in parsers/lexers
- Follow existing code patterns and conventions
- Keep dependencies up to date
- Review security scan results in CI

---

**Need help?** Create an issue or email legal@deuos.io
