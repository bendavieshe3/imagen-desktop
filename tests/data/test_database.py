"""Tests for database initialization and migrations."""
import unittest
from pathlib import Path
import tempfile
import os

from imagen_desktop.data import initialize_database
from imagen_desktop.data.database import Database

class TestDatabaseInitialization(unittest.TestCase):
    """Test database initialization and basic operations."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for the test database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_database_initialization(self):
        """Test database initialization."""
        # Initialize database with temp path
        database = initialize_database(self.db_path)
        
        # Verify database was created
        self.assertTrue(database is not None)
        self.assertTrue(self.db_path.exists())
        
        # Check that we can get a session
        session = database.get_session()
        self.assertTrue(session is not None)
        
        # Verify database health
        self.assertTrue(database.check_database_health())
    
    def test_run_migrations(self):
        """Test that migrations are applied correctly."""
        # Initialize database
        database = initialize_database(self.db_path)
        
        # Check that expected tables exist
        from sqlalchemy import inspect
        inspector = inspect(database.engine)
        tables = inspector.get_table_names()
        
        # Verify some core tables we expect to exist
        self.assertIn('orders', tables)
        self.assertIn('generations', tables)
        self.assertIn('products', tables)
        self.assertIn('projects', tables)
        
        # Check for alembic version table
        self.assertIn('alembic_version', tables)

if __name__ == '__main__':
    unittest.main()