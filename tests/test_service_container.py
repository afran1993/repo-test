"""
Tests for ServiceContainer - Advanced Dependency Injection Container.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.service_container import (
    ServiceContainer,
    ServiceNotFoundError,
    CircularDependencyError,
)


class TestServiceContainerBasic:
    """Tests for basic ServiceContainer operations."""
    
    def test_container_initialization(self):
        """Test ServiceContainer initializes correctly."""
        container = ServiceContainer()
        
        assert container is not None
        assert container.get_stats() == {
            'instances': 0,
            'singletons': 0,
            'factories': 0,
            'total': 0
        }
    
    def test_register_and_resolve_instance(self):
        """Test registering and resolving an instance."""
        container = ServiceContainer()
        service = Mock(name="test_service")
        
        container.register_instance('test', service)
        
        assert container.resolve('test') is service
    
    def test_register_and_resolve_singleton(self):
        """Test singleton service creation and reuse."""
        container = ServiceContainer()
        call_count = 0
        
        def create_service():
            nonlocal call_count
            call_count += 1
            return Mock(name=f"service_{call_count}")
        
        container.register_singleton('singleton', create_service)
        
        # First resolution
        service1 = container.resolve('singleton')
        assert call_count == 1
        
        # Second resolution - should get same instance
        service2 = container.resolve('singleton')
        assert call_count == 1  # Factory not called again
        assert service1 is service2
    
    def test_register_and_resolve_factory(self):
        """Test factory service creates new instance each time."""
        container = ServiceContainer()
        call_count = 0
        
        def create_service():
            nonlocal call_count
            call_count += 1
            return Mock(name=f"service_{call_count}")
        
        container.register_factory('factory', create_service)
        
        # First resolution
        service1 = container.resolve('factory')
        assert call_count == 1
        
        # Second resolution - should get new instance
        service2 = container.resolve('factory')
        assert call_count == 2
        assert service1 is not service2
    
    def test_resolve_nonexistent_service(self):
        """Test resolving non-existent service raises error."""
        container = ServiceContainer()
        
        with pytest.raises(ServiceNotFoundError) as exc_info:
            container.resolve('nonexistent')
        
        assert 'nonexistent' in str(exc_info.value)


class TestServiceRegistration:
    """Tests for service registration and validation."""
    
    def test_register_instance_twice_raises_error(self):
        """Test registering same instance name twice fails."""
        container = ServiceContainer()
        
        container.register_instance('service', Mock())
        
        with pytest.raises(ValueError) as exc_info:
            container.register_instance('service', Mock())
        
        assert 'already registered' in str(exc_info.value)
    
    def test_register_singleton_twice_raises_error(self):
        """Test registering same singleton name twice fails."""
        container = ServiceContainer()
        
        container.register_singleton('service', Mock)
        
        with pytest.raises(ValueError):
            container.register_singleton('service', Mock)
    
    def test_register_factory_twice_raises_error(self):
        """Test registering same factory name twice fails."""
        container = ServiceContainer()
        
        container.register_factory('service', Mock)
        
        with pytest.raises(ValueError):
            container.register_factory('service', Mock)
    
    def test_register_different_types_same_name_fails(self):
        """Test registering different service types with same name fails."""
        container = ServiceContainer()
        
        container.register_instance('service', Mock())
        
        with pytest.raises(ValueError):
            container.register_singleton('service', Mock)
        
        with pytest.raises(ValueError):
            container.register_factory('service', Mock)


class TestServiceResolution:
    """Tests for service resolution order and behavior."""
    
    def test_resolution_order_instances_first(self):
        """Test instances are resolved before singletons/factories."""
        container = ServiceContainer()
        instance_service = Mock(name="instance")
        
        container.register_instance('instance', instance_service)
        container.register_singleton('singleton', lambda: Mock(name="singleton"))
        
        # Should resolve to instance
        assert container.resolve('instance') is instance_service
        # And to singleton separately
        singleton_resolved = container.resolve('singleton')
        assert singleton_resolved is not instance_service
    
    def test_resolution_order_singletons_before_factories(self):
        """Test singletons are resolved before factories."""
        container = ServiceContainer()
        singleton_service = Mock(name="singleton")
        
        container.register_singleton('singleton', lambda: singleton_service)
        
        factory_service = Mock(name="factory")
        container.register_factory('factory', lambda: factory_service)
        
        # Resolve singleton
        resolved_singleton = container.resolve('singleton')
        assert resolved_singleton is singleton_service
        
        # Resolve factory
        resolved_factory = container.resolve('factory')
        assert resolved_factory is factory_service
    
    def test_lazy_singleton_creation(self):
        """Test singleton is only created on first resolution."""
        container = ServiceContainer()
        created = False
        
        def create_service():
            nonlocal created
            created = True
            return Mock()
        
        container.register_singleton('lazy', create_service)
        assert not created  # Not created yet
        
        container.resolve('lazy')
        assert created  # Created on first resolution


class TestContainerHelpers:
    """Tests for helper methods."""
    
    def test_has_service(self):
        """Test checking if service is registered."""
        container = ServiceContainer()
        
        assert not container.has('service')
        
        container.register_instance('service', Mock())
        assert container.has('service')
    
    def test_get_instance_returns_none_if_not_created(self):
        """Test get_instance returns None for uncreated singletons."""
        container = ServiceContainer()
        
        container.register_singleton('singleton', Mock)
        
        assert container.get_instance('singleton') is None
    
    def test_get_instance_returns_created_instance(self):
        """Test get_instance returns created instance."""
        container = ServiceContainer()
        service = Mock()
        
        container.register_instance('service', service)
        
        assert container.get_instance('service') is service
    
    def test_unregister_service(self):
        """Test unregistering a service."""
        container = ServiceContainer()
        container.register_instance('service', Mock())
        
        assert container.has('service')
        
        result = container.unregister('service')
        assert result is True
        assert not container.has('service')
    
    def test_unregister_nonexistent_service(self):
        """Test unregistering non-existent service returns False."""
        container = ServiceContainer()
        
        result = container.unregister('nonexistent')
        assert result is False
    
    def test_clear_container(self):
        """Test clearing all services."""
        container = ServiceContainer()
        
        container.register_instance('instance', Mock())
        container.register_singleton('singleton', Mock)
        container.register_factory('factory', Mock)
        
        assert container.get_stats()['total'] == 3
        
        container.clear()
        
        assert container.get_stats()['total'] == 0
    
    def test_get_stats(self):
        """Test getting container statistics."""
        container = ServiceContainer()
        
        container.register_instance('instance', Mock())
        container.register_singleton('singleton', Mock)
        container.register_factory('factory', Mock)
        
        stats = container.get_stats()
        
        assert stats['instances'] == 1
        assert stats['singletons'] == 1
        assert stats['factories'] == 1
        assert stats['total'] == 3


class TestCircularDependencies:
    """Tests for circular dependency detection."""
    
    def test_direct_circular_dependency(self):
        """Test direct circular dependency is detected."""
        container = ServiceContainer()
        
        def create_a():
            return container.resolve('a')
        
        container.register_singleton('a', create_a)
        
        with pytest.raises(CircularDependencyError):
            container.resolve('a')
    
    def test_indirect_circular_dependency(self):
        """Test indirect circular dependency is detected."""
        container = ServiceContainer()
        
        def create_a():
            return container.resolve('b')
        
        def create_b():
            return container.resolve('a')
        
        container.register_singleton('a', create_a)
        container.register_singleton('b', create_b)
        
        with pytest.raises(CircularDependencyError):
            container.resolve('a')
    
    def test_factory_circular_dependency(self):
        """Test circular dependency with factories."""
        container = ServiceContainer()
        
        def create_a():
            return container.resolve('b')
        
        def create_b():
            return container.resolve('a')
        
        container.register_factory('a', create_a)
        container.register_factory('b', create_b)
        
        with pytest.raises(CircularDependencyError):
            container.resolve('a')


class TestComplexDependencies:
    """Tests for complex dependency scenarios."""
    
    def test_multiple_levels_of_dependencies(self):
        """Test resolving services with multiple dependency levels."""
        container = ServiceContainer()
        
        # Create a dependency chain: A -> B -> C
        service_c = Mock(name="c")
        container.register_instance('c', service_c)
        
        container.register_singleton(
            'b',
            lambda: Mock(dependency=container.resolve('c'))
        )
        
        container.register_singleton(
            'a',
            lambda: Mock(dependency=container.resolve('b'))
        )
        
        service_a = container.resolve('a')
        service_b = service_a.dependency
        
        assert service_b.dependency is service_c
    
    def test_shared_dependency(self):
        """Test multiple services using same singleton dependency."""
        container = ServiceContainer()
        
        shared = Mock(name="shared")
        container.register_instance('shared', shared)
        
        container.register_singleton('service_a', lambda: Mock(dep=container.resolve('shared')))
        container.register_singleton('service_b', lambda: Mock(dep=container.resolve('shared')))
        
        service_a = container.resolve('service_a')
        service_b = container.resolve('service_b')
        
        # Both should get same shared instance
        assert service_a.dep is shared
        assert service_b.dep is shared
        assert service_a.dep is service_b.dep
    
    def test_factory_with_singleton_dependency(self):
        """Test factory service using singleton dependency."""
        container = ServiceContainer()
        singleton = Mock(name="singleton")
        
        container.register_instance('singleton', singleton)
        container.register_factory('factory', lambda: Mock(dep=container.resolve('singleton')))
        
        service1 = container.resolve('factory')
        service2 = container.resolve('factory')
        
        # Different factory instances
        assert service1 is not service2
        # But same singleton dependency
        assert service1.dep is singleton
        assert service2.dep is singleton


class TestContainerIntegration:
    """Integration tests for complete container usage."""
    
    def test_realistic_application_setup(self):
        """Test realistic application service setup."""
        container = ServiceContainer()
        
        # Configuration (instance)
        config = Mock(name="config", debug=True)
        container.register_instance('config', config)
        
        # Database (singleton)
        container.register_singleton('database', lambda: Mock(name="db"))
        
        # Repositories (singletons depending on database)
        container.register_singleton(
            'user_repo',
            lambda: Mock(db=container.resolve('database'))
        )
        
        # Services (factories depending on repos)
        container.register_factory(
            'user_service',
            lambda: Mock(repo=container.resolve('user_repo'))
        )
        
        # Resolve components
        config_resolved = container.resolve('config')
        service1 = container.resolve('user_service')
        service2 = container.resolve('user_service')
        
        assert config_resolved.debug is True
        assert service1 is not service2  # Different instances
        assert service1.repo is service2.repo  # Same repo
    
    def test_container_with_many_services(self):
        """Test container performance with many services."""
        container = ServiceContainer()
        
        # Register many services
        for i in range(100):
            container.register_instance(f'service_{i}', Mock(id=i))
        
        # Verify stats
        stats = container.get_stats()
        assert stats['instances'] == 100
        assert stats['total'] == 100
        
        # Verify resolution
        for i in range(100):
            service = container.resolve(f'service_{i}')
            assert service.id == i


class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_service_factory_raises_exception(self):
        """Test exception in service factory is propagated."""
        container = ServiceContainer()
        
        def failing_factory():
            raise ValueError("Factory creation failed")
        
        container.register_singleton('failing', failing_factory)
        
        with pytest.raises(ValueError) as exc_info:
            container.resolve('failing')
        
        assert "Factory creation failed" in str(exc_info.value)
    
    def test_clear_while_resolving(self):
        """Test container behavior when cleared during resolution."""
        container = ServiceContainer()
        
        container.register_instance('service', Mock())
        
        container.clear()
        
        with pytest.raises(ServiceNotFoundError):
            container.resolve('service')
    
    def test_resolve_after_unregister(self):
        """Test resolution after unregistering service."""
        container = ServiceContainer()
        
        container.register_instance('service', Mock())
        container.unregister('service')
        
        with pytest.raises(ServiceNotFoundError):
            container.resolve('service')
