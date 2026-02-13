"""Combat package."""
from src.combat.event_engine import CombatEngine, CombatEvent, CombatEventType
from src.combat.cli_adapter import CombatCLIRenderer, create_fight_with_engine
from src.combat.damage_engine import DamageCalculator, DamageContext, DamageType, DamageResult
from src.combat.abilities import (
    AbilityDefinition,
    AbilitiesRegistry,
    init_abilities_registry,
    get_registry,
    apply_ability,
    apply_boss_ability_legacy,
)

__all__ = [
    "CombatEngine",
    "CombatEvent",
    "CombatEventType",
    "CombatCLIRenderer",
    "create_fight_with_engine",
    "DamageCalculator",
    "DamageContext",
    "DamageType",
    "DamageResult",
    "AbilityDefinition",
    "AbilitiesRegistry",
    "init_abilities_registry",
    "get_registry",
    "apply_ability",
    "apply_boss_ability_legacy",
]