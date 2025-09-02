"""
Factory pattern for service creation
"""

from typing import Dict, Type, Any
from ..repositories import (
    AccountRepository, PositionRepository, 
    OrderRepository, TransactionRepository
)
from ..utils.singleton import Singleton


class RepositoryFactory(Singleton):
    """Factory for creating repository instances"""
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._repositories: Dict[str, Any] = {}
            self.initialized = True
    
    def get_account_repository(self) -> AccountRepository:
        """Get account repository instance"""
        if 'account' not in self._repositories:
            self._repositories['account'] = AccountRepository()
        return self._repositories['account']
    
    def get_position_repository(self) -> PositionRepository:
        """Get position repository instance"""
        if 'position' not in self._repositories:
            self._repositories['position'] = PositionRepository()
        return self._repositories['position']
    
    def get_order_repository(self) -> OrderRepository:
        """Get order repository instance"""
        if 'order' not in self._repositories:
            self._repositories['order'] = OrderRepository()
        return self._repositories['order']
    
    def get_transaction_repository(self) -> TransactionRepository:
        """Get transaction repository instance"""
        if 'transaction' not in self._repositories:
            self._repositories['transaction'] = TransactionRepository()
        return self._repositories['transaction']
    
    def clear_all_repositories(self):
        """Clear all repository data (for testing)"""
        for repo in self._repositories.values():
            if hasattr(repo, 'clear_all'):
                repo.clear_all()


class ServiceFactory(Singleton):
    """Factory for creating service instances"""
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._services: Dict[str, Any] = {}
            self._repository_factory = RepositoryFactory()
            self.initialized = True
    
    def get_repository_factory(self) -> RepositoryFactory:
        """Get repository factory"""
        return self._repository_factory
    
    def create_service(self, service_type: str, **kwargs) -> Any:
        """Create service instance"""
        if service_type not in self._services:
            if service_type == 'auth':
                from .auth_service import AuthService
                self._services[service_type] = AuthService(self._repository_factory)
            elif service_type == 'order':
                from .order_service import OrderService
                self._services[service_type] = OrderService(self._repository_factory)
            elif service_type == 'position':
                from .position_service import PositionService
                self._services[service_type] = PositionService(self._repository_factory)
            elif service_type == 'transaction':
                from .transaction_service import TransactionService
                self._services[service_type] = TransactionService(self._repository_factory)
            elif service_type == 'price':
                from .price_service import PriceService
                self._services[service_type] = PriceService()
            else:
                raise ValueError(f"Unknown service type: {service_type}")
        
        return self._services[service_type]