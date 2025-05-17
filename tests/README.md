# Imagen Desktop Testing

This directory contains tests for the Imagen Desktop application.

## Test Structure

Tests are organized into directories that mirror the application structure:

- `tests/core/` - Tests for core domain models and logic
- `tests/data/` - Tests for database and repositories
- `tests/api/` - Tests for API client and related functionality
- `tests/ui/` - Tests for UI components and features
- `tests/utils/` - Tests for utility functions and CI/CD configurations

Each test directory has its own README with specific guidelines.

## Running Tests

Run all tests with pytest:

```bash
python -m pytest
```

Run specific test categories using markers:

```bash
# Run only unit tests
python -m pytest -m unit

# Run UI tests
python -m pytest -m ui

# Run API tests
python -m pytest -m api

# Run integration tests
python -m pytest -m integration
```

Generate coverage report:

```bash
python -m pytest --cov=imagen_desktop --cov-report=html
```

Run tests with HTML report generation:

```bash
python -m pytest --html=pytest-report.html --self-contained-html
```

## CI/CD Pipeline

Tests are automatically run in our GitHub Actions-based CI/CD pipeline:

- Tests run on every push and pull request
- Multiple Python versions are tested (3.9, 3.10, 3.11)
- Tests are run in parallel where possible
- Coverage reports are generated and published
- UI tests run in a virtual display environment
- Code quality checks (flake8, mypy, black) are enforced
- Test reports are published to GitHub Pages

See `.github/workflows/python-tests.yml` for the complete workflow configuration.

## Test Types

1. **Unit Tests** (fast, no external dependencies)
   - Test individual components in isolation
   - Mock dependencies
   - Focus on logic and edge cases
   - Marked with `@pytest.mark.unit`

2. **Integration Tests** (moderate speed, may use database)
   - Test components working together
   - May use test database
   - Verify data flows correctly between components
   - Marked with `@pytest.mark.integration`

3. **UI Tests** (slower, test user interface)
   - Test UI functionality
   - Verify UI events and signals
   - Simulate user interactions
   - Marked with `@pytest.mark.ui`
   - See `tests/ui/README.md` for detailed guidelines

4. **API Tests** (external dependencies, may be slow)
   - Test API client functionality
   - Mock external API calls
   - Verify API request and response handling
   - Marked with `@pytest.mark.api`

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `test_database` - Initialized test database
- `db_session` - SQLAlchemy session with automatic rollback
- `qapp` - QApplication instance for UI tests (defined in `tests/ui/conftest.py`)
- `mock_pixmap` - Mock for QPixmap to avoid loading actual images
- `wait_for_signal` - Helper to wait for Qt signals with timeout

## Test Factories

The `factories.py` module provides factories for creating test data:

- `ProductFactory` - Creates Product objects
- `GenerationFactory` - Creates Generation objects
- `OrderFactory` - Creates Order objects

## Mocking

- Use `pytest-mock` for general mocking
- Use `responses` for mocking HTTP requests
- Use dedicated fixtures for common mocks
- For UI tests, mock all external dependencies and data sources

## Coverage Requirements

The project enforces automated test coverage thresholds through CI/CD. The coverage requirements are defined in the `.coveragerc` file and are enforced by pytest-cov.

- **Overall coverage**: Minimum 50% (will increase over time)
- **Core domain models**: Minimum 90% 
- **API client modules**: Minimum 80%
- **Data repositories**: Minimum 60%

You can view current coverage reports:
- Locally: Run `python -m pytest --cov=imagen_desktop` and view the HTML report in `htmlcov/`
- CI/CD: Coverage reports and badges are published to GitHub Pages after each successful build

### Coverage Enforcement

- Pull requests with coverage below the threshold will fail CI checks
- Coverage is tracked per module and overall
- For new code, aim for 90%+ coverage
- Use `.coveragerc` to configure coverage reporting and set thresholds

## Best Practices

1. **Test Independence**: Keep tests independent and isolated
2. **Test Organization**: Use appropriate test markers and directory structure
3. **Test Focus**: Avoid testing implementation details
4. **Test Clarity**: Keep tests focused with clear names and documentation
5. **Test Structure**: Follow Arrange-Act-Assert pattern for test structure
6. **Test Data**: Use factories and fixtures for test data
7. **Test Coverage**: Aim for at least 80% code coverage
8. **Test UI**: Use the `qtbot` fixture for UI interactions
9. **Continuous Testing**: Run tests frequently during development
10. **Test Documentation**: Document testing approach and patterns