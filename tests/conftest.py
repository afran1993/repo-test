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


# GameRunner and CLI fixtures

@pytest.fixture
def mock_player():
    """Create a mock player with common attributes."""
    from unittest.mock import Mock
    player = Mock(spec=Player)
    player.name = "TestHero"
    player.level = 1
    player.hp = 30
    player.max_hp = 30
    player.xp = 0
    player.gold = 100
    player.current_location = "village"
    player.is_alive = Mock(return_value=True)
    player.status = Mock(return_value="Hero Lvl 1 | 30/30 HP | 100 Gold")
    player.gain_xp = Mock(return_value=False)
    player.dialogue_choices = {}
    player.story_progress = "start"
    player.inventory = []
    player.skills = {}
    player.get_total_max_hp = Mock(return_value=30)
    return player


@pytest.fixture
def mock_location():
    """Create a mock location."""
    from unittest.mock import Mock
    location = Mock(spec=Location)
    location.id = "village"
    location.name = "Village"
    location.description = "A peaceful village"
    location.connections = {"north": "forest"}
    location.get_random_enemy = Mock(return_value=None)
    location.describe = Mock(return_value="A peaceful village")
    return location


@pytest.fixture
def mock_boss():
    """Create a mock boss enemy."""
    from unittest.mock import Mock
    boss = Mock(spec=Enemy)
    boss.id = "boss_guardian"
    boss.name = "Ancient Guardian"
    boss.hp = 100
    boss.xp_reward = 500
    boss.gold_reward = 200
    return boss


@pytest.fixture
def mock_context():
    """Create a mock GameContext."""
    from unittest.mock import Mock
    context = Mock(spec=GameContext)
    context.get_npcs = Mock(return_value={"npcs": []})
    return context


@pytest.fixture
def game_runner_dependencies():
    """Create all dependencies for GameRunner."""
    from unittest.mock import Mock
    return {
        'fight_fn': Mock(return_value=True),
        'get_location_fn': Mock(return_value=None),
        'get_boss_fn': Mock(return_value=None),
        'check_access_fn': Mock(return_value=(True, "")),
        'check_milestone_fn': Mock(return_value=None),
        'get_current_quest_fn': Mock(return_value=None),
        'get_story_status_fn': Mock(return_value="Story progress: start"),
        'get_learned_skills_fn': Mock(return_value=[]),
        'get_available_skills_fn': Mock(return_value=[]),
        'teach_skill_fn': Mock(),
        'update_story_fn': Mock(),
        'get_npcs_in_location_fn': Mock(return_value=[]),
        'interact_with_npc_fn': Mock(),
        'save_game_fn': Mock(),
    }
