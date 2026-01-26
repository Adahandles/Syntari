# Automation Scripts

This directory contains automation scripts for repository management.

## Branch Protection Setup

**Script**: `setup-branch-protection.py`

Automates the configuration of branch protection rules via GitHub API, eliminating manual UI configuration.

### Requirements

```bash
pip install requests
```

### Usage

```bash
# Set GitHub token (requires admin permissions)
export GITHUB_TOKEN="your_github_personal_access_token"

# Dry run (preview changes)
python3 scripts/setup-branch-protection.py --dry-run

# Apply to main and develop branches (default)
python3 scripts/setup-branch-protection.py

# Apply to specific branch
python3 scripts/setup-branch-protection.py --branch main

# Custom repository
python3 scripts/setup-branch-protection.py --owner YourOrg --repo YourRepo
```

### Features

- ✅ Automated branch protection setup
- ✅ Configurable per-branch rules
- ✅ Dry-run mode for safety
- ✅ Status check verification
- ✅ Matches rules in `.github/branch-protection-rules.md`

### Protection Rules Applied

**Main Branch**:
- Required reviews: 1 approval
- Required status checks: test, lint, security, build, CodeQL, Security Audit
- Code owner review required
- Linear history enforced
- Signed commits recommended
- No force pushes or deletions

**Develop Branch**:
- Required reviews: 1 approval
- Required status checks: test, lint, security
- Merge commits allowed
- No force pushes or deletions

### Troubleshooting

**Error: GITHUB_TOKEN not set**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

**Error: requests not installed**
```bash
pip install requests
```

**Permission denied**
- Ensure token has `repo` and `admin:repo_hook` scopes
- Verify you have admin access to the repository

## Future Scripts

Additional automation scripts will be added here as needed:
- Dependency update automation
- Release automation
- Security scanning automation
- Documentation generation
