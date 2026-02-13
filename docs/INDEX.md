# 🎮 RPG Game - Technical Wiki

Welcome to the complete technical documentation of the RPG Game project. This wiki explains the architecture, systems, and how to extend the game.

## 📚 Documentation Structure

- **[Architecture Overview](01-architecture.md)** - High-level system design and module organization
- **[Game Systems](02-game-systems.md)** - Core mechanics (combat, dialogue, quests, items)
- **[Data Format](03-data-format.md)** - JSON structure for enemies, locations, items, NPCs, quests
- **[Combat Engine](04-combat-engine.md)** - Detailed damage calculation and combat flow
- **[Player System](05-player-system.md)** - Character stats, progression, inventory
- **[Story & Dialogue](06-story-dialogue.md)** - Branching narrative and NPC interaction
- **[Dependency Injection](07-dependency-injection.md)** - Repository pattern and service architecture
- **[Exception Handling](08-exception-handling.md)** - Custom exceptions and error recovery
- **[Game Loop Flow](09-game-loop.md)** - Main game flow and menu system
- **[Configuration & Localization](10-config-localization.md)** - Language support and settings
- **[Testing & Coverage](11-testing.md)** - Unit tests, integration tests, coverage metrics
- **[Development Guide](12-development-guide.md)** - How to extend the game with new features

---

## 🚀 Quick Start for Developers

### Understanding the Project Structure

```
rpg-game/
├── main.py                 # Entry point - application startup
├── rpg.py                  # Legacy main loop (deprecated, see main.py)
├── 
├── src/                    # Main source code
│   ├── __init__.py
│   ├── cli.py             # User interface - pure presentation layer
│   ├── game_runner.py     # Main game loop orchestration
│   ├── data_loader.py     # GameContext - centralized state management
│   ├── models.py          # Entity classes (Location, Enemy)
│   ├── npc_system.py      # NPC dialogue and interaction
│   ├── utils.py           # Utilities (element matchups, emojis)
│   ├── color_manager.py   # Console output formatting
│   ├── i18n.py            # Internationalization (Italian, English)
│   ├── persistence.py     # Save/load game logic
│   ├── repositories.py    # Abstract repository interfaces
│   ├── repository_impl.py # Concrete repository implementations
│   ├── exceptions.py      # Custom exception classes (25+)
│   │
│   ├── players/
│   │   ├── player.py      # Player class with stats and progression
│   │   └── __init__.py
│   │
│   ├── combat/
│   │   ├── combat.py      # Combat flow and turn structure
│   │   ├── damage_engine.py # Unified damage calculation
│   │   ├── abilities.py    # Special abilities system
│   │   ├── event_engine.py # Combat event system
│   │   ├── cli_adapter.py  # UI bridge for combat
│   │   └── __init__.py
│   │
│   ├── story/
│   │   ├── story.py       # Story progression and quests
│   │   └── dialogue.py    # Dialogue branching
│   │
│   ├── items/
│   │   └── item.py        # Item system
│   │
│   ├── quests/
│   │   ├── quest.py       # Quest data structure
│   │   └── generator.py   # Dynamic quest generation
│   │
│   ├── enemies/
│   │   ├── enemy.py       # Enemy AI behavior
│   │   ├── abilities.py   # Enemy-specific abilities
│   │   └── ai.py          # Combat AI
│   │
│   └── world/
│       └── world.py       # World state management
│
├── tests/                 # Test suite (83 tests, 22.55% coverage)
│   ├── conftest.py       # Pytest fixtures
│   ├── test_player.py    # Player system tests
│   ├── test_models.py    # Entity model tests
│   ├── test_exceptions.py # Exception tests
│   ├── test_repositories.py # Repository pattern tests
│   ├── test_persistence.py # Save/load tests
│   └── test_damage_engine.py # Combat calculation tests
│
├── data/                 # Game data (JSON)
│   ├── locations.json   # Map locations
│   ├── enemies.json     # Enemy definitions
│   ├── items.json       # Item catalog
│   ├── quests.json      # Quest definitions
│   ├── npcs.json        # NPC definitions
│   ├── abilities.json   # Special abilities
│   ├── archetypes.json  # Player archetypes
│   ├── regions.json     # World regions
│   └── spawn_tables.json # Enemy spawn rates
│
├── locales/             # Translations
│   ├── en.json         # English strings
│   └── it.json         # Italian strings
│
├── docs/                # Documentation (this wiki)
│   ├── index.md        # This file
│   ├── 01-architecture.md
│   ├── 02-game-systems.md
│   ├── 03-data-format.md
│   ├── 04-combat-engine.md
│   ├── 05-player-system.md
│   ├── 06-story-dialogue.md
│   ├── 07-dependency-injection.md
│   ├── 08-exception-handling.md
│   ├── 09-game-loop.md
│   ├── 10-config-localization.md
│   ├── 11-testing.md
│   └── 12-development-guide.md
│
├── locales/             # Internationalization
│   ├── en.json
│   └── it.json
│
├── README.md           # Project overview
├── requirements.txt    # Python dependencies
├── setup.py           # Package configuration
├── pytest.ini         # Test configuration
├── .coveragerc        # Coverage configuration
└── PRIORITIES_COMPLETE.md # Recent improvements

```

---

## 🎯 Key Concepts

### Dependency Injection
The game uses a centralized `GameContext` object that holds:
- All game data (locations, enemies, items, NPCs, quests)
- Repository instances for data access
- Event bus for decoupled communication

```python
context = GameContext()
context.load_all()

# Access repositories
location_repo = context.get_location_repository()
enemy_repo = context.get_enemy_repository()
event_bus = context.get_event_bus()
```

### Exception Handling
25+ custom exceptions organized by domain:
- `LocationNotFound`, `EnemyNotFound`, `NPCNotFound`
- `InsufficientGold`, `InsufficientXP`
- `SaveFailed`, `CorruptedSave`, `LoadFailed`
- `AbilityOnCooldown`, `InsufficientMana`

All exceptions inherit from `GameException` with context preservation:
```python
try:
    location = repo.get_location("forest")
except LocationNotFound as e:
    print(f"Error: {e.message}")
    print(f"Context: {e.context}")
```

### Test Coverage
- **83 total tests** (all passing ✅)
- **22.55% coverage** with focus on critical paths
- Test files:
  - `test_player.py` (17 tests) - Player stats, progression
  - `test_models.py` (7 tests) - Entity models
  - `test_exceptions.py` (22 tests) - Exception hierarchy
  - `test_repositories.py` (23 tests) - Repository patterns
  - `test_persistence.py` (9 tests) - Save/load
  - `test_damage_engine.py` (4 tests) - Combat math

---

## 📖 Documentation Files

Each markdown file in this wiki covers a specific aspect:

1. **01-architecture.md** - Design patterns, module dependencies, layer separation
2. **02-game-systems.md** - Combat, dialogue, quests, items, NPCs
3. **03-data-format.md** - JSON schemas for all game data
4. **04-combat-engine.md** - Damage calculation, resistances, abilities
5. **05-player-system.md** - Character creation, stats, progression
6. **06-story-dialogue.md** - Narrative branching, NPC dialogue
7. **07-dependency-injection.md** - Repository pattern, ServiceContainer
8. **08-exception-handling.md** - Custom exceptions, error recovery
9. **09-game-loop.md** - Main loop flow, menu system
10. **10-config-localization.md** - Settings, language support
11. **11-testing.md** - Test strategy, running tests, adding tests
12. **12-development-guide.md** - Adding features, extending systems

---

## 💻 Running the Game

### Installation
```bash
cd rpg-game
pip install -r requirements.txt
```

### Start Game
```bash
python main.py
```

### Run Tests
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### Debug Mode
```bash
python main.py --debug
```

### Demo Mode
```bash
python main.py --demo
```

---

## 🔄 Architecture Layers

```
┌─────────────────────────────────────────┐
│  Presentation Layer (CLI)               │
│  - cli.py: Menu display, input capture  │
│  - color_manager.py: Output formatting  │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│  Game Logic Layer (GameRunner)          │
│  - game_runner.py: Main loop            │
│  - game_logic.py: Action handling       │
│  - combat/: Battle system               │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│  Business Logic Layer                   │
│  - players/: Character system           │
│  - story.py: Narrative progression      │
│  - npc_system.py: NPC interaction       │
│  - quests/: Quest system                │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│  Data Access Layer (Repositories)       │
│  - repositories.py: Interfaces          │
│  - repository_impl.py: Implementations  │
│  - persistence.py: Save/load            │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│  Data Layer (GameContext)               │
│  - data_loader.py: GameContext          │
│  - models.py: Data models              │
│  - data/*.json: Game data               │
└─────────────────────────────────────────┘
```

---

## 🎮 Starting Development

### 1. Understand the Architecture
Read [01-architecture.md](01-architecture.md) to understand how systems interact.

### 2. Explore Game Systems
Read [02-game-systems.md](02-game-systems.md) for concrete examples.

### 3. Run Tests
```bash
pytest tests/ -v
```
This establishes a working baseline.

### 4. Add Your Feature
Follow [12-development-guide.md](12-development-guide.md) for step-by-step instructions.

### 5. Write Tests
Add tests to `tests/` directory before implementation (TDD).

---

## ⚙️ System Highlights

### Unified Damage Engine
All damage calculations (player attacks, enemy attacks, abilities) go through `DamageCalculator`:
- Consistent application of modifiers
- Support for resistances, vulnerabilities, immunities
- Element type system
- Ability multipliers

### Dialogue Branching
NPCs have dynamic dialogue trees with:
- Skill-based dialogue options (locked behind skills)
- Story state checking
- Multiple dialogue sequences

### Elemental System
Elements (Fire, Water, Ice, Air, Earth, Arcane, Lightning, etc.) with:
- Type matchups (Fire > Ice > Water > Fire)
- Resistance/immunity/vulnerability support
- Damage modifiers

### Boss/Endgame System
Special enemy flags:
- `boss: true` - Boss enemies with enhanced drops
- `final_boss: true` - Final boss difficulty spike
- `endgame: true` - Post-game content

---

## 📊 Project Statistics

- **Total Lines of Code**: ~2,600 (src/)
- **Test Lines**: ~600 (tests/)
- **Documentation**: ~1,500 lines (docs/)
- **Test Coverage**: 22.55% (83 tests, focused on critical paths)
- **Architecture Rating**: 9.3/10

---

## 🤝 Contributing

When adding new features:

1. **Design** - Plan in `12-development-guide.md`
2. **Test First** - Write tests before code
3. **Implement** - Follow existing patterns
4. **Document** - Update wiki if changing architecture
5. **Run Tests** - Ensure all tests pass: `pytest tests/ -v`

---

## 📝 License

This project is part of a learning/demonstration codebase.

---

**Last Updated**: February 2026  
**Current Version**: 1.3 (Post-Refactoring, with DI & Exception Systems)  
**Maintainer**: Development Team
