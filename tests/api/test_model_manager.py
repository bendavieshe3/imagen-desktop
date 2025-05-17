"""Tests for the ReplicateModelManager."""
import pytest
from unittest.mock import patch, MagicMock

from imagen_desktop.api.model_manager import ReplicateModelManager


@pytest.fixture
def mock_core_client():
    """Create a mock ReplicateClientCore."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def model_manager(mock_core_client):
    """Create a ReplicateModelManager with a mock client."""
    return ReplicateModelManager(mock_core_client)


@pytest.mark.api
class TestReplicateModelManager:
    """Tests for the ReplicateModelManager class."""
    
    def test_initialization(self, mock_core_client):
        """Test model manager initialization."""
        manager = ReplicateModelManager(mock_core_client)
        assert manager.client == mock_core_client
    
    def test_categorize_model(self, model_manager):
        """Test model categorization logic."""
        # Test fast model detection
        assert "🚀 Fast generation model." in model_manager._categorize_model("luma/flash-model")
        assert "🚀 Fast generation model." in model_manager._categorize_model("some/lightning-model")
        assert "🚀 Fast generation model." in model_manager._categorize_model("model/turbo-generator")
        assert "🚀 Fast generation model." in model_manager._categorize_model("ssd-model/v1")
        
        # Test high quality model detection
        assert "✨ High quality model." in model_manager._categorize_model("model/pro-version")
        assert "✨ High quality model." in model_manager._categorize_model("large-model/v1")
        assert "✨ High quality model." in model_manager._categorize_model("luma/photon")
        
        # Test text rendering model detection
        assert "📝 Excellent text rendering." in model_manager._categorize_model("ideogram/v1")
        
        # Test aesthetic model detection
        assert "🎨 Aesthetic focused." in model_manager._categorize_model("aesthetic-model/v1")
        
        # Test default (no category)
        assert model_manager._categorize_model("generic-model/v1") == ""
    
    def test_list_available_models(self, model_manager):
        """Test listing available models."""
        # Mock the replicate.models.get method
        with patch("imagen_desktop.api.model_manager.replicate.models.get") as mock_get:
            # Create mock models with necessary attributes
            mock_models = []
            
            for i, model_string in enumerate(model_manager.FEATURED_MODELS):
                model_id, version = model_string.split(':')
                owner, name = model_id.split('/')
                
                mock_model = MagicMock()
                mock_model.name = name
                mock_model.owner = owner
                mock_model.description = f"Description for {name}"
                
                mock_get.return_value = mock_model
                mock_models.append(mock_model)
            
            # Set up mock_get to return the appropriate model based on the input
            def get_model(model_id):
                for model_string in model_manager.FEATURED_MODELS:
                    if model_string.startswith(model_id):
                        owner, name = model_id.split('/')
                        mock_model = MagicMock()
                        mock_model.name = name
                        mock_model.owner = owner
                        mock_model.description = f"Description for {name}"
                        return mock_model
                raise ValueError(f"Model {model_id} not found")
            
            mock_get.side_effect = get_model
            
            # Call the method to test
            models = model_manager.list_available_models()
            
            # Verify results
            assert len(models) == len(model_manager.FEATURED_MODELS)
            
            # Check a few specific models
            for model in models:
                assert "identifier" in model
                assert "name" in model
                assert "owner" in model
                assert "description" in model
                assert "version" in model
                assert model["featured"] is True
                
                # Check categorization
                if "flash" in model["identifier"].lower():
                    assert "🚀 Fast generation model." in model["description"]
                elif "photon" in model["identifier"].lower():
                    assert "✨ High quality model." in model["description"]
    
    def test_list_models_with_api_error(self, model_manager):
        """Test handling of API errors when listing models."""
        # Mock the replicate.models.get method to raise an exception
        with patch("imagen_desktop.api.model_manager.replicate.models.get") as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            # Call the method to test
            models = model_manager.list_available_models()
            
            # Verify results
            assert models == []
    
    def test_get_model(self, model_manager):
        """Test getting a specific model."""
        # Mock the replicate.models.get method
        with patch("imagen_desktop.api.model_manager.replicate.models.get") as mock_get:
            # Create a mock model
            mock_model = MagicMock()
            mock_model.name = "sdxl"
            mock_model.owner = "stability-ai"
            mock_model.description = "A powerful text-to-image model"
            
            # Mock the latest_version property
            mock_version = MagicMock()
            mock_version.id = "v1.0.0"
            mock_model.latest_version = mock_version
            
            mock_get.return_value = mock_model
            
            # Call the method to test
            model_info = model_manager.get_model("stability-ai/sdxl")
            
            # Verify results
            assert model_info["name"] == "sdxl"
            assert model_info["owner"] == "stability-ai"
            assert model_info["description"] == "A powerful text-to-image model"
            assert model_info["identifier"] == "stability-ai/sdxl"
            assert model_info["latest_version"] == "v1.0.0"
            
            # Verify the correct model ID was used
            mock_get.assert_called_once_with("stability-ai/sdxl")
    
    def test_get_model_invalid_id(self, model_manager):
        """Test error handling for invalid model IDs."""
        # Test with invalid model ID (no slash)
        with pytest.raises(ValueError, match="Invalid model identifier"):
            model_manager.get_model("invalidmodel")
    
    def test_get_model_api_error(self, model_manager):
        """Test handling of API errors when getting a model."""
        # Mock the replicate.models.get method to raise an exception
        with patch("imagen_desktop.api.model_manager.replicate.models.get") as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            # Call the method to test
            with pytest.raises(Exception, match="API Error"):
                model_manager.get_model("stability-ai/sdxl")