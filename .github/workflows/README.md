# GitHub Workflows Security Documentation

This directory contains GitHub Actions workflows that enforce security and quality standards for the Syntari repository.

## Workflow Overview

### Core CI/CD Workflows

#### `ci.yml` - Continuous Integration
**Triggers**: Push to main/develop, Pull Requests  
**Purpose**: Run tests, linting, type checking, and security scans

**Jobs**:
- `test` - Run test suite on multiple OS and Python versions
- `lint` - Code formatting and style checks (Black, flake8, mypy)
- `security` - Security scanning (Bandit, Safety)
- `build` - Build distribution packages

**Required for**: All branches

#### `codeql.yml` - CodeQL Security Analysis
**Triggers**: Push, PR, Weekly schedule, Manual  
**Purpose**: Deep security analysis using GitHub's CodeQL

**Features**:
- Detects security vulnerabilities in Python code
- Uses `security-extended` and `security-and-quality` query packs
- Creates security alerts in GitHub Security tab

**Required for**: Main branch

### Security Workflows

#### `security-audit.yml` - Comprehensive Security Audit
**Triggers**: Push, PR, Weekly schedule  
**Purpose**: Multi-layered security scanning

**Jobs**:
- `security-scan` - Bandit, Safety, pip-audit, security tests
- `dependency-review` - Check for vulnerable dependencies in PRs
- `secrets-scan` - TruffleHog secret detection

**Features**:
- Posts summary comments on PRs
- Uploads security reports as artifacts
- Continues on error but reports issues

#### `security-policy-enforcement.yml` - Security Policy Checks
**Triggers**: PR, Push, Daily schedule, Manual  
**Purpose**: Enforce security policies and standards
**SHA Pinned**: ✅ All actions pinned to commit SHAs

**Jobs**:
- `sensitive-data-check` - Scan for secrets, API keys, sensitive files
- `dependency-security` - Verify dependencies are secure and legitimate
- `code-security-standards` - Enforce coding standards (Bandit, Semgrep)
- `license-compliance` - Check dependency licenses
- `security-summary` - Aggregate results and comment on PR

**Features**:
- Prevents commits of sensitive data
- Detects typosquatting in dependencies
- Validates file permissions
- Ensures license compatibility

#### `sbom.yml` - Software Bill of Materials
**Triggers**: Push, PR, Release, Weekly schedule, Manual  
**Purpose**: Generate transparent dependency inventory
**SHA Pinned**: ✅ All actions pinned to commit SHAs
**SLSA Level 3**: ✅ Cryptographic signing with cosign

**Jobs**:
- `generate-sbom` - Create SBOM in multiple formats (CycloneDX, SPDX)
- `verify-sbom` - Validate SBOM completeness and compliance

**Outputs**:
- CycloneDX JSON SBOM
- Cryptographic signature bundle (cosign)
- Dependency tree
- Vulnerability report
- License inventory

**Features**:
- Attaches SBOM to GitHub Releases
- Comments on PRs with SBOM summary
- NTIA minimum elements compliance
- Verifiable cryptographic attestation

#### `dependabot-auto-merge.yml` - Automated Dependency Updates
**Triggers**: Pull Requests from Dependabot  
**Purpose**: Auto-approve and merge safe dependency updates
**SHA Pinned**: ✅ All actions pinned to commit SHAs

**Jobs**:
- `auto-approve` - Auto-approve patch/minor updates
- `auto-merge` - Enable auto-merge after status checks pass

**Features**:
- Auto-approves patch and minor version updates
- Requires manual review for major updates
- Waits for all status checks to pass
- Comments on PRs with merge status
- Faster security patch deployment

### Other Workflows

#### `dependency-scan.yml` - Dependency Analysis
**Triggers**: Weekly schedule  
**Purpose**: Monitor and update dependencies

#### `scorecard.yml` - OpenSSF Scorecard
**Triggers**: Weekly schedule  
**Purpose**: Assess project security best practices

#### `pr-checks.yml` - Pull Request Validation
**Triggers**: Pull Requests  
**Purpose**: Additional PR-specific checks

#### `benchmarks.yml` - Performance Benchmarks
**Triggers**: Push, Manual  
**Purpose**: Track performance metrics

#### `docker.yml` - Docker Image Build
**Triggers**: Push, Release  
**Purpose**: Build and publish Docker images

#### `release.yml` - Release Automation
**Triggers**: Release published  
**Purpose**: Automate release process

#### `docs.yml` - Documentation
**Triggers**: Push to docs, Manual  
**Purpose**: Build and deploy documentation

## Security Best Practices

### Action Pinning
All actions should be pinned to specific SHA hashes for security:
```yaml
# ❌ Avoid
uses: actions/checkout@v4

# ✅ Preferred
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

See [WORKFLOW_SECURITY.md](WORKFLOW_SECURITY.md) for current SHA hashes.

### Minimal Permissions
Each workflow uses minimal required permissions:
```yaml
permissions:
  contents: read  # Most restrictive by default
```

Jobs override with specific permissions as needed.

### Secret Handling
- Never log secrets or sensitive data
- Use GitHub Secrets for credentials
- Mask sensitive outputs
- Use environment variables, not inline values

### Input Validation
- Validate all external inputs
- Use intermediate environment variables for untrusted data
- Never use `${{ github.event.* }}` directly in shell commands

## Workflow Status Checks

### Required for Main Branch
These checks must pass before merging to `main`:
- ✅ `test (ubuntu-latest, 3.12)` - Core test suite
- ✅ `lint` - Code quality
- ✅ `security` - Security scan
- ✅ `build` - Package build
- ✅ `CodeQL` - Security analysis
- ✅ `Security Audit / security-scan` - Comprehensive security

### Required for Pull Requests
Additional checks for PRs:
- ✅ All main branch checks
- ✅ `Security Audit / dependency-review` - Dependency analysis
- ✅ `Security Policy Enforcement` - Policy compliance

## Monitoring and Maintenance

### Weekly Tasks
- [ ] Review workflow run results
- [ ] Check for failed security scans
- [ ] Review Dependabot PRs
- [ ] Update pinned action versions if needed

### Monthly Tasks
- [ ] Audit workflow permissions
- [ ] Review security findings
- [ ] Update workflow documentation
- [ ] Check for workflow updates

### Quarterly Tasks
- [ ] Comprehensive workflow review
- [ ] Update security policies
- [ ] Review and update action pins
- [ ] Performance optimization

## Troubleshooting

### Common Issues

**Issue**: Workflow fails with "Resource not accessible by integration"  
**Solution**: Check workflow permissions in YAML file

**Issue**: Secret scanning fails with false positives  
**Solution**: Update TruffleHog configuration or add to allowlist

**Issue**: Dependency scan finds vulnerabilities  
**Solution**: Update dependencies, or document/accept risk if false positive

**Issue**: CodeQL analysis times out  
**Solution**: Increase timeout or optimize queries

### Debug Mode

Enable debug logging:
1. Go to Settings > Secrets and variables > Actions
2. Add repository secret: `ACTIONS_STEP_DEBUG` = `true`
3. Add repository secret: `ACTIONS_RUNNER_DEBUG` = `true`

### Getting Help

- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **Security Issues**: legal@deuos.io
- **Workflow Issues**: Open an issue in the repository

## Workflow Artifacts

### Retention Policies
- Security reports: 90 days
- Build artifacts: 30 days
- Test results: 30 days
- SBOM: 90 days (also attached to releases)

### Artifact Contents

**Security Reports**:
- `bandit-report.json` - Python security linter results
- `safety-report.json` - Dependency vulnerability scan
- `pip-audit.json` - Comprehensive dependency audit
- `semgrep-report.json` - Semantic security analysis

**Build Artifacts**:
- `dist/` - Python distribution packages (.whl, .tar.gz)

**SBOM Artifacts**:
- `sbom-cyclonedx.json` - CycloneDX format SBOM
- `sbom-vulnerabilities.json` - Known vulnerabilities
- `dependency-tree.json` - Dependency graph
- `licenses.json` - License inventory

## Performance Optimization

### Workflow Optimization Tips

1. **Use caching**: Cache pip packages, dependencies
2. **Parallel jobs**: Independent checks run in parallel
3. **Conditional steps**: Skip unnecessary steps with `if` conditions
4. **Artifact efficiency**: Only upload necessary artifacts
5. **Matrix strategy**: Test on critical platforms only in some workflows

### Current Optimization
- Python dependency caching enabled
- Matrix testing on 3 OS × 5 Python versions
- Security checks continue on error but report issues
- Artifact retention optimized by type

## Compliance and Reporting

### Compliance Reports
Workflows help maintain compliance with:
- OWASP Top 10
- NIST Cybersecurity Framework
- SLSA Framework
- CIS Controls

### Audit Trail
All workflow runs are logged and auditable:
- GitHub Actions audit log
- Security alerts and advisories
- Dependency updates via Dependabot
- SBOM generation for transparency

## Updates and Changelog

Track workflow changes in:
- Git commit history for this directory
- [CHANGELOG.md](../CHANGELOG.md) for major changes
- [SECURITY.md](../SECURITY.md) for security-related updates

---

**Last Updated**: January 26, 2026  
**Maintained By**: @Adahandles  
**Review Frequency**: Quarterly
