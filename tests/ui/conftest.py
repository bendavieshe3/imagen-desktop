"""Pytest configuration for UI tests."""

import os
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the test session."""
    # Use same application name and organization for all tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([''])
        app.setApplicationName("Imagen Desktop Testing")
        app.setOrganizationName("Imagen")
    
    # Disable animations for testing
    app.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
    
    # Don't actually show windows during testing
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    yield app


@pytest.fixture
def close_all_windows(qapp):
    """Close all windows after test."""
    yield
    for window in qapp.topLevelWidgets():
        window.close()


@pytest.fixture
def mock_api_key(monkeypatch):
    """Mock the API key for tests."""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_api_key")


@pytest.fixture
def mock_pixmap(mocker):
    """Mock QPixmap to avoid loading actual images."""
    mocker.patch('PyQt6.QtGui.QPixmap.load', return_value=True)
    mocker.patch('PyQt6.QtGui.QPixmap.scaled', return_value=mocker.MagicMock())


@pytest.fixture
def wait_for_signal(qtbot):
    """Utility to wait for a signal with timeout."""
    def _wait_for_signal(signal, timeout=1000):
        """Wait for signal to be emitted with timeout."""
        timer = QTimer()
        timer.setSingleShot(True)
        timer.setInterval(timeout)
        
        # Either signal fires or timeout occurs
        with qtbot.waitSignal(signal, timeout=timeout):
            timer.start()
        
        return not timer.isActive()  # True if signal was emitted before timeout
    
    return _wait_for_signal


@pytest.fixture
def click_button_in_widget(qtbot):
    """Utility to find and click a button in a widget by its text."""
    def _click_button(widget, button_text):
        """Find and click a button with the given text."""
        for button in widget.findChildren(QPushButton):
            if button_text in button.text():
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
                return True
        return False
    
    return _click_button