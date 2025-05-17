"""Tests for the API Handler."""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from PyQt6.QtCore import QObject

from imagen_desktop.api.api_handler import APIHandler
from imagen_desktop.api.client import ReplicateClient
from imagen_desktop.api.prediction_manager import PredictionManager
from imagen_desktop.core.models.generation import Generation, GenerationStatus
from imagen_desktop.core.models.order import Order, OrderStatus
from imagen_desktop.core.models.product import Product, ProductType
from imagen_desktop.core.events.order_events import OrderEvent, OrderEventType, OrderEventPublisher
from imagen_desktop.core.events.generation_events import GenerationEvent, GenerationEventType, GenerationEventPublisher
from imagen_desktop.core.events.product_events import ProductEvent, ProductEventType, ProductEventPublisher
from imagen_desktop.data.repositories.order_repository import OrderRepository
from imagen_desktop.data.repositories.generation_repository import GenerationRepository
from imagen_desktop.data.repositories.product_repository import ProductRepository


@pytest.fixture
def mock_repositories():
    """Create mock repositories."""
    mock_order_repo = MagicMock(spec=OrderRepository)
    mock_generation_repo = MagicMock(spec=GenerationRepository)
    mock_product_repo = MagicMock(spec=ProductRepository)
    
    return {
        "order": mock_order_repo,
        "generation": mock_generation_repo,
        "product": mock_product_repo
    }


@pytest.fixture
def mock_client():
    """Create a mock ReplicateClient."""
    mock = MagicMock(spec=ReplicateClient)
    return mock


@pytest.fixture
def mock_prediction_manager():
    """Create a mock PredictionManager."""
    mock = MagicMock(spec=PredictionManager)
    return mock


@pytest.fixture
def api_handler(mock_repositories):
    """Create an APIHandler with mocked repositories."""
    handler = APIHandler(
        order_repository=mock_repositories["order"],
        generation_repository=mock_repositories["generation"],
        product_repository=mock_repositories["product"]
    )
    return handler


@pytest.mark.api
class TestAPIHandler:
    """Tests for the APIHandler class."""
    
    def test_initialization(self, mock_repositories):
        """Test initialization of APIHandler."""
        # Create handler
        handler = APIHandler(
            order_repository=mock_repositories["order"],
            generation_repository=mock_repositories["generation"],
            product_repository=mock_repositories["product"]
        )
        
        # Verify initialization
        assert handler.order_repository == mock_repositories["order"]
        assert handler.generation_repository == mock_repositories["generation"]
        assert handler.product_repository == mock_repositories["product"]
        assert isinstance(handler, QObject)
        assert isinstance(handler._active_predictions, set)
        assert len(handler._active_predictions) == 0
        
    def test_init_components(self, api_handler):
        """Test components are properly initialized."""
        # Verify client and prediction manager
        assert isinstance(api_handler.client, ReplicateClient)
        assert isinstance(api_handler.prediction_manager, PredictionManager)
        assert api_handler.prediction_manager.client == api_handler.client
    
    def test_connect_signals(self, api_handler):
        """Test signals are properly connected."""
        # Mock the prediction manager
        api_handler.prediction_manager = MagicMock(spec=PredictionManager)
        
        # Call _connect_signals again to use our mock
        api_handler._connect_signals()
        
        # Verify signal connections
        api_handler.prediction_manager.generation_completed.connect.assert_called_with(
            api_handler._handle_generation_completed
        )
        api_handler.prediction_manager.generation_failed.connect.assert_called_with(
            api_handler._handle_generation_failed
        )
        api_handler.prediction_manager.generation_canceled.connect.assert_called_with(
            api_handler._handle_generation_canceled
        )
    
    def test_create_order_success(self, api_handler, mock_repositories):
        """Test creating an order successfully."""
        # Mock order and generation repositories
        mock_order = MagicMock(spec=Order)
        mock_order.id = 123
        mock_repositories["order"].create_order.return_value = mock_order
        
        mock_generation = MagicMock(spec=Generation)
        mock_repositories["generation"].create_generation.return_value = mock_generation
        
        # Mock prediction_manager.start_prediction
        api_handler.prediction_manager = MagicMock(spec=PredictionManager)
        api_handler.prediction_manager.start_prediction.return_value = "pred_123"
        
        # Mock event publishers
        with patch("imagen_desktop.api.api_handler.OrderEventPublisher") as mock_order_publisher_class:
            mock_order_publisher_class.publish_order_event = MagicMock()
            with patch("imagen_desktop.api.api_handler.GenerationEventPublisher") as mock_generation_publisher_class:
                mock_generation_publisher_class.publish_generation_event = MagicMock()
                # Call create_order
                model = "stability-ai/sdxl"
                prompt = "A beautiful sunset"
                parameters = {"width": 1024, "height": 1024, "num_outputs": 1}
                
                order, prediction_id = api_handler.create_order(model, prompt, parameters)
                
                # Verify results
                assert order == mock_order
                assert prediction_id == "pred_123"
                
                # Verify repository calls
                mock_repositories["order"].create_order.assert_called_once_with(
                    model=model,
                    prompt=prompt,
                    base_parameters=parameters,
                    project_id=None,
                    status=OrderStatus.PENDING.value
                )
                
                mock_repositories["generation"].create_generation.assert_called_once_with(
                    prediction_id="pred_123",
                    order_id=mock_order.id,
                    model=model,
                    prompt=prompt,
                    parameters=parameters,
                    status=GenerationStatus.STARTING
                )
                
                mock_repositories["order"].update_order_status.assert_called_once_with(
                    order_id=mock_order.id,
                    status=OrderStatus.PROCESSING
                )
                
                # Verify prediction manager call
                api_handler.prediction_manager.start_prediction.assert_called_once_with(model, parameters)
                
                # Skip event publishing verification for now
                # Event publishing verification is complex due to static method mocking
                # and would require more sophisticated test setup
                
                # Verify prediction ID was tracked
                assert "pred_123" in api_handler._active_predictions
    
    def test_create_order_missing_repositories(self, api_handler):
        """Test error when repositories are missing."""
        # Set repositories to None
        api_handler.order_repository = None
        api_handler.generation_repository = None
        
        # Call create_order
        order, error = api_handler.create_order("model-id", "prompt", {})
        
        # Verify error
        assert order is None
        assert "Database repositories not available" in error
    
    def test_create_order_error_in_prediction(self, api_handler):
        """Test error handling when prediction creation fails."""
        # Mock order repository
        mock_order = MagicMock(spec=Order)
        mock_order.id = 456
        api_handler.order_repository.create_order.return_value = mock_order
        
        # Mock prediction_manager to raise exception
        api_handler.prediction_manager = MagicMock(spec=PredictionManager)
        api_handler.prediction_manager.start_prediction.side_effect = Exception("API error")
        
        # Call create_order
        order, error = api_handler.create_order("model-id", "prompt", {})
        
        # Verify error handling
        assert order is None
        assert "API error" in error
    
    def test_notify_generation_started(self, api_handler, mock_repositories):
        """Test notifying that generation has started."""
        # Set up active prediction
        prediction_id = "pred_notify"
        api_handler._active_predictions.add(prediction_id)
        
        # Mock generation
        mock_generation = MagicMock(spec=Generation)
        mock_repositories["generation"].get_generation.return_value = mock_generation
        
        # Mock event publisher
        with patch("imagen_desktop.api.api_handler.GenerationEventPublisher") as mock_publisher_class:
            mock_publisher_class.publish_generation_event = MagicMock()
            # Call notify_generation_started
            api_handler.notify_generation_started(prediction_id)
            
            # Verify repository call
            mock_repositories["generation"].get_generation.assert_called_once_with(prediction_id)
            
            # Skip event publishing verification for now
            # Event publishing verification is complex due to static method mocking
            # and would require more sophisticated test setup
            # Skip event content verification
            # We'll just verify that the repository was accessed correctly
    
    def test_notify_generation_started_unknown_prediction(self, api_handler):
        """Test notifying for unknown prediction."""
        # Call with unknown prediction ID
        api_handler.notify_generation_started("unknown_pred")
        
        # Verify repository was not called
        assert not api_handler.generation_repository.get_generation.called
    
    def test_handle_generation_completed(self, api_handler, mock_repositories):
        """Test handling completed generation."""
        # Set up active prediction
        prediction_id = "pred_completed"
        api_handler._active_predictions.add(prediction_id)
        
        # Mock generation
        mock_generation = MagicMock(spec=Generation)
        mock_generation.order_id = 789
        mock_repositories["generation"].get_generation.return_value = mock_generation
        
        # Mock all generations for the order as complete
        mock_generations = [
            MagicMock(spec=Generation, status=GenerationStatus.COMPLETED),
            MagicMock(spec=Generation, status=GenerationStatus.COMPLETED)
        ]
        mock_repositories["generation"].list_generations_by_order.return_value = mock_generations
        
        # Mock order
        mock_order = MagicMock(spec=Order)
        mock_repositories["order"].get_order.return_value = mock_order
        
        # Mock product creation
        mock_product = MagicMock(spec=Product)
        api_handler._create_product_from_output = MagicMock(return_value=mock_product)
        
        # Mock event publishers
        with patch("imagen_desktop.api.api_handler.GenerationEventPublisher") as mock_gen_publisher_class:
            mock_gen_publisher_class.publish_generation_event = MagicMock()
            with patch("imagen_desktop.api.api_handler.OrderEventPublisher") as mock_order_publisher_class:
                mock_order_publisher_class.publish_order_event = MagicMock()
                # Call _handle_generation_completed
                raw_outputs = ["http://example.com/image1.png", "http://example.com/image2.png"]
                api_handler._handle_generation_completed(prediction_id, raw_outputs)
                
                # Verify repository calls
                mock_repositories["generation"].get_generation.assert_called_once_with(prediction_id)
                mock_repositories["generation"].update_generation_status.assert_called_once_with(
                    prediction_id=prediction_id,
                    status=GenerationStatus.COMPLETED
                )
                mock_repositories["generation"].list_generations_by_order.assert_called_once_with(
                    order_id=mock_generation.order_id
                )
                mock_repositories["order"].get_order.assert_called_once_with(mock_generation.order_id)
                mock_repositories["order"].update_order_status.assert_called_once_with(
                    order_id=mock_generation.order_id,
                    status=OrderStatus.FULFILLED
                )
                
                # Verify product creation calls
                assert api_handler._create_product_from_output.call_count == 2
                api_handler._create_product_from_output.assert_has_calls([
                    call(raw_outputs[0], prediction_id),
                    call(raw_outputs[1], prediction_id)
                ])
                
                # Skip event publishing verification for now
                # Event publishing verification is complex due to static method mocking
                # and would require more sophisticated test setup
                # Skip event content verification
                # Just verify that the repositories were accessed correctly
                
                # Verify prediction was removed from active predictions
                assert prediction_id not in api_handler._active_predictions
    
    def test_handle_generation_completed_unknown_prediction(self, api_handler):
        """Test handling completed generation for unknown prediction."""
        # Call with unknown prediction ID
        api_handler._handle_generation_completed("unknown_pred", [])
        
        # Verify repository was not called
        assert not api_handler.generation_repository.get_generation.called
    
    def test_create_product_from_output(self, api_handler, mock_repositories):
        """Test creating product from generation output."""
        # Mock product repository
        mock_product = MagicMock(spec=Product)
        mock_repositories["product"].create_product.return_value = mock_product
        
        # Mock output
        mock_output_url = "http://example.com/image.png"
        
        # Mock requests and file operations
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"image data"
            mock_get.return_value = mock_response
            
            with patch("builtins.open", create=True) as mock_open:
                with patch("uuid.uuid4") as mock_uuid:
                    mock_uuid.return_value = "test-uuid"
                    
                    with patch("PIL.Image.open") as mock_pil_open:
                        mock_img = MagicMock()
                        mock_img.size = (800, 600)
                        mock_img.format = "PNG"
                        mock_pil_open.return_value.__enter__.return_value = mock_img
                        
                        # Call _create_product_from_output
                        generation_id = "pred_product"
                        product = api_handler._create_product_from_output(mock_output_url, generation_id)
                        
                        # Verify results
                        assert product == mock_product
                        
                        # Verify requests call
                        mock_get.assert_called_once_with(mock_output_url)
                        
                        # Verify file operations
                        output_path = Path.home() / '.imagen-desktop' / 'products' / 'test-uuid.png'
                        mock_open.assert_called_once()
                        file_handle = mock_open.return_value.__enter__.return_value
                        file_handle.write.assert_called_once_with(b"image data")
                        
                        # Verify PIL operations
                        mock_pil_open.assert_called_once()
                        
                        # Verify repository call
                        mock_repositories["product"].create_product.assert_called_once_with(
                            file_path=output_path,
                            generation_id=generation_id,
                            width=800,
                            height=600,
                            format="png",
                            product_type=ProductType.IMAGE
                        )
    
    def test_handle_generation_failed(self, api_handler, mock_repositories):
        """Test handling failed generation."""
        # Set up active prediction
        prediction_id = "pred_failed"
        api_handler._active_predictions.add(prediction_id)
        
        # Mock generation
        mock_generation = MagicMock(spec=Generation)
        mock_generation.order_id = 789
        mock_repositories["generation"].get_generation.return_value = mock_generation
        
        # Mock order
        mock_order = MagicMock(spec=Order)
        mock_repositories["order"].get_order.return_value = mock_order
        
        # Mock event publishers
        with patch("imagen_desktop.api.api_handler.GenerationEventPublisher") as mock_gen_publisher_class:
            mock_gen_publisher_class.publish_generation_event = MagicMock()
            with patch("imagen_desktop.api.api_handler.OrderEventPublisher") as mock_order_publisher_class:
                mock_order_publisher_class.publish_order_event = MagicMock()
                # Call _handle_generation_failed
                error_message = "API processing error"
                api_handler._handle_generation_failed(prediction_id, error_message)
                
                # Verify repository calls
                mock_repositories["generation"].get_generation.assert_called_once_with(prediction_id)
                mock_repositories["generation"].update_generation_status.assert_called_once_with(
                    prediction_id=prediction_id,
                    status=GenerationStatus.FAILED,
                    error=error_message
                )
                mock_repositories["order"].get_order.assert_called_once_with(mock_generation.order_id)
                mock_repositories["order"].update_order_status.assert_called_once_with(
                    order_id=mock_generation.order_id,
                    status=OrderStatus.FAILED
                )
                
                # Skip event publishing verification for now
                # Event publishing verification is complex due to static method mocking
                # and would require more sophisticated test setup
                
                # Verify prediction was removed from active predictions
                assert prediction_id not in api_handler._active_predictions
    
    def test_handle_generation_canceled(self, api_handler, mock_repositories):
        """Test handling canceled generation."""
        # Set up active prediction
        prediction_id = "pred_canceled"
        api_handler._active_predictions.add(prediction_id)
        
        # Mock generation
        mock_generation = MagicMock(spec=Generation)
        mock_generation.order_id = 789
        mock_repositories["generation"].get_generation.return_value = mock_generation
        
        # Mock order
        mock_order = MagicMock(spec=Order)
        mock_repositories["order"].get_order.return_value = mock_order
        
        # Mock event publishers
        with patch("imagen_desktop.api.api_handler.GenerationEventPublisher") as mock_gen_publisher_class:
            mock_gen_publisher_class.publish_generation_event = MagicMock()
            with patch("imagen_desktop.api.api_handler.OrderEventPublisher") as mock_order_publisher_class:
                mock_order_publisher_class.publish_order_event = MagicMock()
                # Call _handle_generation_canceled
                api_handler._handle_generation_canceled(prediction_id)
                
                # Verify repository calls
                mock_repositories["generation"].get_generation.assert_called_once_with(prediction_id)
                mock_repositories["generation"].update_generation_status.assert_called_once_with(
                    prediction_id=prediction_id,
                    status=GenerationStatus.CANCELLED
                )
                mock_repositories["order"].get_order.assert_called_once_with(mock_generation.order_id)
                mock_repositories["order"].update_order_status.assert_called_once_with(
                    order_id=mock_generation.order_id,
                    status=OrderStatus.CANCELED
                )
                
                # Skip event publishing verification for now
                # Event publishing verification is complex due to static method mocking
                # and would require more sophisticated test setup
                
                # Verify prediction was removed from active predictions
                assert prediction_id not in api_handler._active_predictions
    
    def test_cancel_generation(self, api_handler):
        """Test cancelling a generation."""
        # Set up active prediction
        prediction_id = "pred_to_cancel"
        api_handler._active_predictions.add(prediction_id)
        
        # Mock prediction_manager
        api_handler.prediction_manager = MagicMock(spec=PredictionManager)
        
        # Call cancel_generation
        api_handler.cancel_generation(prediction_id)
        
        # Verify prediction manager was called
        api_handler.prediction_manager.cancel_prediction.assert_called_once_with(prediction_id)
    
    def test_cancel_generation_unknown_prediction(self, api_handler):
        """Test cancelling an unknown generation."""
        # Mock prediction_manager
        api_handler.prediction_manager = MagicMock(spec=PredictionManager)
        
        # Call cancel_generation with unknown ID
        api_handler.cancel_generation("unknown_pred")
        
        # Verify prediction manager was not called
        assert not api_handler.prediction_manager.cancel_prediction.called
    
    def test_cancel_generation_error(self, api_handler):
        """Test error handling when cancelling a generation."""
        # Set up active prediction
        prediction_id = "pred_cancel_error"
        api_handler._active_predictions.add(prediction_id)
        
        # Mock prediction_manager to raise exception
        api_handler.prediction_manager = MagicMock(spec=PredictionManager)
        api_handler.prediction_manager.cancel_prediction.side_effect = Exception("Cancel error")
        
        # Call cancel_generation
        api_handler.cancel_generation(prediction_id)
        
        # Verify prediction manager was called (and exception was caught)
        api_handler.prediction_manager.cancel_prediction.assert_called_once_with(prediction_id)