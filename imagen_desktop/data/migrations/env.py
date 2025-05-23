"""Alembic environment configuration."""
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import the SQLAlchemy models
from imagen_desktop.data.schema import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = Base.metadata

def get_url():
    """Get database URL from environment or configuration."""
    # Get URL from alembic.ini if provided
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url
        
    # Otherwise use default location
    data_dir = Path.home() / '.imagen-desktop'
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / 'imagen.db'
    return f"sqlite:///{db_path}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Override sqlalchemy.url in the config
    config_section = config.get_section(config.config_ini_section) or {}
    config_section["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()