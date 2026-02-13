"""
Abilities System - Data-Driven

Centralizes ability definitions and application via a registry.
Abilities are defined in data/abilities.json and loaded at startup.

This allows:
- Easy modification without code changes
- Reusable abilities across enemies and players
- Consistent damage calculation via DamageCalculator
- Future UI/tooltip generation from data
"""

import json
import os
import random
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class AbilityDefinition:
    """Represents a single ability."""
    id: str
    name: str
    description: str
    damage_multiplier: float = 1.0
    element: str = "None"
    effect_text: str = ""
    healing_multiplier: float = 0.0  # Heals caster for X% of boss max_hp
    mana_cost: int = 0
    cooldown: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def __repr__(self):
        return f"Ability({self.id}: {self.name}, dmg={self.damage_multiplier}x, elem={self.element})"


class AbilitiesRegistry:
    """
    Central registry for all abilities.
    
    Loads from data/abilities.json and provides lookup/iteration.
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize registry.
        
        Args:
            data_path: Path to abilities.json (auto-detected if None)
        """
        self.abilities: Dict[str, AbilityDefinition] = {}
        self.data_path = data_path or self._default_path()
        self._load()

    def _default_path(self) -> str:
        """Get default path to abilities.json relative to repo root."""
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(root, "data", "abilities.json")

    def _load(self):
        """Load abilities from JSON file."""
        if not os.path.exists(self.data_path):
            print(f"⚠️  Abilities file not found: {self.data_path}")
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading abilities: {e}")
            return

        # Parse abilities
        abilities_data = data.get("abilities", {})
        for ability_id, ability_dict in abilities_data.items():
            try:
                ability = AbilityDefinition(
                    id=ability_id,
                    name=ability_dict.get("name", ability_id),
                    description=ability_dict.get("description", ""),
                    damage_multiplier=ability_dict.get("damage_multiplier", 1.0),
                    element=ability_dict.get("element", "None"),
                    effect_text=ability_dict.get("effect_text", ""),
                    healing_multiplier=ability_dict.get("healing_multiplier", 0.0),
                    mana_cost=ability_dict.get("mana_cost", 0),
                    cooldown=ability_dict.get("cooldown", 0),
                    metadata=ability_dict.get("metadata", {}),
                )
                self.abilities[ability_id] = ability
            except Exception as e:
                print(f"⚠️  Error parsing ability {ability_id}: {e}")

    def get(self, ability_id: str) -> Optional[AbilityDefinition]:
        """Get ability by ID."""
        return self.abilities.get(ability_id)

    def has(self, ability_id: str) -> bool:
        """Check if ability exists."""
        return ability_id in self.abilities

    def list_all(self):
        """Return all abilities."""
        return list(self.abilities.values())

    def find_by_element(self, element: str) -> list:
        """Find all abilities of a specific element."""
        return [a for a in self.abilities.values() if a.element == element]

    def __repr__(self):
        return f"AbilitiesRegistry({len(self.abilities)} abilities)"


# Global registry instance
_registry: Optional[AbilitiesRegistry] = None


def init_abilities_registry(data_path: Optional[str] = None) -> AbilitiesRegistry:
    """Initialize the global abilities registry."""
    global _registry
    _registry = AbilitiesRegistry(data_path)
    return _registry


def get_registry() -> AbilitiesRegistry:
    """Get the global abilities registry."""
    global _registry
    if _registry is None:
        _registry = AbilitiesRegistry()
    return _registry


def apply_ability(
    caster,
    target,
    ability_id: str,
    damage_calculator=None,
) -> Tuple[int, str]:
    """
    Apply an ability from the registry.
    
    Args:
        caster: Character/Enemy using the ability
        target: Character/Enemy receiving the ability
        ability_id: ID of the ability to use
        damage_calculator: Optional DamageCalculator for damage computation
        
    Returns:
        Tuple of (damage, effect_text)
    """
    registry = get_registry()
    ability = registry.get(ability_id)

    if not ability:
        return 0, f"Unknown ability: {ability_id}"

    # Calculate damage
    if damage_calculator is not None:
        from src.combat.damage_engine import DamageContext, DamageType
        
        context = DamageContext(
            attacker=caster,
            defender=target,
            damage_type=DamageType.ABILITY,
            element=ability.element,
            ability_multiplier=ability.damage_multiplier,
            metadata={"ability_id": ability_id},
        )
        result = damage_calculator.calculate(context)
        damage = result.final_damage
    else:
        # Fallback: simple calculation without full damage pipeline
        base = int(caster.atk * ability.damage_multiplier * random.uniform(0.8, 1.2))
        damage = max(1, base)

    # Handle healing
    if ability.healing_multiplier > 0:
        heal = int(caster.max_hp * ability.healing_multiplier)
        caster.hp = min(caster.max_hp, caster.hp + heal)

    effect_text = ability.effect_text or f"{ability.name} is cast!"

    return damage, effect_text


# Legacy compatibility function (for rpg.py)
def apply_boss_ability_legacy(player, boss, ability_name: str) -> Tuple[int, str]:
    """
    Legacy wrapper for backward compatibility with rpg.py.
    
    This allows the old code to work without modification while using
    the new data-driven system under the hood.
    """
    return apply_ability(boss, player, ability_name)
