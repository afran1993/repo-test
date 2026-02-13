# 07 - Dependency Injection & Repository Pattern

Deep dive into the game's inversion of control architecture, service repositories, and factory patterns.

## Table of Contents
- [Dependency Injection Overview](#dependency-injection-overview)
- [GameContext](#gamecontext)
- [Repository Pattern](#repository-pattern)
- [Service Interfaces](#service-interfaces)
- [Event Bus](#event-bus)
- [Example: Adding a New System](#example-adding-a-new-system)

---

## Dependency Injection Overview

### What is Dependency Injection?

Dependency Injection (DI) is a design pattern that:
1. **Decouples** components from their dependencies
2. **Centralizes** object creation
3. **Simplifies** testing through mocking
4. **Enables** runtime configuration

### Without DI (Problems)

```python
# ❌ TIGHTLY COUPLED - Hard to test, hard to maintain
class Combat:
    def __init__(self):
        self.persistence = FilePersistence()  # Hard-coded dependency
        self.event_engine = EventEngine()
        self.damage_calc = DamageCalculator()
    
    # Problem: Cannot use mock or different implementation
    # Problem: Difficult to test in isolation
    # Problem: Changing implementation requires code change
```

### With DI (Solutions)

```python
# ✅ LOOSELY COUPLED - Easy to test, easy to extend
class Combat:
    def __init__(
        self,
        persistence: PersistenceRepository,
        event_engine: EventEngine,
        damage_calc: DamageCalculator
    ):
        self.persistence = persistence  # Injected dependency
        self.event_engine = event_engine
        self.damage_calc = damage_calc
    
    # Can inject Mock objects for testing
    # Can swap implementations at runtime
    # Code remains unchanged
```

### Inversion of Control

The application's control flow is inverted:
- **Traditional**: Components create what they need
- **IoC**: Framework provides what components need

```
Traditional:
┌─────────────┐
│  Combat     │──────→ Creates DamageCalc
│             │──────→ Creates EventEngine
│             │──────→ Creates Persistence
└─────────────┘

With DI:
┌──────────────────────┐
│   GameContext        │ ← Creates all dependencies
│   (Service Manager)  │
└──────────┬───────────┘
           │
           ├─ Injects ──→ Combat
           ├─ Injects ──→ Combat
           └─ Injects ──→ Combat
```

---

## GameContext

### Purpose

`src/data_loader.py` defines `GameContext`, the central dependency container:

```python
class GameContext:
    """
    Central service locator and dependency injection container.
    
    Manages all singleton services and provides factory methods
    for lazy loading on first access.
    """
    
    def __init__(self):
        # Services cache
        self._services = {}
        
        # Configuration
        self.config = GameConfig.load()
        self.i18n = I18nManager.load(self.config.language)
        
        # Repositories (lazy-loaded)
        self._persistence_repo = None
        self._enemy_repo = None
        self._quest_repo = None
```

### Singleton Pattern

Services are created once and reused:

```python
@property
def persistence_repository(self) -> PersistenceRepository:
    """Get or create persistence repository."""
    if self._persistence_repo is None:
        self._persistence_repo = JsonPersistenceImpl()
    return self._persistence_repo

@property
def enemy_repository(self) -> EnemyRepository:
    """Get or create enemy repository."""
    if self._enemy_repo is None:
        self._enemy_repo = JsonEnemyRepositoryImpl()
    return self._enemy_repo
```

### Factory Methods

GameContext provides factories for creating transient objects:

```python
def create_player(self, player_data: dict) -> "Player":
    """Create a new player instance."""
    from src.characters import Player
    return Player(player_data)

def create_combat(
    self,
    player_team: List["Character"],
    enemy_team: List["Enemy"]
) -> "Combat":
    """Create a new combat instance with injected dependencies."""
    from src.combat import Combat
    return Combat(
        player_team=player_team,
        enemy_team=enemy_team,
        event_engine=SimpleEventBus(),
        damage_calculator=DamageCalculator(),
        persistence=self.persistence_repository
    )

def create_dialogue(self, npc_id: str) -> "Dialogue":
    """Create dialogue with NPC."""
    from src.dialogue import Dialogue
    dialogue_data = self.quest_repository.get_dialogue(npc_id)
    return Dialogue(dialogue_data, npc=self.world.get_npc(npc_id))
```

### Global Access

While singleton, GameContext is accessible globally:

```python
# In any component
from src.data_loader import GameContext

ctx = GameContext()
player = ctx.current_player
persistence = ctx.persistence_repository
```

Use sparingly - prefer injection when possible:

```python
# ✅ GOOD - Explicit dependency
class GameRunner:
    def __init__(self, context: GameContext):
        self.context = context

# ❌ AVOID - Hidden dependency
class GameRunner:
    def run(self):
        context = GameContext()  # Implicit, hard to test
```

---

## Repository Pattern

### What is Repository Pattern?

Repository acts as an abstraction layer:

```
Application Code
     ↓
Repository Interface (Abstract)
     ↓
Repository Implementation (Concrete)
     ↓
Data Source (Files, Database, Network)
```

### Benefits

1. **Swap Implementations**: Use JSON today, database tomorrow
2. **Mock for Tests**: Use in-memory repository for unit tests
3. **Single Responsibility**: Data access separated from business logic
4. **Consistent Interface**: All repositories follow same contract

### Repository Hierarchy

Located in `src/repositories.py`:

```python
# Abstract Interfaces
class Repository(ABC):
    """Base repository interface."""
    
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Any]:
        """Find item by unique ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Any]:
        """Find all items."""
        pass
    
    @abstractmethod
    def save(self, item: Any) -> bool:
        """Save item to storage."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete item by ID."""
        pass


class PersistenceRepository(Repository):
    """Persistence for game saves."""
    
    @abstractmethod
    def save_game(self, game_state: dict, slot: int) -> bool:
        pass
    
    @abstractmethod
    def load_game(self, slot: int) -> Optional[dict]:
        pass


class EnemyRepository(Repository):
    """Enemy definitions from data."""
    
    @abstractmethod
    def find_by_tier(self, tier: int) -> List[dict]:
        pass


class QuestRepository(Repository):
    """Quest definitions."""
    
    @abstractmethod
    def find_by_giver(self, npc_id: str) -> List[dict]:
        pass
```

### Concrete Implementations

Located in `src/repository_impl.py`:

```python
class JsonPersistenceImpl(PersistenceRepository):
    """Persist to JSON files (save.json)."""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
    
    def save_game(self, game_state: dict, slot: int) -> bool:
        """Save game state to JSON file."""
        filepath = f"{self.save_dir}/save_{slot}.json"
        try:
            with open(filepath, 'w') as f:
                json.dump(game_state, f, indent=2)
            return True
        except IOError as e:
            raise PersistenceError(f"Failed to save: {e}")
    
    def load_game(self, slot: int) -> Optional[dict]:
        """Load game state from JSON file."""
        filepath = f"{self.save_dir}/save_{slot}.json"
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            raise CorruptedSaveError(f"Save file corrupted: {filepath}")


class JsonEnemyRepositoryImpl(EnemyRepository):
    """Load enemies from data/enemies.json."""
    
    def __init__(self, data_file: str = "data/enemies.json"):
        self.data_file = data_file
        self._enemies_cache = None
    
    def find_by_id(self, enemy_id: str) -> Optional[dict]:
        """Find enemy by ID."""
        enemies = self._load_all()
        for enemy in enemies:
            if enemy["id"] == enemy_id:
                return enemy
        return None
    
    def find_by_tier(self, tier: int) -> List[dict]:
        """Find all enemies of given tier."""
        enemies = self._load_all()
        return [e for e in enemies if e.get("tier") == tier]
    
    def _load_all(self) -> List[dict]:
        """Load all enemies (cached)."""
        if self._enemies_cache is None:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self._enemies_cache = data.get("enemies", [])
        return self._enemies_cache
```

### Swapping Implementations

Easy to change at runtime:

```python
# Use JSON (default)
repos = RepositoryFactory.create_json_repositories()

# Use in-memory for testing
repos = RepositoryFactory.create_mock_repositories()

# Use database (future)
repos = RepositoryFactory.create_database_repositories()

# All interfaces identical
combat = Combat(
    persistence=repos.persistence,
    enemy_repo=repos.enemies,
    quest_repo=repos.quests
)
```

---

## Service Interfaces

### Core Services

The application requires these services:

| Service | Purpose | Implementation |
|---------|---------|-----------------|
| PersistenceRepository | Save/load games | JsonPersistenceImpl |
| EnemyRepository | Enemy definitions | JsonEnemyRepositoryImpl |
| QuestRepository | Quest definitions | JsonQuestRepositoryImpl |
| NPCRepository | NPC definitions | JsonNPCRepositoryImpl |
| ItemRepository | Item definitions | JsonItemRepositoryImpl |

### Creating New Services

Step 1: Define abstract interface

```python
# In src/repositories.py
class MyNewRepository(Repository, ABC):
    @abstractmethod
    def do_something(self) -> bool:
        pass
```

Step 2: Implement concretely

```python
# In src/repository_impl.py
class JsonMyNewRepositoryImpl(MyNewRepository):
    def do_something(self) -> bool:
        # Implementation
        return True
```

Step 3: Add to GameContext

```python
# In src/data_loader.py
class GameContext:
    @property
    def my_new_repository(self) -> MyNewRepository:
        if self._my_new_repo is None:
            self._my_new_repo = JsonMyNewRepositoryImpl()
        return self._my_new_repo
```

Step 4: Inject into components

```python
class MyComponent:
    def __init__(self, repo: MyNewRepository):
        self.repo = repo
    
    def use_repo(self):
        self.repo.do_something()
```

---

## Event Bus

### Simple Event Bus

Located in `src/repositories.py`:

```python
class SimpleEventBus:
    """Pub/Sub event system for loose coupling."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to events of given type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish event to all subscribers."""
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
```

### Event-Driven Architecture

Example: Enemy defeated

```python
# Combat publishes event
event_bus.publish("enemy_defeated", {
    "enemy_id": "goblin_1",
    "experience": 150,
    "drops": ["gold", "item_id"]
})

# Quest system subscribes and updates
quest_system.subscribe("enemy_defeated", lambda event: 
    quest_system.on_enemy_defeat(event["enemy_id"])
)

# Player system subscribes and gains XP
player_system.subscribe("enemy_defeated", lambda event:
    player.add_experience(event["experience"])
)

# Inventory subscribes and adds drops
inventory.subscribe("enemy_defeated", lambda event:
    inventory.add_items(event["drops"])
)
```

### Decoupling with Events

Without event bus:
```python
# ❌ Tightly coupled - Combat needs to know about everything
combat.on_victory_signal_quests()
combat.on_victory_give_xp()
combat.on_victory_drop_items()
combat.on_victory_update_stats()
```

With event bus:
```python
# ✅ Loosely coupled - Combat just publishes
event_bus.publish("enemy_defeated", event_data)
# Listeners respond independently
```

---

## Example: Adding a New System

Let's add an **AchievementSystem** following DI patterns.

### Step 1: Create Repository Interface

```python
# In src/repositories.py
class AchievementRepository(Repository, ABC):
    """Manage achievement state and definitions."""
    
    @abstractmethod
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock achievement for player."""
        pass
    
    @abstractmethod
    def get_unlocked(self) -> List[str]:
        """Get list of unlocked achievement IDs."""
        pass
```

### Step 2: Create Implementation

```python
# In src/repository_impl.py
class JsonAchievementRepositoryImpl(AchievementRepository):
    """Store achievements in JSON."""
    
    def __init__(self, data_file: str = "data/achievements.json"):
        self.data_file = data_file
        self.unlocked = set()
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock and persist achievement."""
        self.unlocked.add(achievement_id)
        self._persist()
        return True
    
    def _persist(self):
        """Save unlocked achievements to file."""
        with open(self.data_file, 'w') as f:
            json.dump(list(self.unlocked), f)
```

### Step 3: Add Achievement System

```python
# In src/achievements.py
class AchievementSystem:
    def __init__(self, repo: AchievementRepository, event_bus: SimpleEventBus):
        self.repo = repo
        self.event_bus = event_bus
        
        # Listen to game events
        event_bus.subscribe("enemy_defeated", self.on_enemy_defeat)
        event_bus.subscribe("level_up", self.on_level_up)
        event_bus.subscribe("quest_complete", self.on_quest_complete)
    
    def on_enemy_defeat(self, event):
        """Check if enemy defeat unlocks achievement."""
        if event["enemy_id"] == "final_boss":
            self.repo.unlock_achievement("defeated_final_boss")
    
    def on_level_up(self, event):
        """Check if level-up unlocks achievement."""
        if event["new_level"] == 50:
            self.repo.unlock_achievement("reached_level_50")
```

### Step 4: Integrate into GameContext

```python
# In src/data_loader.py
class GameContext:
    @property
    def achievement_repository(self) -> AchievementRepository:
        if self._achievement_repo is None:
            self._achievement_repo = JsonAchievementRepositoryImpl()
        return self._achievement_repo
    
    @property
    def achievement_system(self) -> "AchievementSystem":
        """Lazy-load achievement system."""
        if self._achievement_system is None:
            from src.achievements import AchievementSystem
            self._achievement_system = AchievementSystem(
                repo=self.achievement_repository,
                event_bus=self.event_bus
            )
        return self._achievement_system
```

### Step 5: Use in Game Loop

```python
# In src/game_runner.py or wherever events happen
game_context = GameContext()

# Event happens
game_context.event_bus.publish("enemy_defeated", {
    "enemy_id": "final_boss"
})

# Achievement system automatically processes
game_context.achievement_system.on_enemy_defeat(...)
```

### Benefits of This Approach

✅ AchievementSystem is independent of other systems  
✅ Can mock AchievementRepository for testing  
✅ Can swap JSON implementation for database later  
✅ Responds to game events without coupling  
✅ Easy to extend with new achievements  

---

## Testing with DI

### Injecting Mocks

```python
# Test file
from unittest.mock import MagicMock

def test_combat_damage_calculation():
    # Create mock repositories
    mock_persistence = MagicMock(spec=PersistenceRepository)
    mock_enemies = MagicMock(spec=EnemyRepository)
    mock_event_bus = MagicMock(spec=SimpleEventBus)
    
    # Inject mocks
    combat = Combat(
        persistence=mock_persistence,
        enemy_repository=mock_enemies,
        event_bus=mock_event_bus
    )
    
    # Test in isolation
    damage = combat.calculate_damage(player, enemy, ability)
    assert damage > 0
    
    # Verify event was published
    mock_event_bus.publish.assert_called_with("damage_dealt", ...)
```

---

## Integration with Other Systems

See:
- [01-ARCHITECTURE.md](01-ARCHITECTURE.md) for system architecture
- [09-game-loop.md](09-game-loop.md) for game loop integration
- [08-exception-handling.md](08-exception-handling.md) for error handling
