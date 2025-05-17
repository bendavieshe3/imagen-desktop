"""Tests for the BaseRepository class."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from imagen_desktop.data.repositories.base_repository import BaseRepository
from imagen_desktop.data.database import Database


class TestBaseRepository:
    """Test cases for the BaseRepository class."""
    
    @pytest.fixture
    def mock_database(self):
        """Create a mock database."""
        mock_db = Mock(spec=Database)
        mock_session = MagicMock()
        mock_db.get_session.return_value = mock_session
        
        # Make the session context manager return the session itself
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None
        
        return mock_db, mock_session
    
    @pytest.fixture
    def repository(self, mock_database):
        """Create a BaseRepository with a mock database."""
        mock_db, _ = mock_database
        return BaseRepository(mock_db)
    
    def test_initialization(self, repository, mock_database):
        """Test repository initialization."""
        mock_db, _ = mock_database
        assert repository.database == mock_db
    
    def test_get_session(self, repository, mock_database):
        """Test _get_session method."""
        mock_db, mock_session = mock_database
        session = repository._get_session()
        
        mock_db.get_session.assert_called_once()
        assert session == mock_session
    
    def test_add_success(self, repository, mock_database):
        """Test add method with successful addition."""
        _, mock_session = mock_database
        
        # Create a mock model
        mock_model = Mock()
        
        # Configure the session mock
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        # Call the method
        result = repository.add(mock_model)
        
        # Verify interactions
        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_model)
        assert result == mock_model
    
    def test_add_failure(self, repository, mock_database):
        """Test add method with failure."""
        _, mock_session = mock_database
        
        # Create a mock model
        mock_model = Mock()
        
        # Configure the session to raise an exception
        mock_session.add.side_effect = SQLAlchemyError("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.base_repository.logger") as mock_logger:
            result = repository.add(mock_model)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Verify result
        assert result is None
    
    def test_get_by_id_success(self, repository, mock_database):
        """Test get_by_id method with successful retrieval."""
        _, mock_session = mock_database
        
        # Create a mock model and class
        mock_model_class = Mock()
        mock_model = Mock()
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.get.return_value = mock_model
        
        # Call the method
        result = repository.get_by_id(mock_model_class, 1)
        
        # Verify interactions
        mock_session.query.assert_called_once_with(mock_model_class)
        mock_query.get.assert_called_once_with(1)
        assert result == mock_model
    
    def test_get_by_id_failure(self, repository, mock_database):
        """Test get_by_id method with failure."""
        _, mock_session = mock_database
        
        # Create a mock model class
        mock_model_class = Mock()
        
        # Configure the session to raise an exception
        mock_session.query.side_effect = SQLAlchemyError("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.base_repository.logger") as mock_logger:
            result = repository.get_by_id(mock_model_class, 1)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Verify result
        assert result is None
    
    def test_update_success(self, repository, mock_database):
        """Test update method with successful update."""
        _, mock_session = mock_database
        
        # Create a mock model
        mock_model = Mock()
        
        # Configure the session mock
        mock_session.merge.return_value = None
        mock_session.commit.return_value = None
        
        # Call the method
        result = repository.update(mock_model)
        
        # Verify interactions
        mock_session.merge.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert result is True
    
    def test_update_failure(self, repository, mock_database):
        """Test update method with failure."""
        _, mock_session = mock_database
        
        # Create a mock model
        mock_model = Mock()
        
        # Configure the session to raise an exception
        mock_session.merge.side_effect = SQLAlchemyError("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.base_repository.logger") as mock_logger:
            result = repository.update(mock_model)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Verify result
        assert result is False
    
    def test_delete_success(self, repository, mock_database):
        """Test delete method with successful deletion."""
        _, mock_session = mock_database
        
        # Create a mock model
        mock_model = Mock()
        
        # Configure the session mock
        mock_session.delete.return_value = None
        mock_session.commit.return_value = None
        
        # Call the method
        result = repository.delete(mock_model)
        
        # Verify interactions
        mock_session.delete.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert result is True
    
    def test_delete_failure(self, repository, mock_database):
        """Test delete method with failure."""
        _, mock_session = mock_database
        
        # Create a mock model
        mock_model = Mock()
        
        # Configure the session to raise an exception
        mock_session.delete.side_effect = SQLAlchemyError("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.base_repository.logger") as mock_logger:
            result = repository.delete(mock_model)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Verify result
        assert result is False
    
    def test_list_all_success(self, repository, mock_database):
        """Test list_all method with successful retrieval."""
        _, mock_session = mock_database
        
        # Create mock models and class
        mock_model_class = Mock()
        mock_models = [Mock(), Mock()]
        
        # Configure the query mock
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = mock_models
        
        # Call the method
        result = repository.list_all(mock_model_class)
        
        # Verify interactions
        mock_session.query.assert_called_once_with(mock_model_class)
        mock_query.all.assert_called_once()
        assert result == mock_models
    
    def test_list_all_failure(self, repository, mock_database):
        """Test list_all method with failure."""
        _, mock_session = mock_database
        
        # Create a mock model class
        mock_model_class = Mock()
        
        # Configure the session to raise an exception
        mock_session.query.side_effect = SQLAlchemyError("Test error")
        
        # Call the method
        with patch("imagen_desktop.data.repositories.base_repository.logger") as mock_logger:
            result = repository.list_all(mock_model_class)
            
            # Verify logger was called
            mock_logger.error.assert_called_once()
            assert "Test error" in mock_logger.error.call_args[0][0]
        
        # Verify result
        assert result == []