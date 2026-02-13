"""
Tests for repository pattern and event bus.

Validates repository implementations and event bus functionality.
"""

import pytest
from src.repositories import (
    SimpleEventBus,
    LocationRepository,
    EnemyRepository,
    NPCRepository,
)
from src.repository_impl import (
    JsonLocationRepository,
    JsonEnemyRepository,
    JsonNPCRepository,
)
from src.exceptions import LocationNotFound, EnemyNotFound, NPCNotFound
from src.data_loader import GameContext


@pytest.fixture
def game_context():
    """Create a game context with loaded data."""
    context = GameContext()
    context.load_all()
    return context


class TestSimpleEventBus:
    """Test SimpleEventBus implementation."""
    
    def test_event_bus_creation(self):
        """Test creating event bus."""
        bus = SimpleEventBus()
        assert bus is not None
    
    def test_subscribe_and_publish(self):
        """Test subscribe and publish events."""
        bus = SimpleEventBus()
        events = []
        
        def handler(event_type, data):
            events.append((event_type, data))
        
        bus.subscribe("test_event", handler)
        bus.publish("test_event", {"value": 42})
        
        assert len(events) == 1
        assert events[0] == ("test_event", {"value": 42})
    
    def test_unsubscribe(self):
        """Test unsubscribe from event."""
        bus = SimpleEventBus()
        events = []
        
        def handler(event_type, data):
            events.append((event_type, data))
        
        bus.subscribe("test_event", handler)
        bus.unsubscribe("test_event", handler)
        bus.publish("test_event", {"value": 42})
        
        assert len(events) == 0
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event."""
        bus = SimpleEventBus()
        events1 = []
        events2 = []
        
        def handler1(event_type, data):
            events1.append(data)
        
        def handler2(event_type, data):
            events2.append(data)
        
        bus.subscribe("test_event", handler1)
        bus.subscribe("test_event", handler2)
        bus.publish("test_event", {"value": 42})
        
        assert len(events1) == 1
        assert len(events2) == 1
        assert events1[0] == {"value": 42}
        assert events2[0] == {"value": 42}
    
    def test_publish_no_subscribers(self):
        """Test publishing event with no subscribers (should not error)."""
        bus = SimpleEventBus()
        bus.publish("unsubscribed_event", {"value": 42})
        # Should not raise


class TestLocationRepository:
    """Test LocationRepository implementations."""
    
    def test_location_repository_get_location(self, game_context):
        """Test getting location from repository."""
        repo = game_context.get_location_repository()
        location = repo.get_location("beach")
        
        assert location is not None
        assert location.id == "beach"
    
    def test_location_repository_location_not_found(self, game_context):
        """Test LocationNotFound exception."""
        repo = game_context.get_location_repository()
        
        with pytest.raises(LocationNotFound):
            repo.get_location("nonexistent_location")
    
    def test_location_repository_get_all(self, game_context):
        """Test getting all locations."""
        repo = game_context.get_location_repository()
        locations = repo.get_all_locations()
        
        assert len(locations) > 0
        assert all(hasattr(loc, 'id') for loc in locations)
    
    def test_location_repository_get_by_name(self, game_context):
        """Test getting location by name."""
        repo = game_context.get_location_repository()
        # Use Italian name from actual data
        location = repo.get_location_by_name("Spiaggia dell'Isola")
        
        assert location is not None
        assert location.id == "beach"
    
    def test_location_repository_caching(self, game_context):
        """Test that locations are cached."""
        repo = game_context.get_location_repository()
        loc1 = repo.get_location("beach")
        loc2 = repo.get_location("beach")
        
        # Should be same instance (cached)
        assert loc1 is loc2


class TestEnemyRepository:
    """Test EnemyRepository implementations."""
    
    def test_enemy_repository_get_enemy(self, game_context):
        """Test getting enemy from repository."""
        repo = game_context.get_enemy_repository()
        
        # Try to get first enemy from data
        enemies_data = game_context.get_enemies()
        first_enemy_id = enemies_data["enemies"][0]["id"]
        
        enemy = repo.get_enemy(first_enemy_id)
        assert enemy is not None
        assert enemy.id == first_enemy_id
    
    def test_enemy_repository_enemy_not_found(self, game_context):
        """Test EnemyNotFound exception."""
        repo = game_context.get_enemy_repository()
        
        with pytest.raises(EnemyNotFound):
            repo.get_enemy("nonexistent_enemy")
    
    def test_enemy_repository_get_all(self, game_context):
        """Test getting all enemies."""
        repo = game_context.get_enemy_repository()
        enemies = repo.get_all_enemies()
        
        assert len(enemies) > 0
        assert all(hasattr(e, 'id') for e in enemies)
    
    def test_enemy_repository_get_by_location(self, game_context):
        """Test getting enemies for a location."""
        repo = game_context.get_enemy_repository()
        enemies = repo.get_enemies_by_location("beach")
        
        # Beach should have some enemies
        assert len(enemies) > 0


class TestNPCRepository:
    """Test NPCRepository implementations."""
    
    def test_npc_repository_get_npc(self, game_context):
        """Test getting NPC from repository."""
        repo = game_context.get_npc_repository()
        
        # Get first NPC from data
        npcs_data = game_context.get_npcs()
        if npcs_data["npcs"]:
            first_npc_id = npcs_data["npcs"][0]["id"]
            npc = repo.get_npc(first_npc_id)
            
            assert npc is not None
            assert npc["id"] == first_npc_id
    
    def test_npc_repository_npc_not_found(self, game_context):
        """Test NPCNotFound exception."""
        repo = game_context.get_npc_repository()
        
        with pytest.raises(NPCNotFound):
            repo.get_npc("nonexistent_npc")
    
    def test_npc_repository_get_all(self, game_context):
        """Test getting all NPCs."""
        repo = game_context.get_npc_repository()
        npcs = repo.get_all_npcs()
        
        assert isinstance(npcs, list)


class TestGameContextRepositories:
    """Test GameContext repository creation."""
    
    def test_context_provides_location_repo(self, game_context):
        """Test context provides location repository."""
        repo = game_context.get_location_repository()
        assert isinstance(repo, LocationRepository)
    
    def test_context_provides_enemy_repo(self, game_context):
        """Test context provides enemy repository."""
        repo = game_context.get_enemy_repository()
        assert isinstance(repo, EnemyRepository)
    
    def test_context_provides_npc_repo(self, game_context):
        """Test context provides NPC repository."""
        repo = game_context.get_npc_repository()
        assert isinstance(repo, NPCRepository)
    
    def test_context_provides_event_bus(self, game_context):
        """Test context provides event bus."""
        bus = game_context.get_event_bus()
        assert bus is not None
        assert hasattr(bus, 'subscribe')
        assert hasattr(bus, 'publish')
    
    def test_context_repositories_are_singletons(self, game_context):
        """Test repositories are singletons per context."""
        repo1 = game_context.get_location_repository()
        repo2 = game_context.get_location_repository()
        
        assert repo1 is repo2
    
    def test_context_event_bus_is_singleton(self, game_context):
        """Test event bus is singleton per context."""
        bus1 = game_context.get_event_bus()
        bus2 = game_context.get_event_bus()
        
        assert bus1 is bus2
