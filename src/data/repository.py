"""Database repository pattern implementation."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import json

from .models import Generation, Image, Model, Tag

class Repository:
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_generation(self, 
                      prediction_id: str,
                      model: str,
                      prompt: str,
                      parameters: Dict[str, Any],
                      status: str = 'starting',
                      error: Optional[str] = None) -> Generation:
        """Add a new generation to the database."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO generations (id, model, prompt, parameters, timestamp, status, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction_id,
                model,
                prompt,
                json.dumps(parameters),
                datetime.now().isoformat(),
                status,
                error
            ))
            conn.commit()
            
            return self.get_generation(prediction_id)
    
    def get_generation(self, prediction_id: str) -> Optional[Generation]:
        """Get a specific generation by ID."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM generations WHERE id = ?', (prediction_id,))
            row = cursor.fetchone()
            return Generation.from_row(tuple(row)) if row else None
    
    def update_generation_status(self, 
                               prediction_id: str,
                               status: str,
                               error: Optional[str] = None) -> None:
        """Update the status of a generation."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE generations 
                SET status = ?, error = ?
                WHERE id = ?
            ''', (status, error, prediction_id))
            conn.commit()
    
    def add_image(self,
                 generation_id: str,
                 file_path: Path,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 format: Optional[str] = None) -> Image:
        """Add a new generated image."""
        file_size = file_path.stat().st_size if file_path.exists() else None
        
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO images (
                    generation_id, file_path, width, height, 
                    format, file_size, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                generation_id,
                str(file_path),
                width,
                height,
                format,
                file_size,
                datetime.now().isoformat()
            ))
            image_id = cursor.lastrowid
            conn.commit()
            
            return Image(
                id=image_id,
                generation_id=generation_id,
                file_path=file_path,
                width=width,
                height=height,
                format=format,
                file_size=file_size,
                created_at=datetime.now()
            )
    
    def get_generation_images(self, generation_id: str) -> List[Image]:
        """Get all images for a generation."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM images WHERE generation_id = ?', (generation_id,))
            return [Image.from_row(tuple(row)) for row in cursor.fetchall()]
    
    def list_generations(self,
                        limit: Optional[int] = None,
                        status: Optional[str] = None) -> List[Generation]:
        """List generations with optional filtering."""
        with self.connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM generations'
            params = []
            
            if status:
                query += ' WHERE status = ?'
                params.append(status)
            
            query += ' ORDER BY timestamp DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            return [Generation.from_row(tuple(row)) for row in cursor.fetchall()]

    def add_or_update_model(self,
                           identifier: str,
                           name: str,
                           owner: str,
                           description: Optional[str] = None) -> Model:
        """Add or update a model in the cache."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO models (
                    identifier, name, owner, description, last_updated
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (
                identifier,
                name,
                owner,
                description,
                datetime.now().isoformat()
            ))
            conn.commit()
            
            return self.get_model(identifier)
    
    def get_model(self, identifier: str) -> Optional[Model]:
        """Get a specific model by identifier."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM models WHERE identifier = ?', (identifier,))
            row = cursor.fetchone()
            return Model.from_row(tuple(row)) if row else None