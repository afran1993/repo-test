# 10 - Configuration and Localization

Game configuration management, i18n (internationalization), language support, and settings system.

## Table of Contents
- [Configuration System](#configuration-system)
- [Settings Management](#settings-management)
- [i18n & Localization](#i18n--localization)
- [Language Files](#language-files)
- [Dynamic Translation](#dynamic-translation)
- [Adding New Languages](#adding-new-languages)

---

## Configuration System

### Config File Structure

Game configuration in `config.json`:

```json
{
  "game": {
    "title": "RPG Game",
    "version": "1.0.0",
    "build_date": "2026-02-13"
  },
  "display": {
    "width": 80,
    "height": 24,
    "colors": true,
    "animations": true
  },
  "gameplay": {
    "difficulty": "normal",
    "experience_multiplier": 1.0,
    "enemy_scaling": true
  },
  "audio": {
    "enabled": false,
    "master_volume": 100,
    "music_volume": 80,
    "sfx_volume": 90
  },
  "localization": {
    "language": "en",
    "date_format": "MM/DD/YYYY",
    "time_format": "12h"
  },
  "performance": {
    "fps_cap": 60,
    "debug_mode": false,
    "log_level": "INFO"
  }
}
```

### Configuration Class

Located in `src/config.py`:

```python
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class GameConfig:
    """Game configuration."""
    
    # Game info
    title: str = "RPG Game"
    version: str = "1.0.0"
    
    # Display
    width: int = 80
    height: int = 24
    colors_enabled: bool = True
    animations_enabled: bool = True
    
    # Gameplay
    difficulty: str = "normal"  # easy, normal, hard
    experience_multiplier: float = 1.0
    enemy_scaling: bool = True
    
    # Audio
    audio_enabled: bool = False
    master_volume: int = 100
    music_volume: int = 80
    sfx_volume: int = 90
    
    # Localization
    language: str = "en"
    date_format: str = "MM/DD/YYYY"
    time_format: str = "12h"  # 12h or 24h
    
    # Performance
    fps_cap: int = 60
    debug_mode: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def load_from_file(cls, filepath: str = "config.json") -> "GameConfig":
        """Load configuration from JSON file."""
        try:
            with open(filepath) as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {filepath}, using defaults")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid config JSON: {e}")
            return cls()
        
        # Flatten nested config
        config_dict = {
            "title": data.get("game", {}).get("title", cls.title),
            "version": data.get("game", {}).get("version", cls.version),
            "width": data.get("display", {}).get("width", cls.width),
            "height": data.get("display", {}).get("height", cls.height),
            "colors_enabled": data.get("display", {}).get("colors", cls.colors_enabled),
            "difficulty": data.get("gameplay", {}).get("difficulty", cls.difficulty),
            "language": data.get("localization", {}).get("language", cls.language),
            "fps_cap": data.get("performance", {}).get("fps_cap", cls.fps_cap),
            "debug_mode": data.get("performance", {}).get("debug_mode", cls.debug_mode),
        }
        
        return cls(**config_dict)
    
    def save_to_file(self, filepath: str = "config.json") -> bool:
        """Save configuration to JSON file."""
        try:
            data = {
                "game": {
                    "title": self.title,
                    "version": self.version,
                },
                "display": {
                    "width": self.width,
                    "height": self.height,
                    "colors": self.colors_enabled,
                    "animations": self.animations_enabled,
                },
                "gameplay": {
                    "difficulty": self.difficulty,
                    "experience_multiplier": self.experience_multiplier,
                },
                "localization": {
                    "language": self.language,
                    "date_format": self.date_format,
                },
                "performance": {
                    "fps_cap": self.fps_cap,
                    "debug_mode": self.debug_mode,
                    "log_level": self.log_level,
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except IOError as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    @classmethod
    def create_default(cls) -> "GameConfig":
        """Create default configuration."""
        return cls()
```

---

## Settings Management

### Settings Menu

```python
class SettingsMenu:
    """In-game settings menu."""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.options = [
            ("Difficulty", self._change_difficulty),
            ("Language", self._change_language),
            ("Display", self._change_display),
            ("Audio", self._change_audio),
            ("Back", self._back),
        ]
    
    def _change_difficulty(self):
        """Change game difficulty."""
        difficulties = [
            ("Easy (1.5x XP, 0.5x enemy damage)", "easy"),
            ("Normal (1x XP, 1x enemy damage)", "normal"),
            ("Hard (0.5x XP, 1.5x enemy damage)", "hard"),
            ("Back", None),
        ]
        
        choice = display_menu(difficulties)
        if choice:
            self.config.difficulty = choice
            self.config.experience_multiplier = {
                "easy": 1.5,
                "normal": 1.0,
                "hard": 0.5,
            }[choice]
    
    def _change_language(self):
        """Change game language."""
        available_languages = [
            ("English", "en"),
            ("Italian", "it"),
            ("Spanish", "es"),
            ("Back", None),
        ]
        
        choice = display_menu(available_languages)
        if choice:
            self.config.language = choice
            # Reload localization
            from src.i18n import I18nManager
            i18n = I18nManager.load(choice)
    
    def _change_display(self):
        """Change display settings."""
        display_options = [
            ("Toggle Colors", self._toggle_colors),
            ("Toggle Animations", self._toggle_animations),
            ("Back", None),
        ]
        
        choice = display_menu(display_options)
        if choice:
            choice()
    
    def _toggle_colors(self):
        """Toggle color support."""
        self.config.colors_enabled = not self.config.colors_enabled
    
    def _toggle_animations(self):
        """Toggle animations."""
        self.config.animations_enabled = not self.config.animations_enabled
```

---

## i18n & Localization

### I18n Manager

Located in `src/i18n.py`:

```python
class I18nManager:
    """Internationalization manager."""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.translations = {}
        self.fallback_language = "en"
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translation file for current language."""
        filepath = f"locales/{self.language}.json"
        
        try:
            with open(filepath) as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Translation file not found: {filepath}")
            logger.info(f"Falling back to {self.fallback_language}")
            self.language = self.fallback_language
            self._load_translations()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid translation JSON: {e}")
            self.translations = {}
    
    def translate(self, key: str, **kwargs) -> str:
        """Get translated string.
        
        Args:
            key: Translation key (e.g., "ui.menu.quit")
            **kwargs: Variables to interpolate
        
        Returns:
            Translated string with interpolated variables
        """
        # Navigate nested dict
        keys = key.split(".")
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                logger.warning(f"Translation key not found: {key}")
                return key  # Return key if not found
        
        # Interpolate variables
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing variable in translation: {e}")
                return value
        
        return str(value)
    
    def pluralize(self, key: str, count: int, **kwargs) -> str:
        """Get plural form translation.
        
        Args:
            key: Translation key
            count: Item count
            **kwargs: Variables to interpolate
        
        Returns:
            Translated string (singular or plural)
        """
        # Get plural entry
        plural_key = f"{key}.plural" if count != 1 else f"{key}.singular"
        return self.translate(plural_key, count=count, **kwargs)
    
    @classmethod
    def load(cls, language: str = "en") -> "I18nManager":
        """Load i18n manager for language."""
        return cls(language)

# Global instance
_i18n = None

def init_i18n(language: str = "en"):
    global _i18n
    _i18n = I18nManager(language)

def _(key: str, **kwargs) -> str:
    """Shorthand for translation."""
    global _i18n
    if _i18n is None:
        init_i18n()
    return _i18n.translate(key, **kwargs)
```

---

## Language Files

### English Translation (`locales/en.json`)

```json
{
  "game": {
    "title": "RPG Game",
    "version": "1.0.0"
  },
  "ui": {
    "menu": {
      "new_game": "New Game",
      "load_game": "Load Game",
      "settings": "Settings",
      "quit": "Quit"
    },
    "combat": {
      "attack": "Attack",
      "ability": "Ability",
      "item": "Item",
      "defend": "Defend"
    },
    "dialogue": {
      "choice": "What will you do?",
      "skill_check": "Make a {skill} check (DC {dc})"
    }
  },
  "messages": {
    "welcome": "Welcome to the RPG world!",
    "victory": "You have won the battle!",
    "defeat": "You were defeated...",
    "level_up": "You reached level {level}!",
    "item_found": {
      "singular": "You found 1 item!",
      "plural": "You found {count} items!"
    }
  },
  "errors": {
    "invalid_input": "Invalid input. Try again.",
    "not_enough_mp": "Not enough MP for this ability.",
    "inventory_full": "Your inventory is full!"
  }
}
```

### Italian Translation (`locales/it.json`)

```json
{
  "game": {
    "title": "Gioco RPG",
    "version": "1.0.0"
  },
  "ui": {
    "menu": {
      "new_game": "Nuova Partita",
      "load_game": "Carica Partita",
      "settings": "Impostazioni",
      "quit": "Esci"
    },
    "combat": {
      "attack": "Attacca",
      "ability": "Abilità",
      "item": "Oggetto",
      "defend": "Difendi"
    },
    "dialogue": {
      "choice": "Cosa farai?",
      "skill_check": "Fai una prova di {skill} (CD {dc})"
    }
  },
  "messages": {
    "welcome": "Benvenuto nel mondo RPG!",
    "victory": "Hai vinto la battaglia!",
    "defeat": "Sei stato sconfitto...",
    "level_up": "Hai raggiunto il livello {level}!",
    "item_found": {
      "singular": "Hai trovato 1 oggetto!",
      "plural": "Hai trovato {count} oggetti!"
    }
  },
  "errors": {
    "invalid_input": "Input non valido. Riprova.",
    "not_enough_mp": "Non hai abbastanza MP per questa abilità.",
    "inventory_full": "Il tuo inventario è pieno!"
  }
}
```

---

## Dynamic Translation

### Using Translations in Code

```python
# Simple translation
from src.i18n import _

def fight_dragon(player, dragon):
    print(_("messages.victory"))  # "You have won the battle!"

# With variables
damage = 150
print(_("messages.damage_dealt", damage=damage))
# → "You dealt 150 damage!"

# Plural forms
item_count = 3
print(_("messages.item_found", count=item_count))
# → "You found 3 items!"

# Nested keys
print(_("ui.menu.new_game"))  # "New Game"
```

### Location Names and Descriptions

```python
class Location:
    def __init__(self, location_id: str):
        self.id = location_id
        self.name = _(f"locations.{location_id}.name")
        self.description = _(f"locations.{location_id}.description")
    
    def display(self):
        print("="*50)
        print(self.name.center(50))
        print("="*50)
        print(f"\n{self.description}\n")

# Translation file entry
# "locations": {
#   "town_plaza": {
#     "name": "Town Plaza",
#     "description": "The heart of the town, bustling with activity..."
#   }
# }
```

### NPC Names and Dialogues

```python
class NPC:
    def __init__(self, npc_data: dict):
        self.id = npc_data["id"]
        self.name = _(f"npcs.{self.id}.name")
        self.role = _(f"npcs.{self.id}.role")
    
    def get_dialogue(self, dialogue_id: str) -> str:
        """Get dialogue text."""
        key = f"dialogue.{self.id}.{dialogue_id}"
        return _(key)

# Translation file
# "npcs": {
#   "guildmaster": {
#     "name": "Master of Guilds",
#     "role": "Quest Giver"
#   }
# },
# "dialogue": {
#   "guildmaster": {
#     "first_meeting": "Welcome to the guild!"
#   }
# }
```

---

## Missing Translations Tool

### Extract Missing Keys

```python
def extract_missing_translations(config_language: str) -> List[str]:
    """Find translation keys that exist in one language but not another."""
    
    default_lang = I18nManager("en")
    target_lang = I18nManager(config_language)
    
    missing = []
    
    def find_missing_recursive(en_dict, target_dict, prefix=""):
        for key, value in en_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if key not in target_dict:
                missing.append(full_key)
            elif isinstance(value, dict) and isinstance(target_dict.get(key), dict):
                find_missing_recursive(value, target_dict[key], full_key)
    
    find_missing_recursive(default_lang.translations, target_lang.translations)
    return missing

# Usage
missing = extract_missing_translations("it")
if missing:
    print(f"Missing {len(missing)} translations in Italian:")
    for key in missing:
        print(f"  - {key}")
```

---

## Adding New Languages

### Step 1: Create Translation File

Create `locales/es.json` for Spanish:

```json
{
  "game": {
    "title": "Juego RPG",
    "version": "1.0.0"
  },
  "ui": {
    "menu": {
      "new_game": "Nuevo Juego",
      "load_game": "Cargar Juego",
      "settings": "Configuración",
      "quit": "Salir"
    }
  }
}
```

### Step 2: Add to Config

Update `config.json`:

```json
{
  "localization": {
    "language": "es",
    "available_languages": ["en", "it", "es"]
  }
}
```

### Step 3: Update Settings Menu

Add language option in settings:

```python
available_languages = [
    ("English", "en"),
    ("Italian", "it"),
    ("Spanish", "es"),  # Add this
    ("Back", None),
]
```

---

## Best Practices

### 1. Use Consistent Key Naming
```
Good:  messages.victory, ui.menu.new_game, dialogue.npc_name.greeting
Bad:   msg_you_win, MainMenuNewGameOption, npc_greeting
```

### 2. Provide Context with Variables
```python
# ❌ Different for singular/plural
print(_("item_found_one"))  # "Found item"
print(_("item_found_many"))  # "Found items"

# ✅ Single key with variable
print(_("item_found", count=item_count))  # Handles both
```

### 3. Keep Translations Updated
```python
# Run weekly to find missing translations
missing = extract_missing_translations("it")
if missing:
    logger.warning(f"Missing Italian translations: {missing}")
```

### 4. Mark Translatable Strings
Use comments to help translators:
```python
# TRANSLATE: Player reward message
reward_msg = _("messages.quest_reward", amount=gold)
```

---

## Integration with Other Systems

See:
- [01-ARCHITECTURE.md](01-ARCHITECTURE.md) for i18n in architecture
- [09-game-loop.md](09-game-loop.md) for menu i18n
- [06-story-dialogue.md](06-story-dialogue.md) for dialogue translations
