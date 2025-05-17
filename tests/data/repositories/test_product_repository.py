"""Tests for ProductRepository class."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from datetime import datetime

from imagen_desktop.data.repositories.product_repository import ProductRepository
from imagen_desktop.data.schema import Product as ProductModel
from imagen_desktop.core.models.product import Product, ProductType


class TestProductRepository:
    """Test suite for ProductRepository class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        mock_session = MagicMock()
        
        # Make the session context manager return the session itself
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None
        
        return mock_session
    
    @pytest.fixture
    def mock_db(self, mock_db_session):
        """Create a mock database with session."""
        mock_db = Mock()
        mock_db.get_session.return_value = mock_db_session
        return mock_db, mock_db_session
    
    @pytest.fixture
    def repository(self, mock_db):
        """Create a ProductRepository with a mock database."""
        mock_db_obj, _ = mock_db
        return ProductRepository(mock_db_obj)
    
    @pytest.fixture
    def sample_product_model(self):
        """Create a sample product model for testing."""
        model = Mock(spec=ProductModel)
        model.id = 42
        model.file_path = "/tmp/test.png"
        model.product_type = "image"
        model.generation_id = "gen-123"
        model.created_at = datetime(2025, 5, 17, 12, 0, 0)
        model.width = 512
        model.height = 512
        model.format = "png"
        model.file_size = 1024 * 1024  # 1MB
        model.product_metadata = {"key": "value"}
        return model
    
    def test_model_to_domain(self, repository, sample_product_model):
        """Test conversion from DB model to domain model."""
        # Convert model to domain
        product = repository._model_to_domain(sample_product_model)
        
        # Check all attributes were correctly copied
        assert product.id == 42
        assert product.file_path == Path("/tmp/test.png")
        assert product.product_type == ProductType.IMAGE
        assert product.generation_id == "gen-123"
        assert product.created_at == datetime(2025, 5, 17, 12, 0, 0)
        assert product.width == 512
        assert product.height == 512
        assert product.format == "png"
        assert product.file_size == 1024 * 1024
        assert product.metadata == {"key": "value"}
    
    def test_model_to_domain_with_none_metadata(self, repository):
        """Test conversion from DB model with None metadata."""
        # Create a model with None metadata
        model = Mock(spec=ProductModel)
        model.id = 42
        model.file_path = "/tmp/test.png"
        model.product_type = "image"
        model.generation_id = "gen-123"
        model.created_at = datetime(2025, 5, 17, 12, 0, 0)
        model.width = 512
        model.height = 512
        model.format = "png"
        model.file_size = 1024 * 1024
        model.product_metadata = None
        
        # Convert model to domain
        product = repository._model_to_domain(model)
        
        # Check metadata is an empty dict
        assert product.metadata == {}
    
    @patch("imagen_desktop.data.repositories.product_repository.ProductEventPublisher")
    def test_create_product_success(self, mock_publisher, repository, mock_db):
        """Test create_product with successful creation."""
        _, mock_session = mock_db
        
        # Mock a file_path that "exists"
        mock_file_path = Mock(spec=Path)
        mock_file_path.exists.return_value = True
        mock_file_path.stat.return_value = Mock(st_size=1024 * 1024)
        mock_file_path.__str__ = lambda x: "/tmp/test.png"
        
        # Mock the session operations
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        # Configure the added model to be returned with an ID
        def session_add_side_effect(model):
            model.id = 42
            model.created_at = datetime(2025, 5, 17, 12, 0, 0)
            return None
        
        mock_session.add.side_effect = session_add_side_effect
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger"):
            product = repository.create_product(
                file_path=mock_file_path,
                generation_id="gen-123",
                width=512,
                height=512,
                format="png",
                product_type=ProductType.IMAGE
            )
        
        # Verify that a model was created and added to the session
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Check the created model was passed as an argument
        model_arg = mock_session.add.call_args[0][0]
        assert model_arg.file_path == "/tmp/test.png"
        assert model_arg.product_type == "image"
        assert model_arg.generation_id == "gen-123"
        assert model_arg.width == 512
        assert model_arg.height == 512
        assert model_arg.format == "png"
        
        # Verify event was published
        mock_publisher.publish_product_event.assert_called_once()
        
        # Check the returned product
        assert product is not None
        assert product.id == 42
        assert product.product_type == ProductType.IMAGE
        assert product.generation_id == "gen-123"
        assert product.width == 512
        assert product.height == 512
        assert product.format == "png"
    
    def test_create_product_file_not_found(self, repository):
        """Test create_product with file not found."""
        # Mock a file_path that doesn't exist
        mock_file_path = Mock(spec=Path)
        mock_file_path.exists.return_value = False
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
            product = repository.create_product(file_path=mock_file_path)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "File not found" in mock_logger.error.call_args[0][0]
        
        # Check the returned product
        assert product is None
    
    def test_create_product_exception(self, repository, mock_db):
        """Test create_product with exception."""
        _, mock_session = mock_db
        
        # Mock a file_path that "exists"
        mock_file_path = Mock(spec=Path)
        mock_file_path.exists.return_value = True
        mock_file_path.stat.return_value = Mock(st_size=1024 * 1024)
        
        # Configure the session to raise an exception
        mock_session.add.side_effect = Exception("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
            product = repository.create_product(file_path=mock_file_path)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Check the returned product
        assert product is None
    
    def test_get_product_success(self, repository, sample_product_model):
        """Test get_product with successful retrieval."""
        # Configure the repository to return the sample model
        with patch.object(repository, "get_by_id", return_value=sample_product_model):
            product = repository.get_product(42)
        
        # Check the returned product
        assert product is not None
        assert product.id == 42
        assert product.file_path == Path("/tmp/test.png")
        assert product.product_type == ProductType.IMAGE
    
    def test_get_product_not_found(self, repository):
        """Test get_product with product not found."""
        # Configure the repository to return None
        with patch.object(repository, "get_by_id", return_value=None):
            with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
                product = repository.get_product(42)
                
                # Verify logger was called
                mock_logger.debug.assert_called_once()
                assert "not found" in mock_logger.debug.call_args[0][0]
        
        # Check the returned product
        assert product is None
    
    def test_get_product_exception(self, repository):
        """Test get_product with exception."""
        # Configure the repository to raise an exception
        with patch.object(repository, "get_by_id", side_effect=Exception("Test error")):
            with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
                product = repository.get_product(42)
                
                # Verify logger was called
                mock_logger.error.assert_called_once()
                assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Check the returned product
        assert product is None
    
    def test_get_all_products_success(self, repository, mock_db, sample_product_model):
        """Test get_all_products with successful retrieval."""
        _, mock_session = mock_db
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_product_model, sample_product_model]
        
        # Call the method
        products = repository.get_all_products()
        
        # Verify interactions
        mock_session.query.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
        
        # Check the returned products
        assert len(products) == 2
        assert all(isinstance(p, Product) for p in products)
        assert all(p.id == 42 for p in products)
    
    def test_get_all_products_exception(self, repository, mock_db):
        """Test get_all_products with exception."""
        _, mock_session = mock_db
        
        # Configure the session to raise an exception
        mock_session.query.side_effect = Exception("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
            products = repository.get_all_products()
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Check the returned products
        assert products == []
    
    @patch("imagen_desktop.data.repositories.product_repository.ProductEventPublisher")
    def test_update_product_success(self, mock_publisher, repository, mock_db):
        """Test update_product with successful update."""
        _, mock_session = mock_db
        
        # Create a domain model for updating
        product = Product(
            id=42,
            file_path=Path("/tmp/updated.png"),
            product_type=ProductType.IMAGE,
            generation_id="gen-456",
            created_at=datetime(2025, 5, 17, 12, 0, 0),
            width=1024,
            height=768,
            format="png",
            file_size=2048576,
            metadata={"updated": True}
        )
        
        # Create a mock DB model to be updated
        mock_db_model = Mock(spec=ProductModel)
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.return_value = mock_db_model
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger"):
            result = repository.update_product(product)
        
        # Verify interactions
        mock_session.query.assert_called_once()
        mock_query.get.assert_called_once_with(42)
        mock_session.commit.assert_called_once()
        
        # Check model was updated correctly
        assert mock_db_model.file_path == str(product.file_path)
        assert mock_db_model.product_type == product.product_type.value
        assert mock_db_model.generation_id == product.generation_id
        assert mock_db_model.width == product.width
        assert mock_db_model.height == product.height
        assert mock_db_model.format == product.format
        assert mock_db_model.file_size == product.file_size
        assert mock_db_model.product_metadata == product.metadata
        
        # Verify event was published
        mock_publisher.publish_product_event.assert_called_once()
        
        # Check the result
        assert result is True
    
    def test_update_product_not_found(self, repository, mock_db):
        """Test update_product with product not found."""
        _, mock_session = mock_db
        
        # Create a domain model for updating
        product = Product(
            id=42,
            file_path=Path("/tmp/updated.png"),
            product_type=ProductType.IMAGE,
            generation_id="gen-456",
            created_at=datetime(2025, 5, 17, 12, 0, 0)
        )
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.return_value = None
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
            result = repository.update_product(product)
            
            # Verify logger was called
            mock_logger.debug.assert_called_once()
            assert "not found" in mock_logger.debug.call_args[0][0]
        
        # Check the result
        assert result is False
    
    @patch("imagen_desktop.data.repositories.product_repository.ProductEventPublisher")
    def test_update_product_exception(self, mock_publisher, repository, mock_db):
        """Test update_product with exception."""
        _, mock_session = mock_db
        
        # Create a domain model for updating
        product = Product(
            id=42,
            file_path=Path("/tmp/updated.png"),
            product_type=ProductType.IMAGE,
            generation_id="gen-456",
            created_at=datetime(2025, 5, 17, 12, 0, 0)
        )
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.side_effect = Exception("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
            result = repository.update_product(product)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Verify error event was published
        mock_publisher.publish_product_event.assert_called_once()
        event = mock_publisher.publish_product_event.call_args[0][0]
        assert event.event_type.value == "product.error"
        assert event.data.product == product
        assert isinstance(event.data.error, str)
        assert "Test error" in event.data.error
        
        # Check the result
        assert result is False
    
    @patch("imagen_desktop.data.repositories.product_repository.ProductEventPublisher")
    def test_delete_product_success(self, mock_publisher, repository, mock_db, sample_product_model):
        """Test delete_product with successful deletion."""
        _, mock_session = mock_db
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.return_value = sample_product_model
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger"):
            result = repository.delete_product(42)
        
        # Verify interactions
        mock_session.query.assert_called_once()
        mock_query.get.assert_called_once_with(42)
        mock_session.delete.assert_called_once_with(sample_product_model)
        mock_session.commit.assert_called_once()
        
        # Verify event was published
        mock_publisher.publish_product_event.assert_called_once()
        
        # Check the result
        assert result is True
    
    def test_delete_product_not_found(self, repository, mock_db):
        """Test delete_product with product not found."""
        _, mock_session = mock_db
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.return_value = None
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
            result = repository.delete_product(42)
            
            # Verify logger was called
            mock_logger.debug.assert_called_once()
            assert "not found" in mock_logger.debug.call_args[0][0]
        
        # Check the result
        assert result is False
    
    def test_delete_product_exception(self, repository, mock_db):
        """Test delete_product with exception."""
        _, mock_session = mock_db
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.side_effect = Exception("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.product_repository.logger") as mock_logger:
            result = repository.delete_product(42)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Check the result
        assert result is False