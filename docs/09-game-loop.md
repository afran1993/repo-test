# 09 - Game Loop and Menu System

Main game loop, menu architecture, state machine, and UI flow.

## Table of Contents
- [Game Loop Architecture](#game-loop-architecture)
- [Game States](#game-states)
- [Menu System](#menu-system)
- [CLI Adapter](#cli-adapter)
- [User Input Handling](#user-input-handling)
- [State Transitions](#state-transitions)

---

## Game Loop Architecture

### Main Loop

The main game loop is in `src/game_runner.py`:

```python
class GameRunner:
    """Main game loop orchestrator."""
    
    def __init__(self, context: GameContext):
        self.context = context
        self.current_state = GameState.MAIN_MENU
        self.running = True
        self.logger = logging.getLogger(__name__)
    
    def run(self) -> None:
        """Main game loop."""
        self.context.display.show_title_screen()
        
        while self.running:
            try:
                self._process_state()
            except GameError as e:
                self.logger.error(f"Game error: {e}")
                self.context.display.show_error(str(e))
            except KeyboardInterrupt:
                self.context.display.show_message("Game interrupted")
                self.running = False
            except Exception as e:
                self.logger.critical(f"Unexpected error: {e}", exc_info=True)
                self.context.display.show_fatal_error()
                self.running = False
    
    def _process_state(self) -> None:
        """Handle current game state."""
        state_handler = {
            GameState.MAIN_MENU: self._handle_main_menu,
            GameState.PLAYING: self._handle_playing,
            GameState.IN_COMBAT: self._handle_combat,
            GameState.IN_DIALOGUE: self._handle_dialogue,
            GameState.INVENTORY: self._handle_inventory,
            GameState.PAUSED: self._handle_paused,
            GameState.QUIT: self._handle_quit,
        }
        
        handler = state_handler.get(self.current_state)
        if handler:
            handler()
        else:
            self.logger.warning(f"Unknown state: {self.current_state}")
            self.current_state = GameState.MAIN_MENU
```

### Loop Frequency

```python
# Target 60 FPS for UI responsiveness
TARGET_FPS = 60
FRAME_DURATION = 1 / TARGET_FPS  # ~16.67ms

while self.running:
    frame_start = time.time()
    
    # Process game logic
    self._process_state()
    
    # Maintain frame rate
    elapsed = time.time() - frame_start
    sleep_time = FRAME_DURATION - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)
```

### Loop Phases

Each iteration handles:

```
1. Input Phase
   └─ Read user input from terminal
   └─ Validate input
   └─ Queue actions

2. Update Phase
   └─ Process queued actions
   └─ Update game state
   └─ Check state transitions
   └─ Publish events

3. Render Phase
   └─ Calculate display state
   └─ Render UI
   └─ Output to terminal

4. Cleanup Phase
   └─ Remove completed effects
   └─ Log metrics
   └─ Prepare for next frame
```

---

## Game States

### State Diagram

```
┌──────────────┐
│  MAIN_MENU   │
└────┬─────────┘
     │ Start Game
     ▼
┌──────────────┐      Combat Start      ┌──────────────┐
│   PLAYING    ├─────────────────────→  │  IN_COMBAT   │
│              │                         │              │
│              │←─────────────────────   │              │
│              │     Combat End          │              │
└─┬──────────┬─┘                         └──────────────┘
  │          │
  │ Interact │
  │ with NPC │ Dialogue Start
  │          └─→ ┌──────────────┐
  │              │ IN_DIALOGUE  │
  │              │              │
  │              │              │
  └─ ∧ Dialogue──┴──────────────┘
    │ End
    │
    │ Open Menu
    ▼
┌──────────────┐
│  INVENTORY   │◄──┐ Switch Menu
│   SETTINGS   │───┘
│   CHARACTER  │
└───┬──────────┘
    │ Close Menu
    ▼
┌──────────────┐
│   PAUSED     │
└───┬──────────┘
    │
    └─ Enter/Exit Game
    
    ▼
┌──────────────┐
│     QUIT     │
└──────────────┘
```

### State Classes

```python
from enum import Enum, auto

class GameState(Enum):
    """Possible game states."""
    
    MAIN_MENU = auto()      # Main menu display
    LOADING = auto()        # Loading save game
    PLAYING = auto()        # Free exploration
    IN_COMBAT = auto()       # Active combat
    IN_DIALOGUE = auto()      # NPC conversation
    INVENTORY = auto()       # Item management
    CHARACTER = auto()       # Character sheet
    SETTINGS = auto()        # Settings menu
    PAUSED = auto()          # Game paused
    GAME_OVER = auto()       # Defeat
    VICTORY = auto()         # Story complete
    QUIT = auto()            # Exiting game

class GameContext:
    """Current game context."""
    
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.previous_state = None
        self.current_location = None
        self.current_player = None
        self.current_combat = None
        self.current_dialogue = None
```

### State Handlers

```python
def _handle_main_menu(self) -> None:
    """Handle main menu state."""
    menu_options = [
        ("New Game", self._start_new_game),
        ("Load Game", self._load_game),
        ("Settings", self._open_settings),
        ("Quit", self._quit_game),
    ]
    
    choice = display_menu(menu_options)
    if choice:
        choice[1]()  # Execute selected action

def _handle_playing(self) -> None:
    """Handle free exploration state."""
    location = self.context.current_location
    
    # Show location
    self.context.display.show_location(location)
    
    # Get player action
    actions = location.get_available_actions()
    choice = display_menu(actions)
    
    if choice == "explore":
        # Move to new location
        next_location = choice["destination"]
        self.context.current_location = next_location
    
    elif choice == "interact":
        # Start dialogue with NPC
        npc = choice["npc"]
        self.current_state = GameState.IN_DIALOGUE
        self.context.current_dialogue = Dialogue.start(npc.id)
    
    elif choice == "encounter_enemy":
        # Start combat
        enemies = choice["enemies"]
        self.current_state = GameState.IN_COMBAT
        self.context.current_combat = Combat(
            player_team=[self.context.current_player],
            enemy_team=enemies
        )
        self.context.current_combat.start()

def _handle_combat(self) -> None:
    """Handle combat state."""
    combat = self.context.current_combat
    
    if not combat.is_active():
        # Combat ended
        if combat.is_victory():
            self.context.display.show_victory_screen()
            # Award rewards
            self._award_combat_rewards(combat)
        else:
            self.context.display.show_defeat_screen()
            # Handle player defeat
            self._handle_player_defeat()
        
        self.current_state = GameState.PLAYING
        return
    
    # Display combat status
    self.context.display.show_combat_status(combat)
    
    # Get player action
    action = self.context.display.get_combat_action()
    
    # Execute action
    try:
        combat.execute_turn(action)
    except GameError as e:
        self.context.display.show_error(str(e))

def _handle_dialogue(self) -> None:
    """Handle dialogue state."""
    dialogue = self.context.current_dialogue
    
    if not dialogue.is_active():
        # Dialogue ended
        self.current_state = GameState.PLAYING
        return
    
    # Show dialogue text
    node = dialogue.get_current_node()
    self.context.display.show_dialogue(node)
    
    # Get player choice
    choices = dialogue.get_choices()
    choice_index = self.context.display.get_choice(choices)
    
    # Process choice
    result = dialogue.select_choice(choice_index)
    
    # Handle triggers (quest updates, etc.)
    if result.triggers:
        self._process_triggers(result.triggers)
```

---

## Menu System

### Menu Architecture

Menus are defined in `src/menus.py`:

```python
class Menu:
    """Base menu class."""
    
    def __init__(self, title: str, options: List[MenuOption]):
        self.title = title
        self.options = options
        self.cursor_position = 0
    
    def render(self) -> str:
        """Render menu as string."""
        output = f"\n{'='*40}\n"
        output += f"  {self.title}\n"
        output += f"{'='*40}\n\n"
        
        for i, option in enumerate(self.options):
            marker = "►" if i == self.cursor_position else " "
            output += f"{marker} {i+1}. {option.label}\n"
        
        output += "\n"
        return output
    
    def handle_input(self, input_key: str) -> Optional[Any]:
        """Handle user input navigation."""
        if input_key == "UP":
            self.cursor_position = max(0, self.cursor_position - 1)
        elif input_key == "DOWN":
            self.cursor_position = min(len(self.options) - 1, self.cursor_position + 1)
        elif input_key == "ENTER":
            selected = self.options[self.cursor_position]
            return selected.action
        
        return None

class MainMenu(Menu):
    """Main title screen menu."""
    
    def __init__(self):
        options = [
            MenuOption("New Game", action="new_game"),
            MenuOption("Load Game", action="load_game"),
            MenuOption("Settings", action="settings"),
            MenuOption("Quit", action="quit"),
        ]
        super().__init__("MAIN MENU", options)

class CombatMenu(Menu):
    """Combat action selection menu."""
    
    def __init__(self, player: Character):
        options = [
            MenuOption("Attack", action="attack"),
            MenuOption("Abilities", action="abilities"),
            MenuOption("Items", action="items"),
            MenuOption("Defend", action="defend"),
        ]
        super().__init__("CHOOSE ACTION", options)
```

### Submenu Navigation

```python
class MenuStack:
    """Manage menu hierarchy."""
    
    def __init__(self):
        self.stack: List[Menu] = []
    
    def push(self, menu: Menu) -> None:
        """Open new menu (goes on top)."""
        self.stack.append(menu)
    
    def pop(self) -> Optional[Menu]:
        """Close current menu (return to previous)."""
        if len(self.stack) > 1:
            self.stack.pop()
            return self.current()
        return None
    
    def current(self) -> Menu:
        """Get active menu."""
        return self.stack[-1] if self.stack else None
    
    def back_to_main(self) -> None:
        """Close all menus (return to main menu)."""
        self.stack = [self.stack[0]]

# Usage
menu_stack = MenuStack()
menu_stack.push(MainMenu())

while game_running:
    current_menu = menu_stack.current()
    action = current_menu.handle_input(get_input())
    
    if action == "abilities":
        menu_stack.push(AbilitiesMenu(player))
    elif action == "back":
        menu_stack.pop()
```

---

## CLI Adapter

### Display Interface

Located in `src/commands.py`, provides all display functions:

```python
class Display:
    """Abstract display interface."""
    
    def show_title_screen(self) -> None:
        """Show game title and main menu."""
        pass
    
    def show_location(self, location: Location) -> None:
        """Show current location description."""
        pass
    
    def show_combat_status(self, combat: Combat) -> None:
        """Show current combat state."""
        pass
    
    def show_dialogue(self, dialogue_node: dict) -> None:
        """Show dialogue box with NPC text."""
        pass
    
    def show_inventory(self, inventory: Inventory) -> None:
        """Show player inventory."""
        pass
    
    def show_character_sheet(self, player: Character) -> None:
        """Show character stats and equipment."""
        pass

class CLIDisplay(Display):
    """Terminal-based display implementation."""
    
    def show_location(self, location: Location) -> None:
        """Render location to terminal."""
        print("\n" + "="*50)
        print(f"  {location.name}".center(50))
        print("="*50)
        print(f"\n{location.description}\n")
        
        if location.npcs:
            print("NPCs here:")
            for npc in location.npcs:
                print(f"  • {npc.name}")
        
        if location.enemies:
            print("\nEnemies:")
            for enemy in location.enemies:
                print(f"  • {enemy.name} (Level {enemy.tier})")
    
    def show_combat_status(self, combat: Combat) -> None:
        """Show combat state."""
        print("\n" + "="*50)
        print("  COMBAT".center(50))
        print("="*50 + "\n")
        
        # Show player team
        print("Your Party:")
        for char in combat.player_team:
            hp_bar = self._get_hp_bar(char)
            print(f"  {char.name}: {hp_bar} {char.hp}/{char.max_hp}")
        
        print()
        
        # Show enemies
        print("Enemies:")
        for enemy in combat.enemy_team:
            hp_bar = self._get_hp_bar(enemy)
            print(f"  {enemy.name}: {hp_bar} {enemy.hp}/{enemy.max_hp}")
    
    def _get_hp_bar(self, character: Character) -> str:
        """Get visual HP bar."""
        filled = int((character.hp / character.max_hp) * 10)
        empty = 10 - filled
        return f"[{'█' * filled}{'░' * empty}]"
```

---

## User Input Handling

### Input Processing

```python
def get_user_input(self) -> str:
    """Get input from player."""
    try:
        user_input = input("> ").strip().lower()
        return user_input
    except EOFError:
        return "quit"
    except KeyboardInterrupt:
        return "quit"

def process_input(self, user_input: str) -> Optional[Action]:
    """Convert user input to game action."""
    
    # Parse command
    parts = user_input.split()
    if not parts:
        return None
    
    command = parts[0]
    args = parts[1:]
    
    # Handle commands
    if command in ["a", "attack"]:
        return Action(type="attack", args=args)
    
    elif command in ["use", "u"]:
        if len(args) < 1:
            self.display.show_message("Use what?")
            return None
        return Action(type="use", target=args[0])
    
    elif command in ["inventory", "i"]:
        return Action(type="inventory")
    
    elif command in ["character", "c"]:
        return Action(type="character_sheet")
    
    elif command in ["talk", "t"]:
        if len(args) < 1:
            self.display.show_message("Talk to whom?")
            return None
        return Action(type="dialogue", target=args[0])
    
    elif command in ["go", "move", "m"]:
        if len(args) < 1:
            self.display.show_message("Go where?")
            return None
        return Action(type="move", destination=args[0])
    
    elif command in ["quit", "q"]:
        return Action(type="quit")
    
    else:
        self.display.show_message(f"Unknown command: {command}")
        return None
```

---

## State Transitions

### Transition Rules

```python
def process_state_transition(self) -> None:
    """Handle transitions between states."""
    
    # Playing → Combat
    if self.current_state == GameState.PLAYING:
        location = self.context.current_location
        if location.has_random_encounter():
            enemies = location.generate_enemies()
            self.context.current_combat = Combat(
                player_team=[self.context.current_player],
                enemy_team=enemies
            )
            self.current_state = GameState.IN_COMBAT
    
    # Combat → Playing (victory)
    elif self.current_state == GameState.IN_COMBAT:
        combat = self.context.current_combat
        if not combat.is_active() and combat.is_victory():
            self._award_rewards(combat)
            self.current_state = GameState.PLAYING
    
    # Combat → GameOver (defeat)
    elif self.current_state == GameState.IN_COMBAT:
        combat = self.context.current_combat
        if not combat.is_active() and not combat.is_victory():
            self.current_state = GameState.GAME_OVER
    
    # Playing → Dialogue (interact with NPC)
    elif self.current_state == GameState.PLAYING:
        action = self.last_action
        if action.type == "dialogue":
            npc = self.context.current_location.get_npc(action.target)
            self.context.current_dialogue = Dialogue.start(npc.id)
            self.current_state = GameState.IN_DIALOGUE
```

---

## Integration with Other Systems

See:
- [02-game-systems.md](02-game-systems.md) for combat and dialogue integration
- [05-player-system.md](05-player-system.md) for character menu display
- [01-ARCHITECTURE.md](01-ARCHITECTURE.md) for overall system flow
