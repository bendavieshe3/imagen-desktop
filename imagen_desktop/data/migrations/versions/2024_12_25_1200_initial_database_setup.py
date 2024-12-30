"""Initial database setup.

Revision ID: initial_setup
Create Date: 2024-03-25 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic
revision = 'initial_setup'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create generations table
    op.create_table(
        'generations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('parameters', sqlite.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create images table
    op.create_table(
        'images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('generation_id', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('width', sa.Integer()),
        sa.Column('height', sa.Integer()),
        sa.Column('format', sa.String()),
        sa.Column('file_size', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['generation_id'], ['generations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create models table
    op.create_table(
        'models',
        sa.Column('identifier', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('identifier')
    )
    
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create generation_tags association table
    op.create_table(
        'generation_tags',
        sa.Column('generation_id', sa.String(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['generation_id'], ['generations.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('generation_id', 'tag_id')
    )
    
    # Create indexes
    op.create_index('idx_generations_timestamp', 'generations', ['timestamp'])
    op.create_index('idx_images_generation_id', 'images', ['generation_id'])
    op.create_index('idx_generation_tags_tag_id', 'generation_tags', ['tag_id'])

def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_index('idx_generation_tags_tag_id')
    op.drop_index('idx_images_generation_id')
    op.drop_index('idx_generations_timestamp')
    op.drop_table('generation_tags')
    op.drop_table('tags')
    op.drop_table('models')
    op.drop_table('images')
    op.drop_table('generations')