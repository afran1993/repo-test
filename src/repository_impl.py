"""
Repository implementations - Data access layer.

Concrete implementations of abstract repository interfaces.
"""

from typing import Dict, Any, Optional, List
import logging
from src.repositories import (
    LocationRepository,
    EnemyRepository, 
    NPCRepository,
    QuestRepository,
    ItemRepository,
)
from src.exceptions import LocationNotFound, EnemyNotFound, NPCNotFound
from src.models import Location, Enemy

logger = logging.getLogger(__name__)


class JsonLocationRepository(LocationRepository):
    """Location repository backed by JSON data."""
    
    def __init__(self, locations_data: Dict[str, Any], enemies_data: Dict[str, Any]):
        """Initialize repository.
        
        Args:
            locations_data: Locations JSON data
            enemies_data: Enemies JSON data (for spawning)
        """
        self.locations_data = locations_data
        self.enemies_data = enemies_data
        self._cache: Dict[str, Location] = {}
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID.
        
        Args:
            location_id: ID of the location
        
        Returns:
            Location object
        
        Raises:
            LocationNotFound: If not found
        """
        if location_id in self._cache:
            logger.debug(f"Cache hit: location {location_id}")
            return self._cache[location_id]
        
        for loc_data in self.locations_data.get("locations", []):
            if loc_data.get("id") == location_id:
                location = Location(loc_data, self.enemies_data)
                self._cache[location_id] = location
                logger.debug(f"Loaded location from data: {location_id}")
                return location
        
        logger.warning(f"Location not found: {location_id}")
        raise LocationNotFound(location_id)
    
    def get_all_locations(self) -> List[Location]:
        """Get all locations.
        
        Returns:
            List of Location objects
        """
        locations = []
        for loc_data in self.locations_data.get("locations", []):
            loc_id = loc_data.get("id")
            if loc_id not in self._cache:
                self._cache[loc_id] = Location(loc_data, self.enemies_data)
            locations.append(self._cache[loc_id])
        return locations
    
    def get_location_by_name(self, name: str) -> Optional[Location]:
        """Get a location by name.
        
        Args:
            name: Name of the location
        
        Returns:
            Location object or None
        """
        for loc_data in self.locations_data.get("locations", []):
            if loc_data.get("name", "").lower() == name.lower():
                loc_id = loc_data.get("id")
                if loc_id not in self._cache:
                    self._cache[loc_id] = Location(loc_data, self.enemies_data)
                return self._cache[loc_id]
        return None


class JsonEnemyRepository(EnemyRepository):
    """Enemy repository backed by JSON data."""
    
    def __init__(self, enemies_data: Dict[str, Any], locations_data: Dict[str, Any]):
        """Initialize repository.
        
        Args:
            enemies_data: Enemies JSON data
            locations_data: Locations data (for lookups)
        """
        self.enemies_data = enemies_data
        self.locations_data = locations_data
        self._cache: Dict[str, Enemy] = {}
    
    def get_enemy(self, enemy_id: str) -> Optional[Enemy]:
        """Get an enemy by ID.
        
        Args:
            enemy_id: ID of the enemy
        
        Returns:
            Enemy object
        
        Raises:
            EnemyNotFound: If not found
        """
        if enemy_id in self._cache:
            logger.debug(f"Cache hit: enemy {enemy_id}")
            return self._cache[enemy_id]
        
        for enemy_data in self.enemies_data.get("enemies", []):
            if enemy_data.get("id") == enemy_id:
                enemy = Enemy(enemy_data, self.enemies_data)
                # Don't cache since enemies get damaged
                logger.debug(f"Loaded enemy from data: {enemy_id}")
                return enemy
        
        logger.warning(f"Enemy not found: {enemy_id}")
        raise EnemyNotFound(enemy_id)
    
    def get_enemies_by_location(self, location_id: str) -> List[Enemy]:
        """Get enemies that spawn at a location.
        
        Args:
            location_id: ID of the location
        
        Returns:
            List of Enemy objects
        """
        enemies = []
        for loc_data in self.locations_data.get("locations", []):
            if loc_data.get("id") == location_id:
                for enemy_ref in loc_data.get("enemies", []):
                    enemy_id = enemy_ref.get("id")
                    for enemy_data in self.enemies_data.get("enemies", []):
                        if enemy_data.get("id") == enemy_id:
                            enemies.append(Enemy(enemy_data, self.enemies_data))
                            break
        return enemies
    
    def get_all_enemies(self) -> List[Enemy]:
        """Get all enemies.
        
        Returns:
            List of all Enemy objects
        """
        enemies = []
        for enemy_data in self.enemies_data.get("enemies", []):
            enemies.append(Enemy(enemy_data, self.enemies_data))
        return enemies


class JsonNPCRepository(NPCRepository):
    """NPC repository backed by JSON data."""
    
    def __init__(self, npcs_data: Dict[str, Any]):
        """Initialize repository.
        
        Args:
            npcs_data: NPCs JSON data
        """
        self.npcs_data = npcs_data
    
    def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Get an NPC by ID.
        
        Args:
            npc_id: ID of the NPC
        
        Returns:
            NPC data dict
        
        Raises:
            NPCNotFound: If not found
        """
        for npc_data in self.npcs_data.get("npcs", []):
            if npc_data.get("id") == npc_id:
                logger.debug(f"Loaded NPC from data: {npc_id}")
                return npc_data
        
        logger.warning(f"NPC not found: {npc_id}")
        raise NPCNotFound(npc_id)
    
    def get_npcs_in_location(self, location_id: str) -> List[Dict[str, Any]]:
        """Get NPCs in a specific location.
        
        Args:
            location_id: ID of the location
        
        Returns:
            List of NPC data dicts
        """
        npcs = []
        for npc_data in self.npcs_data.get("npcs", []):
            if npc_data.get("location") == location_id:
                npcs.append(npc_data)
        return npcs
    
    def get_all_npcs(self) -> List[Dict[str, Any]]:
        """Get all NPCs.
        
        Returns:
            List of all NPC data dicts
        """
        return self.npcs_data.get("npcs", [])


class JsonQuestRepository(QuestRepository):
    """Quest repository backed by JSON data."""
    
    def __init__(self, quests_data: Dict[str, Any]):
        """Initialize repository.
        
        Args:
            quests_data: Quests JSON data
        """
        self.quests_data = quests_data
    
    def get_quest(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get a quest by ID.
        
        Args:
            quest_id: ID of the quest
        
        Returns:
            Quest data dict or None
        """
        for quest_data in self.quests_data.get("quests", []):
            if quest_data.get("id") == quest_id:
                logger.debug(f"Loaded quest from data: {quest_id}")
                return quest_data
        return None
    
    def get_main_quest_for_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get the main quest for a location.
        
        Args:
            location_id: ID of the location
        
        Returns:
            Quest data dict or None
        """
        for quest_data in self.quests_data.get("quests", []):
            if quest_data.get("location") == location_id:
                return quest_data
        return None


class JsonItemRepository(ItemRepository):
    """Item repository backed by JSON data."""
    
    def __init__(self, items_data: Dict[str, Any]):
        """Initialize repository.
        
        Args:
            items_data: Items JSON data
        """
        self.items_data = items_data
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get an item by ID.
        
        Args:
            item_id: ID of the item
        
        Returns:
            Item data dict or None
        """
        for item_data in self.items_data.get("items", []):
            if item_data.get("id") == item_id:
                logger.debug(f"Loaded item from data: {item_id}")
                return item_data
        return None
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items.
        
        Returns:
            List of all item data dicts
        """
        return self.items_data.get("items", [])
