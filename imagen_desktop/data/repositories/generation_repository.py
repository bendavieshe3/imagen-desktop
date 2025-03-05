"""Repository for generation management."""
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from imagen_desktop.data.repositories.base_repository import BaseRepository
from imagen_desktop.data.schema import Generation as GenerationModel
from imagen_desktop.data.schema import Product as ProductModel
from imagen_desktop.core.models.generation import Generation, GenerationStatus
from imagen_desktop.utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class GenerationRepository(BaseRepository):
    """Repository for handling generation data."""
    
    def create_generation(self, 
                         prediction_id: str,
                         order_id: int,
                         model: str,
                         prompt: str,
                         parameters: Dict[str, Any],
                         status: GenerationStatus = GenerationStatus.STARTING) -> Optional[Generation]:
        """
        Create a new generation record.
        
        Args:
            prediction_id: Unique identifier for the generation
            order_id: ID of the parent order
            model: Model identifier used for generation
            prompt: Text prompt used
            parameters: Generation parameters
            status: Initial status for the generation
            
        Returns:
            Created Generation or None if creation failed
        """
        try:
            generation_model = GenerationModel(
                id=prediction_id,
                order_id=order_id,
                model=model,
                prompt=prompt,
                parameters=parameters,
                status=status.value,
                timestamp=datetime.utcnow()
            )
            
            result = self.add(generation_model)
            if result:
                logger.debug(f"Created generation {prediction_id} with status {status.value}")
                return Generation.from_db_model(result)
            
            logger.error(f"Failed to create generation {prediction_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error creating generation: {e}")
            return None
    
    def get_generation(self, prediction_id: str) -> Optional[Generation]:
        """
        Get a generation by ID.
        
        Args:
            prediction_id: Generation ID
            
        Returns:
            Generation or None if not found
        """
        try:
            generation_model = self.get_by_id(GenerationModel, prediction_id)
            if generation_model:
                return Generation.from_db_model(generation_model)
            return None
        except Exception as e:
            logger.error(f"Error getting generation {prediction_id}: {e}")
            return None
    
    def get_generation_with_products(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a generation with its products.
        
        Args:
            prediction_id: Generation ID
            
        Returns:
            Dict containing generation and products
        """
        try:
            with self._get_session() as session:
                generation_model = session.query(GenerationModel)\
                    .options(joinedload(GenerationModel.products))\
                    .filter(GenerationModel.id == prediction_id)\
                    .first()
                
                if not generation_model:
                    return None
                
                generation = Generation.from_db_model(generation_model)
                
                # Extract products
                products = []
                for prod_model in generation_model.products:
                    from imagen_desktop.core.models.product import Product as ProdDomain
                    prod = ProdDomain.from_db_model(prod_model)
                    products.append(prod)
                
                return {
                    'generation': generation,
                    'products': products
                }
                
        except Exception as e:
            logger.error(f"Error getting generation with products {prediction_id}: {e}")
            return None
    
    def update_generation_status(self, 
                              prediction_id: str, 
                              status: GenerationStatus,
                              error: Optional[str] = None) -> bool:
        """
        Update the status of a generation.
        
        Args:
            prediction_id: ID of the generation to update
            status: New generation status
            error: Optional error message
            
        Returns:
            True if update was successful
        """
        try:
            with self._get_session() as session:
                generation_model = session.query(GenerationModel)\
                    .filter(GenerationModel.id == prediction_id)\
                    .first()
                
                if generation_model:
                    generation_model.status = status.value
                    if error:
                        generation_model.error = error
                    session.commit()
                    logger.debug(f"Updated generation {prediction_id} status to {status.value}")
                    return True
                
                logger.warning(f"Generation {prediction_id} not found for status update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating generation status: {e}")
            return False
    
    def update_generation_return_parameters(self,
                                         prediction_id: str,
                                         return_parameters: Dict[str, Any]) -> bool:
        """
        Update the return parameters of a generation.
        
        Args:
            prediction_id: ID of the generation
            return_parameters: Parameters returned by the API
            
        Returns:
            True if update was successful
        """
        try:
            with self._get_session() as session:
                generation_model = session.query(GenerationModel)\
                    .filter(GenerationModel.id == prediction_id)\
                    .first()
                
                if generation_model:
                    generation_model.return_parameters = return_parameters
                    session.commit()
                    logger.debug(f"Updated return parameters for generation {prediction_id}")
                    return True
                
                logger.warning(f"Generation {prediction_id} not found for parameter update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating generation return parameters: {e}")
            return False
    
    def list_generations_by_order(self, 
                               order_id: int,
                               status: Optional[GenerationStatus] = None) -> List[Generation]:
        """
        List generations for an order.
        
        Args:
            order_id: Order ID
            status: Optional status filter
            
        Returns:
            List of Generation objects
        """
        try:
            with self._get_session() as session:
                query = session.query(GenerationModel)\
                    .filter(GenerationModel.order_id == order_id)
                
                if status:
                    query = query.filter(GenerationModel.status == status.value)
                
                query = query.order_by(desc(GenerationModel.timestamp))
                generation_models = query.all()
                
                generations = [Generation.from_db_model(model) for model in generation_models]
                logger.debug(f"Retrieved {len(generations)} generations for order {order_id}")
                return generations
                
        except Exception as e:
            logger.error(f"Error listing generations for order {order_id}: {e}")
            return []
    
    def list_generations(self, 
                      limit: Optional[int] = None,
                      status: Optional[GenerationStatus] = None) -> List[Generation]:
        """
        List generations with optional filtering.
        
        Args:
            limit: Maximum number of generations to return
            status: Filter by generation status
            
        Returns:
            List of Generation objects
        """
        try:
            with self._get_session() as session:
                query = session.query(GenerationModel)
                
                # Apply filters
                if status:
                    query = query.filter(GenerationModel.status == status.value)
                
                # Apply ordering and limit
                query = query.order_by(desc(GenerationModel.timestamp))
                
                if limit:
                    query = query.limit(limit)
                
                generation_models = query.all()
                
                # Convert to domain models
                generations = [Generation.from_db_model(model) for model in generation_models]
                
                logger.debug(f"Retrieved {len(generations)} generations")
                return generations
                
        except Exception as e:
            logger.error(f"Error listing generations: {e}")
            return []
    
    def count_generations_by_status(self) -> Dict[str, int]:
        """
        Count generations by status.
        
        Returns:
            Dictionary mapping status values to counts
        """
        try:
            with self._get_session() as session:
                result = {}
                
                # Count by status
                counts = session.query(
                    GenerationModel.status,
                    session.func.count(GenerationModel.id)
                ).group_by(GenerationModel.status).all()
                
                # Convert to dict
                for status, count in counts:
                    result[status] = count
                
                logger.debug(f"Generation counts by status: {result}")
                return result
                
        except Exception as e:
            logger.error(f"Error counting generations by status: {e}")
            return {}