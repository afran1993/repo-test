"""
Tests for game persistence (save/load).
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from src.persistence import save_game, load_game, hospital
from src.players import Player


class TestPersistence:
    """Tests for save/load persistence."""
    
    @pytest.fixture
    def temp_save_path(self):
        """Create a temporary save file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = f.name
        yield path
        # Cleanup
        if os.path.exists(path):
            os.remove(path)
    
    def test_save_game(self, sample_player, temp_save_path):
        """Test saving a game."""
        sample_player.language = "it"
        sample_player.current_location = "forest"
        
        save_game(sample_player, path=temp_save_path)
        
        assert os.path.exists(temp_save_path)
        
        with open(temp_save_path, 'r') as f:
            data = json.load(f)
        
        assert data["name"] == "TestHero"
        assert data["level"] == sample_player.level
        assert data["gold"] == sample_player.gold
        assert data["language"] == "it"
    
    def test_save_game_persists_equipment(self, sample_player, temp_save_path):
        """Test that equipment is saved."""
        sample_player.equipped_weapon = {"id": "sword", "name": "Sword", "atk": 5}
        
        save_game(sample_player, path=temp_save_path)
        
        with open(temp_save_path, 'r') as f:
            data = json.load(f)
        
        assert data["equipped_weapon"] is not None
        assert data["equipped_weapon"]["id"] == "sword"
    
    def test_load_game(self, sample_player, temp_save_path):
        """Test loading a game."""
        sample_player.language = "it"
        sample_player.current_location = "village"
        sample_player.gold = 100
        sample_player.level = 5
        
        save_game(sample_player, path=temp_save_path)
        loaded_player = load_game(path=temp_save_path)
        
        assert loaded_player is not None
        assert loaded_player.name == "TestHero"
        assert loaded_player.gold == 100
        assert loaded_player.level == 5
        assert loaded_player.current_location == "village"
        assert loaded_player.language == "it"
    
    def test_load_game_nonexistent_file(self):
        """Test loading from nonexistent file."""
        player = load_game(path="/nonexistent/path.json")
        
        assert player is None
    
    def test_load_game_corrupted_file(self, temp_save_path):
        """Test loading from corrupted JSON file."""
        with open(temp_save_path, 'w') as f:
            f.write("{ invalid json")
        
        player = load_game(path=temp_save_path)
        
        assert player is None
    
    def test_hospital_heals_player(self, sample_player):
        """Test hospital function heals player."""
        sample_player.hp = 5
        initial_max_hp = sample_player.get_total_max_hp()
        
        hospital(sample_player)
        
        assert sample_player.hp == initial_max_hp
    
    def test_hospital_deducts_gold(self, sample_player):
        """Test hospital deducts gold penalty."""
        sample_player.gold = 100
        initial_gold = sample_player.gold
        
        hospital(sample_player)
        
        # Should lose 1/3 of gold (minimum 5)
        penalty = max(5, initial_gold // 3)
        assert sample_player.gold == initial_gold - penalty
    
    def test_hospital_gold_protection_minimum(self):
        """Test hospital doesn't go negative on gold."""
        player = Player("TestHero")
        player.gold = 0
        
        hospital(player)
        
        assert player.gold == 0
    
    def test_hospital_maintains_other_stats(self, sample_player):
        """Test hospital doesn't change other stats."""
        sample_player.level = 5
        sample_player.xp = 50
        initial_level = sample_player.level
        initial_xp = sample_player.xp
        
        hospital(sample_player)
        
        assert sample_player.level == initial_level
        assert sample_player.xp == initial_xp
