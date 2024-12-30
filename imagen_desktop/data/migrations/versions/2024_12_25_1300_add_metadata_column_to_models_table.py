"""Add metadata column to models table.

Revision ID: add_model_metadata
Create Date: 2024-12-25 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic
revision = 'add_model_metadata'
down_revision = 'initial_setup'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add metadata column to models table
    op.add_column('models',
        sa.Column('model_metadata', sqlite.JSON(), nullable=False, server_default='{}')
    )

def downgrade() -> None:
    # Remove metadata column from models table
    op.drop_column('models', 'model_metadata')