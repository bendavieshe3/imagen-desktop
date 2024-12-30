"""Database utility functions for managing migrations and connections."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from imagen_desktop.utils.debug_logger import logger

def get_db_path() -> Path:
    """Get the database file path."""
    data_dir = Path.home() / '.replicate-desktop'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / 'replicate.db'

def get_engine(db_path: Path = None):
    """Create SQLAlchemy engine."""
    if db_path is None:
        db_path = get_db_path()
    return create_engine(f'sqlite:///{db_path}')

def get_session_factory(engine = None):
    """Create a session factory."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine)

def run_migrations(db_path: Path = None):
    """Run all pending migrations."""
    try:
        if db_path is None:
            db_path = get_db_path()
        
        # Get the directory containing this file
        current_dir = Path(__file__).resolve().parent
        migrations_dir = current_dir / 'migrations'
        
        # Create Alembic configuration
        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', 
                                   str(migrations_dir))
        alembic_cfg.set_main_option('sqlalchemy.url', 
                                   f'sqlite:///{db_path}')
        
        # Run the migration
        command.upgrade(alembic_cfg, 'head')
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise

def init_database():
    """Initialize the database and run migrations."""
    try:
        db_path = get_db_path()
        engine = get_engine(db_path)
        session_factory = sessionmaker(bind=engine)
        
        # Run migrations
        run_migrations(db_path)
        
        return session_factory
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise