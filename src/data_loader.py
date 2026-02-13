"""
Data loader and GameContext.

Centralizes all global state management and data loading.
Replaces scattered global variables with a single context object.
"""

import json
import os
from typing import Optional, Dict, Any


class GameContext:
    """
    Centralizes all game data and state.
    
    This replaces global variables like LOCATIONS_DATA, ENEMIES_DATA, etc.
    with a single injectable context object.
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                '..',
                'data'
            )
        
        self.data_dir = data_dir
        
        # Data containers
        self.locations_data: Optional[Dict[str, Any]] = None
        self.enemies_data: Optional[Dict[str, Any]] = None
        self.items_data: Optional[Dict[str, Any]] = None
        self.quests_data: Optional[Dict[str, Any]] = None
        self.npcs_data: Optional[Dict[str, Any]] = None
        self.abilities_data: Optional[Dict[str, Any]] = None
        
        # Repository instances (created on-demand)
        self._location_repo: Optional[Any] = None
        self._enemy_repo: Optional[Any] = None
        self._npc_repo: Optional[Any] = None
        self._quest_repo: Optional[Any] = None
        self._item_repo: Optional[Any] = None
        self._event_bus: Optional[Any] = None
    
    def load_all(self) -> None:
        """Load all required data files."""
        self.load_locations()
        self.load_enemies()
        self.load_items()
        self.load_quests()
        self.load_npcs()
        self.load_abilities()
    
    def load_locations(self) -> None:
        """Load locations data."""
        path = os.path.join(self.data_dir, 'locations.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.locations_data = json.load(f)
    
    def load_enemies(self) -> None:
        """Load enemies data."""
        path = os.path.join(self.data_dir, 'enemies.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.enemies_data = json.load(f)
    
    def load_items(self) -> None:
        """Load items data."""
        path = os.path.join(self.data_dir, 'items.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.items_data = json.load(f)
    
    def load_quests(self) -> None:
        """Load quests data."""
        path = os.path.join(self.data_dir, 'quests.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.quests_data = json.load(f)
    
    def load_npcs(self) -> None:
        """Load NPCs data."""
        path = os.path.join(self.data_dir, 'npcs.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.npcs_data = json.load(f)
    
    def load_abilities(self) -> None:
        """Load abilities data."""
        path = os.path.join(self.data_dir, 'abilities.json')
        with open(path, 'r', encoding='utf-8') as f:
            self.abilities_data = json.load(f)
        
        # Initialize abilities registry
        from src.combat import init_abilities_registry
        init_abilities_registry(path)
    
    def get_locations(self) -> Optional[Dict[str, Any]]:
        """Get locations data."""
        if self.locations_data is None:
            self.load_locations()
        return self.locations_data
    
    def get_enemies(self) -> Optional[Dict[str, Any]]:
        """Get enemies data."""
        if self.enemies_data is None:
            self.load_enemies()
        return self.enemies_data
    
    def get_items(self) -> Optional[Dict[str, Any]]:
        """Get items data."""
        if self.items_data is None:
            self.load_items()
        return self.items_data
    
    def get_quests(self) -> Optional[Dict[str, Any]]:
        """Get quests data."""
        if self.quests_data is None:
            self.load_quests()
        return self.quests_data
    
    def get_npcs(self) -> Optional[Dict[str, Any]]:
        """Get NPCs data."""
        if self.npcs_data is None:
            self.load_npcs()
        return self.npcs_data
    
    def get_abilities(self) -> Optional[Dict[str, Any]]:
        """Get abilities data."""
        if self.abilities_data is None:
            self.load_abilities()
        return self.abilities_data
    
    def get_location_repository(self) -> 'LocationRepository':
        """Get or create location repository.
        
        Returns:
            LocationRepository instance
        """
        if self._location_repo is None:
            from src.repository_impl import JsonLocationRepository
            self._location_repo = JsonLocationRepository(
                self.get_locations(), 
                self.get_enemies()
            )
        return self._location_repo
    
    def get_enemy_repository(self) -> 'EnemyRepository':
        """Get or create enemy repository.
        
        Returns:
            EnemyRepository instance
        """
        if self._enemy_repo is None:
            from src.repository_impl import JsonEnemyRepository
            self._enemy_repo = JsonEnemyRepository(
                self.get_enemies(),
                self.get_locations()
            )
        return self._enemy_repo
    
    def get_npc_repository(self) -> 'NPCRepository':
        """Get or create NPC repository.
        
        Returns:
            NPCRepository instance
        """
        if self._npc_repo is None:
            from src.repository_impl import JsonNPCRepository
            self._npc_repo = JsonNPCRepository(self.get_npcs())
        return self._npc_repo
    
    def get_quest_repository(self) -> 'QuestRepository':
        """Get or create quest repository.
        
        Returns:
            QuestRepository instance
        """
        if self._quest_repo is None:
            from src.repository_impl import JsonQuestRepository
            self._quest_repo = JsonQuestRepository(self.get_quests())
        return self._quest_repo
    
    def get_item_repository(self) -> 'ItemRepository':
        """Get or create item repository.
        
        Returns:
            ItemRepository instance
        """
        if self._item_repo is None:
            from src.repository_impl import JsonItemRepository
            self._item_repo = JsonItemRepository(self.get_items())
        return self._item_repo
    
    def get_event_bus(self) -> 'EventBus':
        """Get or create event bus.
        
        Returns:
            EventBus instance
        """
        if self._event_bus is None:
            from src.repositories import SimpleEventBus
            self._event_bus = SimpleEventBus()
        return self._event_bus
_default_context: Optional[GameContext] = None


def get_default_context() -> GameContext:
    """Get or create the default GameContext."""
    global _default_context
    if _default_context is None:
        _default_context = GameContext()
    return _default_context


def set_default_context(context: GameContext) -> None:
    """Set the default GameContext."""
    global _default_context
    _default_context = context
