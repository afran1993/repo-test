"""
Game models - Location, Enemy, and related classes.

Contains core game entity models.
"""

import random
import logging
from typing import Dict, Any, Optional, List
from src.exceptions import LocationNotFound, EnemyNotFound

logger = logging.getLogger(__name__)

# Module-level data caches (for backward compatibility)
_locations_data: Optional[Dict[str, Any]] = None
_enemies_data: Optional[Dict[str, Any]] = None


def set_locations_data(data: Dict[str, Any]) -> None:
    """Set the locations data cache."""
    global _locations_data
    _locations_data = data


def set_enemies_data(data: Dict[str, Any]) -> None:
    """Set the enemies data cache."""
    global _enemies_data
    _enemies_data = data


def get_location(location_id: str, context: Optional['GameContext'] = None) -> Optional['Location']:
    """Get a location by ID.
    
    Args:
        location_id: ID of the location
        context: GameContext (optional, uses module cache if not provided)
    
    Returns:
        Location object or None
    
    Raises:
        LocationNotFound: If location ID not found
    """
    if context:
        locations_data = context.get_locations()
        enemies_data = context.get_enemies()
    else:
        locations_data = _locations_data
        enemies_data = _enemies_data
    
    if not locations_data:
        logger.error("Locations data not loaded")
        raise LocationNotFound(location_id)
    
    for loc_data in locations_data.get("locations", []):
        if loc_data.get("id") == location_id:
            logger.debug(f"Loaded location: {location_id}")
            return Location(loc_data, enemies_data)
    
    logger.warning(f"Location not found: {location_id}")
    raise LocationNotFound(location_id)


class Enemy:
    """Enemy character in the game."""
    
    def __init__(self, enemy_data: Dict[str, Any], enemies_data: Optional[Dict[str, Any]] = None):
        """Initialize an enemy.
        
        Args:
            enemy_data: Enemy data dictionary
            enemies_data: Global enemies data (for lookup)
        """
        self.id = enemy_data.get("id")
        self.name = enemy_data.get("display", "Unknown")
        self.hp = enemy_data.get("hp", 10)
        self.max_hp = self.hp
        self.atk = enemy_data.get("atk", 3)
        self.def_ = enemy_data.get("def", 0)
        self.element = enemy_data.get("element", "None")
        self.tier = enemy_data.get("tier", 1)
        
        # XP and gold rewards
        self.xp_reward = self.tier * 10
        self.gold_reward = random.randint(self.tier * 2, self.tier * 5)
        
        # Advanced enemy properties
        self.speed = enemy_data.get("speed", 5)  # Combat speed (evasion/turn order)
        self.tags = enemy_data.get("tags", [])
        self.abilities = enemy_data.get("abilities", [])
        self.behaviors = enemy_data.get("behaviors", [])
        
        # Elemental resistances/immunities/vulnerabilities
        self.resistances: Dict[str, float] = enemy_data.get("resistances", {})  # e.g., {"Fire": 0.5}
        self.immunities: List[str] = enemy_data.get("immunities", [])  # e.g., ["Poison", "Physical"]
        self.vulnerabilities: List[str] = enemy_data.get("vulnerabilities", [])  # e.g., ["Holy", "Lightning"]
        
        # Special mechanics
        self.regeneration = enemy_data.get("regeneration", 0)  # HP recovered per turn
        
        # Boss/endgame flags
        self.is_boss = enemy_data.get("boss", False)
        self.is_final_boss = enemy_data.get("final_boss", False)
        self.is_endgame = enemy_data.get("endgame", False)
        
        # Item drops (probabilistic)
        self.drops = enemy_data.get("drops", [])  # List of {"gold": {...}, "chance": 0.5} or {"item": "...", "chance": 0.3}
    
    def is_alive(self) -> bool:
        """Check if enemy is alive.
        
        Returns:
            True if hp > 0
        """
        return self.hp > 0
    
    def describe(self) -> str:
        """Get enemy description.
        
        Returns:
            String description of enemy
        """
        status = f"{self.name} ({self.element}) - HP {self.hp}/{self.max_hp}"
        
        # Add special status indicators
        if self.is_final_boss:
            status += " [FINAL BOSS]"
        elif self.is_boss:
            status += " [BOSS]"
        elif self.is_endgame:
            status += " [ENDGAME]"
        
        return status
    
    def take_damage(self, damage: float) -> None:
        """Take damage with resistance/immunity calculations.
        
        Args:
            damage: Damage amount
        """
        self.hp -= damage
        logger.debug(f"{self.name} takes {damage} damage, hp now {self.hp}")
    
    def get_resistance(self, element: str) -> float:
        """Get damage multiplier for element (resistance/vulnerability).
        
        Args:
            element: Element type (e.g., "Fire", "Ice")
        
        Returns:
            Damage multiplier (0.5 = 50% damage, 2.0 = 200% damage)
        """
        # Check immunity first (immune = 0 damage)
        if element in self.immunities:
            return 0.0
        
        # Check vulnerability (takes extra damage)
        if element in self.vulnerabilities:
            return 1.5  # 150% damage
        
        # Check resistance
        return self.resistances.get(element, 1.0)
    
    def regenerate(self) -> None:
        """Apply regeneration at end of turn."""
        if self.regeneration > 0:
            self.hp = min(self.max_hp, self.hp + self.regeneration)
            logger.debug(f"{self.name} regenerated {self.regeneration} HP")
    
    def roll_drops(self) -> Dict[str, Any]:
        """Calculate which drops this enemy will give on defeat.
        
        Returns:
            Dictionary with "gold" and "items" keys
        """
        drops_result = {"gold": 0, "items": []}
        
        for drop_entry in self.drops:
            # Check if drop happens
            if random.random() >= drop_entry.get("chance", 1.0):
                continue
            
            # Gold drop
            if "gold" in drop_entry:
                gold_data = drop_entry["gold"]
                amount = random.randint(gold_data["min"], gold_data["max"])
                drops_result["gold"] += amount
            
            # Item drop
            if "item" in drop_entry:
                item_id = drop_entry["item"]
                drops_result["items"].append(item_id)
        
        return drops_result
    
    def has_ability(self, ability_id: str) -> bool:
        """Check if enemy knows an ability.
        
        Args:
            ability_id: ID of the ability
        
        Returns:
            True if enemy has this ability
        """
        return ability_id in self.abilities


class Location:
    """A location on the game map."""
    
    def __init__(self, location_data: Dict[str, Any], enemies_data: Optional[Dict[str, Any]] = None):
        """Initialize a location.
        
        Args:
            location_data: Location data dictionary
            enemies_data: Global enemies data (for spawning)
        """
        self.id = location_data.get("id")
        self.name = location_data.get("name")
        self.description = location_data.get("description")
        self.difficulty = location_data.get("difficulty", 0)
        self.element = location_data.get("element", "None")
        self.terrain = location_data.get("terrain", "unknown")
        self.enemies = location_data.get("enemies", [])
        self.connections = location_data.get("connections", {})
        self.treasure = location_data.get("treasure", [])
        self.npc = location_data.get("npc", None)
        
        self.enemies_data = enemies_data
    
    def describe(self) -> str:
        """Get basic location description.
        
        Returns:
            Location description string
        """
        desc = f"\n=== {self.name} ===\n{self.description}\n"
        return desc
    
    def describe_for(self, player: Any = None, check_access_fn = None) -> str:
        """Get extended location description with access info.
        
        Args:
            player: Player object (optional)
            check_access_fn: Function to check location access
        
        Returns:
            Extended description string
        """
        desc = f"\n=== {self.name} ===\n{self.description}\n"
        
        if player and check_access_fn:
            can_access, err = check_access_fn(player, self.id, self.element)
            if not can_access:
                desc += f"\n>>> BLOCCATO: {err} <<<\n"
        
        if self.connections:
            desc += "\nConnessioni:\n"
            for direction, loc_id in self.connections.items():
                if player and check_access_fn:
                    can_access, err = check_access_fn(player, loc_id, None)
                    if can_access:
                        desc += f"  - {direction}: {loc_id}\n"
                    else:
                        desc += f"  - {direction}: {loc_id} [BLOCCATO: {err}]\n"
                else:
                    desc += f"  - {direction}: {loc_id}\n"
        
        return desc
    
    def get_random_enemy(self) -> Optional[Enemy]:
        """Get a random enemy for this location.
        
        Returns:
            Random enemy or None if no enemies
        
        Raises:
            EnemyNotFound: If enemy ID not found in global data
        """
        if not self.enemies or not self.enemies_data:
            return None
        
        # Weight-based selection
        choice = random.choices(
            self.enemies,
            weights=[e.get("chance", 0.5) for e in self.enemies]
        )[0]
        
        enemy_id = choice.get("id")
        
        # Find enemy in global data
        for enemy_data in self.enemies_data.get("enemies", []):
            if enemy_data.get("id") == enemy_id:
                logger.debug(f"Spawned {enemy_id} at {self.id}")
                return Enemy(enemy_data, self.enemies_data)
        
        logger.warning(f"Enemy not found: {enemy_id}")
        raise EnemyNotFound(enemy_id)
