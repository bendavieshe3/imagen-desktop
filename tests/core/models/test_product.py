"""Tests for the Product domain model."""
import pytest
from datetime import datetime
from pathlib import Path

from imagen_desktop.core.models.product import Product, ProductType
from tests.factories import ProductFactory


class TestProduct:
    """Tests for the Product domain model."""
    
    def test_product_creation(self):
        """Test creating a Product instance."""
        # Create a product with specific values
        product = Product(
            id=1,
            file_path=Path("/tmp/test_image.jpg"),
            product_type=ProductType.IMAGE,
            generation_id="gen-123",
            created_at=datetime(2025, 5, 17, 12, 0, 0),
            width=1024,
            height=768,
            format="jpg",
            file_size=2048576,
            metadata={"prompt": "test prompt"}
        )
        
        # Check attributes
        assert product.id == 1
        assert product.file_path == Path("/tmp/test_image.jpg")
        assert product.product_type == ProductType.IMAGE
        assert product.generation_id == "gen-123"
        assert product.created_at == datetime(2025, 5, 17, 12, 0, 0)
        assert product.width == 1024
        assert product.height == 768
        assert product.format == "jpg"
        assert product.file_size == 2048576
        assert product.metadata == {"prompt": "test prompt"}
    
    def test_product_types(self):
        """Test ProductType enum values."""
        assert ProductType.IMAGE == "image"
        assert ProductType.VIDEO == "video"
        assert ProductType.AUDIO == "audio"
        
        # Test creating products with different types
        image_product = ProductFactory(product_type=ProductType.IMAGE)
        video_product = ProductFactory(product_type=ProductType.VIDEO)
        audio_product = ProductFactory(product_type=ProductType.AUDIO)
        
        assert image_product.product_type == ProductType.IMAGE
        assert video_product.product_type == ProductType.VIDEO
        assert audio_product.product_type == ProductType.AUDIO
    
    def test_from_db_model(self):
        """Test creating a Product from a database model."""
        # Create a mock DB model with the expected attributes
        class MockDbModel:
            id = 42
            file_path = "/tmp/mock_image.png"
            product_type = "image"
            generation_id = "gen-456"
            created_at = datetime(2025, 5, 17, 12, 30, 0)
            width = 800
            height = 600
            format = "png"
            file_size = 1048576
            product_metadata = {"model": "test-model"}
        
        db_model = MockDbModel()
        
        # Create a Product from the DB model
        product = Product.from_db_model(db_model)
        
        # Check that attributes were copied correctly
        assert product.id == 42
        assert product.file_path == Path("/tmp/mock_image.png")
        assert product.product_type == ProductType.IMAGE
        assert product.generation_id == "gen-456"
        assert product.created_at == datetime(2025, 5, 17, 12, 30, 0)
        assert product.width == 800
        assert product.height == 600
        assert product.format == "png"
        assert product.file_size == 1048576
        assert product.metadata == {"model": "test-model"}
    
    def test_from_db_model_with_none_metadata(self):
        """Test creating a Product from DB model with None metadata."""
        # Create a mock DB model with None metadata
        class MockDbModel:
            id = 42
            file_path = "/tmp/mock_image.png"
            product_type = "image"
            generation_id = "gen-456"
            created_at = datetime(2025, 5, 17, 12, 30, 0)
            width = 800
            height = 600
            format = "png"
            file_size = 1048576
            product_metadata = None
        
        db_model = MockDbModel()
        
        # Create a Product from the DB model
        product = Product.from_db_model(db_model)
        
        # Check that metadata is an empty dict
        assert product.metadata == {}