"""Core database management for the application."""
from pathlib import Path
from typing import Optional, List
import alembic.config
from alembic import command
import os
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.util.exc import CommandError

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from imagen_desktop.utils.debug_logger import logger

class Database:
    """Central database management for the application."""
    
    def __init__(self, path: Path):
        """Initialize database with path.
        
        Args:
            path: Path to SQLite database file
        """
        self.path = path.resolve()  # Get absolute path
        self.engine: Optional[Engine] = None
        self._session_factory = None
    
    def initialize(self) -> None:
        """Initialize database, creating directories and running migrations."""
        try:
            # Ensure directory exists
            self.path.parent.mkdir(parents=True, exist_ok=True)
            
            db_url = f"sqlite:///{self.path}"
            logger.debug(f"Initializing database with URL: {db_url}")
            
            # Create engine
            self.engine = create_engine(db_url)
            self._session_factory = sessionmaker(bind=self.engine)
            
            # Run migrations if needed
            self._run_migrations()
            
            # Log initialized tables
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"Found tables after migration: {', '.join(tables) if tables else 'No tables found'}")
            
            logger.info(f"Database initialized at {self.path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if not self._session_factory:
            raise RuntimeError("Database not initialized")
        return self._session_factory()
    
    def _get_migration_files(self) -> List[str]:
        """Get list of available migration files."""
        migrations_dir = Path(__file__).parent / 'migrations' / 'versions'
        abs_migrations_dir = migrations_dir.resolve()
        logger.debug(f"Looking for migrations in: {abs_migrations_dir}")
        
        if not abs_migrations_dir.exists():
            logger.error(f"Migrations directory not found at {abs_migrations_dir}")
            return []
            
        migration_files = sorted([f.name for f in abs_migrations_dir.glob('*.py') 
                                if f.name != '__init__.py'])
        if migration_files:
            logger.debug(f"Found migration files: {', '.join(migration_files)}")
        else:
            logger.warning("No migration files found")
        return migration_files
    
    def _get_current_revision(self) -> Optional[str]:
        """Get current migration revision."""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                logger.debug(f"Current migration revision: {current_rev}")
                return current_rev
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
            
    def _verify_migrations_structure(self) -> bool:
        """Verify the migrations directory structure is correct."""
        migrations_dir = Path(__file__).parent / 'migrations'
        versions_dir = migrations_dir / 'versions'
        env_file = migrations_dir / 'env.py'
        
        logger.debug(f"Verifying migrations structure at {migrations_dir}")
        
        if not migrations_dir.exists():
            logger.error(f"Migrations directory not found: {migrations_dir}")
            return False
            
        if not versions_dir.exists():
            logger.error(f"Versions directory not found: {versions_dir}")
            return False
            
        if not env_file.exists():
            logger.error(f"env.py not found: {env_file}")
            return False
            
        return True
    
    def _run_migrations(self) -> None:
        """Run any pending database migrations."""
        try:
            # Verify migrations structure
            if not self._verify_migrations_structure():
                raise RuntimeError("Invalid migrations structure")
            
            # Get the migrations directory
            migrations_dir = Path(__file__).parent / 'migrations'
            abs_migrations_dir = migrations_dir.resolve()
            logger.debug(f"Using migrations directory: {abs_migrations_dir}")
            
            # List available migrations
            migration_files = self._get_migration_files()
            logger.info(f"Found {len(migration_files)} migration files")
            
            # Get initial revision state
            initial_rev = self._get_current_revision()
            logger.debug(f"Initial revision state: {initial_rev}")
            
            # Create alembic.ini dynamically
            alembic_cfg = alembic.config.Config()
            alembic_cfg.set_main_option('script_location', str(abs_migrations_dir))
            alembic_cfg.set_main_option('sqlalchemy.url', f'sqlite:///{self.path}')
            
            # Initialize migration scripts
            script_dir = ScriptDirectory.from_config(alembic_cfg)
            
            try:
                # Run migrations
                logger.debug("Starting migration upgrade to 'head'")
                command.upgrade(alembic_cfg, 'head')
                logger.debug("Migration upgrade completed")
                
                # Get final revision state
                final_rev = self._get_current_revision()
                if final_rev is None:
                    raise RuntimeError("Migrations did not complete - no revision found")
                    
                if final_rev == initial_rev:
                    logger.warning("No migrations were applied")
                else:
                    logger.info(f"Successfully migrated from {initial_rev or 'None'} to {final_rev}")
                
                logger.info(f"Migration complete. Final revision: {final_rev}")
                
            except CommandError as e:
                logger.error(f"Alembic command error: {e}")
                raise
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            raise
    
    def execute_query(self, query_text, params=None):
        """Execute a raw SQL query using SQLAlchemy's text() construct.
        
        Args:
            query_text: SQL query string
            params: Optional parameters dictionary
            
        Returns:
            Query result
        """
        with self.get_session() as session:
            result = session.execute(text(query_text), params or {})
            return result
            
    def check_database_health(self) -> bool:
        """Check if database is operational.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            with self.get_session() as session:
                # Simple query to test database connectivity
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False