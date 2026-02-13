# 04 - Combat Engine Deep Dive

In-depth technical guide to damage calculation, resistance system, abilities, and combat mechanics.

## Table of Contents
- [Damage Calculator](#damage-calculator)
- [Resistance System](#resistance-system)
- [Ability System](#ability-system)
- [Critical Hits](#critical-hits)
- [Status Effects](#status-effects)
- [Combat Optimization](#combat-optimization)

---

## Damage Calculator

### Core Formula

The damage calculation in `src/combat/damage_engine.py` follows this formula:

```
Final Damage = ((Base Damage + Modifiers) × Resistance Multiplier) × RNG Variance
```

### Calculation Breakdown

#### Step 1: Base Damage

```python
base_damage = (
    attacker.atk +
    ability.power +
    weapon_bonus +
    stat_bonuses
)
```

- `attacker.atk`: Unit's Attack stat (1-100)
- `ability.power`: Ability's power multiplier (0-100)
- `weapon_bonus`: If using equipped weapon
- `stat_bonuses`: From temporary buffs or effects

**Example**:
- Warrior ATK = 45
- Iron Sword bonus = +5
- Fireball ability power = 30
- Base Damage = 45 + 5 + 30 = **80**

#### Step 2: Resistance Multiplier

```python
resistance_multiplier = defender.get_resistance(element)
```

The `get_resistance()` method returns:

```python
def get_resistance(self, element: str) -> float:
    # Check immunity first (highest priority)
    if element in self.immunities:
        return 0.0  # No damage taken
    
    # Check vulnerability (lowest priority)
    if element in self.vulnerabilities:
        return 1.5  # 150% damage (takes extra damage)
    
    # Check resistances dict
    if element in self.resistances:
        return self.resistances[element]  # e.g., 0.5 = 50% reduction
    
    # Default: normal damage
    return 1.0
```

**Examples**:
- Element: Fire, Defender has `{"Fire": 0.5}` → Multiplier = **0.5**
- Element: Poison, Defender has `["Poison"]` in immunities → Multiplier = **0.0**
- Element: Holy, Defender has `["Holy"]` in vulnerabilities → Multiplier = **1.5**
- Element: Physical, no resistance → Multiplier = **1.0**

#### Step 3: Apply Resistance Multiplier

```python
post_resistance_damage = base_damage × resistance_multiplier
```

**Examples**:
- 80 damage × 0.5 resistance = **40 damage**
- 80 damage × 0.0 immunity = **0 damage**
- 80 damage × 1.5 vulnerability = **120 damage**

#### Step 4: Critical Hit Check

```python
if roll_d100() < attacker.critical_chance:
    post_resistance_damage *= CRITICAL_MULTIPLIER  # 1.5x or 2.0x
```

#### Step 5: RNG Variance

```python
variance = random.uniform(0.85, 1.15)  # ±15% variance
final_damage = post_resistance_damage × variance
```

This adds unpredictability to combat. Same attack won't always deal same damage.

#### Step 6: Apply Damage

```python
defender.hp -= final_damage
if defender.hp < 0:
    defender.hp = 0
    trigger_defeat()
```

### Complete Example

**Setup**:
- Attacker: Warrior (ATK 50)
- Ability: Fireball (Power 25, Element: Fire)
- Weapon: Magic Staff (ATK bonus +5)
- Defender: Fire Elemental
  - DEF 20
  - Fire resistance: 60% (multiplier 0.4)
  - HP: 150

**Calculation**:
```
1. Base Damage = 50 (ATK) + 5 (weapon) + 25 (ability) = 80
2. Resistance check = 0.4x (60% reduction)
3. After resistance = 80 × 0.4 = 32
4. Critical? = 15% chance (failed this turn)
5. Variance = 0.95 (95% of normal)
6. Final Damage = 32 × 0.95 = 30.4 → 30
7. Defender HP: 150 - 30 = 120 HP remaining
```

---

## Resistance System

### Enemy Resistances Data

In `data/enemies.json`, resistances are defined:

```json
{
  "id": "fire_dragon",
  "name": "Dragon of Flame",
  "resistances": {
    "Fire": 0.2,
    "Ice": 2.0,
    "Physical": 0.7
  },
  "immunities": ["Poison"],
  "vulnerabilities": ["Holy", "Water"]
}
```

### Resistance Types

| Multiplier | Effect | Use Case |
|-----------|--------|----------|
| `0.0` | Immunity (must use immunities list) | Poison-immune undead |
| `0.1 - 0.4` | High resistance | Fire dragon vs fire |
| `0.5 - 0.9` | Moderate resistance | Armored enemy vs physical |
| `1.0` | No resistance (default) | Normal damage type |
| `1.1 - 1.5` | Vulnerability | Undead vs holy |
| `2.0+` | Extreme vulnerability | Water dragon vs water |

### Implementation in Enemy Class

```python
class Enemy:
    def __init__(self, enemy_data: dict):
        # Resistances as multiplier dict
        self.resistances: Dict[str, float] = enemy_data.get("resistances", {})
        
        # Immunities (no damage taken)
        self.immunities: List[str] = enemy_data.get("immunities", [])
        
        # Vulnerabilities (extra damage)
        self.vulnerabilities: List[str] = enemy_data.get("vulnerabilities", [])
    
    def get_resistance(self, element: str) -> float:
        """Returns damage multiplier for given element."""
        if element in self.immunities:
            return 0.0
        if element in self.vulnerabilities:
            return 1.5  # 150% damage
        return self.resistances.get(element, 1.0)
```

### Strategic Depth

Players must:
1. **Scout enemy** → See resistances
2. **Choose ability** → Match weak point
3. **Allocate resources** → Use buffed/critical abilities on resistant enemies

**Example Strategy**:
```
Enemy: Fire Drake (Fire resistance 0.2, Ice vulnerability 1.5)
- Avoid: Fire spells (80% reduction)
- Use: Ice spells (150% weakness)
- Result: Deal ~7.5x more damage with correct element!
```

---

## Ability System

### Ability Definition

Abilities define what actions are available in combat:

```python
class Ability:
    def __init__(self, ability_data: dict):
        self.id = ability_data["id"]
        self.name = ability_data["name"]
        self.element = ability_data["element"]  # Fire, Ice, Lightning, Poison, Physical, Holy
        self.power = ability_data["power"]       # 0-100
        self.cost = ability_data["cost"]         # MP/Stamina
        self.accuracy = ability_data.get("accuracy", 100)  # Hit chance %
        self.description = ability_data["description"]
```

### Ability Elements

| Element | Counter | Example |
|---------|---------|---------|
| Physical | Armor/DEF | Slash, Punch, Kick |
| Fire | Ice resistance | Fireball, Flame burst |
| Ice | Fire resistance | Blizzard, Freeze |
| Lightning | Grounding | Thunder, Chain lightning |
| Poison | Anti-poison | Toxic cloud, Envenom |
| Holy | Demonic | Smite, Divine protection |
| Dark | Holy | Shadow bolt, Dark ritual |

### Ability Data Structure

From `data/abilities.json`:

```json
{
  "id": "fireball",
  "name": "Fireball",
  "element": "Fire",
  "power": 30,
  "cost": {
    "type": "mp",
    "amount": 15
  },
  "accuracy": 100,
  "description": "Engulf target in flames",
  "effects": {
    "single_target": true,
    "status_effect": null
  }
}
```

#### Advanced Abilities

```json
{
  "id": "poison_cloud",
  "name": "Poison Cloud",
  "element": "Poison",
  "power": 15,
  "cost": {"type": "mp", "amount": 20},
  "accuracy": 85,
  "effects": {
    "area_of_effect": true,
    "radius": 2,
    "status_effect": {
      "type": "poison",
      "duration": 3,
      "damage_per_turn": 5
    }
  }
}
```

### Ability Usage in Combat

```python
# Player selects ability
ability = Ability.load(ability_id="fireball")

# Check resource availability
if player.mp < ability.cost["amount"]:
    raise InsufficientResourceError("Not enough MP")

# Check accuracy
if random.random() > ability.accuracy / 100:
    return "Miss!"  # Failed to hit

# Calculate damage with ability
damage = calculate_damage(
    attacker=player,
    defender=enemy,
    ability=ability
)

# Apply damage and check resistance
actual_damage = damage * enemy.get_resistance(ability.element)
```

---

## Critical Hits

### Critical Hit Calculation

```python
def roll_critical_hit(attacker: Character) -> bool:
    """
    Returns True if attack is critical based on attacker's critical chance.
    """
    critical_chance = attacker.get_critical_chance()  # %
    return random.random() < (critical_chance / 100)
```

### Critical Chance Calculation

```python
def get_critical_chance(self) -> float:
    """
    Base 5% + 1% per 10 DEX (evasion stat)
    """
    base_critical = 5.0
    dex_bonus = self.dex / 10  # Up to 10% for 100 DEX
    return base_critical + dex_bonus  # 5-15% normally
```

### Critical Multiplier

```
Critical Damage = Normal Damage × 1.5 (or 2.0 for rare crits)
```

**Example**:
- Normal damage: 50
- Critical: 50 × 1.5 = **75 damage** (+50% boost)

### Display

In event output:
```
► Warrior attacks Fire Drake
  ⚡ CRITICAL HIT! ⚡
  Fireball deals 120 damage! (resisted to 36 × 1.5 crit = 54)
```

---

## Status Effects

### Effect System

Status effects are applied for skill duration:

```python
class StatusEffect:
    def __init__(self, effect_data: dict):
        self.type = effect_data["type"]  # poison, burn, freeze, etc.
        self.duration = effect_data["duration"]  # turns
        self.damage_per_turn = effect_data.get("damage_per_turn", 0)
        self.stat_modifier = effect_data.get("stat_modifier", {})
```

### Effect Types

| Effect | Source | Impact |
|--------|--------|--------|
| Poison | Poison abilities/items | 5-10 HP/turn damage |
| Burn | Fire ability | 8-12 HP/turn damage |
| Freeze | Ice ability | Reduce SPD by 50% |
| Stun | Lightning ability | Skip next turn (50% chance) |
| Weakness | Magic | Reduce ATK by 30% |
| Cursed | Dark ability | Reduce DEF by 40% |
| Blessed | Holy ability | Increase ATK by 20% |
| Regenerating | Holy item/ability | Restore 10 HP/turn |

### Effect Processing

```python
def process_status_effects(character: Character):
    """Process all active status effects."""
    for effect in character.active_effects:
        # Apply damage/modification
        if effect.damage_per_turn > 0:
            character.hp -= effect.damage_per_turn
        
        # Apply stat modifiers
        for stat, modifier in effect.stat_modifier.items():
            apply_modifier(character, stat, modifier)
        
        # Reduce duration
        effect.duration -= 1
        if effect.duration <= 0:
            character.remove_effect(effect.type)
            # Notify: "Poison wore off"
```

---

## Combat Optimization

### Performance Considerations

1. **Damage Calculation**:
   - Pre-calculate base stats on load
   - Cache ability data
   - Use fast random number generation

2. **Event Emission**:
   - Batch event creation
   - Defer rendering until turn complete
   - Use event buffering for multiple hits

3. **Memory**:
   - Reuse Combat instance for multiple turns
   - Don't clone enemy data (use references)
   - Clear completed effects immediately

### Balancing Guide

**Enemy Difficulty Scaling**:
```python
enemy_level = base_level + difficulty_modifier

# Scale stats
enemy.hp = base_hp * (1 + 0.1 * enemy_level)
enemy.atk = base_atk * (1 + 0.05 * enemy_level)
enemy.def = base_def * (1 + 0.05 * enemy_level)
```

**Ability Power Balance**:
- Physical abilities: Power 20-40
- Elemental abilities: Power 25-35
- Ultimate abilities: Power 50-80
- Support abilities: Power 0-20

**Resistance Balance**:
- Common resistances: 0.5-0.8x
- Rare resistances: 0.2-0.4x
- Immunities: Only for special enemies
- Vulnerabilities: Max 1.5x for balance

---

## Integration with Other Systems

See:
- [02-game-systems.md](02-game-systems.md) for combat system overview
- [05-player-system.md](05-player-system.md) for player stat scaling
- [09-game-loop.md](09-game-loop.md) for turn order and timing
