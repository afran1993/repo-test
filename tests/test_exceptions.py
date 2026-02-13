"""
Tests for custom exception classes.

Validates that exceptions are properly raised and contain correct context.
"""

import pytest
from src.exceptions import (
    GameException,
    GameStateError,
    PlayerException,
    InsufficientGold,
    LocationNotFound,
    NPCNotFound,
    EnemyNotFound,
    SaveNotFound,
    CorruptedSave,
    LoadFailed,
    SaveFailed,
    is_game_exception,
)


class TestGameException:
    """Test base GameException."""
    
    def test_game_exception_creation(self):
        """Test creating base GameException."""
        exc = GameException("Test error")
        assert exc.message == "Test error"
        assert exc.context == {}
    
    def test_game_exception_with_context(self):
        """Test GameException with context."""
        context = {"player_id": 1, "location": "beach"}
        exc = GameException("Test error", context)
        assert exc.message == "Test error"
        assert exc.context == context


class TestGameStateExceptions:
    """Test game state exceptions."""
    
    def test_game_not_started(self):
        """Test GameNotStarted exception."""
        from src.exceptions import GameNotStarted
        exc = GameNotStarted()
        assert "not been started" in exc.message


class TestPlayerExceptions:
    """Test player-related exceptions."""
    
    def test_insufficient_gold(self):
        """Test InsufficientGold exception."""
        exc = InsufficientGold(100, 50)
        assert exc.context["required"] == 100
        assert exc.context["have"] == 50
        assert "100" in exc.message
        assert "50" in exc.message
    
    def test_insufficient_xp(self):
        """Test InsufficientXP exception."""
        from src.exceptions import InsufficientXP
        exc = InsufficientXP(200, 150)
        assert exc.context["required"] == 200
        assert exc.context["have"] == 150


class TestLocationExceptions:
    """Test location-related exceptions."""
    
    def test_location_not_found(self):
        """Test LocationNotFound exception."""
        exc = LocationNotFound("forest")
        assert exc.context["location_id"] == "forest"
        assert "forest" in exc.message
    
    def test_invalid_connection(self):
        """Test InvalidConnection exception."""
        from src.exceptions import InvalidConnection
        exc = InvalidConnection("beach", "north")
        assert exc.context["from_id"] == "beach"
        assert exc.context["direction"] == "north"


class TestNPCExceptions:
    """Test NPC-related exceptions."""
    
    def test_npc_not_found(self):
        """Test NPCNotFound exception."""
        exc = NPCNotFound("merchant_001")
        assert exc.context["npc_id"] == "merchant_001"
        assert "merchant_001" in exc.message


class TestCombatExceptions:
    """Test combat-related exceptions."""
    
    def test_enemy_not_found(self):
        """Test EnemyNotFound exception."""
        exc = EnemyNotFound("goblin_boss")
        assert exc.context["enemy_id"] == "goblin_boss"
        assert "goblin_boss" in exc.message
    
    def test_combat_error(self):
        """Test CombatError exception."""
        from src.exceptions import CombatError
        exc = CombatError("Invalid state")
        assert exc.message == "Combat error: Invalid state"
    
    def test_invalid_action(self):
        """Test InvalidAction exception."""
        from src.exceptions import InvalidAction
        exc = InvalidAction("fireball", "mana too low")
        assert exc.context["action"] == "fireball"
        assert exc.context["reason"] == "mana too low"
    
    def test_insufficient_mana(self):
        """Test InsufficientMana exception."""
        from src.exceptions import InsufficientMana
        exc = InsufficientMana(50, 20)
        assert exc.context["required"] == 50
        assert exc.context["have"] == 20


class TestPersistenceExceptions:
    """Test save/load exceptions."""
    
    def test_save_failed(self):
        """Test SaveFailed exception."""
        exc = SaveFailed("Disk full")
        assert exc.message == "Save failed: Disk full"
    
    def test_load_failed(self):
        """Test LoadFailed exception."""
        exc = LoadFailed("File permissions")
        assert exc.message == "Load failed: File permissions"
    
    def test_save_not_found(self):
        """Test SaveNotFound exception."""
        exc = SaveNotFound("autosave")
        assert exc.context["save_name"] == "autosave"
        assert "autosave" in exc.message
    
    def test_corrupted_save(self):
        """Test CorruptedSave exception."""
        exc = CorruptedSave("save.json", "Missing level field")
        assert exc.context["save_name"] == "save.json"
        assert exc.context["reason"] == "Missing level field"


class TestExceptionHierarchy:
    """Test exception class hierarchy."""
    
    def test_insufficient_gold_is_player_exception(self):
        """Test that InsufficientGold is a PlayerException."""
        exc = InsufficientGold(100, 50)
        assert isinstance(exc, PlayerException)
        assert isinstance(exc, GameException)
    
    def test_location_not_found_is_location_exception(self):
        """Test that LocationNotFound is a LocationException."""
        from src.exceptions import LocationException
        exc = LocationNotFound("forest")
        assert isinstance(exc, LocationException)
        assert isinstance(exc, GameException)
    
    def test_game_state_error_is_game_exception(self):
        """Test that GameStateError is a GameException."""
        exc = GameStateError("Test")
        assert isinstance(exc, GameException)


class TestExceptionUtility:
    """Test exception utility functions."""
    
    def test_is_game_exception_true(self):
        """Test is_game_exception returns True for game exceptions."""
        exc = LocationNotFound("forest")
        assert is_game_exception(exc) is True
    
    def test_is_game_exception_false(self):
        """Test is_game_exception returns False for standard exceptions."""
        exc = ValueError("test")
        assert is_game_exception(exc) is False
    
    def test_is_game_exception_inheritance(self):
        """Test is_game_exception with exception inheritance."""
        from src.exceptions import LocationException
        exc = LocationException("test location error")
        assert is_game_exception(exc) is True
