"""Add products and collections tables.

Revision ID: add_products_collections
Create Date: 2024-12-25 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic
revision = 'add_products_collections'
down_revision = 'add_model_metadata'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('generation_id', sa.String(), sa.ForeignKey('generations.id')),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('product_type', sa.String(), nullable=False),
        sa.Column('width', sa.Integer()),
        sa.Column('height', sa.Integer()),
        sa.Column('format', sa.String()),
        sa.Column('file_size', sa.Integer()),
        sa.Column('product_metadata', sqlite.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create collections table
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create collection_products association table
    op.create_table(
        'collection_products',
        sa.Column('collection_id', sa.Integer(), sa.ForeignKey('collections.id'), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), primary_key=True),
        sa.Column('added_at', sa.DateTime(), nullable=False)
    )
    
    # Create indexes
    op.create_index('idx_products_generation_id', 'products', ['generation_id'])
    op.create_index('idx_products_created_at', 'products', ['created_at'])
    op.create_index('idx_collection_products_product_id', 'collection_products', ['product_id'])

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_collection_products_product_id')
    op.drop_index('idx_products_created_at')
    op.drop_index('idx_products_generation_id')
    op.drop_table('collection_products')
    op.drop_table('collections')  
    op.drop_table('products')