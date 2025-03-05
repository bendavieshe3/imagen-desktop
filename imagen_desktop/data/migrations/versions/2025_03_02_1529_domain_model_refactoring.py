"""Domain model refactoring.

Revision ID: domain_model_refactoring
Create Date: 2025-03-02 15:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic
revision = 'domain_model_refactoring'
down_revision = 'add_products_collections'  # Replace with your actual last migration
branch_labels = None
depends_on = None

def table_exists(conn, table_name):
    """Check if a table exists in the database."""
    inspector = inspect(conn)
    return table_name in inspector.get_table_names()

def upgrade() -> None:
    conn = op.get_bind()
    
    # Create projects table if it doesn't exist
    if not table_exists(conn, 'projects'):
        op.create_table(
            'projects',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('status', sa.String(), default="active"),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create orders table if it doesn't exist
    if not table_exists(conn, 'orders'):
        op.create_table(
            'orders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('model', sa.String(), nullable=False),
            sa.Column('prompt', sa.Text(), nullable=False),
            sa.Column('base_parameters', sqlite.JSON(), nullable=False),
            sa.Column('status', sa.String(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Check if generations table exists
    if table_exists(conn, 'generations'):
        # Check if order_id column exists
        inspector = inspect(conn)
        generations_columns = [c['name'] for c in inspector.get_columns('generations')]
        
        # Add order_id if it doesn't exist
        if 'order_id' not in generations_columns:
            op.add_column('generations', 
                sa.Column('order_id', sa.Integer(), nullable=True)
            )
        
        # Add return_parameters if it doesn't exist
        if 'return_parameters' not in generations_columns:
            op.add_column('generations', 
                sa.Column('return_parameters', sqlite.JSON(), nullable=True)
            )
    
    # Check if products table exists
    if table_exists(conn, 'products'):
        # Check if is_favorite column exists
        inspector = inspect(conn)
        products_columns = [c['name'] for c in inspector.get_columns('products')]
        
        # Add is_favorite if it doesn't exist
        if 'is_favorite' not in products_columns:
            op.add_column('products', 
                sa.Column('is_favorite', sa.Boolean(), default=False)
            )
    
    # Create product_tags table if it doesn't exist
    if not table_exists(conn, 'product_tags'):
        op.create_table(
            'product_tags',
            sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), primary_key=True),
            sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id'), primary_key=True),
        )
    
    # Only perform data migration if we have generations without orders
    try:
        # Check if there are generations without order_id
        has_generations_without_orders = conn.execute(
            text("SELECT COUNT(*) FROM generations WHERE order_id IS NULL")
        ).scalar() > 0
        
        if has_generations_without_orders:
            # Get all generations without order_id
            generations = conn.execute(
                text("SELECT id, model, prompt, parameters, timestamp, status FROM generations WHERE order_id IS NULL")
            ).fetchall()
            
            # Create orders and link generations
            for gen in generations:
                # Create order with same parameters as generation
                order_id_result = conn.execute(
                    text("""INSERT INTO orders 
                   (model, prompt, base_parameters, status, created_at)
                   VALUES (:model, :prompt, :parameters, :status, :timestamp)
                   RETURNING id"""), 
                    {"model": gen[1], "prompt": gen[2], "parameters": gen[3], "status": 'fulfilled', "timestamp": gen[4]}
                ).fetchone()
                
                if order_id_result:
                    order_id = order_id_result[0]
                    
                    # Associate generation with order
                    conn.execute(
                        text("""UPDATE generations
                       SET order_id = :order_id
                       WHERE id = :gen_id"""),
                        {"order_id": order_id, "gen_id": gen[0]}
                    )
        
        # Set order_id to not nullable if it exists and all generations have orders
        has_null_order_ids = conn.execute(
            text("SELECT COUNT(*) FROM generations WHERE order_id IS NULL")
        ).scalar() > 0
        
        if not has_null_order_ids and 'order_id' in generations_columns:
            with op.batch_alter_table('generations') as batch_op:
                batch_op.alter_column('order_id', nullable=False)
    except Exception as e:
        # Log but continue if there's an issue with the data migration
        print(f"Warning: Could not complete data migration: {e}")
    
    # Migrate any image data to products if images table exists
    if table_exists(conn, 'images'):
        try:
            images = conn.execute(
                text("""SELECT id, generation_id, file_path, width, height, format, file_size, created_at
                   FROM images""")
            ).fetchall()
            
            if images:
                for img in images:
                    # Check if product already exists for this file path
                    existing = conn.execute(
                        text("""SELECT id FROM products WHERE file_path = :file_path"""),
                        {"file_path": img[2]}
                    ).fetchone()
                    
                    if not existing:
                        # Insert as new product
                        conn.execute(
                            text("""INSERT INTO products
                                   (generation_id, file_path, product_type, width, height, format, file_size, created_at)
                                   VALUES (:gen_id, :file_path, :product_type, :width, :height, :format, :file_size, :created_at)"""),
                            {"gen_id": img[1], "file_path": img[2], "product_type": 'image', 
                             "width": img[3], "height": img[4], "format": img[5], "file_size": img[6], "created_at": img[7]}
                        )
            
            # Optional: Drop the images table if it exists and we've migrated the data
            try:
                op.drop_table('images')
            except:
                pass  # Table might have already been dropped
        except Exception as e:
            # Log but continue if there's an issue with the image migration
            print(f"Warning: Could not complete image migration: {e}")


def downgrade() -> None:
    # This is a major refactoring, so downgrading might not be fully possible
    # But we'll try to provide a path back
    
    conn = op.get_bind()
    
    # Recreate images table if it was dropped
    if not table_exists(conn, 'images'):
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
            sa.ForeignKeyConstraint(['generation_id'], ['generations.id']),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Copy data from products to images
    try:
        products = conn.execute(
            text("""SELECT id, generation_id, file_path, width, height, format, file_size, created_at
                   FROM products
                   WHERE product_type = 'image'""")
        ).fetchall()
        
        for product in products:
            conn.execute(
                text("""INSERT INTO images
                       (generation_id, file_path, width, height, format, file_size, created_at)
                       VALUES (:gen_id, :file_path, :width, :height, :format, :file_size, :created_at)"""),
                {"gen_id": product[1], "file_path": product[2], "width": product[3], 
                 "height": product[4], "format": product[5], "file_size": product[6], "created_at": product[7]}
            )
    except Exception as e:
        print(f"Warning: Could not migrate data back to images table: {e}")
    
    # Remove added columns and tables
    if table_exists(conn, 'product_tags'):
        op.drop_table('product_tags')
    
    inspector = inspect(conn)
    
    if 'products' in inspector.get_table_names():
        products_columns = [c['name'] for c in inspector.get_columns('products')]
        if 'is_favorite' in products_columns:
            op.drop_column('products', 'is_favorite')
    
    if 'generations' in inspector.get_table_names():
        generations_columns = [c['name'] for c in inspector.get_columns('generations')]
        if 'return_parameters' in generations_columns:
            op.drop_column('generations', 'return_parameters')
        if 'order_id' in generations_columns:
            op.drop_column('generations', 'order_id')
    
    if table_exists(conn, 'orders'):
        op.drop_table('orders')
    
    if table_exists(conn, 'projects'):
        op.drop_table('projects')