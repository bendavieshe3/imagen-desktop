"""Tests to validate documentation content."""

import os
import pytest
from pathlib import Path


@pytest.mark.unit
def test_claude_md_exists():
    """Test that CLAUDE.md exists."""
    claude_md_path = Path("CLAUDE.md")
    assert claude_md_path.exists(), "CLAUDE.md not found"
    
    # Check file size is reasonable
    assert claude_md_path.stat().st_size > 1000, "CLAUDE.md seems too small"


@pytest.mark.unit
def test_claude_md_contains_key_sections():
    """Test that CLAUDE.md contains key sections."""
    claude_md_path = Path("CLAUDE.md")
    with open(claude_md_path, 'r') as f:
        content = f.read()
        
        # Check for required sections
        assert "# Imagen Desktop Project" in content, "Missing project title"
        assert "## Project Overview" in content, "Missing project overview"
        assert "## Development Setup" in content, "Missing development setup"
        assert "## Development Workflow" in content, "Missing development workflow"
        assert "## Source Control Workflow" in content, "Missing source control workflow"
        assert "### GitHub Flow" in content, "Missing GitHub Flow section"
        assert "## Testing" in content, "Missing testing section"
        assert "## Coding Standards" in content, "Missing coding standards"


@pytest.mark.unit
def test_tdd_guide_exists():
    """Test that test-driven development guide exists."""
    tdd_guide_path = Path("docs/test_driven_development.md")
    assert tdd_guide_path.exists(), "TDD guide not found"
    
    # Check file size is reasonable
    assert tdd_guide_path.stat().st_size > 1000, "TDD guide seems too small"


@pytest.mark.unit
def test_tdd_guide_contains_key_sections():
    """Test that TDD guide contains key sections."""
    tdd_guide_path = Path("docs/test_driven_development.md")
    with open(tdd_guide_path, 'r') as f:
        content = f.read()
        
        # Check for required sections
        assert "# Test-Driven Development Guide" in content, "Missing guide title"
        assert "## TDD Workflow" in content, "Missing TDD workflow section"
        assert "## Best Practices" in content, "Missing best practices section"
        assert "## Testing Patterns for Imagen" in content, "Missing testing patterns section"