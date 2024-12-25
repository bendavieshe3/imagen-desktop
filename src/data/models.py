"""Database models and operations."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import sqlite3

@dataclass
class Generation:
    id: str
    model: str
    prompt: str
    parameters: Dict[str, Any]
    timestamp: datetime
    status: str
    error: Optional[str] = None
    
    @classmethod
    def from_row(cls, row: tuple) -> 'Generation':
        return cls(
            id=row[0],
            model=row[1],
            prompt=row[2],
            parameters=json.loads(row[3]),
            timestamp=datetime.fromisoformat(row[4]),
            status=row[5],
            error=row[6]
        )

@dataclass
class Image:
    id: int
    generation_id: str
    file_path: Path
    width: Optional[int]
    height: Optional[int]
    format: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    
    @classmethod
    def from_row(cls, row: tuple) -> 'Image':
        return cls(
            id=row[0],
            generation_id=row[1],
            file_path=Path(row[2]),
            width=row[3],
            height=row[4],
            format=row[5],
            file_size=row[6],
            created_at=datetime.fromisoformat(row[7])
        )

@dataclass
class Model:
    identifier: str  # owner/name
    name: str
    owner: str
    description: Optional[str]
    last_updated: datetime
    
    @classmethod
    def from_row(cls, row: tuple) -> 'Model':
        return cls(
            identifier=row[0],
            name=row[1],
            owner=row[2],
            description=row[3],
            last_updated=datetime.fromisoformat(row[4])
        )

@dataclass
class Tag:
    id: int
    name: str
    
    @classmethod
    def from_row(cls, row: tuple) -> 'Tag':
        return cls(id=row[0], name=row[1])