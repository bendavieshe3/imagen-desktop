"""Tests to validate GitHub workflow configurations."""

import os
import pytest
import yaml
from pathlib import Path


@pytest.mark.unit
def test_github_workflow_exists():
    """Test that GitHub workflow file exists."""
    workflow_path = Path(".github/workflows/python-tests.yml")
    assert workflow_path.exists(), "GitHub workflow file not found"


@pytest.mark.unit
def test_github_workflow_valid_yaml():
    """Test that GitHub workflow file is valid YAML."""
    workflow_path = Path(".github/workflows/python-tests.yml")
    with open(workflow_path, 'r') as f:
        try:
            workflow = yaml.safe_load(f)
            assert workflow is not None, "Workflow file is empty"
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in workflow file: {e}")


@pytest.mark.unit
def test_github_workflow_required_fields():
    """Test that GitHub workflow file has required fields."""
    workflow_path = Path(".github/workflows/python-tests.yml")
    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)
        
        # Check required top-level fields
        assert 'name' in workflow, "Workflow missing 'name' field"
        assert 'on' in workflow, "Workflow missing 'on' field"
        assert 'jobs' in workflow, "Workflow missing 'jobs' field"
        
        # Check that workflow runs on push and PR to master
        assert 'push' in workflow['on'], "Workflow should run on push"
        assert 'pull_request' in workflow['on'], "Workflow should run on pull_request"
        
        # Check that test job exists and runs on latest Ubuntu
        assert 'test' in workflow['jobs'], "Workflow missing 'test' job"
        assert workflow['jobs']['test']['runs-on'] == 'ubuntu-latest', "Test job should run on ubuntu-latest"
        
        # Check python versions
        assert 'strategy' in workflow['jobs']['test'], "Test job missing 'strategy' field"
        assert 'matrix' in workflow['jobs']['test']['strategy'], "Test strategy missing 'matrix' field"
        assert 'python-version' in workflow['jobs']['test']['strategy']['matrix'], "Matrix missing 'python-version' field"
        assert len(workflow['jobs']['test']['strategy']['matrix']['python-version']) >= 1, "Should test at least one Python version"


@pytest.mark.unit
def test_github_pr_template_exists():
    """Test that GitHub PR template exists."""
    template_path = Path(".github/PULL_REQUEST_TEMPLATE/default.md")
    assert template_path.exists(), "GitHub PR template not found"


@pytest.mark.unit
def test_github_issue_templates_exist():
    """Test that GitHub issue templates exist."""
    bug_report_path = Path(".github/ISSUE_TEMPLATE/bug_report.md")
    feature_request_path = Path(".github/ISSUE_TEMPLATE/feature_request.md")
    
    assert bug_report_path.exists(), "Bug report template not found"
    assert feature_request_path.exists(), "Feature request template not found"