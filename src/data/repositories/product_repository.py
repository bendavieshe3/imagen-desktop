"""Repository for managing Product records."""
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy import or_, and_, desc, asc
from sqlalchemy.orm import joinedload

from .base_repository import BaseRepository
from .schema import Product, Generation, Collection, CollectionProduct
from ..core.events.product_events import ProductEvent, ProductEventType, ProductEventPublisher
from ..utils.debug_logger import logger

class ProductRepository(BaseRepository):
    """Repository for Product model operations."""
    
    def create_product(self,
                      file_path: Path,
                      generation_id: Optional[str] = None,
                      width: Optional[int] = None,
                      height: Optional[int] = None,
                      format: Optional[str] = None,
                      product_type: str = "image",
                      metadata: dict = None) -> Optional[Product]:
        """Create a new product record."""
        try:
            file_size = file_path.stat().st_size if file_path.exists() else None
            
            product = Product(
                file_path=str(file_path),
                generation_id=generation_id,
                width=width,
                height=height,
                format=format,
                file_size=file_size,
                product_type=product_type,
                product_metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            created_product = self.add(product)
            if created_product:
                # Emit creation event
                event = ProductEvent(
                    event_type=ProductEventType.CREATED,
                    product_id=created_product.id,
                    product_type=product_type
                )
                ProductEventPublisher.publish_product_event(event)
                
            return created_product
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return None
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        try:
            with self._get_session() as session:
                return session.query(Product)\
                    .options(joinedload(Product.generation))\
                    .filter(Product.id == product_id)\
                    .first()
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return None
    
    def list_products(self,
                     generation_id: Optional[str] = None,
                     product_type: Optional[str] = None,
                     collection_id: Optional[int] = None,
                     search: Optional[str] = None,
                     file_path: Optional[str] = None,
                     limit: Optional[int] = None,
                     order_by: Optional[tuple] = None) -> List[Product]:
        """List products with filtering."""
        try:
            with self._get_session() as session:
                query = session.query(Product)
                
                # Apply filters
                filters = []
                if generation_id:
                    filters.append(Product.generation_id == generation_id)
                if product_type:
                    filters.append(Product.product_type == product_type)
                if collection_id:
                    query = query.join(CollectionProduct)
                    filters.append(CollectionProduct.collection_id == collection_id)
                if file_path:
                    filters.append(Product.file_path == file_path)
                if search:
                    search_term = f"%{search}%"
                    filters.append(or_(
                        Product.file_path.ilike(search_term),
                        Product.product_metadata.cast(type_=str).ilike(search_term)
                    ))
                
                if filters:
                    query = query.filter(and_(*filters))
                
                # Apply ordering
                if order_by:
                    field_name, direction = order_by
                    field = getattr(Product, field_name)
                    if direction == "desc":
                        query = query.order_by(desc(field))
                    else:
                        query = query.order_by(asc(field))
                else:
                    # Default ordering by created_at desc
                    query = query.order_by(desc(Product.created_at))
                
                # Apply limit
                if limit:
                    query = query.limit(limit)
                
                return query.all()
                
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return []
    
    def update_product_metadata(self,
                              product_id: int,
                              metadata_updates: dict) -> bool:
        """Update product metadata."""
        try:
            with self._get_session() as session:
                product = session.query(Product).get(product_id)
                if product:
                    product.product_metadata.update(metadata_updates)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating product metadata: {e}")
            return False

    def delete_product(self, product_id: int) -> bool:
        """Delete a product record."""
        try:
            with self._get_session() as session:
                product = session.query(Product).get(product_id)
                if product:
                    # Generate event before deletion
                    event = ProductEvent(
                        event_type=ProductEventType.DELETED,
                        product_id=product.id,
                        product_type=product.product_type
                    )
                    
                    # Delete record
                    session.delete(product)
                    session.commit()
                    
                    # Emit event after successful deletion
                    ProductEventPublisher.publish_product_event(event)
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False

    def add_to_collection(self,
                         product_id: int,
                         collection_id: int) -> bool:
        """Add a product to a collection."""
        try:
            with self._get_session() as session:
                association = CollectionProduct(
                    product_id=product_id,
                    collection_id=collection_id
                )
                session.add(association)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding product to collection: {e}")
            return False
    
    def remove_from_collection(self,
                             product_id: int,
                             collection_id: int) -> bool:
        """Remove a product from a collection."""
        try:
            with self._get_session() as session:
                session.query(CollectionProduct)\
                    .filter_by(
                        product_id=product_id,
                        collection_id=collection_id
                    )\
                    .delete()
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error removing product from collection: {e}")
            return False