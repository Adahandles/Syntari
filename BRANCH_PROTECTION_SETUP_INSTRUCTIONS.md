# Branch Protection Setup Instructions

## Quick Start Guide for Repository Administrator

This guide provides step-by-step instructions to configure branch protection for the Syntari repository.

## Prerequisites

- Repository admin access to Adahandles/Syntari
- GitHub account with appropriate permissions

## Step 1: Access Repository Settings

1. Go to: https://github.com/Adahandles/Syntari
2. Click on **Settings** tab (requires admin access)
3. In the left sidebar, look for:
   - **Branches** (for classic branch protection), OR
   - **Rules > Rulesets** (for modern ruleset-based protection - RECOMMENDED)

## Step 2: Configure Main Branch Protection (Recommended Method - Rulesets)

### Using Rulesets (Modern Approach)

1. Navigate to **Settings > Rules > Rulesets**
2. Click **New ruleset** → **New branch ruleset**
3. Configure the ruleset:

**Basic Settings:**
- Ruleset Name: `Main Branch Protection`
- Enforcement status: **Active**
- Bypass list: Leave empty (no bypasses)

**Target branches:**
- Click **Add target** → **Include by pattern**
- Enter pattern: `main`
- Click **Add target** again → **Include by pattern**  
- Enter pattern: `master` (fallback)

**Rules - Enable these checkboxes:**

✅ **Restrict deletions** - Prevent branch deletion

✅ **Require a pull request before merging**
- Required approvals: `1`
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners
- ✅ Require approval of the most recent reviewable push
- ✅ Require conversation resolution before merging

✅ **Require status checks to pass before merging**
- ✅ Require branches to be up to date before merging
- Add required status checks (click "Add checks"):
  - `test (ubuntu-latest, 3.12)`
  - `lint`
  - `security`
  - `build`
  - `CodeQL`
  - `Security Audit / security-scan`

✅ **Block force pushes**

✅ **Require signed commits** (Recommended for maximum security)

✅ **Require linear history** (Recommended for clean history)

4. Click **Create** to save the ruleset

## Step 3: Configure Develop Branch Protection

Repeat Step 2 with these modifications:

**Basic Settings:**
- Ruleset Name: `Develop Branch Protection`
- Target pattern: `develop`

**Rules - Modified settings:**
- Required approvals: `1`
- Do NOT require Code Owner review (more flexible)
- Do NOT require signed commits (optional)
- Do NOT require linear history (allow merge commits)
- Required status checks (fewer):
  - `test (ubuntu-latest, 3.12)`
  - `lint`
  - `security`

## Alternative: Classic Branch Protection Rules

If you prefer classic branch protection:

1. Navigate to **Settings > Branches**
2. Click **Add rule** or **Add branch protection rule**
3. Enter branch name pattern: `main`
4. Configure settings as described in Step 2 above
5. Click **Create** or **Save changes**
6. Repeat for `develop` branch

## Step 4: Verify Configuration

1. Try to push directly to main branch (should be blocked)
2. Create a test PR to main
3. Verify that:
   - Status checks are required
   - Approval is required
   - Direct push is blocked

## Step 5: Enable Required Workflows

Ensure these workflows are enabled in **Settings > Actions > General**:

✅ Allow all actions and reusable workflows
✅ Allow GitHub Actions to create and approve pull requests (if needed for automation)

## Step 6: Configure Code Owners (Already configured)

The `.github/CODEOWNERS` file is already configured. Verify it includes:

```
* @Adahandles
```

## Step 7: Set Up Secrets (If needed)

If workflows require secrets:

1. Go to **Settings > Secrets and variables > Actions**
2. Add required secrets (none currently required for security workflows)

## Verification Checklist

After configuration, verify:

- [ ] Cannot push directly to main branch
- [ ] Cannot delete main branch
- [ ] Cannot force push to main branch
- [ ] PRs to main require 1 approval
- [ ] PRs to main require status checks to pass
- [ ] Status checks run automatically on PRs
- [ ] Security workflows execute successfully
- [ ] SBOM generation works (check weekly schedule)

## Troubleshooting

### Issue: Status checks not showing up

**Solution**: 
1. Make sure workflows have run at least once
2. Status check names must match exactly (case-sensitive)
3. Check workflow names in `.github/workflows/*.yml` files

### Issue: Can't add status checks

**Solution**:
1. Push a commit to trigger workflows first
2. Wait for workflows to complete
3. Then add them as required checks

### Issue: Accidentally locked out

**Solution**:
1. Admin users can temporarily disable protection
2. Make necessary changes
3. Re-enable protection immediately
4. Document the bypass in audit log

## Maintenance

Review and update branch protection settings:

- **Weekly**: Check for failed protection events
- **Monthly**: Review and update required status checks
- **Quarterly**: Complete security review and update settings

## Support

For questions or issues:

- Review: `.github/branch-protection-rules.md`
- Security: `.github/SECURITY_COMPLIANCE.md`
- Contact: legal@deuos.io

---

**Last Updated**: January 26, 2026  
**Next Review**: Quarterly  
**Document Owner**: @Adahandles
