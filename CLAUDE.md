# Imagen Desktop Project

## IMPORTANT
- Always activate the virtual environment before running commands: `source ./venv/bin/activate` (macOS/Linux) or `./venv/Scripts/activate` (Windows)
- We shouldn't commit code before running or testing it

## Project Overview
Imagen Desktop is a PyQt6-based desktop application for running generative AI models, with a focus on image generation using Replicate's API. For detailed information about features and concepts, see [About](./docs/about.md).

## Project Structure
- `/imagen_desktop/` - Main package directory
  - `/api/` - API client for Replicate
  - `/core/` - Core application logic and events
    - `/config/` - Application configuration
    - `/events/` - Event system for inter-component communication
    - `/models/` - Domain models (Generation, Order, Product)
  - `/data/` - Database, models, and repositories
    - `/migrations/` - Alembic database migrations
    - `/repositories/` - Data access layer
    - `/schema/` - SQLAlchemy models
  - `/ui/` - User interface components
    - `/features/` - UI feature modules
      - `/gallery/` - Gallery management and display
      - `/generation/` - Generation form and controls
    - `/shared/` - Reusable UI components
  - `/utils/` - Utility functions

## Development Setup
1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python -m imagen_desktop.main
```

## Development Workflow

### Planning Significant Changes
For any significant changes to source code (excluding tests and bug fixes):

1. Always create a detailed plan before implementation
2. Present the plan to the user for approval before making changes
3. Include:
   - Overview of the proposed changes
   - Files that will be modified
   - New components or modules that will be created
   - Impact on existing functionality
   - Implementation approach and design patterns
4. Wait for explicit approval before proceeding with implementation

### Test-Driven Development
Always follow a test-driven development approach:

1. Write tests first that describe the expected behavior
2. Run the tests to confirm they fail
3. Implement the minimum code needed to pass the tests
4. Refactor while ensuring tests continue to pass
5. Repeat

See [Tests README](./tests/README.md) for detailed testing guidelines and 
[TDD Guide](./docs/test_driven_development.md) for specific patterns and examples.

### API Key Setup
Make sure to set up your Replicate API key in a `.env` file:
```
REPLICATE_API_TOKEN=your_api_token_here
```

Alternatively, you can store it in a config file:
```json
// at ~/.imagen-desktop/config.json
{
  "api_key": "your_api_token_here"
}
```

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

For a complete workflow including issue resolution and PR management, see the [GitHub Workflow Guide](./docs/github_workflow.md).

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

## Cost Considerations
This application connects to Replicate's API for generating images. Please be aware:

1. Running image generation models via Replicate incurs costs based on usage
2. You need a valid Replicate API key with associated billing information
3. Each model has different pricing - check Replicate documentation for specific costs
4. Consider implementing user-facing limits or warnings about potential costs
5. When testing, prefer smaller batch sizes and fewer parameters to minimize costs

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
- Maintain test coverage above 80%
- Use domain-driven design principles as outlined in [About](./docs/about.md)
- Prefer composition over inheritance
- Follow the presenter-first architecture for UI components

## Requirements and Specifications
See [Requirements](./docs/requirements.md) for detailed project requirements.

## TODO Items
See [TODO.md](./TODO.md) for current tasks.

## Tech Stack
- UI: PyQt6
- API: Replicate client
- Database: SQLAlchemy with SQLite
- Migration: Alembic
- Testing: pytest
- Image Processing: Pillow