"""Tests for the Order domain model."""
import pytest
from datetime import datetime

from imagen_desktop.core.models.order import Order, OrderStatus
from tests.factories import OrderFactory


class TestOrder:
    """Tests for the Order domain model."""
    
    def test_order_creation(self):
        """Test creating an Order instance."""
        # Create an order with specific values
        order = Order(
            id=5,
            model="stability-ai/sdxl",
            prompt="A beautiful sunset over mountains",
            base_parameters={"width": 1024, "height": 1024, "steps": 50},
            status=OrderStatus.PENDING,
            created_at=datetime(2025, 5, 17, 12, 0, 0),
            project_id=10
        )
        
        # Check attributes
        assert order.id == 5
        assert order.model == "stability-ai/sdxl"
        assert order.prompt == "A beautiful sunset over mountains"
        assert order.base_parameters == {"width": 1024, "height": 1024, "steps": 50}
        assert order.status == OrderStatus.PENDING
        assert order.created_at == datetime(2025, 5, 17, 12, 0, 0)
        assert order.project_id == 10
    
    def test_order_status_enum(self):
        """Test OrderStatus enum values."""
        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.PROCESSING == "processing"
        assert OrderStatus.FULFILLED == "fulfilled"
        assert OrderStatus.FAILED == "failed"
        assert OrderStatus.CANCELED == "canceled"
        
        # Test creating orders with different statuses
        pending_order = OrderFactory(status=OrderStatus.PENDING)
        processing_order = OrderFactory(status=OrderStatus.PROCESSING)
        fulfilled_order = OrderFactory(status=OrderStatus.FULFILLED)
        failed_order = OrderFactory(status=OrderStatus.FAILED)
        canceled_order = OrderFactory(status=OrderStatus.CANCELED)
        
        assert pending_order.status == OrderStatus.PENDING
        assert processing_order.status == OrderStatus.PROCESSING
        assert fulfilled_order.status == OrderStatus.FULFILLED
        assert failed_order.status == OrderStatus.FAILED
        assert canceled_order.status == OrderStatus.CANCELED
    
    def test_from_db_model(self):
        """Test creating an Order from a database model."""
        # Create a mock DB model with the expected attributes
        class MockDbModel:
            id = 42
            model = "stability-ai/sdxl"
            prompt = "A futuristic city at night"
            base_parameters = {"width": 512, "height": 512, "steps": 25}
            status = "processing"
            created_at = datetime(2025, 5, 17, 12, 30, 0)
            project_id = 3
        
        db_model = MockDbModel()
        
        # Create an Order from the DB model
        order = Order.from_db_model(db_model)
        
        # Check that attributes were copied correctly
        assert order.id == 42
        assert order.model == "stability-ai/sdxl"
        assert order.prompt == "A futuristic city at night"
        assert order.base_parameters == {"width": 512, "height": 512, "steps": 25}
        assert order.status == OrderStatus.PROCESSING
        assert order.created_at == datetime(2025, 5, 17, 12, 30, 0)
        assert order.project_id == 3
    
    def test_is_active(self):
        """Test is_active method for different order statuses."""
        # Test with pending status
        pending_order = OrderFactory(status=OrderStatus.PENDING)
        assert pending_order.is_active() is True
        
        # Test with processing status
        processing_order = OrderFactory(status=OrderStatus.PROCESSING)
        assert processing_order.is_active() is True
        
        # Test with fulfilled status
        fulfilled_order = OrderFactory(status=OrderStatus.FULFILLED)
        assert fulfilled_order.is_active() is False
        
        # Test with failed status
        failed_order = OrderFactory(status=OrderStatus.FAILED)
        assert failed_order.is_active() is False
        
        # Test with canceled status
        canceled_order = OrderFactory(status=OrderStatus.CANCELED)
        assert canceled_order.is_active() is False
    
    def test_can_be_canceled(self):
        """Test can_be_canceled method."""
        # Create orders with different statuses
        pending_order = OrderFactory(status=OrderStatus.PENDING)
        processing_order = OrderFactory(status=OrderStatus.PROCESSING)
        fulfilled_order = OrderFactory(status=OrderStatus.FULFILLED)
        failed_order = OrderFactory(status=OrderStatus.FAILED)
        canceled_order = OrderFactory(status=OrderStatus.CANCELED)
        
        # Only pending and processing orders can be canceled
        assert pending_order.can_be_canceled() is True
        assert processing_order.can_be_canceled() is True
        assert fulfilled_order.can_be_canceled() is False
        assert failed_order.can_be_canceled() is False
        assert canceled_order.can_be_canceled() is False