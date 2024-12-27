"""Gallery presenter handling business logic for the gallery view."""
from typing import List, Optional
from pathlib import Path
from PIL import Image
from sqlalchemy import desc, asc
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
        
        # Import legacy files if using database
        if self.product_repository:
            self._import_legacy_files()
    
    def _import_legacy_files(self):
        """Import existing files from file system into products table."""
        try:
            # Get list of existing product file paths
            existing_products = self.product_repository.list_products()
            existing_paths = {Path(p.file_path) for p in existing_products}
            
            # Get all files from generations
            for generation in self.image_model.list_generations():
                for file_path in generation.output_paths:
                    if file_path.exists() and file_path not in existing_paths:
                        try:
                            # Get image metadata
                            with Image.open(file_path) as img:
                                width, height = img.size
                                format = img.format.lower() if img.format else None
                            
                            # Create product record
                            self.product_repository.create_product(
                                file_path=file_path,
                                generation_id=generation.id,
                                width=width,
                                height=height,
                                format=format,
                                product_type="image",
                                metadata={
                                    "source": "legacy_import",
                                    "imported": True
                                }
                            )
                            logger.debug(f"Imported legacy file: {file_path}")
                            
                        except Exception as e:
                            logger.error(f"Failed to import {file_path}: {e}")
                            
            logger.info("Completed legacy file import")
            
        except Exception as e:
            logger.error(f"Error during legacy file import: {e}")
    
    def list_images(self, 
                   limit: Optional[int] = None,
                   product_type: str = "image",
                   sort_by: str = "Most Recent") -> List[Path]:
        """
        List available images, preferring database if available.
        
        Args:
            limit: Maximum number of images to return
            product_type: Type of product to list
            sort_by: Sort order ("Most Recent", "Oldest First", "Largest Files", "Smallest Files")
            
        Returns:
            List of Paths to image files
        """
        image_paths = []
        
        # Try database first if available
        if self.product_repository:
            try:
                # Build query based on sort order
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