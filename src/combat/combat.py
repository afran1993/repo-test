"""Light compatibility layer for combat utilities.

This module provides two convenience functions kept for backward
compatibility with older imports:

- `calculate_damage(attacker, defender, ...)` -> returns integer damage
- `turn_based_fight(player, enemy, engine=None)` -> runs a CLI fight loop

Internally the project uses the event-driven `CombatEngine` and the
`CombatCLIRenderer` adapter in `src.combat.event_engine` and
`src.combat.cli_adapter`. This module delegates to those implementations
so other modules that import `src.combat.combat` keep working.
"""

from src.combat.damage_engine import DamageCalculator, create_attack_damage, create_enemy_attack_damage
from src.combat.event_engine import CombatEngine
from src.combat.cli_adapter import create_fight_with_engine
from src.elements.elements import element_modifier
from src.combat.abilities import apply_ability


def calculate_damage(attacker, defender, base=5, element=None):
    """Return an estimated damage value for a basic attack.

    This delegates to the centralized `DamageCalculator` pipeline and
    returns the final integer damage.
    """
    calc = DamageCalculator(element_modifier_fn=element_modifier)
    # Use create_attack_damage for player-like attackers, otherwise enemy
    try:
        # If attacker has get_total_atk assume player-like
        if hasattr(attacker, 'get_total_atk'):
            res = create_attack_damage(calc, attacker, defender)
        else:
            res = create_enemy_attack_damage(calc, attacker, defender)
        return res.final_damage
    except Exception:
        # Fallback simple formula
        base_atk = getattr(attacker, 'atk', getattr(attacker, 'stats', {}).get('str', 5))
        defense = getattr(defender, 'def', getattr(defender, 'stats', {}).get('end', 3))
        raw = max(1, base_atk - int(defense * 0.5))
        return max(1, int(raw))


def turn_based_fight(player, enemy, engine=None):
    """Run a CLI fight using the event-driven engine and CLI adapter.

    This keeps the old function signature while delegating behaviour to
    `CombatEngine` and `create_fight_with_engine`.
    """
    from src.elements.elements import element_modifier as _elem

    engine_instance = CombatEngine(
        player=player,
        enemy=enemy,
        element_modifier_fn=_elem,
        apply_ability_fn=apply_ability,
        damage_calculator=None,
    )

    return create_fight_with_engine(engine_instance, player, enemy)
