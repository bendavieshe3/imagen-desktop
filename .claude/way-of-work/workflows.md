# Workflows

## How to make changes to source code (bugs/enhancements) for an issue
1. Check the readiness of the local environment (See below)
2. Review the requirements (See below)
3. Create a plan (see below)
4. Implement the Plan (see below)
5. Review the outcome (see below)

## Check the Readiness of the Local Environment
1. Check that there are no modified or new files waiting to be committed
   - If so, prompt the user to commit the files to source control and push to the remote repo
2. Check that there is not a [current_plan](../working/current_plan.md) in progress
   - If so ask the user what to do

## Review Issue Requirements
1. If the request is about a Github issue (enhancement or bug), retrieve it
   - use the gh local client to retrieve information
   - Make sure it has the required detail
      - See the [bug report](../../.github/ISSUE_TEMPLATE/bug_report.md) or [feature request](../../.github/ISSUE_TEMPLATE/feature_request.md) templates for suggested detail
      - if not, ask the user to Elaborate the Issue

## Create a Plan
1. Consider the [vision](../../docs/vision.md), [concepts](../../docs/concepts.md) and [features](../../docs/features.md) of the project
2. Formulate a plan that achieves the objective of the issue that aligns with the project
3. Share with the user the plan by sharing succinctly: 
   - Overview of the proposed changes
   - Important Technology Decisions
   - Files that will be modified
   - New components or modules that will be created
   - Impact on existing functionality
   - Implementation approach and design patterns
4. Have the user confirm the plan
   - Implement changes to the plan as instructed by the user
   = Record agreed technology decisions in [technology.md](../../docs/technology.md)
5. Record the plan in the [current_plan](../working/current_plan.md) file

## Implement a plan
- update the [current_plan](../working/current_plan.md) as this is progressed

1. Create and switch to a new branch if required (see below)
2. Create tests as required for the new enhancement or bug
   - These should fail as not implemented 
3. Implement the plan by update the source code, documentation
   - Follow a TDD approach:
     1. Write tests first that describe the expected behavior
     2. Run the tests to confirm they fail
     3. Implement the minimum code needed to pass the tests
     4. Refactor while ensuring tests continue to pass
     5. Repeat until the local tests pass
   - Commit locally if substantial progress is made (see below)
4. Make sure all local changes to source code are committed locally (see below)
5. Rebase any changes from the master branch to the current branch locally
7. Raise a pull request for the update (see below)
8. Report the status of the [current_plan](../working/current_plan.md) back to the user before removing the detail and leaving it as a template.

## Creating and Switching to a new Branch
Refer to the [github_workflow.md](../../docs/github_workflow.md).

## Committing Changes Locally
- Ensure reference is made to the Github issue number where applicable
- Refer to the [github_workflow.md](../../docs/github_workflow.md).

## Check the current status
Generate information about the codebase and summarise the results to the user, following these steps:
1. Check that there is not a [current_plan](../working/current_plan.md) in progress to be resumed
2. Check that all local changes have been committed
3. Report if the local repo is ahead or before of the remote github branch
4. Check how many github issues are currently open
5. Check how many tasks and todos have been recorded in [other_tasks.md](..)
6. Check if these TODOs are not captured as github issues, and if so, ask the user if they want to add them. Add them if the user agrees.
7. List the number of tests defined
8. List the current coverage metric for the tests, along with when the coverage was generated. 
9. Perform a quick assessment about the health of the code project and provide it to the user. 


## Elaborate an Issue
Prompt the user to provide sufficient information to complete the relevant issue template

  - See the [bug report](../../.github/ISSUE_TEMPLATE/bug_report.md) or [feature request](../../.github/ISSUE_TEMPLATE/feature_request.md) templates for suggested detail


## Review the Product Design Documents
Review the product design to ensure it is fit for purpose
1. Read the [vision](../../docs/vision.md)
2. Read the [features](../../docs/features.md)
3. Read the [concepts](../../docs/concepts.md)
4. Provide critical feedback on the product design in these files, to keep them concise, orthogonal and expressive:
   - find contradictions, if any
   - identify ambuiguity
5. Offer to ask the user questions to resolve and to update as the files as required based on the answers


## Review the Backlog
Review the current backlog of GitHub issues and tasks in other_tasks.md:

1. Review the design (see Review the Design)
   - if there are critical issues or inconsistences, stop.

1. List all open GitHub issues
   - Use `gh issue list --state open` to view all open issues
   - Sort by priority, age, or milestone as needed  
   - Check if any issues need more detail (see Elaborate an Issue)

2. Organize existing issues
   - Add labels for categorization
   - Assign priority via labels or milestone
   - Group related issues
   - Break large issues into smaller, actionable tasks
   - Add dependencies between issues if needed

2. Review tasks in docs/other_tasks.md
   - 
   - Identify high-priority tasks not yet in GitHub
   - Consider converting important tasks to GitHub issues
     - 
     - Remove any items from other_tasks.md that have been migrated

3. Present a summary to the user
   - Number of open issues
   - Key themes or categories of issues
   - Suggested focus areas based on priority and dependencies


## Build the Backlog
Create and organize GitHub issues for future development:

1. Create issues for items in docs/other_tasks.md
   - For each task, create a new GitHub issue with appropriate detail (see ELaborate an Issue)
   - Follow the feature request or bug report template
   - Assign appropriate labels (enhancement, bug, documentation, etc.)
   - Add to milestone if applicable


3. Clean up backlog
   - Close completed or redundant issues
   - Update outdated issues
   - Merge duplicate issues










### Database Migrations
Always run database migrations before starting development:
```bash
alembic upgrade head
```

When making database schema changes:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Source Control Workflow

### GitHub Flow
1. Create feature branches from `master` with descriptive names:
   ```bash
   git checkout -b feature/add-dark-mode
   ```

2. Commit frequently with atomic changes:
   ```bash
   git add .
   git commit -m "Add toggle button for dark mode"
   ```

3. Push to GitHub and create a Pull Request (PR):
   ```bash
   git push -u origin feature/add-dark-mode
   # Then create PR via GitHub UI or CLI
   ```

4. Ensure CI passes before merging (once GitHub Actions are set up)
5. Get code review from at least one team member
6. Squash and merge when ready

For a complete workflow including issue resolution and PR management, see the [GitHub Workflow Guide](../../docs/github_workflow.md).

### GitHub Actions Configuration
- Automated tests on PRs
- Type checking with mypy
- Code formatting with black
- Linting with flake8
- Coverage reports

See `.github/workflows/python-tests.yml` for the current CI configuration.

### Commit Guidelines
- Write descriptive commit messages in present tense
- Start with a verb (Add, Fix, Update, Refactor, etc.)
- Reference issue numbers when applicable (e.g., "Fix gallery view #123")
- Keep commits focused on single logical changes


## Commands
### Run Application
```bash
python -m imagen_desktop.main
```

### Testing
```bash
# Run all tests
python -m pytest

# Run tests with coverage report (already set in pytest.ini)
python -m pytest

# Run specific test categories
python -m pytest -m unit  # Unit tests
python -m pytest -m integration  # Integration tests 
python -m pytest -m ui  # UI tests
python -m pytest -m api  # API tests

# Or use the convenience script
./run_tests.sh
```

### Code Quality
```bash
# Run type checking (requires mypy)
mypy imagen_desktop

# Run linting (requires flake8)
flake8 imagen_desktop

# Run formatting (requires black)
black imagen_desktop
```

### Database Migrations
```bash
alembic upgrade head
```

### Project Status
```bash
# Get comprehensive codebase status
./scripts/code-status.sh

# Check GitHub workflow configuration
python -m pytest tests/utils/ci/ -v

# Demonstrate GitHub workflow process
python scripts/github_workflow_demo.py
```

### Aliases
We provide aliases for common commands in `.claude-aliases`. To use them:

1. Add the following to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   [ -f /path/to/imagen/.claude-aliases ] && source /path/to/imagen/.claude-aliases
   ```

2. Available aliases:
   - `code-status`: Check codebase status
   - `run-app`: Run the application
   - `run-tests`: Run all tests
   - `run-coverage`: Run tests with coverage
   - `check-workflow`: Validate GitHub workflow configuration

## Coding Standards
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Use docstrings for classes and public methods (Google style)
- Write unit tests for all new functionality
- Maintain test coverage according to defined thresholds:
  - Overall: Minimum 50% (target will increase over time)
  - Core domain models: Minimum 90%
  - API client modules: Minimum 80%
  - Data repositories: Minimum 60%
  - For new code, aim for 90%+
- Use domain-driven design principles as outlined in [concepts.md](../../docs/concepts.md)
- Prefer composition over inheritance
- Follow the presenter-first architecture for UI components






