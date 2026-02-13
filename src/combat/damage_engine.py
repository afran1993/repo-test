"""
Unified Damage Pipeline

Centralizes all damage calculations in the game:
- Player attacks
- Enemy attacks  
- Special abilities
- Elemental modifiers
- Resistances and vulnerabilities

This ensures:
- Consistent damage computation across all systems
- Easy to balance and test
- Support for modifiers and reactions
"""

import random
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class DamageType(Enum):
    """Type of damage being dealt."""
    PHYSICAL = "physical"
    SPELL = "spell"
    ABILITY = "ability"
    STATUS = "status"


@dataclass
class DamageContext:
    """
    Complete damage calculation context.
    
    Contains all information needed to calculate damage consistently
    across different systems (player attacks, enemy attacks, abilities).
    """
    attacker: Any  # Character or Enemy object
    defender: Any  # Character or Enemy object
    
    damage_type: DamageType = DamageType.PHYSICAL
    base_damage: Optional[int] = None  # If provided, use this instead of calculating from attacker stats
    element: str = "None"  # Element type
    ability_multiplier: float = 1.0  # For special abilities (can be > 1.0)
    
    # Optional overrides
    ignore_defense: bool = False
    ignore_resistance: bool = False
    ignore_reaction: bool = False
    
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return (
            f"DamageContext({self.attacker.name if hasattr(self.attacker, 'name') else 'attacker'} "
            f"→ {self.defender.name if hasattr(self.defender, 'name') else 'defender'}, "
            f"{self.damage_type.value}, elem={self.element}, mult={self.ability_multiplier})"
        )


@dataclass
class DamageResult:
    """Result of damage calculation."""
    base_damage: int
    defense_reduction: int
    element_modifier: float
    reaction_modifier: float
    ability_multiplier: float
    
    final_damage: int
    
    # Breakdown metadata
    element_reaction: Optional[str] = None
    resisted: bool = False
    vulnerable: bool = False
    
    def __repr__(self):
        return (
            f"DamageResult(base={self.base_damage}, def_red={self.defense_reduction}, "
            f"elem_mod={self.element_modifier:.2f}, react_mod={self.reaction_modifier:.2f}, "
            f"final={self.final_damage})"
        )


class DamageCalculator:
    """
    Centralized damage calculation engine.
    
    Applies modifiers in consistent order:
    1. Base damage (from stats or parameter)
    2. Defense reduction
    3. Elemental modifier
    4. Reaction bonus/penalty
    5. Ability multiplier
    6. Final clamp to max(1, damage)
    """

    def __init__(
        self,
        element_modifier_fn=None,
        reaction_fn=None,
    ):
        """
        Initialize damage calculator.
        
        Args:
            element_modifier_fn: Function(attack_element, defender_resistances) -> float
            reaction_fn: Function(element_a, element_b) -> (has_reaction, reaction_dict)
        """
        self.element_modifier_fn = element_modifier_fn or self._default_element_modifier
        self.reaction_fn = reaction_fn or self._default_reaction

    def calculate(self, context: DamageContext) -> DamageResult:
        """
        Calculate damage according to context.
        
        Args:
            context: DamageContext with attack/defense information
            
        Returns:
            DamageResult with full breakdown
        """
        # ========== STEP 1: Base Damage ==========
        if context.base_damage is not None:
            base_dmg = context.base_damage
        else:
            base_dmg = self._calculate_base_damage(context)

        # ========== STEP 2: Defense Reduction ==========
        defense_reduction = 0
        if not context.ignore_defense:
            defense_reduction = self._calculate_defense_reduction(context)
        
        damage_after_defense = max(1, base_dmg - defense_reduction)

        # ========== STEP 3: Elemental Modifier ==========
        element_modifier = 1.0
        if not context.ignore_resistance and context.element != "None":
            defender_resistances = getattr(context.defender, "resistances", {})
            element_modifier = self.element_modifier_fn(context.element, defender_resistances)

        damage_after_element = int(damage_after_defense * element_modifier)

        # ========== STEP 4: Reaction Modifier ==========
        reaction_modifier = 1.0
        element_reaction = None
        
        if not context.ignore_reaction and context.element != "None":
            defender_element = getattr(context.defender, "element", "None")
            has_reaction, reaction = self.reaction_fn(context.element, defender_element)
            if has_reaction:
                reaction_modifier = reaction.get("modifier", 1.0)
                element_reaction = reaction.get("name", "")

        damage_after_reaction = int(damage_after_element * reaction_modifier)

        # ========== STEP 5: Ability Multiplier ==========
        if context.ability_multiplier != 1.0:
            damage_after_ability = int(damage_after_reaction * context.ability_multiplier)
        else:
            damage_after_ability = damage_after_reaction

        # ========== STEP 6: Final Clamp ==========
        final_damage = max(1, damage_after_ability)

        # ========== DETERMINE FLAGS ==========
        resisted = element_modifier < 1.0
        vulnerable = element_modifier > 1.0

        return DamageResult(
            base_damage=base_dmg,
            defense_reduction=defense_reduction,
            element_modifier=element_modifier,
            reaction_modifier=reaction_modifier,
            ability_multiplier=context.ability_multiplier,
            final_damage=final_damage,
            element_reaction=element_reaction,
            resisted=resisted,
            vulnerable=vulnerable,
        )

    def _calculate_base_damage(self, context: DamageContext) -> int:
        """Calculate base damage from attacker stats."""
        attacker = context.attacker
        
        if context.damage_type == DamageType.SPELL:
            # Spell damage uses INT/magic_power instead of STR
            base = getattr(attacker, "spell_power", 5)
            rng = random.randint(max(1, base - 1), base + 1)
        else:
            # Physical damage
            # Get total ATK including equipment bonuses
            if hasattr(attacker, "get_total_atk"):
                # Player-like object
                total_atk = attacker.get_total_atk()
            else:
                # Enemy-like object
                total_atk = getattr(attacker, "atk", 5)
            
            rng = random.randint(max(1, total_atk - 2), total_atk + 2)
        
        return rng

    def _calculate_defense_reduction(self, context: DamageContext) -> int:
        """Calculate damage reduction from defender's defense."""
        defender = context.defender
        
        # Get defender's defense/endurance
        if hasattr(defender, "get_total_def"):
            total_def = defender.get_total_def()
        elif hasattr(defender, "stats"):
            # Character-like with stats dict
            total_def = int(defender.stats.get("end", 3) * 0.5)
        else:
            # Enemy-like object
            total_def = int(getattr(defender, "def", 0) * 0.5)
        
        return total_def

    def _default_element_modifier(self, attack_element: str, defender_resistances: Dict) -> float:
        """
        Default element modifier function.
        
        If not provided, uses simple resistance model:
        resist value of 0.2 means 20% damage reduction.
        """
        if not attack_element or attack_element == "None":
            return 1.0
        
        resist = defender_resistances.get(attack_element, 0.0)
        # Positive resist reduces damage; negative (vulnerability) increases
        base = max(0.0, 1.0 - resist)
        return base

    def _default_reaction(self, element_a: str, element_b: str):
        """
        Default reaction function - no reactions.
        Override with actual reaction system if available.
        """
        return False, {}


# ========== Convenience Functions ==========


def create_attack_damage(calculator: DamageCalculator, attacker, defender) -> DamageResult:
    """
    Calculate damage for a basic melee attack.
    
    Args:
        calculator: DamageCalculator instance
        attacker: Attacking character
        defender: Defending character
        
    Returns:
        DamageResult with full breakdown
    """
    weapon_element = "None"
    if hasattr(attacker, "equipped_weapon") and attacker.equipped_weapon:
        weapon_element = attacker.equipped_weapon.get("element", "None")
    
    context = DamageContext(
        attacker=attacker,
        defender=defender,
        damage_type=DamageType.PHYSICAL,
        element=weapon_element,
    )
    
    return calculator.calculate(context)


def create_ability_damage(
    calculator: DamageCalculator,
    attacker,
    defender,
    ability_name: str,
    ability_multiplier: float = 1.5,
    ability_element: str = "None",
) -> DamageResult:
    """
    Calculate damage for a special ability.
    
    Args:
        calculator: DamageCalculator instance
        attacker: Attacking character
        defender: Defending character
        ability_name: Name of the ability
        ability_multiplier: Damage multiplier for the ability
        ability_element: Element associated with the ability
        
    Returns:
        DamageResult with full breakdown
    """
    context = DamageContext(
        attacker=attacker,
        defender=defender,
        damage_type=DamageType.ABILITY,
        element=ability_element,
        ability_multiplier=ability_multiplier,
        metadata={"ability_name": ability_name},
    )
    
    return calculator.calculate(context)


def create_enemy_attack_damage(calculator: DamageCalculator, enemy, defender) -> DamageResult:
    """
    Calculate damage for an enemy basic attack.
    
    Args:
        calculator: DamageCalculator instance
        enemy: Enemy object
        defender: Defending character
        
    Returns:
        DamageResult with full breakdown
    """
    enemy_element = getattr(enemy, "element", "None")
    
    context = DamageContext(
        attacker=enemy,
        defender=defender,
        damage_type=DamageType.PHYSICAL,
        element=enemy_element,
    )
    
    return calculator.calculate(context)
