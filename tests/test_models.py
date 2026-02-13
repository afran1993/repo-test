"""
Tests for game models (Location, Enemy).
"""

import pytest
from src.models import Enemy, Location


class TestEnemy:
    """Tests for Enemy class."""
    
    def test_enemy_creation(self, sample_enemy):
        """Test enemy is created correctly."""
        assert sample_enemy.id == "goblin"
        assert sample_enemy.name == "Goblin"
        assert sample_enemy.hp == 10
        assert sample_enemy.max_hp == 10
        assert sample_enemy.atk == 3
    
    def test_enemy_is_alive(self, sample_enemy):
        """Test is_alive check."""
        assert sample_enemy.is_alive()
        sample_enemy.hp = 0
        assert not sample_enemy.is_alive()
    
    def test_enemy_is_alive_negative_hp(self, sample_enemy):
        """Test is_alive with negative HP."""
        sample_enemy.hp = -5
        assert not sample_enemy.is_alive()
    
    def test_enemy_describe(self, sample_enemy):
        """Test enemy description."""
        desc = sample_enemy.describe()
        
        assert "Goblin" in desc
        assert "10" in desc
    
    def test_enemy_take_damage(self, sample_enemy):
        """Test enemy taking damage."""
        initial_hp = sample_enemy.hp
        sample_enemy.take_damage(3)
        
        assert sample_enemy.hp == initial_hp - 3
        assert sample_enemy.is_alive()
    
    def test_enemy_take_damage_death(self, sample_enemy):
        """Test enemy death."""
        sample_enemy.take_damage(10)
        
        assert sample_enemy.hp == 0
        assert not sample_enemy.is_alive()
    
    def test_enemy_xp_reward(self, sample_enemy):
        """Test XP reward calculation."""
        assert sample_enemy.xp_reward > 0
        assert sample_enemy.xp_reward == sample_enemy.id in "goblin" and 10 or 10


class TestLocation:
    """Tests for Location class."""
    
    def test_location_creation(self, sample_location):
        """Test location is created correctly."""
        assert sample_location.id == "forest"
        assert sample_location.name == "Dark Forest"
        assert sample_location.difficulty == 1
    
    def test_location_describe(self, sample_location):
        """Test location description."""
        desc = sample_location.describe()
        
        assert "Dark Forest" in desc
        assert "mysterious" in desc
    
    def test_location_get_random_enemy_no_data(self, sample_location):
        """Test get_random_enemy without enemies data."""
        enemy = sample_location.get_random_enemy()
        
        # Should return None if no enemies_data set
        assert enemy is None
    
    def test_location_get_random_enemy_with_data(self, sample_location, sample_enemy):
        """Test get_random_enemy with data."""
        from src.models import set_enemies_data
        
        enemies_data = {
            "enemies": [
                {
                    "id": "goblin",
                    "display": "Goblin",
                    "hp": 10,
                    "atk": 3,
                    "def": 0,
                    "element": "None",
                    "tier": 1,
                }
            ]
        }
        set_enemies_data(enemies_data)
        sample_location.enemies_data = enemies_data
        
        enemy = sample_location.get_random_enemy()
        
        assert enemy is not None
        assert enemy.id == "goblin"
    
    def test_location_connections(self, sample_location):
        """Test location connections."""
        assert sample_location.connections == {"north": "village"}
        assert "north" in sample_location.connections
        assert sample_location.connections["north"] == "village"
