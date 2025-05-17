"""Tests for the Replicate API client."""
import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import responses
from replicate.exceptions import ReplicateError

from imagen_desktop.api.client import ReplicateClient
from imagen_desktop.api.client_core import ReplicateClientCore, APIKeyError


@pytest.fixture
def temp_config():
    """Create a temporary config file with API key."""
    temp_dir = tempfile.TemporaryDirectory()
    config_dir = Path(temp_dir.name) / ".imagen-desktop"
    config_dir.mkdir(parents=True)
    
    config_file = config_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump({"api_key": "test_api_key"}, f)
    
    # Save original home directory
    original_home = os.environ.get("HOME")
    # Set home to temp directory
    os.environ["HOME"] = temp_dir.name
    
    yield temp_dir.name
    
    # Restore original home
    if original_home:
        os.environ["HOME"] = original_home
    else:
        del os.environ["HOME"]
    
    # Clean up
    temp_dir.cleanup()


@pytest.fixture
def mock_replicate_client():
    """Mock Replicate client."""
    with patch("imagen_desktop.api.client_core.replicate.Client") as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock models.get method
        mock_models = MagicMock()
        mock_client_instance.models = mock_models
        
        # Mock models.get and predictions methods
        mock_model = MagicMock()
        mock_models.get.return_value = mock_model
        
        mock_predictions = MagicMock()
        mock_client_instance.predictions = mock_predictions
        
        # Patch replicate module directly
        with patch("imagen_desktop.api.client_core.replicate.models") as mock_replicate_models:
            mock_replicate_models.get.return_value = mock_model
            
            with patch("imagen_desktop.api.client_core.replicate.predictions") as mock_replicate_predictions:
                mock_replicate_predictions.get.return_value = MagicMock()
                mock_replicate_predictions.create.return_value = MagicMock()
                
                yield mock_client_instance


@pytest.mark.api
class TestReplicateClientCore:
    """Tests for the ReplicateClientCore class."""
    
    def test_init_with_env_api_key(self, monkeypatch):
        """Test initializing client with API key from environment."""
        # Set API key in environment
        monkeypatch.setenv("REPLICATE_API_TOKEN", "test_api_key")
        
        # Mock client initialization
        with patch("imagen_desktop.api.client_core.replicate.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Initialize client
            client = ReplicateClientCore(show_ui_errors=False)
            
            # Verify API key was loaded and client initialized
            assert client.api_key == "test_api_key"
            assert client.client is not None
            mock_client.assert_called_once_with(api_token="test_api_key")
    
    def test_init_with_config_file(self, temp_config, monkeypatch):
        """Test initializing client with API key from config file."""
        # Ensure no API key in environment
        monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
        
        # Mock client initialization
        with patch("imagen_desktop.api.client_core.replicate.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Initialize client
            client = ReplicateClientCore(show_ui_errors=False)
            
            # Verify API key was loaded from config and client initialized
            assert client.api_key == "test_api_key"
            assert client.client is not None
            mock_client.assert_called_once_with(api_token="test_api_key")
    
    def test_missing_api_key(self, monkeypatch):
        """Test error when no API key is available."""
        # Ensure no API key in environment
        monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
        
        # Mock empty home directory
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("HOME", temp_dir)
            
            # Test initialization fails
            with pytest.raises(APIKeyError):
                ReplicateClientCore(show_ui_errors=False)
    
    def test_create_prediction(self, mock_replicate_client):
        """Test creating a prediction."""
        # Mock successful prediction with fixed ID
        mock_prediction = MagicMock()
        mock_prediction.id = "pred_123"
        
        # Create client with fully mocked replicate module
        with patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_api_key"}):
            with patch("imagen_desktop.api.client_core.replicate.Client") as mock_client:
                mock_client.return_value = mock_replicate_client
                
                with patch("imagen_desktop.api.client_core.replicate.models.get") as mock_get_model:
                    # Mock the model
                    mock_model = MagicMock()
                    mock_model.latest_version = "version_xyz"
                    mock_get_model.return_value = mock_model
                    
                    with patch("imagen_desktop.api.client_core.replicate.predictions.create") as mock_create:
                        # Set up the mock prediction
                        mock_create.return_value = mock_prediction
                        
                        # Initialize client and create prediction
                        client = ReplicateClientCore(show_ui_errors=False)
                        prediction = client.create_prediction(
                            "stability-ai/sdxl",
                            None,
                            prompt="A beautiful sunset",
                            negative_prompt="ugly, blurry",
                            num_outputs=1
                        )
                        
                        # Verify prediction was created correctly
                        assert prediction.id == "pred_123"
                        mock_create.assert_called_once()
                        
                        # Get the kwargs from the call
                        args, kwargs = mock_create.call_args
                        assert "input" in kwargs
                        assert kwargs["input"]["prompt"] == "A beautiful sunset"
                        assert kwargs["input"]["negative_prompt"] == "ugly, blurry"
                        assert kwargs["input"]["num_outputs"] == 1
    
    def test_get_prediction(self, mock_replicate_client):
        """Test getting a prediction by ID."""
        # Mock successful get prediction
        mock_prediction = MagicMock()
        mock_prediction.id = "pred_123"
        mock_prediction.status = "succeeded"
        
        # Create client with fully mocked replicate module
        with patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_api_key"}):
            with patch("imagen_desktop.api.client_core.replicate.Client") as mock_client:
                mock_client.return_value = mock_replicate_client
                
                with patch("imagen_desktop.api.client_core.replicate.predictions.get") as mock_get:
                    # Set up the mock prediction
                    mock_get.return_value = mock_prediction
                    
                    # Initialize client and get prediction
                    client = ReplicateClientCore(show_ui_errors=False)
                    prediction = client.get_prediction("pred_123")
                    
                    # Verify prediction was retrieved correctly
                    assert prediction.id == "pred_123"
                    assert prediction.status == "succeeded"
                    mock_get.assert_called_once_with("pred_123")
    
    def test_cancel_prediction(self, mock_replicate_client):
        """Test cancelling a prediction."""
        # Mock successful get prediction
        mock_prediction = MagicMock()
        mock_prediction.id = "pred_123"
        
        # Create client with fully mocked replicate module
        with patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_api_key"}):
            with patch("imagen_desktop.api.client_core.replicate.Client") as mock_client:
                mock_client.return_value = mock_replicate_client
                
                with patch("imagen_desktop.api.client_core.replicate.predictions.get") as mock_get:
                    # Set up the mock prediction
                    mock_get.return_value = mock_prediction
                    
                    # Initialize client and cancel prediction
                    client = ReplicateClientCore(show_ui_errors=False)
                    client.cancel_prediction("pred_123")
                    
                    # Verify prediction was cancelled correctly
                    mock_get.assert_called_once_with("pred_123")
                    mock_prediction.cancel.assert_called_once()
    
    def test_client_error_handling(self, mock_replicate_client):
        """Test error handling in client methods."""
        # Create client with fully mocked replicate module
        with patch.dict(os.environ, {"REPLICATE_API_TOKEN": "test_api_key"}):
            with patch("imagen_desktop.api.client_core.replicate.Client") as mock_client:
                mock_client.return_value = mock_replicate_client
                
                with patch("imagen_desktop.api.client_core.replicate.models.get") as mock_get_model:
                    # Mock the model
                    mock_model = MagicMock()
                    mock_model.latest_version = "version_xyz"
                    mock_get_model.return_value = mock_model
                    
                    with patch("imagen_desktop.api.client_core.replicate.predictions.create") as mock_create:
                        # Set up mock to raise error
                        mock_create.side_effect = ReplicateError("API error")
                        
                        # Initialize client
                        client = ReplicateClientCore(show_ui_errors=False)
                        
                        # Test that error is raised
                        with pytest.raises(ReplicateError):
                            client.create_prediction(
                                "stability-ai/sdxl",
                                None,
                                prompt="A beautiful sunset"
                            )


@pytest.mark.api
class TestReplicateClient:
    """Tests for the ReplicateClient class."""
    
    def test_client_initialization(self):
        """Test initializing the client wrapper."""
        with patch("imagen_desktop.api.client.ReplicateClientCore") as mock_core:
            with patch("imagen_desktop.api.client.ReplicateModelManager") as mock_manager:
                # Initialize client
                client = ReplicateClient()
                
                # Verify initialization
                assert client.core is not None
                assert client.model_manager is not None
                mock_core.assert_called_once()
                mock_manager.assert_called_once_with(client.core)
    
    def test_list_available_models(self):
        """Test listing available models."""
        with patch("imagen_desktop.api.client.ReplicateClientCore"):
            with patch("imagen_desktop.api.client.ReplicateModelManager") as mock_manager:
                # Mock model list
                mock_models = [
                    {"name": "SDXL", "owner": "stability-ai", "identifier": "stability-ai/sdxl"},
                    {"name": "DALL-E", "owner": "openai", "identifier": "openai/dall-e"}
                ]
                mock_manager.return_value.list_available_models.return_value = mock_models
                
                # Initialize client and list models
                client = ReplicateClient()
                models = client.list_available_models()
                
                # Verify results
                assert len(models) == 2
                assert models[0]["identifier"] == "stability-ai/sdxl"
                assert models[1]["identifier"] == "openai/dall-e"
                mock_manager.return_value.list_available_models.assert_called_once()
    
    def test_get_model(self):
        """Test getting a specific model."""
        with patch("imagen_desktop.api.client.ReplicateClientCore"):
            with patch("imagen_desktop.api.client.ReplicateModelManager") as mock_manager:
                # Mock model info
                mock_model = {
                    "name": "SDXL",
                    "owner": "stability-ai",
                    "identifier": "stability-ai/sdxl",
                    "description": "A text-to-image model",
                    "latest_version": "v1.0"
                }
                mock_manager.return_value.get_model.return_value = mock_model
                
                # Initialize client and get model
                client = ReplicateClient()
                model = client.get_model("stability-ai/sdxl")
                
                # Verify results
                assert model["identifier"] == "stability-ai/sdxl"
                assert model["name"] == "SDXL"
                assert model["latest_version"] == "v1.0"
                mock_manager.return_value.get_model.assert_called_once_with("stability-ai/sdxl")
    
    def test_create_prediction(self):
        """Test creating a prediction."""
        with patch("imagen_desktop.api.client.ReplicateClientCore") as mock_core:
            mock_core_instance = MagicMock()
            mock_core.return_value = mock_core_instance
            
            # Mock prediction
            mock_prediction = MagicMock()
            mock_prediction.id = "pred_456"
            mock_core_instance.create_prediction.return_value = mock_prediction
            
            # Initialize client with mocks
            with patch("imagen_desktop.api.client.ReplicateModelManager"):
                client = ReplicateClient()
                
                # Create prediction
                prediction = client.create_prediction(
                    "stability-ai/sdxl",
                    "v1.0",
                    prompt="A mountain landscape",
                    negative_prompt="blurry, ugly",
                    num_outputs=1
                )
                
                # Verify results
                assert prediction.id == "pred_456"
                mock_core_instance.create_prediction.assert_called_once_with(
                    "stability-ai/sdxl",
                    "v1.0",
                    prompt="A mountain landscape",
                    negative_prompt="blurry, ugly",
                    num_outputs=1
                )
    
    def test_get_prediction(self):
        """Test getting a prediction."""
        with patch("imagen_desktop.api.client.ReplicateClientCore") as mock_core:
            mock_core_instance = MagicMock()
            mock_core.return_value = mock_core_instance
            
            # Mock prediction
            mock_prediction = MagicMock()
            mock_prediction.id = "pred_789"
            mock_prediction.status = "succeeded"
            mock_core_instance.get_prediction.return_value = mock_prediction
            
            # Initialize client with mocks
            with patch("imagen_desktop.api.client.ReplicateModelManager"):
                client = ReplicateClient()
                
                # Get prediction
                prediction = client.get_prediction("pred_789")
                
                # Verify results
                assert prediction.id == "pred_789"
                assert prediction.status == "succeeded"
                mock_core_instance.get_prediction.assert_called_once_with("pred_789")
    
    def test_cancel_prediction(self):
        """Test cancelling a prediction."""
        with patch("imagen_desktop.api.client.ReplicateClientCore") as mock_core:
            mock_core_instance = MagicMock()
            mock_core.return_value = mock_core_instance
            
            # Initialize client with mocks
            with patch("imagen_desktop.api.client.ReplicateModelManager"):
                client = ReplicateClient()
                
                # Cancel prediction
                client.cancel_prediction("pred_abc")
                
                # Verify the call
                mock_core_instance.cancel_prediction.assert_called_once_with("pred_abc")