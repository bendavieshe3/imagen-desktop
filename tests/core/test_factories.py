"""Test the factory classes for creating test objects."""
import pytest
from datetime import datetime
from pathlib import Path

from imagen_desktop.core.models.generation import GenerationStatus
from imagen_desktop.core.models.product import ProductType
from imagen_desktop.core.models.order import OrderStatus
from tests.factories import ProductFactory, GenerationFactory, OrderFactory


class TestFactories:
    """Test factory classes for creating test objects."""
    
    def test_product_factory(self):
        """Test ProductFactory creates valid Product objects."""
        # Create a product using the factory
        product = ProductFactory()
        
        # Check that required attributes are set
        assert product.id is not None
        assert isinstance(product.id, int)
        assert isinstance(product.file_path, Path)
        assert product.product_type == ProductType.IMAGE
        assert isinstance(product.generation_id, str)
        assert isinstance(product.created_at, datetime)
        assert product.width == 512
        assert product.height == 512
        assert product.format == "png"
        assert isinstance(product.file_size, int)
        assert isinstance(product.metadata, dict)
    
    def test_generation_factory(self):
        """Test GenerationFactory creates valid Generation objects."""
        # Create a generation using the factory
        generation = GenerationFactory()
        
        # Check that required attributes are set
        assert generation.id is not None
        assert isinstance(generation.id, str)
        assert isinstance(generation.order_id, int)
        assert generation.model == "stability-ai/sdxl"
        assert generation.prompt == "A beautiful mountain landscape"
        assert generation.status == GenerationStatus.COMPLETED
        assert isinstance(generation.timestamp, datetime)
        assert "prompt" in generation.parameters
        assert "width" in generation.parameters
        assert "height" in generation.parameters
        assert isinstance(generation.return_parameters, dict)
        assert generation.error is None
    
    def test_order_factory(self):
        """Test OrderFactory creates valid Order objects."""
        # Create an order using the factory
        order = OrderFactory()
        
        # Check that required attributes are set
        assert order.id is not None
        assert isinstance(order.id, int)
        assert order.model == "stability-ai/sdxl"
        assert order.prompt == "A beautiful mountain landscape"
        assert order.status == OrderStatus.PENDING
        assert isinstance(order.created_at, datetime)
        assert isinstance(order.base_parameters, dict)
        assert order.project_id is None
        
        # Test order methods
        assert order.is_active() is True
        assert order.can_be_canceled() is True