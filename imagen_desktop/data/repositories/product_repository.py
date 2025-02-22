"""Repository for managing products."""
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from sqlalchemy import desc

from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.data.schema import Product as ProductModel
from imagen_desktop.data.repositories.base_repository import BaseRepository
from imagen_desktop.core.events.product_events import (
    ProductEvent, ProductEventType, ProductEventPublisher
)
from imagen_desktop.utils.debug_logger import logger

class ProductRepository(BaseRepository):
    """Repository for managing product data and persistence."""

    def _model_to_domain(self, model: ProductModel) -> Product:
        """Convert DB model to domain model."""
        return Product(
            id=model.id,
            file_path=Path(model.file_path),
            product_type=ProductType(model.product_type),
            generation_id=model.generation_id,
            created_at=model.created_at,
            width=model.width,
            height=model.height,
            format=model.format,
            file_size=model.file_size,
            metadata=model.product_metadata if model.product_metadata else {}
        )

    def create_product(self,
                      file_path: Path,
                      generation_id: Optional[str] = None,
                      width: Optional[int] = None,
                      height: Optional[int] = None,
                      format: Optional[str] = None,
                      product_type: ProductType = ProductType.IMAGE) -> Optional[Product]:
        """Create a new product.
        
        Args:
            file_path: Path to the product file
            generation_id: Optional ID of generation that created this product
            width: Optional width in pixels
            height: Optional height in pixels
            format: Optional file format (e.g., 'png', 'jpg')
            product_type: Type of product (defaults to IMAGE)
            
        Returns:
            Created Product or None if creation failed
        """
        try:
            # Ensure file exists and get size
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            file_size = file_path.stat().st_size
            
            with self._get_session() as session:
                model = ProductModel(
                    file_path=str(file_path),
                    product_type=product_type.value,
                    generation_id=generation_id,
                    created_at=datetime.now(),
                    width=width,
                    height=height,
                    format=format,
                    file_size=file_size,
                    product_metadata={}
                )
                session.add(model)
                session.commit()
                session.refresh(model)
                
                # Convert to domain model
                product = self._model_to_domain(model)
                
                # Emit creation event
                event = ProductEvent(
                    event_type=ProductEventType.CREATED,
                    product=product
                )
                ProductEventPublisher.publish_product_event(event)
                
                logger.info(f"Created product {product.id}")
                return product
                
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return None

    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        try:
            model = self.get_by_id(ProductModel, product_id)
            if model:
                return self._model_to_domain(model)
            logger.debug(f"Product {product_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {e}")
            return None

    def get_all_products(self) -> List[Product]:
        """Get all products, ordered by creation date."""
        try:
            with self._get_session() as session:
                models = session.query(ProductModel).order_by(
                    desc(ProductModel.created_at)
                ).all()
                return [self._model_to_domain(m) for m in models]
        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            return []

    def update_product(self, product: Product) -> bool:
        """Update an existing product."""
        try:
            with self._get_session() as session:
                model = session.query(ProductModel).get(product.id)
                if model:
                    model.file_path = str(product.file_path)
                    model.product_type = product.product_type.value
                    model.generation_id = product.generation_id
                    model.width = product.width
                    model.height = product.height
                    model.format = product.format
                    model.file_size = product.file_size
                    model.product_metadata = product.metadata
                    session.commit()
                    
                    # Emit update event
                    event = ProductEvent(
                        event_type=ProductEventType.UPDATED,
                        product=product
                    )
                    ProductEventPublisher.publish_product_event(event)
                    
                    logger.info(f"Updated product {product.id}")
                    return True
                    
                logger.debug(f"Product {product.id} not found for update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating product {product.id}: {e}")
            event = ProductEvent(
                event_type=ProductEventType.ERROR,
                product=product,
                error=str(e)
            )
            ProductEventPublisher.publish_product_event(event)
            return False

    def delete_product(self, product_id: int) -> bool:
        """Delete a product."""
        try:
            with self._get_session() as session:
                model = session.query(ProductModel).get(product_id)
                if model:
                    # Convert to domain model for event before deletion
                    product = self._model_to_domain(model)
                    
                    # Delete from database
                    session.delete(model)
                    session.commit()
                    
                    # Emit deletion event
                    event = ProductEvent(
                        event_type=ProductEventType.DELETED,
                        product=product
                    )
                    ProductEventPublisher.publish_product_event(event)
                    
                    logger.info(f"Deleted product {product_id}")
                    return True
                    
                logger.debug(f"Product {product_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False