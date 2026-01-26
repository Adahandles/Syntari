# Workflow Security Best Practices
# This document outlines security best practices for GitHub Actions workflows

## Action Version Pinning

For maximum security, all GitHub Actions should be pinned to specific commit SHAs rather than tags.
This prevents supply chain attacks where action repositories could be compromised.

### Current Action Versions (as of January 2026)

| Action | Tag | SHA (for reference) |
|--------|-----|---------------------|
| actions/checkout@v4 | v4.2.2 | 11bd71901bbe5b1630ceea73d27597364c9af683 |
| actions/setup-python@v5 | v5.3.0 | f677139bbe7f9c59b41e40162b753c062f5d49a3 |
| actions/upload-artifact@v4 | v4.5.0 | ea165472dc06b43ed5a2f6dc0e8c35e8e0c139b8 |
| codecov/codecov-action@v5 | v5.2.0 | 7f8b4b4bde536c465e797be725027e06c3e9e182 |
| github/codeql-action/init@v4 | v4.0.0 | 83a02f7883b12e0e4e1a146174f5e2e48a5d4b4d |
| github/codeql-action/analyze@v4 | v4.0.0 | 83a02f7883b12e0e4e1a146174f5e2e48a5d4b4d |
| actions/github-script@v7 | v7.0.1 | 7804639f0b32c0c674c6d0b5b7c5e9b3c7b7d3e2 |
| trufflesecurity/trufflehog | v3.82.13 | Use specific release tag, not @main |

### How to Pin Actions

**Before (insecure):**
```yaml
- uses: actions/checkout@v4
```

**After (secure):**
```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

### Automated Monitoring

Use Dependabot to monitor action updates:

```yaml
# .github/dependabot.yml
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Workflow Security Checklist

### ✅ Permissions
- [ ] Use minimal required permissions
- [ ] Explicitly define permissions for each job
- [ ] Use `permissions: read-all` or specific permissions, never `write-all`

### ✅ Secrets Management
- [ ] Never log secrets or sensitive data
- [ ] Use environment secrets, not hardcoded values
- [ ] Mask sensitive outputs with `::add-mask::`
- [ ] Use OIDC for cloud provider authentication when possible

### ✅ Code Injection Prevention
- [ ] Never use untrusted input directly in shell commands
- [ ] Use `${{ github.event.inputs.* }}` with caution
- [ ] Validate all external inputs
- [ ] Use intermediate environment variables for untrusted data

### ✅ Third-Party Actions
- [ ] Pin all actions to specific SHAs
- [ ] Review action source code before use
- [ ] Prefer verified/official actions
- [ ] Monitor actions for updates and security advisories

### ✅ Artifact Security
- [ ] Set retention periods for artifacts
- [ ] Don't include secrets in artifacts
- [ ] Use artifact attestations when available
- [ ] Clean up artifacts after use

### ✅ Runner Security
- [ ] Use GitHub-hosted runners when possible
- [ ] Keep self-hosted runners updated and isolated
- [ ] Don't use self-hosted runners for public repositories
- [ ] Limit runner access to specific repositories

## Example Secure Workflow

```yaml
name: Secure CI Example

on:
  pull_request:
    branches: [ main ]

# Minimal permissions
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    
    # Job-specific permissions
    permissions:
      contents: read
      checks: write
    
    steps:
    # Pinned to SHA
    - name: Checkout code
      uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      with:
        persist-credentials: false
    
    # Environment variable for untrusted input
    - name: Validate input
      env:
        PR_TITLE: ${{ github.event.pull_request.title }}
      run: |
        # Safe: input is in environment variable
        echo "PR Title: $PR_TITLE"
    
    # No secrets in commands
    - name: Use secret safely
      env:
        MY_SECRET: ${{ secrets.MY_SECRET }}
      run: |
        # Secret is only in environment, never echoed
        ./script.sh
```

## Security Scanning in Workflows

### CodeQL Integration
```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v4
  with:
    languages: python
    queries: security-extended,security-and-quality
```

### Dependency Scanning
```yaml
- name: Run Dependency Review
  uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: high
```

### Secret Scanning
```yaml
- name: TruffleHog Secret Scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    extra_args: --only-verified
```

## Incident Response

If a workflow security issue is discovered:

1. **Immediate**: Disable the workflow
2. **Investigate**: Review logs and identify scope
3. **Remediate**: Fix the vulnerability
4. **Update**: Update all affected workflows
5. **Monitor**: Watch for similar issues
6. **Document**: Record incident and lessons learned

## References

- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
- [SLSA Framework](https://slsa.dev/)

---

**Last Updated**: January 26, 2026  
**Review Frequency**: Monthly or after security advisories
