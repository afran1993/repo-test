"""
Tests for damage engine.
"""

import pytest
from src.combat.damage_engine import DamageContext, DamageType
from src.players import Player
from src.models import Enemy


class TestDamageContext:
    """Tests for DamageContext dataclass."""
    
    def test_damage_context_creation(self, sample_player, sample_enemy):
        """Test DamageContext is created correctly."""
        context = DamageContext(
            attacker=sample_player,
            defender=sample_enemy,
            damage_type=DamageType.PHYSICAL,
            base_damage=10
        )
        
        assert context.attacker == sample_player
        assert context.defender == sample_enemy
        assert context.damage_type == DamageType.PHYSICAL
        assert context.base_damage == 10
        assert context.ability_multiplier == 1.0
        assert context.element == "None"
    
    def test_damage_context_with_element(self, sample_player, sample_enemy):
        """Test DamageContext with element."""
        context = DamageContext(
            attacker=sample_player,
            defender=sample_enemy,
            element="Fire"
        )
        
        assert context.element == "Fire"
    
    def test_damage_context_with_multiplier(self, sample_player, sample_enemy):
        """Test DamageContext with ability multiplier."""
        context = DamageContext(
            attacker=sample_player,
            defender=sample_enemy,
            ability_multiplier=1.5
        )
        
        assert context.ability_multiplier == 1.5


class TestDamageCalculation:
    """Tests for damage calculation engine."""
    
    def test_context_ignore_flags(self, sample_player, sample_enemy):
        """Test ignore flags in context."""
        context = DamageContext(
            attacker=sample_player,
            defender=sample_enemy,
            ignore_defense=True,
            ignore_resistance=True
        )
        
        assert context.ignore_defense is True
        assert context.ignore_resistance is True
