# Security Policy

## Supported Versions

We take the security of Syntari seriously. The following versions are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | :white_check_mark: |
| 0.3.x   | :x:                |
| 0.2.x   | :x:                |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Syntari, please follow these steps:

### 1. Do Not Open a Public Issue

Please **do not** open a public GitHub issue for security vulnerabilities. This helps prevent malicious actors from exploiting the vulnerability before a fix is available.

### 2. Contact Us Directly

Report security vulnerabilities to our security team:

- **Email**: legal@deuos.io
- **Subject**: [SECURITY] Brief description of the vulnerability

### 3. Provide Detailed Information

In your report, please include:

- **Type of vulnerability** (e.g., code injection, information disclosure, denial of service)
- **Affected component** (e.g., interpreter, parser, runtime)
- **Steps to reproduce** the vulnerability
- **Potential impact** of the vulnerability
- **Suggested remediation** (if you have any)
- **Your contact information** for follow-up questions

### 4. Response Timeline

You can expect:

- **Initial response**: Within 48 hours of your report
- **Status update**: Within 7 days with our assessment and planned actions
- **Resolution timeline**: Depends on severity and complexity
  - Critical: Immediate action (within days)
  - High: Within 2 weeks
  - Medium: Within 30 days
  - Low: Next scheduled release

### 5. Coordinated Disclosure

We believe in coordinated disclosure:

- We will work with you to understand and validate the vulnerability
- We will develop and test a fix
- We will coordinate the timing of the public disclosure
- We will credit you for the discovery (unless you prefer to remain anonymous)

## Security Best Practices for Contributors

When contributing to Syntari, please keep these security considerations in mind:

### Input Validation
- Always validate and sanitize user input in parsers and lexers
- Implement proper bounds checking
- Handle edge cases and malformed input gracefully

### Error Handling
- Never expose sensitive information in error messages
- Use generic error messages for security-critical operations
- Log detailed errors internally, but show sanitized messages to users

### Code Execution Safety
- Implement proper sandboxing for code execution
- Limit resource consumption (memory, CPU, file operations)
- Validate all external code before execution

### Dependency Management
- Keep dependencies up to date
- Review security advisories for dependencies
- Use tools like Dependabot for automated security updates
- Run CodeQL security scanning on all code changes

### Secrets Management
- Never commit API keys, tokens, or credentials
- Use environment variables for sensitive configuration
- Review code for accidental secret exposure before committing

### Authentication & Authorization
- Implement proper authentication mechanisms for protected features
- Follow the principle of least privilege
- Validate permissions before granting access to sensitive operations

## Security Features

Syntari includes several security features:

- **Sandboxed Execution**: Code runs in a controlled environment
- **Type Safety**: Static type checking prevents many common vulnerabilities
- **Input Validation**: Robust parsing with proper error handling
- **Deterministic Output**: Predictable behavior prevents timing attacks
- **CodeQL Scanning**: Automated vulnerability detection in CI/CD
- **Dependency Scanning**: Automated updates via Dependabot
- **Branch Protection**: Enforced code review and status checks on protected branches
- **Security Policy Enforcement**: Automated checks for secrets, vulnerabilities, and compliance
- **SBOM Generation**: Software Bill of Materials for transparency and compliance
- **License Compliance**: Automated license checking for all dependencies
- **Secret Scanning**: Continuous monitoring for leaked credentials
- **Workflow Security**: GitHub Actions pinned and hardened against supply chain attacks

## Security Updates

Security updates are released as soon as possible after validation:

- **Critical vulnerabilities**: Immediate patch release
- **High-severity issues**: Expedited release within days
- **Medium/Low severity**: Included in next regular release

Security advisories will be published on:
- GitHub Security Advisories
- Release notes
- Security page on our website (if applicable)

## Code of Conduct

We expect all security researchers to:
- Act in good faith
- Not exploit vulnerabilities beyond what's necessary for research
- Not access, modify, or delete data without authorization
- Not perform actions that could harm users or the system
- Comply with all applicable laws and regulations

## Recognition

We appreciate the security research community's contributions to keeping Syntari secure. Security researchers who report valid vulnerabilities will be:

- Publicly acknowledged (if desired)
- Listed in our security hall of fame
- Credited in release notes for the fix

Thank you for helping keep Syntari and its users safe!

## Automated Security Workflows

Syntari employs comprehensive automated security checks:

### Continuous Security Monitoring
- **Daily Security Scans**: Automated checks run daily to detect new vulnerabilities
- **Secret Scanning**: TruffleHog scans for exposed credentials and API keys
- **Dependency Auditing**: pip-audit and Safety check for vulnerable dependencies
- **License Compliance**: Automated license verification for all dependencies
- **SBOM Generation**: Weekly Software Bill of Materials creation for transparency

### Pull Request Security
Every pull request is automatically checked for:
- Sensitive data exposure (secrets, keys, credentials)
- Dependency vulnerabilities
- Code security issues (Bandit, Semgrep)
- License compatibility
- File permission security

### Branch Protection
Protected branches (main, develop) enforce:
- Required pull request reviews
- Passing security status checks
- Up-to-date branches before merging
- Code owner approval
- No force pushes or deletions

See [Branch Protection Rules](.github/branch-protection-rules.md) for complete details.

## Additional Resources

- [Contributing Guidelines](CONTRIBUTING.md)
- [Branch Protection Rules](.github/branch-protection-rules.md)
- [Workflow Security Best Practices](.github/WORKFLOW_SECURITY.md)
- [Development Documentation](DEVELOPMENT_SUMMARY.md)

## Legal

Syntari is proprietary software owned by DeuOS, LLC. All security reports and subsequent fixes are subject to the terms of the Syntari Commercial License Agreement.

---

© 2025 DeuOS, LLC. All Rights Reserved.
