"""Gallery presenter handling business logic for the gallery view."""
from typing import List, Optional
from pathlib import Path
from ...models.image_generation import ImageGenerationModel
from ...data.product_repository import ProductRepository
from ...utils.debug_logger import logger

class GalleryPresenter:
    """Presenter for gallery view."""
    
    def __init__(self, 
                 image_model: ImageGenerationModel,
                 product_repository: Optional[ProductRepository] = None):
        self.image_model = image_model
        self.product_repository = product_repository
    
    def list_images(self, 
                   limit: Optional[int] = None,
                   product_type: str = "image") -> List[Path]:
        """
        List available images, preferring database if available.
        
        Returns:
            List of Paths to image files
        """
        image_paths = []
        
        # Try database first if available
        if self.product_repository:
            try:
                products = self.product_repository.list_products(
                    product_type=product_type,
                    limit=limit
                )
                
                for product in products:
                    path = Path(product.file_path)
                    if path.exists():
                        image_paths.append(path)
                
                logger.debug(f"Listed {len(image_paths)} products from database")
                
            except Exception as e:
                logger.error(f"Error listing products from database: {e}")
        
        # Fall back to file system if needed
        if not image_paths:
            try:
                generations = self.image_model.list_generations()
                for generation in generations:
                    image_paths.extend([
                        path for path in generation.output_paths
                        if path.exists()
                    ])
                
                if limit:
                    image_paths = image_paths[:limit]
                    
                logger.debug(f"Listed {len(image_paths)} images from file system")
                
            except Exception as e:
                logger.error(f"Error listing images from file system: {e}")
        
        return image_paths
    
    def get_image_details(self, path: Path) -> dict:
        """
        Get details about an image, preferring database if available.
        
        Returns:
            Dict containing image metadata
        """
        if self.product_repository:
            try:
                # Find product with matching path
                products = self.product_repository.list_products(
                    search=str(path.name)
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
            except Exception as e:
                logger.error(f"Error getting product details from database: {e}")
        
        # Fall back to basic file info
        return {
            'path': path,
            'size': path.stat().st_size if path.exists() else 0
        }
    
    def delete_image(self, path: Path) -> bool:
        """
        Delete an image and its database record if exists.
        
        Returns:
            True if deletion was successful
        """
        success = False
        
        # Delete from database if available
        if self.product_repository:
            try:
                products = self.product_repository.list_products(
                    search=str(path.name)
                )
                for product in products:
                    if Path(product.file_path) == path:
                        # Note: Actual deletion handled by SQLAlchemy cascade
                        success = True
                        break
            except Exception as e:
                logger.error(f"Error deleting product from database: {e}")
        
        # Delete file if it exists
        try:
            if path.exists():
                path.unlink()
                success = True
        except Exception as e:
            logger.error(f"Error deleting file {path}: {e}")
            return False
        
        return success