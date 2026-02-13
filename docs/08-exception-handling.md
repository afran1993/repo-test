# 08 - Exception Handling

Comprehensive guide to custom exception hierarchy, error recovery, and exception handling patterns.

## Table of Contents
- [Exception Hierarchy](#exception-hierarchy)
- [Exception Categories](#exception-categories)
- [Error Recovery Patterns](#error-recovery-patterns)
- [Logging and Debugging](#logging-and-debugging)
- [Best Practices](#best-practices)

---

## Exception Hierarchy

### Overview

The exception hierarchy in `src/exceptions.py` provides specific, actionable exceptions:

```
Exception (base Python exception)
│
└─ GameError (base for all game errors)
   │
   ├─ PersistenceError
   │  ├─ SaveFileError
   │  ├─ LoadFileError
   │  └─ CorruptedSaveError
   │
   ├─ GameStateError
   │  ├─ InvalidGameState
   │  ├─ CharacterNotFoundError
   │  └─ LocationNotFoundError
   │
   ├─ CombatError
   │  ├─ InvalidCombatState
   │  ├─ InvalidAction
   │  └─ InsufficientResources
   │
   ├─ DataError
   │  ├─ DataLoadError
   │  ├─ DataValidationError
   │  └─ MissingDataError
   │
   └─ ConfigurationError
      ├─ InvalidConfiguration
      └─ LanguageNotFoundError
```

### Exception Definitions

Located in `src/exceptions.py` (25+ custom exceptions):

```python
class GameError(Exception):
    """Base exception for all game errors."""
    pass

# Persistence Exceptions
class PersistenceError(GameError):
    """Error during data persistence."""
    pass

class SaveFileError(PersistenceError):
    """Error while saving game."""
    pass

class LoadFileError(PersistenceError):
    """Error while loading game."""
    pass

class CorruptedSaveError(LoadFileError):
    """Save file is corrupted or invalid."""
    pass

# Combat Exceptions
class CombatError(GameError):
    """Error during combat."""
    pass

class InvalidCombatState(CombatError):
    """Combat is not in valid state for action."""
    pass

class InvalidAction(CombatError):
    """Action is not valid in current context."""
    pass

class InsufficientResources(CombatError):
    """Not enough MP/Stamina for action."""
    pass

# Game State Exceptions
class GameStateError(GameError):
    """Error with game state."""
    pass

class CharacterNotFoundError(GameStateError):
    """Referenced character does not exist."""
    pass

# Data Exceptions
class DataError(GameError):
    """Error loading or validating data."""
    pass

class DataLoadError(DataError):
    """Failed to load data file."""
    pass

class DataValidationError(DataError):
    """Data does not meet validation requirements."""
    pass

class MissingDataError(DataError):
    """Required data field is missing."""
    pass
```

---

## Exception Categories

### 1. Persistence Exceptions

Occur when saving/loading game state:

```python
def save_game(self, slot: int) -> None:
    """Save current game state."""
    try:
        game_data = self.serialize_game()
        self.persistence_repo.save_game(game_data, slot)
    except IOError as e:
        raise SaveFileError(f"Failed to save slot {slot}: {e}")
    except PermissionError:
        raise SaveFileError("No permission to write save file")
    except Exception as e:
        raise SaveFileError(f"Unexpected error during save: {e}")

def load_game(self, slot: int) -> None:
    """Load game from save slot."""
    try:
        game_data = self.persistence_repo.load_game(slot)
        if not game_data:
            raise LoadFileError(f"Save slot {slot} does not exist")
        self.deserialize_game(game_data)
    except json.JSONDecodeError:
        raise CorruptedSaveError(f"Save file {slot} is corrupted")
    except KeyError as e:
        raise CorruptedSaveError(f"Missing required field in save: {e}")
```

### 2. Combat Exceptions

Occur during combat execution:

```python
def use_ability(self, actor: Character, ability_id: str, target: Character) -> bool:
    """Use ability on target during combat."""
    if not self.is_active():
        raise InvalidCombatState("Combat is not active")
    
    ability = actor.get_ability(ability_id)
    if not ability:
        raise InvalidAction(f"Character does not know ability: {ability_id}")
    
    if actor.mp < ability.cost:
        raise InsufficientResources(
            f"Not enough MP: need {ability.cost}, have {actor.mp}"
        )
    
    # Execute ability...
    return True
```

### 3. Game State Exceptions

Occur when referencing invalid game entities:

```python
def get_character(character_id: str) -> Character:
    """Get character by ID."""
    character = world.find_character(character_id)
    if not character:
        raise CharacterNotFoundError(
            f"Character '{character_id}' not found in world"
        )
    return character

def start_dialogue(npc_id: str) -> Dialogue:
    """Start dialogue with NPC."""
    npc = world.get_npc(npc_id)
    if not npc:
        raise CharacterNotFoundError(f"NPC '{npc_id}' not found")
    
    dialogue_data = quest_repo.get_dialogue(npc.dialogue_tree)
    if not dialogue_data:
        raise MissingDataError(f"Dialogue tree '{npc.dialogue_tree}' missing")
    
    return Dialogue(dialogue_data, npc)
```

### 4. Data Exceptions

Occur when loading or validating data files:

```python
def load_enemies(self) -> List[Enemy]:
    """Load enemies from data file."""
    try:
        with open("data/enemies.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise DataLoadError("enemies.json not found")
    except json.JSONDecodeError as e:
        raise DataValidationError(f"Invalid JSON in enemies.json: {e}")
    
    enemies = []
    for enemy_data in data.get("enemies", []):
        if "id" not in enemy_data:
            raise MissingDataError("Enemy missing required field: id")
        
        try:
            enemy = Enemy(enemy_data)
            enemies.append(enemy)
        except ValueError as e:
            raise DataValidationError(f"Invalid enemy data: {e}")
    
    return enemies
```

---

## Error Recovery Patterns

### Pattern 1: Try-Catch-Continue

Use when error is recoverable and non-critical:

```python
def load_all_npcs(self) -> List[NPC]:
    """Load all NPCs, skipping invalid ones."""
    npcs = []
    npc_data = load_json("data/npcs.json")
    
    for npc_entry in npc_data.get("npcs", []):
        try:
            npc = NPC(npc_entry)
            npcs.append(npc)
        except DataValidationError as e:
            logger.warning(f"Skipping invalid NPC: {e}")
            continue  # Skip this NPC but continue loading others
    
    if not npcs:
        raise DataLoadError("No valid NPCs loaded")
    
    return npcs
```

### Pattern 2: Try-Except-Raise (with context)

Add context before re-raising:

```python
def process_combat_action(self, action: Action) -> CombatResult:
    """Process player action with error context."""
    try:
        return self._execute_action(action)
    except InsufficientResources as e:
        # Add game context to error
        raise InsufficientResources(
            f"Cannot use {action.ability_id}: {e}. "
            f"Current MP: {self.actor.mp}"
        ) from e  # Preserve original traceback
    except InvalidAction as e:
        raise InvalidCombatState(
            f"Combat state does not allow action: {e}"
        ) from e
```

### Pattern 3: Fallback Strategy

Try multiple options before failing:

```python
def load_game_config(self) -> GameConfig:
    """Load config with fallback strategy."""
    
    # Try 1: Load from user config
    try:
        return GameConfig.load_from("config/user.json")
    except LoadFileError:
        logger.info("User config not found, trying default...")
    
    # Try 2: Load from default config
    try:
        return GameConfig.load_from("config/default.json")
    except LoadFileError:
        logger.warning("Default config not found, using hardcoded defaults")
    
    # Try 3: Return hardcoded defaults
    return GameConfig.create_default()
```

### Pattern 4: Cleanup with Finally

Ensure cleanup even on error:

```python
def save_game_safely(self, slot: int) -> bool:
    """Save game with guaranteed cleanup."""
    temp_file = None
    
    try:
        # Write to temporary file first
        temp_file = f"save_{slot}.tmp"
        self._write_to_file(temp_file, self.game_state)
        
        # Atomic rename
        os.rename(temp_file, f"save_{slot}.json")
        logger.info(f"Game saved to slot {slot}")
        return True
    
    except IOError as e:
        logger.error(f"Failed to save game: {e}")
        raise SaveFileError(f"Save failed: {e}")
    
    finally:
        # Cleanup temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass  # Ignore cleanup errors
```

### Pattern 5: Custom Context Manager

Create reusable error handling:

```python
from contextlib import contextmanager

@contextmanager
def handle_game_error(context: str):
    """Context manager for consistent error handling."""
    try:
        yield
    except GameError:
        raise  # Re-raise game errors as-is
    except KeyboardInterrupt:
        raise  # Always propagate interrupts
    except Exception as e:
        logger.critical(f"Unexpected error in {context}: {e}")
        raise GameError(f"Unhandled error: {e}") from e

# Usage
def play_combat(self):
    with handle_game_error("combat"):
        combat.start()
        while combat.is_active():
            combat.execute_turn()
```

---

## Logging and Debugging

### Logging Configuration

```python
import logging

# Configure logger for game
logger = logging.getLogger("rpg_game")
logger.setLevel(logging.DEBUG)

# Console handler (visible to player)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)

# File handler (detailed logs)
file_handler = logging.FileHandler("game.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

### Logging Best Practices

```python
def load_save_file(self, slot: int) -> dict:
    """Load save file with comprehensive logging."""
    
    logger.debug(f"Loading save slot {slot}...")
    filepath = f"save_{slot}.json"
    
    try:
        with open(filepath) as f:
            data = json.load(f)
        
        logger.info(f"Successfully loaded save slot {slot}")
        logger.debug(f"Loaded save contains: {list(data.keys())}")
        return data
    
    except FileNotFoundError:
        logger.warning(f"Save slot {slot} not found")
        raise
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse save file: {e}", exc_info=True)
        raise CorruptedSaveError(f"Invalid JSON in save_{slot}.json")
    
    except Exception as e:
        logger.critical(f"Unexpected error loading save: {e}", exc_info=True)
        raise
```

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Development info | "Loading 127 enemies from data" |
| INFO | Normal operation | "Game saved successfully" |
| WARNING | Non-critical issues | "NPC not found, skipping" |
| ERROR | Recoverable errors | "Failed to load config, using default" |
| CRITICAL | Severe errors | "Out of memory, corrupted game state" |

---

## Best Practices

### 1. Use Specific Exceptions

```python
# ❌ TOO GENERAL
except Exception:
    pass

# ✅ SPECIFIC
except SaveFileError as e:
    handle_save_error(e)
except LoadFileError as e:
    handle_load_error(e)
```

### 2. Provide Context

```python
# ❌ NO CONTEXT
raise InsufficientResources("Not enough MP")

# ✅ CONTEXT PROVIDED
raise InsufficientResources(
    f"Cannot cast Fireball: need {ability.cost} MP, "
    f"have {character.mp}. "
    f"Restore with Mana Potion or rest."
)
```

### 3. Preserve Traceback

```python
# ❌ LOST TRACEBACK
except ValueError:
    raise DataValidationError("Invalid data")

# ✅ PRESERVED TRACEBACK
except ValueError as e:
    raise DataValidationError("Invalid data") from e
```

### 4. Document Exception Conditions

```python
def use_item(self, item_id: str) -> None:
    """Use item from inventory.
    
    Args:
        item_id: ID of item to use
    
    Raises:
        InvalidItemUse: If item cannot be used in this context
        InsufficientQuantity: If not enough items in inventory
        CombatError: If trying to use item outside allowed times
    """
```

### 5. Never Silently Ignore Errors

```python
# ❌ SILENT FAILURE
try:
    save_game()
except:
    pass

# ✅ LOGGED FAILURE
try:
    save_game()
except Exception as e:
    logger.error(f"Auto-save failed: {e}")
    notify_player("Could not auto-save game")
```

---

## Exception Hierarchy Implementation

### Complete Example

```python
# Using multiple exception types
def complete_quest(self, quest_id: str) -> bool:
    """Complete quest with full error handling."""
    
    try:
        # Validation
        quest = self.quest_repo.find_by_id(quest_id)
        if not quest:
            raise MissingDataError(f"Quest '{quest_id}' not found in data")
        
        if quest.status != QuestStatus.ACCEPTED:
            raise InvalidGameState(
                f"Quest '{quest_id}' must be accepted before completion"
            )
        
        # Process completion
        rewards = self.calculate_rewards(quest)
        
        if not self._can_award_rewards(rewards):
            raise InvalidGameState("Cannot award quest rewards")
        
        # Award rewards
        self.player.add_experience(rewards.xp)
        self.player.add_items(rewards.items)
        
        # Update quest state
        quest.status = QuestStatus.COMPLETED
        self.persistence_repo.save_game(...)
        
        logger.info(f"Quest '{quest_id}' completed")
        return True
    
    except MissingDataError as e:
        logger.error(f"Quest data error: {e}")
        raise  # Cannot recover from missing quest data
    
    except InvalidGameState as e:
        logger.warning(f"Cannot complete quest: {e}")
        notify_player(str(e))
        return False  # Return failure but don't crash
    
    except SaveFileError as e:
        logger.warning(f"Could not persist completion: {e}")
        # Quest is complete, but couldn't save - still OK
        notify_player("Quest complete! (Could not save)")
        return True
    
    except Exception as e:
        logger.critical(f"Unexpected error completing quest: {e}", exc_info=True)
        raise GameError(f"Unrecoverable error: {e}") from e
```

---

## Integration with Other Systems

See:
- [01-ARCHITECTURE.md](01-ARCHITECTURE.md) for error handling strategy
- [07-dependency-injection.md](07-dependency-injection.md) for exception propagation
- [11-testing.md](11-testing.md) for testing exception cases
