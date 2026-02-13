"""
Repository Pattern - Abstract interfaces for data access.

Enables rigorous dependency injection by decoupling data access from business logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class LocationRepository(ABC):
    """Abstract interface for location data access."""
    
    @abstractmethod
    def get_location(self, location_id: str) -> Optional[Any]:
        """Get a location by ID.
        
        Args:
            location_id: ID of the location
        
        Returns:
            Location object or None if not found
        
        Raises:
            LocationNotFound: If location not found
        """
        pass
    
    @abstractmethod
    def get_all_locations(self) -> List[Any]:
        """Get all locations.
        
        Returns:
            List of all location objects
        """
        pass
    
    @abstractmethod
    def get_location_by_name(self, name: str) -> Optional[Any]:
        """Get a location by name.
        
        Args:
            name: Name of the location
        
        Returns:
            Location object or None if not found
        """
        pass


class EnemyRepository(ABC):
    """Abstract interface for enemy data access."""
    
    @abstractmethod
    def get_enemy(self, enemy_id: str) -> Optional[Any]:
        """Get an enemy by ID.
        
        Args:
            enemy_id: ID of the enemy
        
        Returns:
            Enemy object or None if not found
        
        Raises:
            EnemyNotFound: If enemy not found
        """
        pass
    
    @abstractmethod
    def get_enemies_by_location(self, location_id: str) -> List[Any]:
        """Get enemies that spawn at a location.
        
        Args:
            location_id: ID of the location
        
        Returns:
            List of enemy objects
        """
        pass
    
    @abstractmethod
    def get_all_enemies(self) -> List[Any]:
        """Get all enemies.
        
        Returns:
            List of all enemy objects
        """
        pass


class NPCRepository(ABC):
    """Abstract interface for NPC data access."""
    
    @abstractmethod
    def get_npc(self, npc_id: str) -> Optional[Any]:
        """Get an NPC by ID.
        
        Args:
            npc_id: ID of the NPC
        
        Returns:
            NPC data dict or None if not found
        
        Raises:
            NPCNotFound: If NPC not found
        """
        pass
    
    @abstractmethod
    def get_npcs_in_location(self, location_id: str) -> List[Any]:
        """Get NPCs in a specific location.
        
        Args:
            location_id: ID of the location
        
        Returns:
            List of NPC data dicts
        """
        pass
    
    @abstractmethod
    def get_all_npcs(self) -> List[Any]:
        """Get all NPCs.
        
        Returns:
            List of all NPC data dicts
        """
        pass


class QuestRepository(ABC):
    """Abstract interface for quest data access."""
    
    @abstractmethod
    def get_quest(self, quest_id: str) -> Optional[Any]:
        """Get a quest by ID.
        
        Args:
            quest_id: ID of the quest
        
        Returns:
            Quest object or None if not found
        """
        pass
    
    @abstractmethod
    def get_main_quest_for_location(self, location_id: str) -> Optional[Any]:
        """Get the main quest for a location.
        
        Args:
            location_id: ID of the location
        
        Returns:
            Quest object or None
        """
        pass


class ItemRepository(ABC):
    """Abstract interface for item data access."""
    
    @abstractmethod
    def get_item(self, item_id: str) -> Optional[Any]:
        """Get an item by ID.
        
        Args:
            item_id: ID of the item
        
        Returns:
            Item data dict or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_items(self) -> List[Any]:
        """Get all items.
        
        Returns:
            List of all item data dicts
        """
        pass


class EventBus(ABC):
    """Abstract interface for game events (pub/sub pattern)."""
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to an event.
        
        Args:
            event_type: Type of event (e.g., "player_level_up", "enemy_defeated")
            handler: Callable to execute when event is published
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Unsubscribe from an event.
        
        Args:
            event_type: Type of event
            handler: Callable to remove
        """
        pass
    
    @abstractmethod
    def publish(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Publish an event.
        
        Args:
            event_type: Type of event
            data: Event payload data
        """
        pass


class SimpleEventBus(EventBus):
    """Simple in-memory event bus implementation."""
    
    def __init__(self):
        """Initialize event bus."""
        self._subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to an event.
        
        Args:
            event_type: Type of event
            handler: Callable to execute
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Unsubscribe from an event.
        
        Args:
            event_type: Type of event
            handler: Callable to remove
        """
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed from event: {event_type}")
    
    def publish(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Publish an event.
        
        Args:
            event_type: Type of event
            data: Event payload
        """
        if data is None:
            data = {}
        
        if event_type in self._subscribers:
            logger.debug(f"Publishing event: {event_type} with data: {data}")
            for handler in self._subscribers[event_type]:
                try:
                    handler(event_type, data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
        else:
            logger.debug(f"No subscribers for event: {event_type}")


class GameLocalCache:
    """Local data cache repository implementations."""
    
    def __init__(self, context: 'GameContext'):
        """Initialize cache with GameContext.
        
        Args:
            context: GameContext instance
        """
        self.context = context
    
    @property
    def locations_data(self) -> Dict[str, Any]:
        """Get locations data from context."""
        return self.context.get_locations()
    
    @property
    def enemies_data(self) -> Dict[str, Any]:
        """Get enemies data from context."""
        return self.context.get_enemies()
    
    @property
    def npcs_data(self) -> Dict[str, Any]:
        """Get NPCs data from context."""
        return self.context.get_npcs()
    
    @property
    def quests_data(self) -> Dict[str, Any]:
        """Get quests data from context."""
        return self.context.get_quests()
    
    @property
    def items_data(self) -> Dict[str, Any]:
        """Get items data from context."""
        return self.context.get_items()
