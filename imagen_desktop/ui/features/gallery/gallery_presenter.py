"""Gallery presenter handling business logic for the gallery view."""
from typing import List, Optional

from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.data.repositories.product_repository import ProductRepository
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
            # Build query args based on sort order
            query_args = {
                "product_type": product_type,
                "limit": limit
            }
            
            # Add ordering
            if sort_by == "Oldest First":
                query_args["order_by"] = ("created_at", "asc")
            elif sort_by == "Largest Files":
                query_args["order_by"] = ("file_size", "desc")
            elif sort_by == "Smallest Files":
                query_args["order_by"] = ("file_size", "asc")
            else:  # Most Recent
                query_args["order_by"] = ("created_at", "desc")
            
            products = self.product_repository.list_products(**query_args)
            logger.debug(f"Listed {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return []
    
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
                    'metadata': product.product_metadata,
                    'generation_id': product.generation_id
                }
                    
            return {}
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return {}
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product.
        
        Args:
            product_id: ID of product to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            product = self.product_repository.get_product(product_id)
            if product and self.product_repository.delete_product(product.id):
                logger.info(f"Successfully deleted product: {product_id}")
                if self.view:
                    self.view.refresh_gallery()
                return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False