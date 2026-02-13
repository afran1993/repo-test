# Data Format Reference

Complete JSON schemas for all game data files.

## enemies.json

Defines all enemy types in the game with combat stats, abilities, and loot.

```json
{
  "enemies": [
    {
      "id": "red_slime",
      "display": "Red Slime",
      "tier": 1,
      "hp": 8,
      "atk": 2,
      "def": 0,
      "speed": 3,
      "element": "None",
      "tags": ["slime", "common"],
      
      "abilities": ["poison_cloud"],
      "behaviors": ["aggressive"],
      
      "resistances": {"Water": 0.5},
      "immunities": [],
      "vulnerabilities": ["Fire"],
      
      "regeneration": 0,
      "boss": false,
      "endgame": false,
      "drops": [
        {"gold": {"min": 1, "max": 3}, "chance": 0.8},
        {"item": "slime_core", "chance": 0.1}
      ]
    }
  ]
}
```

### Enemy Properties

| Property | Type | Description | Examples |
|----------|------|-------------|----------|
| `id` | string | Unique identifier | "red_slime", "dragon_wyrmling" |
| `display` | string | Display name | "Red Slime", "Dragon Wyrmling" |
| `tier` | int | Enemy difficulty level (1-6) | 1 = weak, 4 = boss, 6 = final boss |
| `hp` | int | Health points | 5-250 |
| `atk` | int | Attack power | 1-22 |
| `def` | int | Defense rating | 0-12 |
| `speed` | int | Combat speed (evasion) | 1-10 (higher = faster) |
| `element` | string | Element type | "Fire", "Ice", "Water", "Air", "Earth", "Arcane", "Lightning", "None" |
| `tags` | array | Categorization tags | ["slime", "fire", "boss"] |
| `abilities` | array | Special abilities | ["fireball", "regenerate", "life_drain"] |
| `behaviors` | array | Combat behaviors | ["steal", "aggressive"] |
| `resistances` | object | Element damage reduction | {"Fire": 0.5} = 50% damage |
| `immunities` | array | Damage types immunity | ["Poison", "Physical"] |
| `vulnerabilities` | array | Extra damage from elements | ["Holy", "Lightning"] = 150% damage |
| `regeneration` | int | HP recovered per turn | 0-5 |
| `boss` | bool | Is this a boss? | true/false |
| `final_boss` | bool | Is this the final boss? | true/false |
| `endgame` | bool | Post-game content? | true/false |
| `drops` | array | Item/gold rewards | See drops format |

### Drop Format

```json
{
  "gold": {"min": 10, "max": 25},
  "chance": 0.8
}
```
or
```json
{
  "item": "dragon_scale",
  "chance": 0.4
}
```

## locations.json

Defines all map locations with connections and spawning.

```json
{
  "locations": [
    {
      "id": "beach",
      "name": "Spiaggia dell'Isola",
      "description": "You are on a sandy beach...",
      "connections": {"north": "forest", "east": "village"},
      "enemies": [
        {"id": "seagull", "chance": 0.5},
        {"id": "crab", "chance": 0.3}
      ],
      "difficulty": 1,
      "npcs": ["merchant_001"]
    }
  ]
}
```

## npcs.json

Defines NPC characters and dialogue trees.

```json
{
  "npcs": [
    {
      "id": "merchant_001",
      "display": "Wandering Merchant",
      "location": "beach",
      "dialogs": [
        {
          "id": "greeting",
          "text": "Welcome, traveler!",
          "choices": [
            {"text": "What do you sell?", "next": "shop"},
            {"text": "Goodbye.", "next": "end"}
          ]
        }
      ]
    }
  ]
}
```

## items.json

Defines all items (weapons, armor, consumables).

```json
{
  "items": [
    {
      "id": "sword_rusty",
      "name": "Rusty Sword",
      "type": "weapon",
      "stats": {"atk": 3, "dex": 1},
      "cost": 10,
      "rarity": "common"
    }
  ]
}
```

## quests.json

Defines gameplay quests and objectives.

```json
{
  "quests": [
    {
      "id": "defeat_slimes",
      "title": "Defeat Red Slimes",
      "description": "Destroy 5 red slimes to protect the village",
      "location": "forest",
      "objective": "defeat_count",
      "target": 5,
      "reward_xp": 50,
      "reward_gold": 100
    }
  ]
}
```

## abilities.json

Defines special abilities for combat.

```json
{
  "abilities": [
    {
      "id": "fireball",
      "name": "Fireball",
      "type": "spell",
      "power": 15,
      "element": "Fire",
      "mana_cost": 20,
      "cooldown": 2,
      "description": "Deal fire damage to enemy"
    }
  ]
}
```

---

**Related Documentation**:
- [Game Systems](02-game-systems.md)
- [Combat Engine](04-combat-engine.md)
- [Development Guide](12-development-guide.md)
