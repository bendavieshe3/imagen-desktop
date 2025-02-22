"""Gallery presenter handling business logic for the gallery view."""
from typing import List, Optional
from operator import attrgetter

from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.data.repositories.product_repository import ProductRepository
from imagen_desktop.core.events.product_events import (
    ProductEvent, ProductEventType, ProductEventPublisher
)
from imagen_desktop.utils.debug_logger import logger

class GalleryPresenter:
    """Presenter for gallery view."""
    
    def __init__(self, 
                 product_repository: ProductRepository,
                 view=None):
        """Initialize the presenter.
        
        Args:
            product_repository: Repository for product access
            view: Optional view reference for updates
        """
        self.product_repository = product_repository
        self.view = view
    
    def list_products(self, 
                     limit: Optional[int] = None,
                     product_type: str = ProductType.IMAGE,
                     sort_by: str = "Most Recent") -> List[Product]:
        """List available products with sorting and filtering.
        
        Args:
            limit: Maximum number of products to return
            product_type: Type of product to list
            sort_by: Sort order ["Most Recent", "Oldest First", "Largest Files", "Smallest Files"]
            
        Returns:
            List of Product objects
        """
        try:
            # Get all products
            products = self.product_repository.get_all_products()
            
            # Filter by type if specified
            if product_type:
                products = [p for p in products if p.product_type == product_type]
            
            # Apply sorting
            if sort_by == "Most Recent":
                products.sort(key=attrgetter('created_at'), reverse=True)
            elif sort_by == "Oldest First":
                products.sort(key=attrgetter('created_at'))
            elif sort_by == "Largest Files":
                products.sort(key=attrgetter('file_size'), reverse=True)
            elif sort_by == "Smallest Files":
                products.sort(key=attrgetter('file_size'))
            
            # Apply limit if specified
            if limit is not None:
                products = products[:limit]
            
            logger.debug(
                f"Listed {len(products)} products",
                extra={
                    'context': {
                        'sort_by': sort_by,
                        'product_type': product_type
                    }
                }
            )
            
            return products
            
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return []
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product.
        
        Args:
            product_id: ID of product to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            success = self.product_repository.delete_product(product_id)
            if not success:
                logger.error(f"Failed to delete product {product_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False
    
    def get_product_details(self, product_id: int) -> dict:
        """Get details about a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Dict containing product metadata
        """
        try:
            product = self.product_repository.get_product(product_id)
            if product:
                return {
                    'width': product.width,
                    'height': product.height,
                    'format': product.format,
                    'size': product.file_size,
                    'metadata': product.metadata,
                    'generation_id': product.generation_id
                }
                    
            return {}
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return {}