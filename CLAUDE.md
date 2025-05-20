# Imagen Desktop Project

## IMPORTANT
- While running in development, always activate the virtual environment before running commands: `source ./venv/bin/activate` (macOS/Linux) or `./venv/Scripts/activate` (Windows)

## Project Overview
Imagen Desktop is a PyQt6-based desktop application for running generative AI models, with an early focus on image generation using Replicate's API, to be expanded to other services and media types over time.

## Design Documents
These documents specify the product, and should be referred to as needed to make design design decisions and refactorings:
- For the product vision, see [vision](./docs/vision.md) 
- For the complete planned feature list, see [features](./docs/features.md)
- For the conceptual domain model, see [concepts](./docs/concepts.md)

## Guides
- Getting started information is maintained in the [readme](./README.md).
- Detailed testing information is maintined in the [testing readme](/tests/README.md).
- To contribute to the project see the [contributing](./docs/contributing.md) guide.

## Tech Stack

The product is coded in Python and runs in a virtual environment. 

- UI: PyQt6
- API: Replicate client
- Database: SQLAlchemy with SQLite
- Migration: Alembic
- Testing: pytest
- Image Processing: Pillow

The technology architecture of the product is described in more detail in [technology](./docs/technology.md). Development-only tools are described in [tooling](./docs/tooling.md).

## Project Structure
- `/docs/` - Design documents and project status information 
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
- `/.claude/` - Claude configuration and way-of-work instructions
  - `/commands/` - Commands available in the Claude Code CLI
  - `/way-of-work/` - Instructions and elaborations for Claude Code

setup: `./run_tests.sh`

## Development Workflow

Follow instructions detailed in the [workflows.md](./.claude/way-of-work/workflows.md)
@/.claude/way-of-work/workflows.md

General rules
- Always create a plan for changes to source code
- Always ensure test coverage and that tests pass before pushing to Github
- Always update impacted tests and documentation when making changes

## Source Control Workflow

### GitHub Flow
@./docs/github_workflow.md

## Testing

We follow test-driven development (TDD) principles:
1. Write failing tests first
2. Implement the minimum code to make tests pass
3. Refactor for clarity and maintainability

## Coding Standards

- Follow PEP 8 for Python code style
- Use meaningful variable and function names
- Document classes, functions, and modules with docstrings
- Keep functions small and focused
- Write unit tests for new code



See [Tests README](./tests/README.md) for detailed testing guidelines and 
[TDD Guide](./docs/test_driven_development.md) for specific patterns and examples.

## Cost Considerations
This application connects to Replicate's API for generating images. Please be aware:

1. Running image generation models via Replicate incurs costs based on usage
2. You need a valid Replicate API key with associated billing information
3. Each model has different pricing - check Replicate documentation for specific costs
4. Consider implementing user-facing limits or warnings about potential costs
5. When testing, prefer smaller batch sizes and fewer parameters to minimize costs

## Project Management

1. Planned features are recorded in the [features.md](./docs/features.md)
2. Features are implemented by enhancements recorded in Github issues
3. Bugs are recorded in GitHub issues
4. Tasks and todos not yet managed in GitHub are collected in [other_tasks.md](./docs/other_tasks.md)



