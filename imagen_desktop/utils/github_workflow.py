"""GitHub workflow utilities for Imagen Desktop."""

import re
import subprocess
from typing import List, Optional, Tuple, Dict
import os


def validate_branch_name(branch_name: str) -> Tuple[bool, str]:
    """
    Validate that a branch name follows the project convention.
    
    Args:
        branch_name: The name of the branch to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_prefixes = ['feature/', 'bugfix/', 'hotfix/', 'release/', 'support/']
    
    # Check if branch name starts with valid prefix
    has_valid_prefix = any(branch_name.startswith(prefix) for prefix in valid_prefixes)
    if not has_valid_prefix:
        return False, f"Branch name must start with one of: {', '.join(valid_prefixes)}"
    
    # Get the prefix used
    prefix = next(p for p in valid_prefixes if branch_name.startswith(p))
    
    # Check if branch has content after prefix
    if len(branch_name) <= len(prefix):
        return False, "Branch name must include a descriptive part after the prefix"
    
    # Branch name should be kebab-case after prefix
    desc_part = branch_name[len(prefix):]
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', desc_part):
        return False, "Descriptive part of branch name must be kebab-case (lowercase with hyphens)"
    
    return True, ""


def validate_commit_message(message: str) -> Tuple[bool, str]:
    """
    Validate that a commit message follows the project convention.
    
    Args:
        message: The commit message to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Split into lines
    lines = message.strip().split('\n')
    first_line = lines[0]
    
    # Check first line length
    if len(first_line) > 50:
        return False, "First line should be 50 characters or less"
    
    # Check first line starts with capitalized verb
    if not re.match(r'^[A-Z][a-z]+', first_line):
        return False, "First line should start with a capitalized verb"
    
    # If there's a body, ensure blank line after subject
    if len(lines) > 1 and lines[1]:
        return False, "Leave a blank line after the subject line"
    
    # Check body line length if it exists
    if len(lines) > 2:
        for i, line in enumerate(lines[2:], 2):
            if len(line) > 72:
                return False, f"Line {i+1} exceeds 72 character limit"
    
    return True, ""


def check_issue_exists(issue_number: int) -> bool:
    """
    Check if a GitHub issue exists.
    
    Args:
        issue_number: The GitHub issue number to check
        
    Returns:
        True if the issue exists, False otherwise
    """
    try:
        # Use gh CLI if available
        result = subprocess.run(
            ["gh", "issue", "view", str(issue_number)], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        # gh CLI not installed
        return True  # Assume issue exists if we can't check


def extract_issue_numbers(message: str) -> List[int]:
    """
    Extract GitHub issue numbers from a commit message.
    
    Args:
        message: The commit message to extract from
        
    Returns:
        List of issue numbers found
    """
    # Look for patterns like #123 or GH-123
    matches = re.findall(r'(?:#|GH-)(\d+)', message)
    return [int(m) for m in matches]


def create_pull_request(title: str, body: str, base_branch: str = "master") -> Optional[str]:
    """
    Create a GitHub pull request.
    
    Args:
        title: The title of the pull request
        body: The body of the pull request
        base_branch: The branch to target (default: master)
        
    Returns:
        URL of the created PR if successful, None otherwise
    """
    try:
        # Get current branch
        current_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            universal_newlines=True
        ).strip()
        
        # Create PR
        result = subprocess.run(
            ["gh", "pr", "create", "--title", title, "--body", body, "--base", base_branch],
            stdout=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
        
        # Extract PR URL from output
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error creating PR: {e}")
        return None


def close_issue(issue_number: int, comment: str = "") -> bool:
    """
    Close a GitHub issue.
    
    Args:
        issue_number: The GitHub issue number to close
        comment: Optional comment to add when closing
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["gh", "issue", "close", str(issue_number)]
        if comment:
            cmd.extend(["--comment", comment])
            
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("GitHub CLI not found. Please install it to use this feature.")
        return False