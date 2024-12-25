"""Database schema definitions."""
import sqlite3
from pathlib import Path
from datetime import datetime

SCHEMA_VERSION = 1

def init_db(db_path: Path) -> None:
    """Initialize the database with required tables."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Version tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        )
    ''')

    # Generations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id TEXT PRIMARY KEY,
            model TEXT NOT NULL,
            prompt TEXT NOT NULL,
            parameters TEXT NOT NULL,  -- JSON stored as text
            timestamp DATETIME NOT NULL,
            status TEXT NOT NULL,
            error TEXT
        )
    ''')

    # Generated images table
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generation_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            width INTEGER,
            height INTEGER,
            format TEXT,
            file_size INTEGER,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (generation_id) REFERENCES generations(id)
        )
    ''')

    # Model cache table for storing info about available models
    c.execute('''
        CREATE TABLE IF NOT EXISTS models (
            identifier TEXT PRIMARY KEY,  -- owner/name
            name TEXT NOT NULL,
            owner TEXT NOT NULL,
            description TEXT,
            last_updated DATETIME NOT NULL
        )
    ''')

    # Tags for generations
    c.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS generation_tags (
            generation_id TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (generation_id, tag_id),
            FOREIGN KEY (generation_id) REFERENCES generations(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
    ''')

    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_generations_timestamp ON generations(timestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_images_generation_id ON images(generation_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_generation_tags_tag_id ON generation_tags(tag_id)')

    # Store schema version
    c.execute('INSERT OR REPLACE INTO schema_version (version) VALUES (?)', (SCHEMA_VERSION,))

    conn.commit()
    conn.close()