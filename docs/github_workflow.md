# GitHub Workflow for Imagen Desktop

This document outlines the complete workflow for using GitHub with the Imagen Desktop project, including branch management, pull requests, and issue resolution.

## Full Development Workflow

### 1. Issue Creation and Assignment

1. **Create an Issue**:
   ```bash
   gh issue create --title "Add dark mode support" --body "Implement a dark mode toggle in settings"
   ```

2. **Assign to Yourself**:
   ```bash
   gh issue edit 123 --add-assignee "@me"
   ```

### 2. Branch Creation

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/add-dark-mode
   ```

2. **Branch Naming Conventions**:
   - `feature/` - New features or enhancements
   - `bugfix/` - Bug fixes
   - `hotfix/` - Urgent fixes for production
   - `release/` - Release preparation
   - `support/` - Maintenance tasks

   All branches should use kebab-case (lowercase with hyphens) after the prefix.

### 3. Development Process

1. **Write Tests First** (following TDD principles):
   ```bash
   python -m pytest tests/ui/test_dark_mode.py -v
   ```

2. **Implement the Feature**:
   - Follow coding standards in CLAUDE.md
   - Ensure tests pass after implementation
   - Run linting and type checking

3. **Make Focused Commits**:
   ```bash
   git add imagen_desktop/ui/features/settings/dark_mode.py
   git commit -m "Add dark mode toggle component"
   ```

4. **Reference Issues in Commits**:
   ```bash
   git commit -m "Add dark mode implementation #123"
   ```

### 4. Pushing and Pull Request Creation

1. **Push to GitHub**:
   ```bash
   git push -u origin feature/add-dark-mode
   ```

2. **Create Pull Request**:
   ```bash
   gh pr create --title "Add dark mode support" --body "Implements dark mode toggle in settings. Closes #123"
   ```

   You can also use our utility function:
   ```python
   from imagen_desktop.utils.github_workflow import create_pull_request
   
   pr_url = create_pull_request(
       title="Add dark mode support",
       body="Implements dark mode toggle in settings.\n\nCloses #123"
   )
   ```

3. **PR Description Best Practices**:
   - Clearly describe the changes
   - Reference the issue(s) addressed
   - Include screenshots for UI changes
   - List manual testing performed
   - Mention any potential risks or side effects

### 5. Code Review Process

1. **Request Reviews**:
   ```bash
   gh pr edit 45 --add-reviewer username1 username2
   ```

2. **Address Review Comments**:
   - Make requested changes
   - Use the suggestion feature when appropriate
   - Re-request review after addressing all comments

3. **Update Branch if Needed**:
   ```bash
   git fetch origin
   git rebase origin/master
   git push --force-with-lease
   ```

### 6. CI/CD Integration

1. **Check CI Status**:
   ```bash
   gh pr checks 45
   ```

2. **Fix CI Issues**:
   - Address any test failures
   - Fix linting or type errors
   - Commit and push fixes

### 7. Merging and Closing

1. **Merge the Pull Request**:
   ```bash
   gh pr merge 45 --squash
   ```

2. **Delete the Branch**:
   ```bash
   git branch -d feature/add-dark-mode
   gh pr close 45 --delete-branch
   ```

3. **Close the Issue**:
   ```bash
   gh issue close 123 --comment "Fixed in PR #45"
   ```

   You can also use our utility function:
   ```python
   from imagen_desktop.utils.github_workflow import close_issue
   
   close_issue(123, "Fixed in PR #45")
   ```

4. **Mark Related TODOs as Completed**:
   - Update TODO.md
   - Release milestone items if applicable

## Automated Validation

We have several utilities to help validate your GitHub workflow compliance:

### Branch Name Validation

```python
from imagen_desktop.utils.github_workflow import validate_branch_name

is_valid, error_message = validate_branch_name("feature/add-dark-mode")
if not is_valid:
    print(f"Branch name issue: {error_message}")
```

### Commit Message Validation

```python
from imagen_desktop.utils.github_workflow import validate_commit_message

is_valid, error_message = validate_commit_message("Add dark mode toggle button")
if not is_valid:
    print(f"Commit message issue: {error_message}")
```

### Issue Reference Checking

```python
from imagen_desktop.utils.github_workflow import extract_issue_numbers, check_issue_exists

issues = extract_issue_numbers("Fix gallery view #123")
for issue in issues:
    if not check_issue_exists(issue):
        print(f"Warning: Referenced issue #{issue} doesn't exist")
```

## Pre-commit Hooks

To enforce these guidelines, consider installing our pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This will check:
- Branch naming conventions
- Commit message format
- Python formatting (black)
- Type checking (mypy)
- Linting (flake8)

## Common Workflows

### Resolving an Issue

1. Create and checkout a branch:
   ```bash
   gh issue view 123
   git checkout -b bugfix/fix-issue-123
   ```

2. Make your changes, commit with issue reference:
   ```bash
   git commit -m "Fix gallery sorting bug #123"
   ```

3. Push and create PR:
   ```bash
   git push -u origin bugfix/fix-issue-123
   gh pr create --title "Fix gallery sorting bug" --body "Resolves #123"
   ```

4. After PR is approved and merged, verify issue closure.

### Addressing Feedback in a PR

1. View PR comments:
   ```bash
   gh pr view 45 --comments
   ```

2. Make requested changes and commit:
   ```bash
   git commit -m "Address PR feedback"
   ```

3. Push updates:
   ```bash
   git push
   ```

4. Re-request review:
   ```bash
   gh pr ready 45
   ```

## Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)