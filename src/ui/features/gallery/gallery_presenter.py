"""Gallery presenter handling business logic for the gallery view."""
from typing import List, Optional
from pathlib import Path
from PIL import Image
from sqlalchemy import desc, asc, or_

from core.models.product import ProductType
from data.repositories.product_repository import ProductRepository
from utils.debug_logger import logger

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
                     sort_by: str = "Most Recent") -> List[Path]:
        """List available products with sorting and filtering.
        
        Args:
            limit: Maximum number of products to return
            product_type: Type of product to list
            sort_by: Sort order ["Most Recent", "Oldest First", "Largest Files", "Smallest Files"]
            
        Returns:
            List of paths to product files
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
            
            # Get products and convert to paths
            products = self.product_repository.list_products(**query_args)
            image_paths = []
            
            for product in products:
                path = Path(product.file_path)
                if path.exists():
                    image_paths.append(path)
            
            logger.debug(f"Listed {len(image_paths)} products")
            return image_paths
            
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            return []
    
    def get_product_details(self, path: Path) -> dict:
        """Get details about a product.
        
        Args:
            path: Path to product file
            
        Returns:
            Dict containing product metadata
        """
        try:
            # Search by file path
            products = self.product_repository.list_products(
                file_path=str(path)
            )
            
            for product in products:
                if Path(product.file_path) == path:
                    return {
                        'width': product.width,
                        'height': product.height,
                        'format': product.format,
                        'size': product.file_size,
                        'metadata': product.product_metadata,
                        'generation_id': product.generation_id
                    }
                    
            # Fall back to basic file info
            return {
                'path': path,
                'size': path.stat().st_size if path.exists() else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return {'path': path}
    
    def delete_product(self, path: Path) -> bool:
        """Delete a product and its file.
        
        Args:
            path: Path to product file
            
        Returns:
            True if deletion was successful
        """
        try:
            products = self.product_repository.list_products(
                file_path=str(path)
            )
            
            deleted = False
            for product in products:
                if Path(product.file_path) == path:
                    if self.product_repository.delete_product(product.id):
                        deleted = True
                        break
            
            # Always try to delete the file
            if path.exists():
                path.unlink()
                deleted = True
            
            if deleted:
                logger.info(f"Successfully deleted product: {path}")
                if self.view:
                    self.view.refresh_gallery()
                    
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False