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
        workflow_content = f.read()
        workflow = yaml.safe_load(workflow_content)
        
        # Print the workflow for debugging
        print(f"Workflow keys: {list(workflow.keys())}")
        
        # Check required top-level fields
        assert 'name' in workflow, "Workflow missing 'name' field"
        
        # Handle potential YAML parsing issue with 'on' being a reserved word
        assert 'on' in workflow or True in workflow, "Workflow missing trigger field"
        
        # Get the 'on' field regardless of key type
        on_field = workflow.get('on', workflow.get(True, {}))
        
        assert 'jobs' in workflow, "Workflow missing 'jobs' field"
        
        # Check that workflow runs on push and PR to master
        assert 'push' in on_field, "Workflow should run on push"
        assert 'pull_request' in on_field, "Workflow should run on pull_request"
        
        # Check that test job exists and runs on latest Ubuntu
        assert 'test' in workflow['jobs'], "Workflow missing 'test' job"
        assert workflow['jobs']['test']['runs-on'] == 'ubuntu-latest', "Test job should run on ubuntu-latest"
        
        # Check python versions
        assert 'strategy' in workflow['jobs']['test'], "Test job missing 'strategy' field"
        assert 'matrix' in workflow['jobs']['test']['strategy'], "Test strategy missing 'matrix' field"
        assert 'python-version' in workflow['jobs']['test']['strategy']['matrix'], "Matrix missing 'python-version' field"
        assert len(workflow['jobs']['test']['strategy']['matrix']['python-version']) >= 1, "Should test at least one Python version"


@pytest.mark.unit
def test_github_workflow_has_ui_tests():
    """Test that GitHub workflow has UI tests job."""
    workflow_path = Path(".github/workflows/python-tests.yml")
    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)
        
        assert 'ui-tests' in workflow['jobs'], "Workflow missing 'ui-tests' job"
        assert workflow['jobs']['ui-tests']['runs-on'] == 'ubuntu-latest', "UI tests job should run on ubuntu-latest"
        assert 'needs' in workflow['jobs']['ui-tests'], "UI tests job should have 'needs' field"
        assert workflow['jobs']['ui-tests']['needs'] == 'test', "UI tests job should depend on 'test' job"


@pytest.mark.unit
def test_github_workflow_generates_reports():
    """Test that GitHub workflow generates and publishes reports."""
    workflow_path = Path(".github/workflows/python-tests.yml")
    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)
        
        # Check for report generation
        test_job = workflow['jobs']['test']
        steps = [step.get('name', '') for step in test_job['steps']]
        assert any('report' in step.lower() or 'coverage' in step.lower() for step in steps), \
            "Test job should generate reports"
        
        # Check for artifact upload
        upload_steps = [step for step in test_job['steps'] if step.get('name', '').lower().startswith('upload')]
        assert len(upload_steps) > 0, "Test job should upload artifacts"
        
        # Check for report publishing
        assert 'publish-report' in workflow['jobs'], "Workflow missing 'publish-report' job"
        
        # Check that publish job runs even if other jobs fail
        assert workflow['jobs']['publish-report'].get('if', '') == 'always()', \
            "Publish report job should run even if other jobs fail"
        
        # Check that publish job depends on test and ui-tests
        assert 'needs' in workflow['jobs']['publish-report'], "Publish report job should have 'needs' field"
        needs = workflow['jobs']['publish-report']['needs']
        assert isinstance(needs, list) and 'test' in needs and 'ui-tests' in needs, \
            "Publish report job should depend on 'test' and 'ui-tests' jobs"


@pytest.mark.unit
def test_github_workflow_enforces_code_quality():
    """Test that GitHub workflow enforces code quality."""
    workflow_path = Path(".github/workflows/python-tests.yml")
    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)
        
        # Get the test job steps
        test_job_steps = workflow['jobs']['test']['steps']
        
        # Check for linting
        lint_steps = [step for step in test_job_steps if 'lint' in step.get('name', '').lower()]
        assert len(lint_steps) > 0, "Workflow should include linting"
        
        # Check for formatting
        format_steps = [step for step in test_job_steps if 'format' in step.get('name', '').lower()]
        assert len(format_steps) > 0, "Workflow should include formatting checks"
        
        # Check for type checking
        type_steps = [step for step in test_job_steps if 'type' in step.get('name', '').lower()]
        assert len(type_steps) > 0, "Workflow should include type checking"
        
        # Check for coverage threshold
        coverage_steps = [step for step in test_job_steps if 'coverage' in step.get('name', '').lower()]
        assert len(coverage_steps) > 0, "Workflow should check coverage thresholds"


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