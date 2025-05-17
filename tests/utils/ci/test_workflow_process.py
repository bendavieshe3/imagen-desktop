"""Tests to validate the GitHub workflow process."""

import subprocess
import pytest
from pathlib import Path
import re


@pytest.mark.unit
def test_branch_naming_validation():
    """Test validation of branch naming convention helper function."""
    def is_valid_branch_name(name):
        """Validate branch names according to our convention."""
        valid_prefixes = ['feature/', 'bugfix/', 'hotfix/', 'release/', 'support/']
        
        # Check if branch name starts with valid prefix and has descriptive part
        for prefix in valid_prefixes:
            if name.startswith(prefix) and len(name) > len(prefix) + 3:
                # Branch name should be kebab-case after prefix
                desc_part = name[len(prefix):]
                return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', desc_part))
        
        return False
    
    # Valid branch names
    assert is_valid_branch_name('feature/add-dark-mode')
    assert is_valid_branch_name('bugfix/fix-gallery-sorting')
    assert is_valid_branch_name('hotfix/urgent-security-patch')
    
    # Invalid branch names
    assert not is_valid_branch_name('feature')  # No description
    assert not is_valid_branch_name('add-feature')  # No prefix
    assert not is_valid_branch_name('feature/Add_Dark_Mode')  # Not kebab-case
    assert not is_valid_branch_name('random/something')  # Invalid prefix


@pytest.mark.unit
def test_commit_message_validation():
    """Test validation of commit message format helper function."""
    def is_valid_commit_message(message):
        """Validate commit messages according to our convention."""
        # First line should be capitalized, start with a verb, and be 50 chars or less
        lines = message.strip().split('\n')
        first_line = lines[0]
        
        if len(first_line) > 50:
            return False
            
        # Should start with capital letter verb
        if not re.match(r'^[A-Z][a-z]+', first_line):
            return False
            
        # If there's a body, there should be a blank line after the subject
        if len(lines) > 1 and lines[1]:
            return False
            
        return True
    
    # Valid commit messages
    assert is_valid_commit_message("Add dark mode toggle button")
    assert is_valid_commit_message("Fix sorting algorithm in gallery view")
    assert is_valid_commit_message("Update documentation with TDD guidelines\n\nAdded comprehensive examples and best practices.")
    
    # Invalid commit messages
    assert not is_valid_commit_message("added dark mode")  # Not capitalized
    assert not is_valid_commit_message("This commit adds the dark mode toggle button which users can click")  # Too long
    assert not is_valid_commit_message("Add dark mode toggle button\nMore details")  # No blank line


@pytest.mark.unit
def test_github_issue_reference_validation():
    """Test validation of GitHub issue references in commit messages."""
    def has_valid_issue_reference(message):
        """Check if commit message has valid issue reference."""
        # Look for patterns like #123 or GH-123
        return bool(re.search(r'(#|GH-)\d+', message))
    
    # Valid issue references
    assert has_valid_issue_reference("Add dark mode toggle button #123")
    assert has_valid_issue_reference("Fix sorting algorithm in gallery view (GH-456)")
    assert has_valid_issue_reference("Update docs\n\nResolves #789")
    
    # Invalid issue references
    assert not has_valid_issue_reference("Add dark mode toggle button")  # No reference
    assert not has_valid_issue_reference("Fix issue number 123")  # Incorrect format