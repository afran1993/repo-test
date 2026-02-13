"""
Tests for player system.
"""

import pytest
from src.players import Player


class TestPlayer:
    """Tests for Player class."""
    
    def test_player_creation(self, sample_player):
        """Test player is created with correct defaults."""
        assert sample_player.name == "TestHero"
        assert sample_player.level == 1
        assert sample_player.hp == 30
        assert sample_player.max_hp == 30
        assert sample_player.atk == 6
        assert sample_player.dex == 5
        assert sample_player.gold == 50
    
    def test_player_is_alive(self, sample_player):
        """Test is_alive check."""
        assert sample_player.is_alive()
        sample_player.hp = 0
        assert not sample_player.is_alive()
    
    def test_player_gain_xp_no_levelup(self, sample_player):
        """Test gaining XP without level up."""
        initial_level = sample_player.level
        sample_player.gain_xp(5)
        assert sample_player.level == initial_level
        assert sample_player.xp == 5
    
    def test_player_gain_xp_with_levelup(self, sample_player):
        """Test level up from XP."""
        # Level 1 requires 12 XP to level up
        initial_level = sample_player.level
        initial_atk = sample_player.atk
        
        leveled = sample_player.gain_xp(12)
        
        assert leveled is True
        assert sample_player.level == initial_level + 1
        assert sample_player.atk == initial_atk + 2
        assert sample_player.xp == 0  # XP should reset after level up
    
    def test_player_gain_xp_multiple_levelups(self, sample_player):
        """Test multiple level ups at once."""
        leveled = sample_player.gain_xp(50)  # Should trigger multiple level ups
        
        assert leveled is True
        assert sample_player.level > 1
        # Can have enough XP for next level after multiple levelups
    
    def test_player_use_potion(self, sample_player):
        """Test using a potion."""
        sample_player.hp = 10  # Reduce HP
        sample_player.potions["potion_small"] = 1
        
        heal = sample_player.use_potion("potion_small")
        
        assert heal == 12
        assert sample_player.hp == 22
        assert sample_player.potions["potion_small"] == 0
    
    def test_player_use_potion_healing_cap(self, sample_player):
        """Test that potion healing is capped at max HP."""
        sample_player.hp = 25
        sample_player.potions["potion_small"] = 1
        
        heal = sample_player.use_potion("potion_small")
        
        # Should only heal 5 HP to reach max
        assert sample_player.hp == 30
    
    def test_player_use_potion_no_potion(self, sample_player):
        """Test using a potion when none available."""
        sample_player.potions["potion_small"] = 0
        
        heal = sample_player.use_potion("potion_small")
        
        # Returns 0 when no potion available
        assert heal == 0
    
    def test_player_status_string(self, sample_player):
        """Test status string generation."""
        status = sample_player.status()
        
        assert "TestHero" in status
        assert str(sample_player.level) in status
        assert str(sample_player.hp) in status
    
    def test_player_get_total_max_hp(self, sample_player):
        """Test max HP calculation."""
        max_hp = sample_player.get_total_max_hp()
        
        assert max_hp == sample_player.max_hp
        assert max_hp > 0
    
    def test_player_get_total_atk(self, sample_player):
        """Test ATK calculation without equipment."""
        atk = sample_player.get_total_atk()
        
        assert atk == sample_player.atk
    
    def test_player_equip_weapon(self, sample_player):
        """Test equipping a weapon."""
        weapon = {"id": "sword", "name": "Sword", "atk": 5}
        sample_player.equipped_weapon = weapon
        
        total_atk = sample_player.get_total_atk()
        
        assert total_atk == sample_player.atk + weapon["atk"]
    
    def test_player_equip_accessory(self, sample_player):
        """Test equipping an accessory."""
        accessory = {
            "id": "ring",
            "name": "Ring of Strength",
            "slot": "ring",
            "stats": {"atk": 3}
        }
        sample_player.accessories["ring"] = accessory
        
        total_atk = sample_player.get_total_atk()
        
        assert total_atk == sample_player.atk + 3
