"""
Common test fixtures and configuration.
"""

import pytest
import os
import json
from pathlib import Path

from src.players import Player
from src.models import Enemy, Location, set_locations_data, set_enemies_data
from src.data_loader import GameContext


@pytest.fixture
def test_data_dir():
    """Get path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_player():
    """Create a sample player for testing."""
    player = Player("TestHero")
    player.level = 1
    player.xp = 0
    player.hp = 30
    player.max_hp = 30
    player.atk = 6
    player.dex = 5
    player.gold = 50
    return player


@pytest.fixture
def sample_enemy():
    """Create a sample enemy for testing."""
    enemy_data = {
        "id": "goblin",
        "display": "Goblin",
        "hp": 10,
        "atk": 3,
        "def": 0,
        "element": "None",
        "tier": 1,
    }
    return Enemy(enemy_data)


@pytest.fixture
def sample_location():
    """Create a sample location for testing."""
    location_data = {
        "id": "forest",
        "name": "Dark Forest",
        "description": "A dark and mysterious forest.",
        "difficulty": 1,
        "element": "None",
        "terrain": "forest",
        "enemies": [
            {"id": "goblin", "chance": 1.0}
        ],
        "connections": {
            "north": "village",
        },
        "treasure": [],
        "npc": None,
    }
    return Location(location_data)


@pytest.fixture
def game_context():
    """Create a game context with test data."""
    context = GameContext()
    return context


@pytest.fixture(scope="session")
def real_test_data():
    """Load real game data for integration testing."""
    root = Path(__file__).parent.parent
    game_context = GameContext(data_dir=str(root / "data"))
    game_context.load_all()
    return game_context
