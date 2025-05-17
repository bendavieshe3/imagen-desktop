#!/usr/bin/env python3
"""
GitHub Workflow Demonstration Script.

This script demonstrates the complete GitHub workflow from issue creation
to PR submission and issue resolution.

Usage:
    python github_workflow_demo.py [issue_title] [issue_body]

Example:
    python github_workflow_demo.py "Add dark mode" "Implement dark mode toggle in settings"
"""

import argparse
import os
import re
import subprocess
import sys
from typing import Optional, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imagen_desktop.utils.github_workflow import (
    validate_branch_name,
    validate_commit_message,
    create_pull_request,
    close_issue,
    check_issue_exists,
    extract_issue_numbers
)


def run_command(cmd: str) -> Tuple[int, str]:
    """Run a shell command and return exit code and output."""
    process = subprocess.run(
        cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    return process.returncode, process.stdout.strip()


def create_issue(title: str, body: str) -> Optional[int]:
    """Create a GitHub issue and return its number."""
    print(f"\n=== Creating issue: {title} ===")
    
    # Check if gh CLI is installed
    code, _ = run_command("which gh")
    if code != 0:
        print("GitHub CLI not found. Please install it: https://cli.github.com/")
        return None
    
    # Create issue
    code, output = run_command(f'gh issue create --title "{title}" --body "{body}"')
    if code != 0:
        print(f"Error creating issue: {output}")
        return None
    
    # Extract issue number from URL
    match = re.search(r'issues/(\d+)', output)
    if not match:
        print(f"Created issue but couldn't extract number: {output}")
        return None
        
    issue_number = int(match.group(1))
    print(f"✅ Created issue #{issue_number}: {output}")
    return issue_number


def create_feature_branch(issue_number: int, feature_name: str) -> bool:
    """Create a feature branch for the issue."""
    branch_name = f"feature/{feature_name}"
    print(f"\n=== Creating branch: {branch_name} ===")
    
    # Validate branch name
    is_valid, error = validate_branch_name(branch_name)
    if not is_valid:
        print(f"Invalid branch name: {error}")
        return False
    
    # Create and checkout branch
    code, output = run_command(f"git checkout -b {branch_name}")
    if code != 0:
        print(f"Error creating branch: {output}")
        return False
        
    print(f"✅ Created and checked out branch: {branch_name}")
    return True


def make_changes(issue_number: int) -> bool:
    """Simulate making changes to files."""
    print("\n=== Making changes for feature ===")
    
    # Create a temp test file
    test_file = "tests/ui/test_demo_feature.py"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    
    with open(test_file, "w") as f:
        f.write(f"""
\"\"\"Test for demo feature.\"\"\"

import pytest

@pytest.mark.unit
def test_demo_feature():
    \"\"\"Test that demo feature works.\"\"\"
    # This test would test the actual feature
    assert True
""")
    
    # Create implementation file
    impl_file = "imagen_desktop/ui/features/demo_feature.py"
    os.makedirs(os.path.dirname(impl_file), exist_ok=True)
    
    with open(impl_file, "w") as f:
        f.write(f"""
\"\"\"Demo feature implementation.\"\"\"

class DemoFeature:
    \"\"\"A demo feature for GitHub workflow demonstration.\"\"\"
    
    def __init__(self):
        \"\"\"Initialize the demo feature.\"\"\"
        self.enabled = False
    
    def enable(self):
        \"\"\"Enable the feature.\"\"\"
        self.enabled = True
        return True
    
    def disable(self):
        \"\"\"Disable the feature.\"\"\"
        self.enabled = False
        return True
""")
    
    print(f"✅ Created test and implementation files")
    return True


def commit_changes(issue_number: int) -> bool:
    """Commit the changes with reference to the issue."""
    print("\n=== Committing changes ===")
    
    # Add files
    code, output = run_command("git add tests/ui/test_demo_feature.py imagen_desktop/ui/features/demo_feature.py")
    if code != 0:
        print(f"Error staging files: {output}")
        return False
    
    # Create commit message
    commit_msg = f"Add demo feature implementation\n\nResolves #{issue_number}"
    
    # Validate commit message
    is_valid, error = validate_commit_message(commit_msg)
    if not is_valid:
        print(f"Invalid commit message: {error}")
        return False
    
    # Commit changes
    code, output = run_command(f'git commit -m "{commit_msg}"')
    if code != 0:
        print(f"Error committing changes: {output}")
        return False
        
    print(f"✅ Committed changes with reference to issue #{issue_number}")
    return True


def push_and_create_pr(issue_number: int) -> bool:
    """Push changes and create a PR."""
    print("\n=== Pushing changes and creating PR ===")
    
    # Get current branch
    code, branch = run_command("git rev-parse --abbrev-ref HEAD")
    if code != 0:
        print(f"Error getting current branch: {branch}")
        return False
    
    # Push to origin
    code, output = run_command(f"git push -u origin {branch}")
    if code != 0:
        print(f"Error pushing to origin: {output}")
        print("If this is a simulation, this is expected as the remote may not exist.")
        # Continue anyway for demo purposes
    else:
        print(f"✅ Pushed to origin/{branch}")
    
    # Create PR using utility function
    pr_title = f"Add demo feature"
    pr_body = f"Implements demo feature.\n\nResolves #{issue_number}"
    
    # In a real scenario, you would use:
    # pr_url = create_pull_request(pr_title, pr_body)
    
    print(f"Would create PR with title: '{pr_title}'")
    print(f"And body: '{pr_body}'")
    
    # For demo purposes, we'll simulate PR creation
    print(f"✅ PR created successfully (simulated)")
    
    return True


def close_related_issue(issue_number: int) -> bool:
    """Close the related issue with a comment."""
    print(f"\n=== Closing issue #{issue_number} ===")
    
    # Check if issue exists
    if not check_issue_exists(issue_number):
        print(f"Issue #{issue_number} doesn't exist or can't be accessed")
        return False
    
    # In a real scenario, you would use:
    # success = close_issue(issue_number, "Closed via PR")
    
    print(f"Would close issue #{issue_number} with comment: 'Closed via PR'")
    
    # For demo purposes, we'll simulate issue closure
    print(f"✅ Issue #{issue_number} closed successfully (simulated)")
    
    return True


def main():
    """Run the complete GitHub workflow demo."""
    parser = argparse.ArgumentParser(description="GitHub Workflow Demo")
    parser.add_argument("issue_title", nargs="?", default="Demo Feature Request", 
                        help="Title for the issue to create")
    parser.add_argument("issue_body", nargs="?", 
                        default="This is a demonstration of the GitHub workflow process.", 
                        help="Body for the issue to create")
    
    args = parser.parse_args()
    
    print("=== GitHub Workflow Demonstration ===")
    print("This script demonstrates the complete GitHub workflow.")
    print("Note: Some operations are simulated for demonstration purposes.")
    
    # Step 1: Create issue
    issue_number = create_issue(args.issue_title, args.issue_body)
    if not issue_number:
        issue_number = 999  # Use a placeholder for demo purposes
        print("Using placeholder issue #999 for demonstration")
    
    # Step 2: Create feature branch
    feature_name = "demo-feature"
    if not create_feature_branch(issue_number, feature_name):
        print("Failed to create feature branch")
        return 1
    
    # Step 3: Make changes
    if not make_changes(issue_number):
        print("Failed to make changes")
        return 1
    
    # Step 4: Commit changes
    if not commit_changes(issue_number):
        print("Failed to commit changes")
        return 1
    
    # Step 5: Push and create PR
    if not push_and_create_pr(issue_number):
        print("Failed to create PR")
        return 1
    
    # Step 6: Close related issue
    if not close_related_issue(issue_number):
        print("Failed to close issue")
        return 1
    
    print("\n=== GitHub Workflow Demo Completed Successfully ===")
    print("The demo has walked through the following steps:")
    print("1. Creating an issue")
    print("2. Creating a feature branch")
    print("3. Making code changes")
    print("4. Committing with issue reference")
    print("5. Pushing and creating a PR")
    print("6. Closing the related issue")
    print("\nFor more details, see docs/github_workflow.md")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())