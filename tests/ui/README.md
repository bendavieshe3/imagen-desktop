# UI Testing Guide

This directory contains UI tests for Imagen Desktop's graphical user interface components. We use pytest-qt for testing PyQt6 components in isolation and as part of integration flows.

## Test Organization

Tests are organized to mirror the application structure:

- `/dialogs/` - Tests for dialog components
- `/features/` - Tests for feature modules
  - `/features/gallery/` - Tests for gallery components
  - `/features/generation/` - Tests for generation components
- `/shared/` - Tests for shared UI components

## Running UI Tests

To run all UI tests:

```bash
python -m pytest -m ui
```

To run a specific UI test file:

```bash
python -m pytest tests/ui/features/test_model_selection.py -v
```

## Writing UI Tests

### Best Practices

1. **Isolate Components**: Test UI components in isolation when possible
2. **Mock Dependencies**: Mock API clients, repositories, and other external dependencies
3. **Use Fixtures**: Use the provided fixtures in `conftest.py` for common setup
4. **Test Signals**: Verify that components emit the right signals with correct arguments
5. **Test User Interactions**: Simulate user interactions with `qtbot` methods like `mouseClick` and `keyClicks`

### Test Structure

UI tests typically follow this pattern:

1. Set up mocks for any dependencies
2. Create the component under test
3. Simulate user interactions
4. Verify component behavior (signals, state changes, visual updates)

### Example

```python
@pytest.mark.ui
def test_button_click(qtbot, mocker):
    # Mock dependencies
    mock_handler = mocker.Mock()
    
    # Create component
    button = QPushButton("Click Me")
    button.clicked.connect(mock_handler)
    qtbot.addWidget(button)
    
    # Simulate user interaction
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    
    # Verify behavior
    mock_handler.assert_called_once()
```

## Testing Complex UI Flows

For complex UI flows involving multiple components, create integration tests that:

1. Set up the entire feature
2. Simulate a complete user workflow
3. Verify the end-to-end behavior

Example: Test the complete generation flow from entering a prompt to displaying the result.

## Debugging UI Tests

If a UI test is failing, you can:

1. Add `qtbot.stop()` at the failure point to pause execution and inspect state
2. Use `print` statements or pytest's `-v` flag for more output
3. Temporarily modify tests to display widgets with `widget.show()` and `qtbot.waitExposed(widget)`

## Running in CI

UI tests run in CI on a virtual display (Xvfb). See the GitHub workflow configuration for details.

## Dependencies

- pytest-qt: PyQt testing plugin for pytest
- pytest-xvfb: Creates a virtual display for running GUI tests in headless environments