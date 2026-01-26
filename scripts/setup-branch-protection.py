#!/usr/bin/env python3
"""
Branch Protection Automation Script

This script automates the setup of branch protection rules for the Syntari repository
using the GitHub API. It implements the rules documented in .github/branch-protection-rules.md

Requirements:
- GITHUB_TOKEN environment variable with admin permissions
- Python 3.8+
- requests library: pip install requests

Usage:
    export GITHUB_TOKEN="your_github_token"
    python3 scripts/setup-branch-protection.py

Options:
    --owner OWNER       Repository owner (default: Adahandles)
    --repo REPO         Repository name (default: Syntari)
    --dry-run           Show what would be done without making changes
    --branch BRANCH     Specific branch to protect (default: main, develop)
"""

import argparse
import json
import os
import sys
from typing import Dict, Optional

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install with: pip install requests")
    sys.exit(1)


class BranchProtectionManager:
    """Manages branch protection rules via GitHub API"""

    def __init__(self, owner: str, repo: str, token: str, dry_run: bool = False):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.dry_run = dry_run
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_branch_protection_config(self, branch: str) -> Dict:
        """Get branch protection configuration based on branch name"""

        if branch == "main":
            return {
                "required_status_checks": {
                    "strict": True,
                    "contexts": [
                        "test (ubuntu-latest, 3.12)",
                        "lint",
                        "security",
                        "build",
                        "CodeQL",
                        "Security Audit / security-scan",
                    ],
                },
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "dismissal_restrictions": {},
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True,
                    "required_approving_review_count": 1,
                    "require_last_push_approval": True,
                },
                "restrictions": None,
                "required_linear_history": True,
                "allow_force_pushes": False,
                "allow_deletions": False,
                "required_conversation_resolution": True,
            }
        elif branch == "develop":
            return {
                "required_status_checks": {
                    "strict": True,
                    "contexts": [
                        "test (ubuntu-latest, 3.12)",
                        "lint",
                        "security",
                    ],
                },
                "enforce_admins": False,
                "required_pull_request_reviews": {
                    "dismissal_restrictions": {},
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": False,
                    "required_approving_review_count": 1,
                    "require_last_push_approval": False,
                },
                "restrictions": None,
                "required_linear_history": False,
                "allow_force_pushes": False,
                "allow_deletions": False,
                "required_conversation_resolution": True,
            }
        else:
            raise ValueError(f"Unknown branch: {branch}")

    def apply_branch_protection(self, branch: str) -> bool:
        """Apply branch protection rules to specified branch"""

        config = self.get_branch_protection_config(branch)
        url = f"{self.base_url}/branches/{branch}/protection"

        if self.dry_run:
            print(f"\n[DRY RUN] Would apply protection to branch '{branch}':")
            print(json.dumps(config, indent=2))
            return True

        print(f"\n⚙️  Applying protection to branch '{branch}'...")

        try:
            response = requests.put(url, headers=self.headers, json=config)

            if response.status_code == 200:
                print(f"✅ Successfully protected branch '{branch}'")
                return True
            else:
                print(f"❌ Failed to protect branch '{branch}'")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error protecting branch '{branch}': {e}")
            return False

    def verify_branch_exists(self, branch: str) -> bool:
        """Verify that branch exists in repository"""
        url = f"{self.base_url}/branches/{branch}"
        try:
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except Exception:
            return False

    def get_current_protection(self, branch: str) -> Optional[Dict]:
        """Get current branch protection settings"""
        url = f"{self.base_url}/branches/{branch}/protection"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Automate branch protection setup for Syntari repository"
    )
    parser.add_argument(
        "--owner", default="Adahandles", help="Repository owner (default: Adahandles)"
    )
    parser.add_argument(
        "--repo", default="Syntari", help="Repository name (default: Syntari)"
    )
    parser.add_argument(
        "--branch",
        action="append",
        help="Branch to protect (can be specified multiple times)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("   Set with: export GITHUB_TOKEN='your_token'")
        sys.exit(1)

    branches = args.branch if args.branch else ["main", "develop"]

    print("=" * 70)
    print("Branch Protection Automation")
    print("=" * 70)
    print(f"Repository: {args.owner}/{args.repo}")
    print(f"Branches: {', '.join(branches)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 70)

    manager = BranchProtectionManager(args.owner, args.repo, token, args.dry_run)

    success_count = 0
    for branch in branches:
        if not manager.verify_branch_exists(branch):
            print(f"\n⚠️  Branch '{branch}' does not exist - skipping")
            continue

        current = manager.get_current_protection(branch)
        if current:
            print(f"\n📋 Current protection for '{branch}': Already protected")
        else:
            print(f"\n📋 Current protection for '{branch}': None")

        if manager.apply_branch_protection(branch):
            success_count += 1

    print("\n" + "=" * 70)
    print(f"✅ Successfully protected {success_count}/{len(branches)} branches")
    print("=" * 70)

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")

    sys.exit(0 if success_count == len(branches) else 1)


if __name__ == "__main__":
    main()
