"""Repository for order management."""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from imagen_desktop.data.repositories.base_repository import BaseRepository
from imagen_desktop.data.schema import Order as OrderModel
from imagen_desktop.data.schema import Generation, Product
from imagen_desktop.core.models.order import Order, OrderStatus
from imagen_desktop.utils.debug_logger import LogManager

logger = LogManager.get_logger(__name__)

class OrderRepository(BaseRepository):
    """Repository for handling order data."""
    
    def create_order(self, 
                    model: str,
                    prompt: str,
                    base_parameters: Dict[str, Any],
                    project_id: Optional[int] = None,
                    status: str = OrderStatus.PENDING) -> Optional[Order]:
        """
        Create a new order record.
        
        Args:
            model: Model identifier
            prompt: Primary prompt text
            base_parameters: Complete parameter set for order
            project_id: Optional project association
            status: Initial order status
        
        Returns:
            Created Order or None if creation failed
        """
        try:
            order_model = OrderModel(
                model=model,
                prompt=prompt,
                base_parameters=base_parameters,
                project_id=project_id,
                status=status,
                created_at=datetime.utcnow()
            )
            
            result = self.add(order_model)
            if result:
                logger.info(f"Created order {result.id}")
                return Order.from_db_model(result)
            
            logger.error("Failed to create order")
            return None
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """
        Get an order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order or None if not found
        """
        try:
            order_model = self.get_by_id(OrderModel, order_id)
            if order_model:
                return Order.from_db_model(order_model)
            return None
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None
    
    def get_order_with_relations(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an order with its generations and products.
        
        Args:
            order_id: Order ID
            
        Returns:
            Dict containing order, generations, and products
        """
        try:
            with self._get_session() as session:
                order_model = session.query(OrderModel)\
                    .options(
                        joinedload(OrderModel.generations)
                        .joinedload(Generation.products)
                    )\
                    .filter(OrderModel.id == order_id)\
                    .first()
                
                if not order_model:
                    return None
                
                # Build comprehensive result
                order = Order.from_db_model(order_model)
                
                # Extract generations
                generations = []
                products = []
                
                for gen_model in order_model.generations:
                    # Add generation
                    from imagen_desktop.core.models.generation import Generation as GenDomain
                    gen = GenDomain.from_db_model(gen_model)
                    generations.append(gen)
                    
                    # Add products
                    for prod_model in gen_model.products:
                        from imagen_desktop.core.models.product import Product as ProdDomain
                        prod = ProdDomain.from_db_model(prod_model)
                        products.append(prod)
                
                return {
                    'order': order,
                    'generations': generations,
                    'products': products
                }
                
        except Exception as e:
            logger.error(f"Error getting order with relations {order_id}: {e}")
            return None
    
    def update_order_status(self, 
                           order_id: int,
                           status: OrderStatus) -> bool:
        """
        Update the status of an order.
        
        Args:
            order_id: ID of the order to update
            status: New order status
            
        Returns:
            True if update was successful
        """
        try:
            with self._get_session() as session:
                order_model = session.query(OrderModel)\
                    .filter(OrderModel.id == order_id)\
                    .first()
                if order_model:
                    order_model.status = status.value
                    session.commit()
                    logger.debug(f"Updated order {order_id} status to {status.value}")
                    return True
                
                logger.warning(f"Order {order_id} not found for status update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False
    
    def list_orders(self,
                   limit: Optional[int] = None,
                   status: Optional[OrderStatus] = None,
                   project_id: Optional[int] = None) -> List[Order]:
        """
        List orders with optional filtering.
        
        Args:
            limit: Maximum number of orders to return
            status: Filter by order status
            project_id: Filter by project
            
        Returns:
            List of matching Order objects
        """
        try:
            with self._get_session() as session:
                query = session.query(OrderModel)
                
                # Apply filters
                if status:
                    query = query.filter(OrderModel.status == status.value)
                
                if project_id:
                    query = query.filter(OrderModel.project_id == project_id)
                
                # Apply ordering and limit
                query = query.order_by(desc(OrderModel.created_at))
                
                if limit:
                    query = query.limit(limit)
                
                order_models = query.all()
                
                # Convert to domain models
                orders = [Order.from_db_model(model) for model in order_models]
                
                logger.debug(f"Retrieved {len(orders)} orders")
                return orders
                
        except Exception as e:
            logger.error(
                f"Error listing orders: {e}", 
                extra={'context': {'status': status, 'project_id': project_id}}
            )
            return []
    
    def delete_order(self, order_id: int) -> Tuple[bool, List[str]]:
        """
        Delete an order and all related data.
        
        Args:
            order_id: ID of order to delete
            
        Returns:
            Tuple of (success, list of file paths to clean up)
        """
        try:
            with self._get_session() as session:
                # Get product file paths for cleanup
                product_files = session.query(Product.file_path)\
                    .join(Generation)\
                    .filter(Generation.order_id == order_id)\
                    .all()
                file_paths = [path for (path,) in product_files]
                
                # Delete the order (cascades to generations and products)
                order_model = session.query(OrderModel).get(order_id)
                if order_model:
                    session.delete(order_model)
                    session.commit()
                    logger.info(f"Deleted order {order_id} with {len(file_paths)} products")
                    return True, file_paths
                
                logger.warning(f"Order {order_id} not found for deletion")
                return False, []
                
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {e}")
            return False, []