"""
Combat Engine - Decoupled from CLI

Pure business logic for turn-based RPG combat.
Emits CombatEvent objects instead of printing directly.

This allows:
- Unit testing
- CLI adaptation
- Future GUI/Web integration
- AI simulation
- Multiplayer/network support
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from enum import Enum

from src.combat.damage_engine import DamageCalculator, create_attack_damage, create_enemy_attack_damage
from src.config import get_config


class CombatEventType(Enum):
    """Types of combat events that can occur."""
    COMBAT_START = "combat_start"
    PLAYER_TURN = "player_turn"
    PLAYER_ATTACK = "player_attack"
    PLAYER_EVADED = "player_evaded"
    PLAYER_TOOK_DAMAGE = "player_took_damage"
    PLAYER_USED_POTION = "player_used_potion"
    PLAYER_FLED_SUCCESS = "player_fled_success"
    PLAYER_FLED_FAIL = "player_fled_fail"
    ENEMY_TURN = "enemy_turn"
    ENEMY_ATTACK = "enemy_attack"
    ENEMY_EVADED = "enemy_evaded"
    ENEMY_TOOK_DAMAGE = "enemy_took_damage"
    ENEMY_ABILITY = "enemy_ability"
    ELEMENT_ADVANTAGE = "element_advantage"
    ELEMENT_DISADVANTAGE = "element_disadvantage"
    COMBAT_END = "combat_end"
    COMBAT_VICTORY = "combat_victory"
    COMBAT_DEFEAT = "combat_defeat"
    LEVEL_UP = "level_up"


@dataclass
class CombatEvent:
    """Represents a single event during combat."""
    type: CombatEventType
    actor: str  # "player" or enemy.id or name
    target: str  # "player" or enemy.id or name
    message: str  # Human-readable message
    damage: int = 0
    healing: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"CombatEvent({self.type.value}: {self.message})"


class CombatEngine:
    """
    Decoupled combat system for turn-based RPG.
    
    Usage:
        engine = CombatEngine(player, enemy, element_modifier_fn)
        while not engine.is_finished():
            events = engine.step(user_action)
            for event in events:
                render(event)
    """

    def __init__(
        self,
        player,
        enemy,
        element_modifier_fn: Callable[[str, str], float],
        apply_ability_fn: Optional[Callable[[Any, Any, str], tuple]] = None,
        is_boss: bool = False,
        current_location: Optional[Any] = None,
        damage_calculator: Optional[DamageCalculator] = None,
    ):
        """
        Initialize combat engine.
        
        Args:
            player: Player object with HP, attack, defense, etc.
            enemy: Enemy object
            element_modifier_fn: Function(attacker_element, defender_element) -> float
            apply_ability_fn: Optional function(player, boss, ability_name) -> (damage, effect_text)
            is_boss: Whether enemy is a boss
            current_location: Optional location context
            damage_calculator: Optional DamageCalculator instance (creates default if None)
        """
        self.player = player
        self.enemy = enemy
        self.element_modifier_fn = element_modifier_fn
        self.apply_ability_fn = apply_ability_fn
        self.is_boss = is_boss
        self.current_location = current_location
        
        # Use provided damage calculator or create default
        self.damage_calculator = damage_calculator or DamageCalculator(
            element_modifier_fn=element_modifier_fn
        )
        
        self.turn = 0
        self.events: List[CombatEvent] = []
        self.finished = False
        self.victory = False
        
        # Store initial HP for potential resets
        self.initial_player_hp = player.hp
        self.initial_enemy_hp = enemy.hp
        
        self._start_combat()

    def _start_combat(self):
        """Emit initial combat start event."""
        event = CombatEvent(
            type=CombatEventType.COMBAT_START,
            actor="system",
            target="system",
            message=f"Combat start: {self.player.name} vs {self.enemy.name}",
            metadata={
                "player_hp": self.player.hp,
                "enemy_hp": self.enemy.hp,
                "enemy_element": getattr(self.enemy, "element", "None"),
                "is_boss": self.is_boss,
            }
        )
        self.events = [event]

    def is_finished(self) -> bool:
        """Check if combat has ended."""
        return self.finished

    def is_won(self) -> bool:
        """Check if player won."""
        return self.victory

    def step(self, action: str) -> List[CombatEvent]:
        """
        Execute one turn of combat based on player action.
        
        Args:
            action: "attack", "potion:<potion_type>", "flee"
            
        Returns:
            List of CombatEvent objects describing what happened
        """
        self.events = []
        
        if self.finished:
            return self.events

        # ========== PLAYER TURN ==========
        self.events.append(
            CombatEvent(
                type=CombatEventType.PLAYER_TURN,
                actor="player",
                target=self.enemy.name,
                message=f"{self.player.name}'s turn",
            )
        )

        if action == "attack":
            self._player_attack()
        elif action.startswith("potion:"):
            potion_type = action.split(":", 1)[1]
            self._player_use_potion(potion_type)
        elif action == "flee":
            self._player_flee()
        else:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.PLAYER_TURN,
                    actor="player",
                    target="system",
                    message=f"Invalid action: {action}",
                )
            )

        # Check if enemy is dead after player action
        if not self.enemy.is_alive():
            self._end_combat(victory=True)
            return self.events

        # ========== ENEMY TURN ==========
        if not self.finished:
            self._enemy_turn()

        # Check if player is dead after enemy action
        if not self.player.is_alive():
            self._end_combat(victory=False)
            return self.events

        self.turn += 1
        return self.events

    def _player_attack(self):
        """Handle player attack action (unified damage calculation)."""
        # Use centralized damage calculator
        damage_result = create_attack_damage(self.damage_calculator, self.player, self.enemy)
        dmg = damage_result.final_damage

        # Log element advantage/disadvantage
        if damage_result.vulnerable:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.ELEMENT_ADVANTAGE,
                    actor="player",
                    target=self.enemy.name,
                    message="It's super effective!",
                    metadata={
                        "modifier": damage_result.element_modifier,
                        "reaction": damage_result.element_reaction,
                    },
                )
            )
        elif damage_result.resisted:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.ELEMENT_DISADVANTAGE,
                    actor="player",
                    target=self.enemy.name,
                    message="It's not very effective...",
                    metadata={"modifier": damage_result.element_modifier},
                )
            )

        # Enemy evasion
        cfg = get_config()
        evasion_chance = cfg.combat.BASE_EVASION
        if self.is_boss:
            evasion_chance = max(0.0, cfg.combat.BASE_EVASION * 0.75)

        if random.random() < evasion_chance:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.PLAYER_EVADED,
                    actor="player",
                    target=self.enemy.name,
                    message=f"{self.enemy.name} evades the attack!",
                )
            )
        else:
            self.enemy.hp = max(0, self.enemy.hp - dmg)
            self.events.append(
                CombatEvent(
                    type=CombatEventType.PLAYER_ATTACK,
                    actor="player",
                    target=self.enemy.name,
                    message=f"Hit {self.enemy.name} for {dmg} damage",
                    damage=dmg,
                    metadata={
                        "enemy_hp": self.enemy.hp,
                        "enemy_max_hp": self.enemy.max_hp,
                        "damage_breakdown": {
                            "base": damage_result.base_damage,
                            "defense": damage_result.defense_reduction,
                            "element_mod": damage_result.element_modifier,
                        },
                    },
                )
            )

    def _player_use_potion(self, potion_type: str):
        """Handle player using a potion."""
        if potion_type not in self.player.potions or self.player.potions[potion_type] <= 0:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.PLAYER_USED_POTION,
                    actor="player",
                    target="player",
                    message=f"No {potion_type} available",
                )
            )
            return

        # Use potion
        healed = self.player.use_potion(potion_type)
        self.events.append(
            CombatEvent(
                type=CombatEventType.PLAYER_USED_POTION,
                actor="player",
                target="player",
                message=f"Used {potion_type} and recovered {healed} HP",
                healing=healed,
                metadata={"player_hp": self.player.hp, "player_max_hp": self.player.max_hp},
            )
        )

    def _player_flee(self):
        """Handle player flee attempt."""
        cfg = get_config()
        # Bosses are harder to flee from; leave a configurable multiplier
        if self.is_boss:
            flee_chance = max(0.0, cfg.combat.FLEE_CHANCE * 0.4)
        else:
            flee_chance = cfg.combat.FLEE_CHANCE

        if random.random() < flee_chance:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.PLAYER_FLED_SUCCESS,
                    actor="player",
                    target="system",
                    message="Fled successfully!",
                )
            )
            self.finished = True
            self.victory = False
        else:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.PLAYER_FLED_FAIL,
                    actor="player",
                    target=self.enemy.name,
                    message=f"Failed to flee from {self.enemy.name}!",
                )
            )

    def _enemy_turn(self):
        """Handle enemy turn."""
        self.events.append(
            CombatEvent(
                type=CombatEventType.ENEMY_TURN,
                actor=self.enemy.name,
                target="player",
                message=f"{self.enemy.name}'s turn",
            )
        )

        # Boss ability logic
        should_use_ability = False
        ability_name = None

        cfg = get_config()
        if self.is_boss and self.turn > 0 and self.turn % cfg.combat.BOSS_ABILITY_INTERVAL == 0:
            abilities = getattr(self.enemy, "abilities", [])
            if abilities and self.apply_ability_fn:
                ability_name = random.choice(abilities)
                should_use_ability = True

        if should_use_ability and ability_name and self.apply_ability_fn:
            self._enemy_use_ability(ability_name)
        else:
            self._enemy_basic_attack()

    def _enemy_use_ability(self, ability_name: str):
        """Handle enemy using special ability."""
        # Call the ability function
        edmg, effect_text = self.apply_ability_fn(self.player, self.enemy, ability_name)

        self.events.append(
            CombatEvent(
                type=CombatEventType.ENEMY_ABILITY,
                actor=self.enemy.name,
                target="player",
                message=f"{self.enemy.name} uses {ability_name}!",
                metadata={"ability": ability_name, "effect": effect_text},
            )
        )

        if edmg > 0:
            # Player evasion (harder to evade abilities)
            if random.random() < self.player.get_evasion_chance() * 0.7:
                self.events.append(
                    CombatEvent(
                        type=CombatEventType.ENEMY_EVADED,
                        actor="player",
                        target=self.enemy.name,
                        message=f"Evaded {self.enemy.name}'s ability!",
                    )
                )
            else:
                self.player.hp = max(0, self.player.hp - edmg)
                self.events.append(
                    CombatEvent(
                        type=CombatEventType.PLAYER_TOOK_DAMAGE,
                        actor=self.enemy.name,
                        target="player",
                        message=f"{self.enemy.name} dealt {edmg} damage!",
                        damage=edmg,
                        metadata={"player_hp": self.player.hp, "player_max_hp": self.player.max_hp},
                    )
                )

    def _enemy_basic_attack(self):
        """Handle enemy basic attack (unified damage calculation)."""
        # Use centralized damage calculator
        damage_result = create_enemy_attack_damage(self.damage_calculator, self.enemy, self.player)
        edmg = damage_result.final_damage

        if damage_result.vulnerable:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.ELEMENT_ADVANTAGE,
                    actor=self.enemy.name,
                    target="player",
                    message=f"{self.enemy.name}'s attack is super effective!",
                    metadata={
                        "modifier": damage_result.element_modifier,
                        "reaction": damage_result.element_reaction,
                    },
                )
            )

        # Player evasion
        if random.random() < self.player.get_evasion_chance():
            self.events.append(
                CombatEvent(
                    type=CombatEventType.ENEMY_EVADED,
                    actor="player",
                    target=self.enemy.name,
                    message=f"Evaded {self.enemy.name}'s attack!",
                )
            )
        else:
            self.player.hp = max(0, self.player.hp - edmg)
            self.events.append(
                CombatEvent(
                    type=CombatEventType.PLAYER_TOOK_DAMAGE,
                    actor=self.enemy.name,
                    target="player",
                    message=f"{self.enemy.name} dealt {edmg} damage",
                    damage=edmg,
                    metadata={
                        "player_hp": self.player.hp,
                        "player_max_hp": self.player.max_hp,
                        "damage_breakdown": {
                            "base": damage_result.base_damage,
                            "defense": damage_result.defense_reduction,
                            "element_mod": damage_result.element_modifier,
                        },
                    },
                )
            )

    def _end_combat(self, victory: bool):
        """End combat and emit victory/defeat event."""
        self.finished = True
        self.victory = victory

        if victory:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.COMBAT_VICTORY,
                    actor="player",
                    target=self.enemy.name,
                    message=f"Defeated {self.enemy.name}!",
                    metadata={
                        "gold_reward": self.enemy.gold_reward,
                        "xp_reward": self.enemy.xp_reward,
                    },
                )
            )
        else:
            self.events.append(
                CombatEvent(
                    type=CombatEventType.COMBAT_DEFEAT,
                    actor=self.enemy.name,
                    target="player",
                    message=f"Defeated by {self.enemy.name}",
                )
            )
