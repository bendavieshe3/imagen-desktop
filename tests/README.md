# Imagen Desktop Testing

This directory contains tests for the Imagen Desktop application.

## Test Structure

Tests are organized into directories that mirror the application structure:

- `tests/core/` - Tests for core domain models and logic
- `tests/data/` - Tests for database and repositories
- `tests/api/` - Tests for API client and related functionality
- `tests/ui/` - Tests for UI components and features
- `tests/utils/` - Tests for utility functions

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
```

Generate coverage report:

```bash
python -m pytest --cov=imagen_desktop --cov-report=html
```

## Test Types

1. **Unit Tests** (fast, no external dependencies)
   - Test individual components in isolation
   - Mock dependencies
   - Focus on logic and edge cases

2. **Integration Tests** (moderate speed, may use database)
   - Test components working together
   - May use test database
   - Verify data flows correctly between components

3. **UI Tests** (slower, test user interface)
   - Test UI functionality
   - Verify UI events and signals
   - Simulate user interactions

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `test_database` - Initialized test database
- `db_session` - SQLAlchemy session with automatic rollback
- `qt_app` - QApplication instance for UI tests

## Test Factories

The `factories.py` module provides factories for creating test data:

- `ProductFactory` - Creates Product objects
- `GenerationFactory` - Creates Generation objects
- `OrderFactory` - Creates Order objects

## Mocking

- Use `pytest-mock` for general mocking
- Use `responses` for mocking HTTP requests
- Use dedicated fixtures for common mocks

## Best Practices

1. Keep tests independent and isolated
2. Use appropriate test markers
3. Avoid testing implementation details
4. Avoid unnecessary assertions
5. Keep tests focused and well-named
6. Arrange-Act-Assert pattern for test structure
7. Use factories for test data