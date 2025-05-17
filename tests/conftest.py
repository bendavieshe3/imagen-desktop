"""
Global pytest fixtures for Imagen Desktop tests.

This file contains shared fixtures that can be used across all test modules.
"""
import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from imagen_desktop.data import initialize_database
from imagen_desktop.data.database import Database


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def test_db_path(temp_dir):
    """Create a path for a test database."""
    return Path(temp_dir) / "test_imagen.db"


@pytest.fixture
def test_database(test_db_path):
    """Initialize a test database with migrations applied."""
    # Initialize empty database
    database = initialize_database(test_db_path)
    
    # Return the database object
    yield database
    
    # Clean up
    if test_db_path.exists():
        os.unlink(test_db_path)


@pytest.fixture
def db_session(test_database):
    """
    Create a database session for testing.
    
    This fixture provides a session that automatically rolls back at the end
    to avoid affecting other tests.
    """
    # Create a new session
    connection = test_database.engine.connect()
    transaction = connection.begin()
    
    session = test_database.Session(bind=connection)
    
    # Begin a nested transaction
    nested = connection.begin_nested()
    
    # If the session is closed, close the transaction as well
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            # Ensure new transactions have a savepoint
            connection.begin_nested()
    
    yield session
    
    # Rollback transaction and return connection to the pool
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def qt_app():
    """
    Create a QApplication instance for UI tests.
    
    This fixture is required for any test that creates PyQt widgets.
    """
    from PyQt6.QtWidgets import QApplication
    
    # Create application instance
    app = QApplication([])
    
    yield app
    
    # Clean up
    app.quit()