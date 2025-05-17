"""Tests for the Generation domain model."""
import pytest
from datetime import datetime

from imagen_desktop.core.models.generation import Generation, GenerationStatus
from tests.factories import GenerationFactory


class TestGeneration:
    """Tests for the Generation domain model."""
    
    def test_generation_creation(self):
        """Test creating a Generation instance."""
        # Create a generation with specific values
        generation = Generation(
            id="gen-123",
            order_id=5,
            model="stability-ai/sdxl",
            prompt="A beautiful sunset over mountains",
            parameters={"width": 1024, "height": 1024, "steps": 50},
            timestamp=datetime(2025, 5, 17, 12, 0, 0),
            status=GenerationStatus.COMPLETED,
            return_parameters={"prediction_id": "123", "status": "succeeded"},
            error=None
        )
        
        # Check attributes
        assert generation.id == "gen-123"
        assert generation.order_id == 5
        assert generation.model == "stability-ai/sdxl"
        assert generation.prompt == "A beautiful sunset over mountains"
        assert generation.parameters == {"width": 1024, "height": 1024, "steps": 50}
        assert generation.timestamp == datetime(2025, 5, 17, 12, 0, 0)
        assert generation.status == GenerationStatus.COMPLETED
        assert generation.return_parameters == {"prediction_id": "123", "status": "succeeded"}
        assert generation.error is None
    
    def test_generation_status_enum(self):
        """Test GenerationStatus enum values."""
        assert GenerationStatus.STARTING == "starting"
        assert GenerationStatus.IN_PROGRESS == "in_progress"
        assert GenerationStatus.COMPLETED == "completed"
        assert GenerationStatus.FAILED == "failed"
        assert GenerationStatus.CANCELLED == "cancelled"
        
        # Test creating generations with different statuses
        starting_gen = GenerationFactory(status=GenerationStatus.STARTING)
        in_progress_gen = GenerationFactory(status=GenerationStatus.IN_PROGRESS)
        completed_gen = GenerationFactory(status=GenerationStatus.COMPLETED)
        failed_gen = GenerationFactory(status=GenerationStatus.FAILED)
        cancelled_gen = GenerationFactory(status=GenerationStatus.CANCELLED)
        
        assert starting_gen.status == GenerationStatus.STARTING
        assert in_progress_gen.status == GenerationStatus.IN_PROGRESS
        assert completed_gen.status == GenerationStatus.COMPLETED
        assert failed_gen.status == GenerationStatus.FAILED
        assert cancelled_gen.status == GenerationStatus.CANCELLED
    
    def test_from_db_model(self):
        """Test creating a Generation from a database model."""
        # Create a mock DB model with the expected attributes
        class MockDbModel:
            id = "gen-456"
            order_id = 10
            model = "stability-ai/sdxl"
            prompt = "A futuristic city at night"
            parameters = {"width": 512, "height": 512, "steps": 25}
            timestamp = datetime(2025, 5, 17, 12, 30, 0)
            status = "completed"
            return_parameters = {"url": "https://example.com/image.png"}
            error = None
        
        db_model = MockDbModel()
        
        # Create a Generation from the DB model
        generation = Generation.from_db_model(db_model)
        
        # Check that attributes were copied correctly
        assert generation.id == "gen-456"
        assert generation.order_id == 10
        assert generation.model == "stability-ai/sdxl"
        assert generation.prompt == "A futuristic city at night"
        assert generation.parameters == {"width": 512, "height": 512, "steps": 25}
        assert generation.timestamp == datetime(2025, 5, 17, 12, 30, 0)
        assert generation.status == GenerationStatus.COMPLETED
        assert generation.return_parameters == {"url": "https://example.com/image.png"}
        assert generation.error is None
    
    def test_failed_generation(self):
        """Test creating a failed generation."""
        # Create a failed generation
        failed_gen = Generation(
            id="gen-fail",
            order_id=7,
            model="stability-ai/sdxl",
            prompt="Test prompt",
            parameters={},
            timestamp=datetime(2025, 5, 17, 12, 0, 0),
            status=GenerationStatus.FAILED,
            return_parameters=None,
            error="API connection error"
        )
        
        # Check attributes
        assert failed_gen.id == "gen-fail"
        assert failed_gen.status == GenerationStatus.FAILED
        assert failed_gen.error == "API connection error"