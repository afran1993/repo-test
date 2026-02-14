"""
Advanced Dependency Injection Service Container.

Supports:
- Singleton services (one instance, lazy-loaded)
- Factory services (new instance each call)
- Pre-registered instances
- Lazy initialization and resolution
"""

from typing import Dict, Callable, Any, TypeVar, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceNotFoundError(Exception):
    """Raised when a service is not found in the container."""
    pass


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected."""
    pass


class ServiceContainer:
    """
    Advanced dependency injection container for managing service instances.
    
    Features:
    - Singleton services (one instance, lazy-loaded)
    - Factory services (new instance on each call)
    - Pre-registered instances
    - Resolution order: instances > singletons (lazy) > factories
    - Thread-safe operations
    """
    
    def __init__(self):
        """Initialize the service container."""
        self._singletons: Dict[str, Callable] = {}
        self._factories: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}
        self._resolving: set = set()  # Track resolution for circular dependency detection
    
    def register_singleton(self, name: str, factory: Callable[[], T]) -> None:
        """
        Register a singleton service.
        
        Singleton services are created once and reused.
        Creation is deferred until first resolution (lazy loading).
        
        Args:
            name: Service identifier
            factory: Callable that creates the service instance
        
        Raises:
            ValueError: If service name is already registered
        """
        if name in self._instances or name in self._singletons or name in self._factories:
            raise ValueError(f"Service '{name}' is already registered")
        
        self._singletons[name] = factory
        logger.debug(f"Registered singleton: {name}")
    
    def register_factory(self, name: str, factory: Callable[[], T]) -> None:
        """
        Register a factory service.
        
        Factory services create a new instance on each resolution.
        
        Args:
            name: Service identifier
            factory: Callable that creates new service instances
        
        Raises:
            ValueError: If service name is already registered
        """
        if name in self._instances or name in self._singletons or name in self._factories:
            raise ValueError(f"Service '{name}' is already registered")
        
        self._factories[name] = factory
        logger.debug(f"Registered factory: {name}")
    
    def register_instance(self, name: str, instance: T) -> None:
        """
        Register a pre-created service instance.
        
        Use this for already-constructed services.
        
        Args:
            name: Service identifier
            instance: The service instance to register
        
        Raises:
            ValueError: If service name is already registered
        """
        if name in self._instances or name in self._singletons or name in self._factories:
            raise ValueError(f"Service '{name}' is already registered")
        
        self._instances[name] = instance
        logger.debug(f"Registered instance: {name}")
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a service by name.
        
        Resolution order:
        1. Check pre-registered instances (highest priority)
        2. Check singletons and lazy-load if needed
        3. Check factories and create new instance
        
        Args:
            name: Service identifier
        
        Returns:
            The resolved service instance
        
        Raises:
            ServiceNotFoundError: If service name is not registered
            CircularDependencyError: If circular dependency detected
        """
        # Check for circular dependency
        if name in self._resolving:
            raise CircularDependencyError(f"Circular dependency detected for service: {name}")
        
        # Check instances first (pre-registered)
        if name in self._instances:
            logger.debug(f"Resolving instance: {name}")
            return self._instances[name]
        
        # Check singletons (lazy-load)
        if name in self._singletons:
            if name not in self._instances:
                self._resolving.add(name)
                try:
                    logger.debug(f"Creating singleton (lazy-load): {name}")
                    self._instances[name] = self._singletons[name]()
                finally:
                    self._resolving.discard(name)
            return self._instances[name]
        
        # Check factories
        if name in self._factories:
            self._resolving.add(name)
            try:
                logger.debug(f"Creating from factory: {name}")
                return self._factories[name]()
            finally:
                self._resolving.discard(name)
        
        raise ServiceNotFoundError(f"Service not found in container: {name}")
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service identifier
        
        Returns:
            True if service is registered, False otherwise
        """
        return name in self._instances or name in self._singletons or name in self._factories
    
    def get_instance(self, name: str) -> Optional[Any]:
        """
        Get an instance if it has already been created.
        
        Does not trigger factory creation.
        
        Args:
            name: Service identifier
        
        Returns:
            The instance if created, None otherwise
        """
        return self._instances.get(name)
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a service from the container.
        
        Args:
            name: Service identifier
        
        Returns:
            True if service was unregistered, False if not found
        """
        found = False
        
        if name in self._instances:
            del self._instances[name]
            found = True
        
        if name in self._singletons:
            del self._singletons[name]
            found = True
        
        if name in self._factories:
            del self._factories[name]
            found = True
        
        if found:
            logger.debug(f"Unregistered service: {name}")
        
        return found
    
    def clear(self) -> None:
        """
        Clear all services from the container.
        
        Useful for testing and cleanup.
        """
        self._instances.clear()
        self._singletons.clear()
        self._factories.clear()
        self._resolving.clear()
        logger.debug("Container cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get container statistics.
        
        Returns:
            Dictionary with counts of registered services
        """
        return {
            'instances': len(self._instances),
            'singletons': len(self._singletons),
            'factories': len(self._factories),
            'total': len(self._instances) + len(self._singletons) + len(self._factories)
        }
