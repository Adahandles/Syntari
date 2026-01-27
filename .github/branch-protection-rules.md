# Branch Protection Rules for Syntari

This document outlines the recommended branch protection rules for the Syntari repository. These rules must be configured in GitHub's repository settings under **Settings > Branches** or **Settings > Rules > Rulesets**.

## Main Branch Protection

### Required Settings for `main` branch:

#### Pull Request Requirements
- ✅ **Require a pull request before merging**
  - Require approvals: **1** (minimum)
  - Dismiss stale pull request approvals when new commits are pushed
  - Require review from Code Owners
  - Require approval of the most recent reviewable push

#### Status Checks
- ✅ **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Required status checks:
    - `test (ubuntu-latest, 3.12)` - CI test suite
    - `lint` - Code linting
    - `security` - Security scanning
    - `CodeQL` - Security analysis
    - `Security Audit / security-scan` - Security audit
    - `Security Audit / dependency-review` (for PRs only)

#### Commit and History Requirements
- ✅ **Require linear history** - Prevents merge commits, ensures clean history
- ✅ **Require signed commits** - Ensures commit authenticity with GPG/SSH signatures
- ✅ **Do not allow bypassing the above settings**

#### Additional Protections
- ✅ **Lock branch** - Prevent all modifications (optional, for production releases)
- ✅ **Restrict who can push to matching branches**
  - Only repository administrators
- ✅ **Allow force pushes** - **DISABLED**
- ✅ **Allow deletions** - **DISABLED**

## Develop Branch Protection

### Required Settings for `develop` branch:

#### Pull Request Requirements
- ✅ **Require a pull request before merging**
  - Require approvals: **1** (minimum)
  - Dismiss stale pull request approvals when new commits are pushed

#### Status Checks
- ✅ **Require status checks to pass before merging**
  - Required status checks:
    - `test (ubuntu-latest, 3.12)` - CI test suite
    - `lint` - Code linting
    - `security` - Security scanning

#### Additional Protections
- ✅ **Restrict who can push to matching branches**
  - Only repository collaborators and team members
- ✅ **Allow force pushes** - **DISABLED**
- ✅ **Allow deletions** - **DISABLED**

## Release Branches

### Pattern: `release/*`

#### Requirements
- ✅ **Require a pull request before merging**
  - Require approvals: **2** (minimum)
  - Require review from Code Owners
  
#### Status Checks
- ✅ All CI/CD checks must pass
- ✅ Security scans must pass
- ✅ Documentation must be updated

## Hotfix Branches

### Pattern: `hotfix/*`

#### Requirements
- ✅ **Require a pull request before merging**
  - Require approvals: **1** (expedited for urgent fixes)
  - Require review from Code Owners
  
#### Status Checks
- ✅ All critical security checks must pass
- ✅ Core test suite must pass

## Configuration via GitHub Settings

### Step-by-Step Setup

1. **Navigate to Repository Settings**
   - Go to: `https://github.com/Adahandles/Syntari/settings`

2. **Access Branch Protection**
   - Click on **Branches** in the left sidebar
   - Or use **Rules > Rulesets** for newer ruleset-based protection

3. **Add Branch Protection Rule**
   - Click "Add rule" or "New ruleset"
   - Enter branch name pattern (e.g., `main`, `develop`)
   - Configure settings as outlined above

4. **Configure Rulesets (Recommended)**
   - Navigate to **Settings > Rules > Rulesets**
   - Click **New ruleset** > **New branch ruleset**
   - Set the ruleset name (e.g., "Main Branch Protection")
   - Set enforcement status to **Active**
   - Add target branches (e.g., `main`)
   - Configure rules as described above

### Ruleset vs Classic Branch Protection

**Use Rulesets** (modern approach):
- More flexible and powerful
- Can apply to multiple branches with patterns
- Better integration with GitHub Actions
- Easier to version control and document

**Classic Branch Protection** (legacy):
- Simpler interface
- Per-branch configuration
- Still widely supported

## Security Best Practices

1. **Never bypass branch protection** - Even administrators should follow the rules
2. **Require signed commits** - Verify commit authenticity
3. **Keep status checks comprehensive** - More checks = more confidence
4. **Regular reviews** - Audit branch protection rules quarterly
5. **Document exceptions** - If bypassing is necessary, document why

## Automation and Enforcement

The following workflows help enforce these rules:

- `.github/workflows/ci.yml` - Runs tests, linting, and security checks
- `.github/workflows/codeql.yml` - Performs security analysis
- `.github/workflows/security-audit.yml` - Comprehensive security scanning
- `.github/workflows/pr-checks.yml` - Additional PR validation

## Emergency Procedures

In case of critical production issues:

1. **Hotfix Process**:
   - Create `hotfix/*` branch from `main`
   - Make minimal necessary changes
   - Get expedited review (1 approval minimum)
   - Ensure all security checks pass
   - Merge to `main` and backport to `develop`

2. **Bypass Procedure** (Admins only, last resort):
   - Document reason in issue
   - Get approval from repository owner
   - Temporarily disable specific rule
   - Make change
   - Re-enable rule immediately
   - Document action in audit log

## Monitoring and Compliance

- **Weekly**: Review branch protection audit logs
- **Monthly**: Verify all rules are properly configured
- **Quarterly**: Update rules based on security best practices
- **After incidents**: Review and update rules to prevent recurrence

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [Required Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)

---

**Last Updated**: January 26, 2026  
**Maintained By**: @Adahandles  
**Review Frequency**: Quarterly
