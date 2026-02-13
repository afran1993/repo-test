# Architecture Overview

## System Design

The RPG Game uses a **layered, modular architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│         Presentation Layer (CLI)            │
│  Pure UI - no game logic, input collection  │
│              cli.py                         │
└──────────────────┬──────────────────────────┘
                   │ User Input / Display Output
┌──────────────────┴──────────────────────────┐
│       Game Loop Layer (GameRunner)          │
│ Orchestrates game flow, menu handling       │
│         game_runner.py (237 lines)          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│      Business Logic Layer                   │
│  - Combat system      (combat/)             │
│  - Player progression (players/)            │
│  - Story/dialogue     (story.py)            │
│  - NPCs              (npc_system.py)        │
│  - Items             (items/)               │
│  - Quests            (quests/)              │
└──────────────────┬──────────────────────────┘
                   │ Repository Interface
┌──────────────────┴──────────────────────────┐
│    Data Access Layer (Repository Pattern)   │
│  Abstract: LocationRepository               │
│           EnemyRepository                   │
│           NPCRepository, etc.               │
│                                             │
│  Concrete: JsonLocationRepository           │
│            JsonEnemyRepository              │
│            JsonNPCRepository, etc.          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│        Data Layer (GameContext)             │
│  Centralized state management               │
│  - Locations, Enemies, Items, NPCs...      │
│  - Event Bus for decoupled communication    │
└─────────────────────────────────────────────┘
```

## Core Principles

### 1. **Dependency Injection**
All subsystems receive their dependencies via constructor injection:

```python
# GameContext provides repositories
context = GameContext()
runner = GameRunner(
    context=context,
    fight_fn=fight_function,
    get_location_fn=location_repository.get_location,
    # ... other injected functions
)
```

### 2. **Repository Pattern**
Data access is abstracted behind interfaces:

```python
# Abstract interface
class LocationRepository(ABC):
    @abstractmethod
    def get_location(self, location_id: str) -> Location:
        pass

# Concrete implementation
class JsonLocationRepository(LocationRepository):
    def get_location(self, location_id: str) -> Location:
        # Load from JSON
        ...
```

### 3. **Centralized State (GameContext)**
All game data flows through one context object:

```python
context = GameContext()
context.load_all()  # Load locations, enemies, items, etc.

# Access data via repositories
location_repo = context.get_location_repository()
enemy_repo = context.get_enemy_repository()
event_bus = context.get_event_bus()
```

### 4. **Exception Hierarchy**
25+ custom exceptions for clear error handling:

```python
try:
    location = repo.get_location("forest")
except LocationNotFound as e:
    logger.error(f"Location error: {e.message}")
    print(f"Available locations: {list_available_locations()}")
except GameException as e:
    logger.error(f"Game error: {e.message}")
```

## Module Organization

### Core Modules

| Module | Purpose | Lines |
|--------|---------|-------|
| `main.py` | Entry point, initialization | 182 |
| `cli.py` | Menu display, user input | 254 |
| `game_runner.py` | Main game loop | 237 |
| `data_loader.py` | GameContext state management | 189 |
| `models.py` | Entity classes (Location, Enemy) | 208 |
| `utils.py` | Utilities, element system | 81 |

### System Modules

| Module | Purpose | Components |
|--------|---------|------------|
| `players/player.py` | Character system | Stats, equipment, potions, progression |
| `combat/` | Combat system | Combat flow, damage engine, abilities, AI |
| `story.py` | Story progression | Quests, story branches, skill checks |
| `npc_system.py` | NPC interaction | Dialogue trees, NPC lookup |
| `items/item.py` | Item system | Equipment, consumables |
| `quests/quest.py` | Quest system | Quest data, objectives |
| `persistence.py` | Save/load | Game serialization |

### Infrastructure Modules

| Module | Purpose |
|--------|---------|
| `repositories.py` | Abstract repository interfaces + EventBus |
| `repository_impl.py` | Concrete repository implementations |
| `exceptions.py` | 25+ custom exception classes |
| `i18n.py` | Internationalization (EN/IT) |
| `color_manager.py` | Console output formatting |

## Dependency Graph

```
main.py
├── GameContext
├── GameRunner
│   ├── Persistence (save_game, load_game)
│   ├── Combat (fight_fn)
│   ├── Story (check_milestone, get_quest)
│   ├── NPCs (interact_with_npc)
│   └── Models (get_location)
├── Player
└── CLI (choose_language, display_*)

GameRunner
├── GameContext
├── Repository functions (injected)
├── Combat system
├── Story system
└── Persistence

combat/
├── DamageEngine (centralized damage calculation)
├── Combat (turn-based flow)
├── Abilities (special abilities system)
└── EventEngine (combat events)

Player
├── Stats (str, dex, atk, def)
├── Equipment
├── Inventory
├── Progression (XP, leveling)
└── Persistence

Story
├── NPCs
├── Quests
├── Dialogue
└── Skills
```

## Data Flow

### Game Initialization
```
├─ main.py
│  ├─ Parse arguments (--debug, --demo)
│  ├─ Create GameContext
│  ├─ Load all data (JSON files)
│  ├─ Set up repositories
│  ├─ Create/load Player
│  └─ Instantiate GameRunner with DI
│
└─ GameRunner.run(player)
   ├─ Initialize game state
   └─ Enter main loop
```

### Main Game Loop
```
GameRunner.run()
├─ Display location info
├─ Display menu
├─ Get user input
│
├─ Branch 1: Combat
│  ├─ Create enemy
│  ├─ Battle loop
│  │  ├─ Player action
│  │  ├─ Calculate damage
│  │  ├─ Enemy reaction
│  │  └─ Check victory/defeat
│  └─ Distribute XP/gold
│
├─ Branch 2: Explore/Shop
│  ├─ Interact with NPCs
│  ├─ Browse treasure
│  └─ Buy items
│
├─ Branch 3: Equipment
│  ├─ Equip weapon
│  └─ Equip accessories
│
└─ Branch 4: Save/Quit
   └─ Persist player state
```

## Design Patterns

### 1. **Repository Pattern**
Abstracts data access behind interfaces, allowing different implementations (JSON, database, API).

```python
# Interface
class LocationRepository(ABC):
    @abstractmethod
    def get_location(self, id: str) -> Location: pass

# Implementation
class JsonLocationRepository(LocationRepository):
    def __init__(self, data: Dict):
        self.data = data
    
    def get_location(self, id: str) -> Location:
        for loc_data in self.data["locations"]:
            if loc_data["id"] == id:
                return Location(loc_data)
        raise LocationNotFound(id)
```

### 2. **Factory Pattern**
Factory methods in GameContext create repositories on-demand:

```python
def get_location_repository(self) -> LocationRepository:
    if self._location_repo is None:
        self._location_repo = JsonLocationRepository(...)
    return self._location_repo
```

### 3. **Singleton Pattern**
Repositories within GameContext are singletons:

```python
repo1 = context.get_location_repository()
repo2 = context.get_location_repository()
assert repo1 is repo2  # Same instance
```

### 4. **Pub/Sub Pattern (Event Bus)**
Decoupled communication between systems:

```python
event_bus = context.get_event_bus()

# Subscribe
event_bus.subscribe("player_level_up", on_level_up_handler)

# Publish
event_bus.publish("player_level_up", {"level": 5, "player_id": "hero"})
```

### 5. **Strategy Pattern**
DamageCalculator applies modifiers in sequence:

```python
class DamageCalculator:
    def calculate(self, context: DamageContext) -> DamageResult:
        # 1. Base damage
        # 2. Defense reduction
        # 3. Element modifier
        # 4. Reaction modifier
        # 5. Ability multiplier
        return final_damage
```

### 6. **Builder Pattern (Implicit)**
DamageContext encapsulates all damage calculation parameters:

```python
damage = DamageContext(
    attacker=player,
    defender=enemy,
    damage_type=DamageType.ABILITY,
    element="Fire",
    ability_multiplier=1.5
)
result = calculator.calculate(damage)
```

## Error Handling Strategy

### Exception Hierarchy
```
GameException (base)
├── PlayerException
│   ├── InsufficientGold
│   └── PlayerDefeated
├── LocationException
│   ├── LocationNotFound
│   └── LocationAccessDenied
├── CombatException
│   ├── EnemyNotFound
│   └── InsufficientMana
├── PersistenceException
│   ├── SaveFailed
│   ├── LoadFailed
│   └── CorruptedSave
└── ...
```

### Recovery Strategy
```python
try:
    # Game logic
    location = repo.get_location(location_id)
except LocationNotFound as e:
    # Log with context
    logger.error(f"Location error: {e.message}", extra=e.context)
    # UI feedback
    display_error("Location not found")
    # Recovery: return to menu
    return show_menu()
```

## Performance Considerations

### Caching
- **Location caching**: JsonLocationRepository caches loaded locations
- **Enemy spawning**: New Enemy instances on each spawn (no caching)
- **Repository singleton**: One repository per GameContext

### Lazy Loading
- Repositories created on first access (GameContext factory methods)
- Game data JSON loaded only when needed

### Potential Optimizations
1. Enemy template caching with instance cloning
2. Location graph pre-computation
3. NPC AI pathfinding cache

## Testing Strategy

### Unit Tests (83 tests, 22.55% coverage)
- Test individual functions in isolation
- Use fixtures for common setup
- Focus on critical paths

### Integration Tests
- Test multiple systems working together
- Test repositories with actual game data
- Test exception handling

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── test_player.py          # Player system
├── test_models.py          # Entity models
├── test_exceptions.py      # Exception handling
├── test_repositories.py    # Repository pattern
├── test_persistence.py     # Save/load
└── test_damage_engine.py   # Combat math
```

## Development Workflow

### Adding a New Feature

1. **Design Phase**
   - Identify which layer (presentation, logic, data)
   - Plan dependencies
   - Design API

2. **Test Phase**
   - Write tests first (TDD)
   - Ensure tests fail initially

3. **Implementation Phase**
   - Create implementation
   - Pass tests
   - Add integration tests

4. **Refactoring Phase**
   - Review code quality
   - Optimize if needed
   - Document

5. **Verification Phase**
   - Run full test suite: `pytest tests/ -v`
   - Check coverage: `pytest --cov=src`
   - Manual testing

---

**Related Documentation**:
- [Game Systems](02-game-systems.md)
- [Data Format](03-data-format.md)
- [Dependency Injection](07-dependency-injection.md)
- [Development Guide](12-development-guide.md)
