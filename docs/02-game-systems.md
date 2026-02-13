# 02 - Game Systems

Complete technical overview of the core game systems: combat, dialogue, quests, and items.

## Table of Contents
- [Combat System](#combat-system)
- [Dialogue System](#dialogue-system)
- [Quest System](#quest-system)
- [Item System](#item-system)
- [NPC System](#npc-system)

---

## Combat System

### Architecture Overview

The combat system is located in `src/combat/` and implements turn-based RPG combat:

```
Combat Flow:
1. CombatInitiator creates Combat instance
2. Combat.start() initializes participants
3. Main loop: execute_turn() for active participant
4. DamageCalculator processes actions
5. EventEngine outputs results
6. Combat ends when one side is defeated
```

### Core Components

#### `combat.py` - Combat State Machine
- **Purpose**: Orchestrate turn-based combat flow
- **Key Methods**:
  - `start()` - Initialize combat teams
  - `execute_turn(action: Action)` - Process player/enemy action
  - `is_active()` - Check if combat ongoing
  - `get_status()` - Return current battle state

#### `damage_engine.py` - Damage Calculation
- **Purpose**: Calculate damage based on attacker, defender, and action
- **Attack Formula**:
  ```
  Base Damage = Attacker.atk + Ability.power
  Resistances = Defender.get_resistance(element)
  Final Damage = Base Damage × Resistances × RNG(0.9-1.1)
  ```
- **Resistance System**:
  - Immunity: `0.0x` (no damage)
  - Vulnerability: `1.5x` (extra damage)
  - Resistance dict: `{"Fire": 0.5}` (50% reduction)
  - Default: `1.0x` (normal)

#### `abilities.py` - Action Definitions
- **Purpose**: Define what actions can be performed in combat
- **Properties**:
  - `id`: unique identifier
  - `name`: display name
  - `element`: Fire, Ice, Lightning, Poison, Physical, Holy
  - `power`: base damage multiplier (0-100)
  - `cost`: resource cost (MP, stamina)
  - `accuracy`: hit chance (0-100%)

#### `event_engine.py` - Combat Log
- **Purpose**: Output combat events to CLI
- **Events**:
  - `AttackEvent` - Show damage dealt
  - `HealEvent` - Show HP recovery
  - `DeathEvent` - Show combatant defeat
  - `CriticalHit` - Show critical strike
  - `Miss` - Show failed attack

### Integration Points

**Combat Initiation** (via `cli_adapter.py`):
```python
# From CLI command
combat = Combat(player_team=[party], enemy_team=[enemies])
combat.start()

# Main combat loop in game_runner.py
while combat.is_active():
    action = get_player_input()  # From CLI menu
    combat.execute_turn(action)
    display_results(combat.get_status())
```

**Damage Calculation Flow**:
```python
# In Combat.execute_turn():
1. Validate action (has resource, valid target?)
2. Calculator.process_action(action, attacker, defender)
3. Apply damage: defender.hp -= calculated_damage
4. Check resistances via: defender.get_resistance(element)
5. Trigger regeneration (if any)
6. Fire event to event_engine
7. Return damage_result for event_engine output
```

**Regeneration System**:
```python
# After each turn
for combatant in all_combatants:
    if combatant.regeneration > 0:
        combatant.regenerate()  # Applies regeneration_amount
```

### Combat Status Display

The CLI shows current combat state:
```
═══════════ COMBAT ═══════════
Player: Aina [████████░░] 112/150 HP
Enemy: Goblin [██░░░░░░░░] 30/120 HP
───────────────────────────
What will you do?
1. Attack
2. Ability
3. Item
4. Defend
```

---

## Dialogue System

### Architecture Overview

The dialogue system in `src/dialogue/` implements branching dialogue trees with skill checks:

```
Dialogue Flow:
1. dialogue.py loads dialogue nodes from story_data
2. Display current dialogue with choices
3. Player selects response
4. Check skill requirements (if any)
5. Execute skill check (STR, INT, CHA, DEX)
6. Transition to next dialogue node
7. Trigger quest events (if flagged)
```

### Core Components

#### `dialogue.py` - Dialogue State Machine
- **Purpose**: Manage dialogue tree traversal
- **Key Methods**:
  - `start(npc_id: str)` - Begin dialogue with NPC
  - `get_current_node()` - Return active dialogue node
  - `get_choices()` - Return available player options
  - `select_choice(choice_id: int)` - Player makes selection
  - `end_dialogue()` - Close conversation

#### Dialogue Data Structure

Located in `data/quests.json`, dialogue nodes:
```json
{
  "dialogue": {
    "goblin_first_meeting": {
      "text": "Halt! Who goes there?",
      "speaker": "Goblin Guard",
      "choices": [
        {
          "id": 1,
          "text": "I come in peace",
          "next": "goblin_peaceful",
          "check": null
        },
        {
          "id": 2,
          "text": "Stand aside, wretch!",
          "next": "goblin_combat",
          "check": {
            "skill": "STR",
            "dc": 15,
            "success": "intimidate_success",
            "failure": "goblin_combat"
          }
        }
      ]
    }
  }
}
```

#### Skill Checks
- **Type**: STR (Strength), INT (Intelligence), CHA (Charisma), DEX (Dexterity)
- **DC**: Difficulty Class (target number, 10-20)
- **Roll**: `d20 + player_stat + bonuses`
- **Success**: Next node if roll >= DC
- **Failure**: Alternate node if roll < DC

### Integration Points

**Dialogue Triggering** (from game loop):
```python
# When NPC interaction happens
dialogue = Dialogue.start("goblin_guard")
while dialogue.is_active():
    choices = dialogue.get_choices()
    choice_id = display_menu(choices)
    result = dialogue.select_choice(choice_id)
    
    # Skill check resolution
    if result.has_check:
        roll = roll_d20()
        success = resolve_skill_check(result.check, player, roll)
```

**Quest Event Triggers**:
```python
# In dialogue_node.json
"choices": [{
    "next": "quest_accepted_node",
    "triggers": [
        {"type": "quest", "action": "accept", "quest_id": "escort_princess"}
    ]
}]
```

---

## Quest System

### Architecture Overview

Quests in `src/quests/` provide goals, rewards, and progression tracking:

```
Quest Lifecycle:
1. Quest.create() from generator or JSON
2. Player accepts quest (quest_accepted state)
3. Track progress (objectives completed)
4. All objectives complete → ready for completion
5. Quest.complete() → rewards given
6. Transition to completed state
```

### Quest Types

#### Main Quests
- Story-critical progression
- Cannot be abandoned
- Unlock new areas/NPCs

#### Side Quests
- Optional content
- Can be abandoned
- Provide experience/gold/items

#### Bounties
- Defeat specific enemy or quantity
- Time-limited (optional)
- High reward for difficulty

### Core Components

#### `quest.py` - Quest State
- **Status**: `not_started → accepted → completed → failed`
- **Properties**:
  - `id`: unique quest identifier
  - `title`: display name
  - `description`: quest objective
  - `giver`: NPC who offers quest
  - `objectives`: list of objectives to complete
  - `rewards`: experience, gold, items, unlocks
  - `required_level`: minimum to accept

#### `generator.py` - Procedural Quests
- **Purpose**: Generate quests dynamically
- **Methods**:
  - `generate_bounty()` - Create enemy hunt
  - `generate_fetch_quest()` - Create item gathering
  - `generate_escort_quest()` - Create protect NPC
  - `generate_exploration()` - Create area discovery

#### Quest Progression

```python
# Accept quest
quest = Quest.from_data(quest_data)
quest.accept(player)

# Update progress (automatic)
quest.on_enemy_defeated(enemy_id)  # For bounties
quest.on_item_collected(item_id)   # For fetch quests
quest.on_area_discovered(location) # For exploration

# Complete when ready
if quest.all_objectives_complete():
    rewards = quest.complete(player)
    player.give_experience(rewards.xp)
    player.give_items(rewards.items)
```

### Integration Points

**Quest Events** (automatic):
- Enemy defeated → bounty progress | location enemies
- Item collected → item tracking | quest objectives
- NPC conversation → dialogue branches
- Area entered → exploration quest completion

**Quest Rewards**:
- Experience points (scaled by difficulty)
- Gold
- Items (unique or random)
- Unlocks (areas, NPCs, abilities)
- Faction reputation

---

## Item System

### Architecture Overview

Items in `src/items/` represent equipment, consumables, and quest objects:

```
Item Usage:
1. Item creation from JSON data
2. Add to inventory
3. Use in combat/town
4. Track quantity/durability
5. Sell back to shop
```

### Item Categories

#### Equipment
- **Weapons**: Increase ATK stat
- **Armor**: Increase DEF stat
- **Accessories**: Various bonuses

#### Consumables
- **Potions**: Restore HP/MP
- **Status Cures**: Remove negative effects
- **Buffs**: Temporary stat boost

#### Quest Items
- **Unique items**: Cannot be used/sold
- **Trade items**: Currency for vendors
- **Key items**: Unlock areas

### Core Components

#### `item.py` - Item Definition
- **Properties**:
  - `id`: unique item identifier
  - `name`: display name
  - `type`: equipment | consumable | quest
  - `description`: usage details
  - `value`: sell price
  - `effects`: bonuses or restoration amounts

#### Equipment Effects
```json
{
  "id": "iron_sword",
  "type": "equipment",
  "effects": {
    "atk": 5
  }
}
```

#### Consumable Effects
```json
{
  "id": "healing_potion",
  "type": "consumable",
  "effects": {
    "hp_restore": 30,
    "quantity_max": 99,
    "use_in_combat": true
  }
}
```

### Integration Points

**Inventory Management**:
```python
# Add/remove items
player.inventory.add_item(item_id, quantity)
player.inventory.use_item(item_id)
player.inventory.remove_item(item_id, quantity)
```

**Equipment System**:
```python
# Equip weapon
player.equipment.equip(item_slot="weapon", item=sword)
player.atk += sword.effects["atk"]  # Update player stat
```

**Combat Usage**:
```python
# Use consumable in combat
action = Action(type="item", item_id="healing_potion")
combat.execute_turn(action)
player.hp += item.effects["hp_restore"]
```

---

## NPC System

### Architecture Overview

NPCs in `src/npcs/` provide dynamic AI and merchant functionality:

```
NPC Interaction:
1. player.interact(npc_id)
2. Load NPC dialogue/state
3. Display dialogue tree
4. Handle merchant/quest/conversation
5. Update NPC state
```

### NPC Types

#### Merchants
- Sell items
- Buy player items at reduced price
- May carry rare items

#### Quest Givers
- Offer quests
- Track quest state
- Provide rewards

#### Story NPCs
- Dialogue branches
- Skill check requirements
- Dynamic personality

### Core Components

#### `ai.py` - NPC Behavior
- **Purpose**: Define NPC state and actions
- **Methods**:
  - `update_state()` - Handle NPC lifecycle
  - `get_dialogue()` - Return dialogue node
  - `process_interaction()` - Handle player action
  - `can_trade()` - Check if merchant

#### NPC Data Structure

```json
{
  "id": "alchemist",
  "name": "Master Alchemist",
  "location": "town_plaza",
  "role": "merchant",
  "inventory": [
    {"item_id": "healing_potion", "quantity": 50},
    {"item_id": "mana_potion", "quantity": 30}
  ],
  "dialogue_tree": "alchemist_first_meeting"
}
```

### Integration Points

**NPC Encounters**:
```python
# When entering location
npc = load_npc(npc_id)
if player.can_interact(npc):
    dialogue = Dialogue.start(npc.dialogue_tree)
    # ... dialogue resolution
```

**Merchant Interaction**:
```python
# Buy/sell items
merchant = NPC.load("alchemist")
player.buy_item(merchant, item_id, quantity)
player.sell_item(merchant, item_id, quantity)
```

---

## System Integration Summary

```
┌─────────────────┐
│   Game Loop     │
│  (game_runner)  │
└────────┬────────┘
         │
    ┌────┴────────────────────┐
    ▼                          ▼
┌──────────────┐        ┌──────────────┐
│   Combat     │        │  Dialogue    │
│   System     │        │  System      │
└──────────────┘        └──────┬───────┘
         │                     │
         ├─ Damage Engine      ├─ Quest Events
         ├─ Event Engine       └─ NPC Transitions
         └─ Abilities
         
    ┌────────────────────┐
    │   Item System      │
    │   Quest System     │
    │   NPC System       │
    └────────────────────┘
```

---

## Next Steps

- See [04-combat-engine.md](04-combat-engine.md) for damage calculation specifics
- See [05-player-system.md](05-player-system.md) for character progression
- See [06-story-dialogue.md](06-story-dialogue.md) for narrative design
- See [07-dependency-injection.md](07-dependency-injection.md) for system architecture
