# 11 - Testing Strategy

Guidelines and implementation details for unit, integration, and regression testing.

## Table of Contents
- [Testing Pyramid](#testing-pyramid)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [End-to-End Tests](#end-to-end-tests)
- [Test Organization](#test-organization)
- [Coverage and CI](#coverage-and-ci)
- [Mocking and Fixtures](#mocking-and-fixtures)
- [Common Test Patterns](#common-test-patterns)

---

## Testing Pyramid

- **Unit Tests**: Fast, isolated tests for small components (70% of tests)
- **Integration Tests**: Test interactions between modules (20%)
- **End-to-End Tests**: Full app flow including I/O (10%)

Aim: majority unit tests, few integration tests, minimal slow E2E tests.

---

## Unit Tests

### Philosophy

- Test single function/class behavior
- Use fixtures to create deterministic objects
- Mock external dependencies (file IO, network, DB)

### Example: Testing Enemy Resistances

```python
def test_get_resistance_immunity():
    data = {"id": "e1", "immunities": ["Poison"]}
    enemy = Enemy(data)
    assert enemy.get_resistance("Poison") == 0.0


def test_get_resistance_vulnerability():
    data = {"id": "e1", "vulnerabilities": ["Holy"]}
    enemy = Enemy(data)
    assert enemy.get_resistance("Holy") == 1.5


def test_get_resistance_dict():
    data = {"id": "e1", "resistances": {"Fire": 0.5}}
    enemy = Enemy(data)
    assert enemy.get_resistance("Fire") == 0.5
```

### Running Unit Tests

```bash
# Run pytest with verbose output
pytest tests/unit -q

# Run a single test
pytest tests/unit/test_enemy.py::test_get_resistance_immunity -q
```

---

## Integration Tests

### Purpose

- Verify interactions between modules: Combat + DamageEngine + EventBus
- Use test fixtures to create small world contexts

### Example: Combat Integration

```python
def test_combat_damage_application(monkeypatch):
    # Setup player and enemy
    player = Player.from_data(sample_player_data)
    enemy = Enemy(sample_enemy_data)

    # Use real DamageCalculator, but mock randomness
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)

    # Create combat
    combat = Combat(player_team=[player], enemy_team=[enemy])
    combat.start()

    # Player attacks
    combat.execute_turn(Action(type="attack", actor=player, target=enemy))

    # Check that enemy lost HP
    assert enemy.hp < enemy.max_hp
```

---

## End-to-End Tests

### Purpose

- Simulate real user flows (New Game → Combat → Save)
- Use small, pre-defined worlds

### Example: E2E Save/Load

```python
def test_save_load_e2e(tmp_path):
    # Start new game
    runner = GameRunner(GameContext())
    runner.start_new_game(sample_player_data, save_dir=tmp_path)

    # Play a bit: defeat an enemy
    runner.simulate_turn("attack")

    # Save game
    runner.save_game(slot=1)

    # Load into new runner
    runner2 = GameRunner(GameContext())
    runner2.load_game(slot=1)

    assert runner2.player.level == runner.player.level
    assert runner2.world_state == runner.world_state
```

---

## Test Organization

```
tests/
  unit/
    test_enemy.py
    test_player.py
  integration/
    test_combat_integration.py
  e2e/
    test_save_load.py

# Fixtures
conftest.py  # pytest fixtures providing sample objects and contexts
```

### Fixtures Example

`tests/conftest.py` provides fixtures for:
- `sample_enemy_data`
- `sample_player_data`
- `game_context` (populated with repos)

```python
@pytest.fixture
def sample_enemy_data():
    return {
        "id": "goblin",
        "name": "Goblin",
        "hp": 50,
        "atk": 10,
        "def": 5,
        "resistances": {},
        "immunities": [],
        "vulnerabilities": [],
    }
```

---

## Coverage and CI

### Coverage Setup

- `pytest` + `pytest-cov` configured in CI
- `.coveragerc` ignores tests and external libs

```ini
[run]
omit =
    tests/*
    src/__main__.py
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    if __name__ == .__main__.:
```

### CI Integration (GitHub Actions)

Workflow includes steps:
1. Checkout
2. Setup Python 3.12
3. Install deps
4. Run `pytest --cov=src --cov-report=xml`
5. Upload coverage report
6. Fail if coverage falls under threshold (optional)

---

## Mocking and Fixtures

### Mocking Patterns

- Use `monkeypatch` for random and time
- Use `unittest.mock.MagicMock` for repositories
- Use `tmp_path` for file system tests

### Example: Mock Persistence

```python
from unittest.mock import MagicMock

mock_repo = MagicMock(spec=PersistenceRepository)
mock_repo.save_game.return_value = True

# Inject into context
ctx = GameContext()
ctx._persistence_repo = mock_repo

runner = GameRunner(ctx)
runner.save_game(slot=1)
mock_repo.save_game.assert_called_once()
```

---

## Common Test Patterns

### Arrange-Act-Assert

```
# Arrange
player = Player(...)  

# Act
player.gain_experience(1000)

# Assert
assert player.level > 1
```

### Parameterized Tests

```python
@pytest.mark.parametrize("resistance,expected", [(0.0, 0), (0.5, 10), (1.5, 30)])
def test_damage_variant(resistance, expected):
    # ... set up and assert expected damage
```

### Flaky Test Handling

- Use `pytest-rerunfailures` only for unstable external tests
- Prefer determinism by mocking random/time

---

## Adding New Tests

1. Add new test file under appropriate folder
2. Use fixtures in `conftest.py`
3. Keep tests isolated (no network/file writes unless tmp_path)
4. Run `pytest -q` locally
5. Submit PR with updated coverage

---

## Useful Commands

- Run all tests: `pytest -q`
- Run unit tests: `pytest tests/unit -q`
- Run single test: `pytest tests/unit/test_enemy.py::test_get_resistance_immunity -q`
- Run with coverage: `pytest --cov=src --cov-report=term-missing`

---

## Integration with Other Docs

See:
- [01-ARCHITECTURE.md](01-ARCHITECTURE.md)
- [04-combat-engine.md](04-combat-engine.md)
- [08-exception-handling.md](08-exception-handling.md)
