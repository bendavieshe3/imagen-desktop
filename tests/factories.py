"""
Test factories for creating test data.

This module provides factories for creating test objects using factory_boy.
"""
import factory
import datetime
from pathlib import Path
from enum import Enum

from imagen_desktop.core.models.generation import Generation, GenerationStatus
from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.core.models.order import Order, OrderStatus


class ProductFactory(factory.Factory):
    """Factory for creating test Product objects."""
    
    class Meta:
        model = Product
    
    id = factory.Sequence(lambda n: n)
    file_path = factory.LazyAttribute(lambda _: Path("/tmp/test_image.png"))
    product_type = ProductType.IMAGE
    generation_id = factory.Sequence(lambda n: f"gen-{n}")
    created_at = factory.LazyFunction(datetime.datetime.now)
    width = 512
    height = 512 
    format = "png"
    file_size = 1024 * 1024  # 1MB
    metadata = factory.Dict({"prompt": "test prompt", "model": "test-model"})


class GenerationFactory(factory.Factory):
    """Factory for creating test Generation objects."""
    
    class Meta:
        model = Generation
    
    id = factory.Sequence(lambda n: f"gen-{n}")
    order_id = factory.Sequence(lambda n: n)
    model = "stability-ai/sdxl"
    prompt = "A beautiful mountain landscape"
    parameters = factory.Dict({
        "prompt": "A beautiful mountain landscape",
        "negative_prompt": "blurry, ugly",
        "width": 1024,
        "height": 1024,
        "num_outputs": 1,
    })
    timestamp = factory.LazyFunction(datetime.datetime.now)
    status = GenerationStatus.COMPLETED
    return_parameters = factory.Dict({"prediction_id": "123", "status": "succeeded"})
    error = None


class OrderFactory(factory.Factory):
    """Factory for creating test Order objects."""
    
    class Meta:
        model = Order
    
    id = factory.Sequence(lambda n: n)
    model = "stability-ai/sdxl"
    prompt = "A beautiful mountain landscape"
    base_parameters = factory.Dict({
        "negative_prompt": "blurry, ugly",
        "width": 1024,
        "height": 1024,
        "num_outputs": 1,
    })
    status = OrderStatus.PENDING
    created_at = factory.LazyFunction(datetime.datetime.now)
    project_id = None