# 05 - Player System

Character progression, stats, skills, equipment, and inventory management.

## Table of Contents
- [Character Model](#character-model)
- [Stat System](#stat-system)
- [Experience and Leveling](#experience-and-leveling)
- [Equipment System](#equipment-system)
- [Inventory Management](#inventory-management)
- [Skill Progression](#skill-progression)

---

## Character Model

### Player Class Definition

The player character is defined in `src/characters/character.py`:

```python
class Character:
    def __init__(self, character_data: dict):
        # Core Identity
        self.id = character_data["id"]
        self.name = character_data["name"]
        self.archetype = character_data["archetype"]  # Warrior, Mage, Rogue, Healer
        
        # Level and Experience
        self.level = 1
        self.experience = 0
        self.experience_for_next_level = 1000
        
        # Health and Mana
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        
        # Core Stats (see Stat System section)
        self.stats = {
            "STR": 10,  # Strength
            "DEX": 10,  # Dexterity
            "INT": 10,  # Intelligence
            "CHA": 10,  # Charisma
            "VIT": 10,  # Vitality
        }
        
        # Equipment slots
        self.equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None,
        }
        
        # Inventory
        self.inventory = Inventory()
        
        # Learned abilities
        self.abilities = []
        
        # Current effects (buffs/debuffs)
        self.active_effects = []
```

### Archetype System

Different archetypes have different stat distributions:

#### Warrior
- **Primary**: STR (Strength)
- **Secondary**: VIT (Vitality)
- **Base HP**: 150
- **Base ATK**: 18
- **Advantages**: High damage, high HP
- **Disadvantages**: Low MP, low INT

```
Stats: STR 15, DEX 8, INT 6, CHA 7, VIT 14
```

#### Mage
- **Primary**: INT (Intelligence)
- **Secondary**: DEX (Dexterity)
- **Base HP**: 80
- **Base MP**: 120
- **Advantages**: High MP, high elemental damage
- **Disadvantages**: Low physical defense

```
Stats: STR 6, DEX 12, INT 16, CHA 10, VIT 6
```

#### Rogue
- **Primary**: DEX (Dexterity)
- **Secondary**: CHA (Charisma)
- **Base HP**: 100
- **Base ATK**: 15
- **Advantages**: High speed, high critical chance
- **Disadvantages**: Medium defense

```
Stats: STR 9, DEX 16, INT 8, CHA 12, VIT 9
```

#### Healer
- **Primary**: CHA (Charisma)
- **Secondary**: INT (Intelligence)
- **Base HP**: 90
- **Base MP**: 110
- **Advantages**: Support abilities, MP recovery
- **Disadvantages**: Lower damage output

```
Stats: STR 7, DEX 10, INT 14, CHA 15, VIT 9
```

---

## Stat System

### Core Stats

Each stat influences multiple mechanics:

#### STR (Strength)
- **Impact**: Physical damage, carrying capacity
- **Formula**: `ATK = 5 + (STR × 0.5)`
- **Level scaling**: +1 STR per 2 warrior levels
- **Effect**: 1 STR = +0.5 physical attack power

#### DEX (Dexterity)
- **Impact**: Speed, evasion, critical chance, accuracy
- **Formula**: `SPD = 5 + (DEX × 0.3)`, `CRIT = 5 + (DEX / 10)`
- **Level scaling**: +1 DEX per 2 rogue levels
- **Effects**: 
  - 1 DEX = +0.3 speed
  - 1 DEX = +0.1% critical chance

#### INT (Intelligence)
- **Impact**: Elemental damage, MP pool, magic defense
- **Formula**: `MAG = 5 + (INT × 0.5)`, `MAX_MP = 20 + (INT × 2)`
- **Level scaling**: +1 INT per 2 mage levels
- **Effect**: 1 INT = +0.5 elemental damage, +2 max MP

#### CHA (Charisma)
- **Impact**: Dialogue options, NPC interactions, shop discounts
- **Formula**: `SHOP_DISCOUNT = 0.05 × CHA / 10`
- **Level scaling**: +1 CHA per level for healers
- **Effect**: 1 CHA = -0.5% shop prices (5% cheaper per 10 CHA)

#### VIT (Vitality)
- **Impact**: HP pool, poison/status resistance
- **Formula**: `MAX_HP = 50 + (VIT × 5)`
- **Level scaling**: +1 VIT per level for all classes
- **Effect**: 1 VIT = +5 max HP

### Stat Calculation

```python
def calculate_stats(self) -> Dict[str, int]:
    """Calculate derived stats from base stats."""
    base_stats = self.stats.copy()
    
    # Add equipment bonuses
    for item in self.equipment.values():
        if item:
            for stat, bonus in item.stat_bonuses.items():
                base_stats[stat] += bonus
    
    # Add active effect modifiers
    for effect in self.active_effects:
        for stat, modifier in effect.stat_modifier.items():
            base_stats[stat] *= modifier
    
    # Calculate derived stats
    derived = {
        "ATK": 5 + (base_stats["STR"] * 0.5),
        "DEF": 5 + (base_stats["VIT"] * 0.3),
        "MAG": 5 + (base_stats["INT"] * 0.5),
        "SPD": 5 + (base_stats["DEX"] * 0.3),
        "CRIT": 5 + (base_stats["DEX"] / 10),
        "MAX_HP": 50 + (base_stats["VIT"] * 5),
        "MAX_MP": 20 + (base_stats["INT"] * 2),
    }
    
    return derived

@property
def atk(self) -> float:
    """Attack power (physical damage)."""
    return self.calculate_stats()["ATK"]

@property
def spd(self) -> float:
    """Speed (acting order in combat)."""
    return self.calculate_stats()["SPD"]
```

---

## Experience and Leveling

### Experience Calculation

When defeating enemies, player gains experience:

```python
def calculate_experience_reward(enemy: Enemy, level_difference: int) -> int:
    """
    Calculate XP reward based on enemy level and player level difference.
    
    Args:
        enemy: Defeated enemy
        level_difference: player.level - enemy.level
    
    Returns:
        Experience points gained
    """
    base_xp = 50 * enemy.tier_level  # Higher tier = more XP
    
    # Level scaling
    if level_difference < -5:
        multiplier = 2.0  # 2x XP for significantly harder enemies
    elif level_difference < 0:
        multiplier = 1.5  # 1.5x XP for harder enemies
    elif level_difference == 0:
        multiplier = 1.0  # Normal
    elif level_difference <= 5:
        multiplier = 0.75  # 75% for easier enemies
    else:
        multiplier = 0.25  # 25% for much easier enemies
    
    return int(base_xp * multiplier)
```

### Leveling Up

When experience reaches threshold, character levels up:

```python
def add_experience(self, amount: int) -> bool:
    """
    Add experience and handle leveling up.
    
    Returns:
        True if level up occurred
    """
    self.experience += amount
    
    leveled_up = False
    while self.experience >= self.experience_for_next_level:
        self.level_up()
        leveled_up = True
    
    return leveled_up

def level_up(self):
    """Process single level up."""
    # Subtract XP required
    self.experience -= self.experience_for_next_level
    
    # Increase level
    self.level += 1
    
    # Calculate new XP requirement (exponential growth)
    self.experience_for_next_level = int(1000 * (1.1 ** self.level))
    
    # Increase stats based on archetype
    self._apply_level_up_bonuses()
    
    # Restore HP/MP
    self.hp = self.max_hp
    self.mp = self.max_mp
    
    # Learn new abilities if applicable
    self._learn_level_abilities()
    
    # Notify player
    notify_level_up(self)

def _apply_level_up_bonuses(self):
    """Apply stat increases on level up."""
    archetype_bonuses = {
        "Warrior": {"STR": 2, "VIT": 2, "DEX": 1},
        "Mage": {"INT": 2, "CHA": 1, "DEX": 1},
        "Rogue": {"DEX": 2, "CHA": 1, "STR": 1},
        "Healer": {"CHA": 2, "INT": 1, "VIT": 1},
    }
    
    bonuses = archetype_bonuses[self.archetype]
    for stat, amount in bonuses.items():
        self.stats[stat] += amount
```

### Experience Table

| Level | XP Required | Cumulative XP |
|-------|-------------|---------------|
| 1 | 0 | 0 |
| 2 | 1,100 | 1,100 |
| 3 | 1,210 | 2,310 |
| 5 | 1,464 | 5,335 |
| 10 | 2,594 | 17,531 |
| 20 | 7,327 | 123,838 |
| 30 | 20,756 | 778,430 |

(Formula: `1000 × 1.1^level`)

---

## Equipment System

### Equipment Slots

Players have 3 equipment slots:

1. **Weapon** - Increases ATK
2. **Armor** - Increases DEF
3. **Accessory** - Various bonuses

### Equipment Data Structure

From `data/items.json`:

```json
{
  "id": "iron_sword",
  "type": "equipment",
  "slot": "weapon",
  "name": "Iron Sword",
  "level_requirement": 1,
  "stat_bonuses": {
    "STR": 2
  },
  "description": "A reliable blade for beginners"
}
```

#### Advanced Equipment

```json
{
  "id": "dragon_slayer",
  "type": "equipment",
  "slot": "weapon",
  "name": "Dragon Slayer",
  "level_requirement": 30,
  "stat_bonuses": {
    "STR": 8,
    "DEX": 3
  },
  "effects": {
    "bonus_vs_boss": 1.2  // 20% more damage to bosses
  },
  "description": "Legendary blade forged to slay dragons"
}
```

### Equipment Management

```python
def equip(self, slot: str, item: Item) -> bool:
    """Equip item to slot."""
    if not self.can_equip(item):
        raise InvalidEquipment(f"Cannot equip {item.name}")
    
    # Unequip old item if present
    if self.equipment[slot]:
        old_item = self.equipment[slot]
        self.inventory.add_item(old_item)
    
    # Equip new item
    self.equipment[slot] = item
    self.inventory.remove_item(item)
    
    return True

def can_equip(self, item: Item) -> bool:
    """Check if player can equip item."""
    # Check level requirement
    if self.level < item.level_requirement:
        return False
    
    # Check class requirements (if any)
    if hasattr(item, "class_requirement"):
        if self.archetype != item.class_requirement:
            return False
    
    return True
```

---

## Inventory Management

### Inventory Class

```python
class Inventory:
    def __init__(self, max_slots: int = 20):
        self.items: Dict[str, int] = {}  # item_id → quantity
        self.max_slots = max_slots
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add item to inventory."""
        if item_id not in self.items:
            if len(self.items) >= self.max_slots:
                raise InventoryFull()
            self.items[item_id] = 0
        
        self.items[item_id] += quantity
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory."""
        if self.items.get(item_id, 0) < quantity:
            raise InsufficientQuantity()
        
        self.items[item_id] -= quantity
        if self.items[item_id] == 0:
            del self.items[item_id]
        
        return True
    
    def use_item(self, item_id: str) -> Effect:
        """Use consumable item."""
        item = Item.load(item_id)
        
        if item.type != "consumable":
            raise InvalidItemUse()
        
        self.remove_item(item_id)
        return item.apply_effect(owner=self.owner)
```

### Item Types

| Type | Max Quantity | Use |
|------|--------------|-----|
| Consumable | 99 | Healing potions, buffs |
| Equipment | 1 | Weapons, armor, accessories |
| Quest Item | Unlimited | Key items, trade goods |
| Currency | Unlimited | Gold, gems |

---

## Skill Progression

### Ability Learning

Players learn abilities through:

1. **Level Up** - Automatic at specific levels
2. **Skill Books** - Find in world
3. **NPC Training** - Purchase from trainers
4. **Quest Rewards** - Complete objectives

### Ability Pool Per Class

#### Warrior Abilities
- Level 1: Attack, Power Slash
- Level 5: Defend, Counter Attack
- Level 10: Whirlwind, Battle Cry
- Level 20: Last Stand (ultimate)

#### Mage Abilities
- Level 1: Fireball, Mana Bolt
- Level 5: Ice Storm, Lightning Strike
- Level 10: Magic Shield, Spell Surge
- Level 20: Meteor Storm (ultimate)

#### Rogue Abilities
- Level 1: Backstab, Quick Strike
- Level 5: Shadow Clone, Evasion
- Level 10: Poison Dart, Assassination
- Level 20: Shadow Dance (ultimate)

#### Healer Abilities
- Level 1: Heal, Bless
- Level 5: Cure Poison, Holy Light
- Level 10: Full Heal, Group Blessing
- Level 20: Resurrection (ultimate)

### Learning Abilities

```python
def learn_ability(self, ability_id: str) -> bool:
    """Learn new ability."""
    ability = Ability.load(ability_id)
    
    if ability_id in self.abilities:
        raise AlreadyLearned()
    
    if not self.can_learn(ability):
        raise RequirementsNotMet()
    
    self.abilities.append(ability_id)
    return True

def can_learn(self, ability: Ability) -> bool:
    """Check if player can learn ability."""
    # Must be correct archetype
    if self.archetype != ability.archetype:
        return False
    
    # Must meet level requirement
    if self.level < ability.level_requirement:
        return False
    
    # Must not already know it
    if ability.id in self.abilities:
        return False
    
    return True
```

---

## Integration with Other Systems

See:
- [04-combat-engine.md](04-combat-engine.md) for combat mechanics
- [06-story-dialogue.md](06-story-dialogue.md) for stat checks in dialogues
- [09-game-loop.md](09-game-loop.md) for character menu in game loop
