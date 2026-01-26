# Automation Scripts

This directory contains automation scripts for repository management and development workflow optimization.

## Development Setup Scripts

### Quick Setup

**Script**: `quick-setup.sh`

One-command setup for complete development environment.

```bash
# Run from repository root
bash scripts/quick-setup.sh
```

**Features**:
- ✅ Checks Python version
- ✅ Creates/activates virtual environment
- ✅ Installs all dependencies
- ✅ Sets up pre-commit hooks
- ✅ Runs initial tests
- ✅ Displays quick start guide

**Time**: ~2-3 minutes for complete setup

### Pre-commit Hook Installation

**Script**: `install-pre-commit-hooks.sh`

Installs and configures pre-commit hooks for local code quality validation.

```bash
# Install pre-commit hooks
bash scripts/install-pre-commit-hooks.sh
```

**Features**:
- ✅ Auto-installs pre-commit if not present
- ✅ Configures Git hooks
- ✅ Updates hooks to latest versions
- ✅ Validates on all existing files

**Hooks Installed**:
- Black (code formatting)
- flake8 (linting)
- Bandit (security)
- isort (import sorting)
- mypy (type checking)
- detect-secrets (secret scanning)
- YAML/JSON validation
- Trailing whitespace removal

## Repository Management Scripts

### Branch Protection Setup

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

## Workflow Optimization

The repository now includes several workflow optimizations:

### Automated Workflows

1. **Dependabot Auto-Merge** (`.github/workflows/dependabot-auto-merge.yml`)
   - Auto-approves patch/minor dependency updates
   - Enables auto-merge after checks pass

2. **Auto-Labeling** (`.github/workflows/auto-label.yml`)
   - Automatically labels PRs based on changed files
   - Labels issues based on content

3. **Stale Management** (`.github/workflows/stale-management.yml`)
   - Auto-closes inactive issues (60 days)
   - Auto-closes stale PRs (30 days)

4. **Release Automation** (`.github/workflows/release-automation.yml`)
   - Generates release notes from commits
   - Categorizes changes by type

5. **Optimized CI** (`.github/workflows/optimized-ci.yml`)
   - Conditional job execution
   - Dependency caching
   - Parallel test execution

### Development Environment

**Dev Container** (`.devcontainer/devcontainer.json`)
- Pre-configured VS Code environment
- GitHub Codespaces compatible
- All tools pre-installed

### Enhanced Templates

**Issue Templates**:
- Bug report with guided fields
- Feature request with categorization

**PR Template**:
- Comprehensive checklist
- Type categorization
- Testing section

## Best Practices

### Daily Development Workflow

```bash
# 1. Start development (first time)
bash scripts/quick-setup.sh

# 2. Activate environment (subsequent times)
source venv/bin/activate

# 3. Pull latest changes
git pull

# 4. Create feature branch
git checkout -b feature/my-feature

# 5. Make changes (hooks run automatically on commit)
git add .
git commit -m "feat: add new feature"

# 6. Push and create PR
git push origin feature/my-feature
```

### Pre-commit Hooks

Hooks run automatically on every commit. To run manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Skip hooks (not recommended)
git commit --no-verify
```

## Future Scripts

Additional automation scripts planned:
- Performance benchmarking automation
- Documentation generation
- Multi-environment deployment
- Database migration helpers

## Contributing

When adding new scripts:
1. Make them executable: `chmod +x script.sh`
2. Add shebang: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`
3. Include help/usage information
4. Document in this README
5. Test on clean environment

