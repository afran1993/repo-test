# 06 - Story and Dialogue

Narrative design, branching dialogue trees, skill checks, and NPC interactions.

## Table of Contents
- [Story Architecture](#story-architecture)
- [Dialogue System](#dialogue-system)
- [Skill Checks](#skill-checks)
- [NPC Relationships](#npc-relationships)
- [Narrative Branching](#narrative-branching)
- [Story Data Format](#story-data-format)

---

## Story Architecture

### Story Layers

The game's story is structured in layers:

```
┌──────────────────────────────┐
│      Global Story Arc        │ (Main plot: Save the kingdom)
│                              │
│  ┌────────────────────────┐  │
│  │   Regional Chapters    │  │ (Each region has its own story)
│  │                        │  │
│  │  ┌──────────────────┐  │  │
│  │  │ NPC Quest Chains│  │  │ (Individual side quests)
│  │  │                │  │  │
│  │  │ • Quest A      │  │  │
│  │  │ • Quest B      │  │  │
│  │  │ (connected)    │  │  │
│  │  └──────────────────┘  │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```

### Story Progression

Story progresses through:

1. **Main Quests** - Story-critical, cannot be skipped
2. **Regional Gates** - Complete all main quests to progress
3. **NPC Events** - Dynamic story beats based on interactions

### Example Story Structure

**Act 1: The Beginning**
- Location: Starting Village
- Quests: Introduction, Meet Elder, First Combat
- Goals: Gather information, gather starter items
- Exit: Talk to Elder about the Prophecy

**Act 2: The Journey**
- Location: Multiple regions (Forest, Desert, Mountains)
- Quests: Region-specific challenges (Rescue NPCs, Defeat Bosses)
- Goals: Collect elemental artifacts
- Gating: Must complete all regional quests

**Act 3: The Reckoning**
- Location: Final Fortress
- Quests: Ultimate challenges
- Goals: Face the dark lord
- End: Victory or defeat

---

## Dialogue System

### Dialogue Architecture

Located in `src/dialogue/dialogue.py`, the dialogue system manages branching conversations:

```python
class Dialogue:
    def __init__(self, dialogue_tree: dict, npc: NPC):
        self.npc = npc
        self.tree = dialogue_tree
        self.current_node_id = "start"
        self.choices_made = []  # Track player decisions
        self.state_flags = {}   # Dialogue-specific flags
        self.is_active = True
    
    def get_current_node(self) -> dict:
        """Get dialogue node by ID."""
        return self.tree["nodes"][self.current_node_id]
    
    def get_choices(self) -> List[dict]:
        """Get available response options."""
        node = self.get_current_node()
        return node.get("choices", [])
    
    def select_choice(self, choice_id: int) -> "DialogueResult":
        """Player selects a response."""
        node = self.get_current_node()
        choice = node["choices"][choice_id]
        
        # Track choice
        self.choices_made.append({
            "node": self.current_node_id,
            "choice": choice_id,
            "text": choice["text"]
        })
        
        # Check skill requirements
        if "skill_check" in choice:
            success = self._resolve_skill_check(choice["skill_check"])
            if success:
                next_node = choice.get("success_next", choice.get("next"))
            else:
                next_node = choice.get("failure_next", choice.get("next"))
        else:
            next_node = choice.get("next")
        
        # Transition to next node
        if next_node:
            self.current_node_id = next_node
        else:
            self.is_active = False
        
        # Handle side effects (quest triggers, etc.)
        if "triggers" in choice:
            self._execute_triggers(choice["triggers"])
        
        return DialogueResult(
            next_text=self.get_current_node()["text"] if self.is_active else None,
            effects=choice.get("effects", [])
        )
    
    def _resolve_skill_check(self, check: dict) -> bool:
        """Resolve a skill check."""
        skill = check["skill"]  # STR, INT, CHA, DEX
        dc = check["dc"]  # Difficulty Class
        
        roll = roll_d20()  # 1-20
        player_bonus = getattr(self.player, skill.lower()) // 2
        
        total = roll + player_bonus
        return total >= dc
```

### Dialogue Node Structure

```json
{
  "nodes": {
    "start": {
      "text": "Greetings, traveler. What brings you to my humble village?",
      "speaker": "Village Elder",
      "choices": [
        {
          "id": 0,
          "text": "I seek the artifact of power.",
          "next": "artifact_mention",
          "effects": []
        },
        {
          "id": 1,
          "text": "Just passing through.",
          "next": "passing_through"
        },
        {
          "id": 2,
          "text": "[STR 12] Demand respect!",
          "next": "combat_start",
          "skill_check": {
            "skill": "STR",
            "dc": 15,
            "success_next": "combat_won",
            "failure_next": "combat_lost"
          }
        }
      ]
    },
    "artifact_mention": {
      "text": "Ah, I see. The artifact lies in the temple to the north. Beware the guardians.",
      "speaker": "Village Elder",
      "choices": [
        {
          "text": "Thank you for the information.",
          "next": "end",
          "triggers": [
            {
              "type": "quest",
              "action": "accept",
              "quest_id": "find_artifact"
            },
            {
              "type": "location_unlock",
              "location": "temple"
            }
          ]
        }
      ]
    }
  }
}
```

### Dialogue Features

#### Conditional Display

Show different choices based on game state:

```json
{
  "text": "What are your opinions?",
  "choices": [
    {
      "text": "I have great news!",
      "condition": "quest_complete('major_victory')",
      "next": "celebrate"
    },
    {
      "text": "Times are dark.",
      "condition": "inventory_has('dark_artifact')",
      "next": "corruption_path"
    }
  ]
}
```

#### Dynamic Text

Use variables in dialogue:

```json
{
  "text": "Greetings, {player_name}! You look like level {player_level}."
}
```

Rendered as: `"Greetings, Aina! You look like level 15."`

---

## Skill Checks

### Skill Check System

Skill checks are integrated into dialogue and quests:

```python
def resolve_skill_check(
    player: Character,
    skill: str,  # STR, DEX, INT, CHA, VIT
    dc: int,     # Difficulty Class (10-20)
) -> bool:
    """
    Resolve a skill check.
    Roll d20 + (Skill/2) + modifiers >= DC
    """
    roll = roll_d20()  # 1-20
    skill_bonus = player.stats.get(skill) // 2  # Convert stat to bonus
    
    # Add temporary modifiers (buffs/debuffs)
    modifier = 0
    for effect in player.active_effects:
        if effect.type == f"skill_{skill.lower()}":
            modifier += effect.modifier
    
    total = roll + skill_bonus + modifier
    
    return total >= dc
```

### Skill Check Display

```
═══════════ SKILL CHECK ═══════════
You attempt to bargain with the merchant...
[CHA check, DC 15]

Rolling d20...
  d20 roll: 14
  CHA bonus: +3 (12 CHA → 6 bonus)
  Total: 17 ✓

Success! You got a 10% discount!
```

### Skill Check Difficulty Scale

| DC | Difficulty | Example |
|----|-----------|---------|
| 8 | Very Easy | Notice obvious clues |
| 10 | Easy | Convince friendly NPC |
| 12 | Moderate | Pick a simple lock |
| 15 | Hard | Intimidate a trained guard |
| 18 | Very Hard | Deceive the king |
| 20+ | Nearly Impossible | Impossible odds |

### Consequence Types

#### Success Only
```json
{
  "text": "Can you sneak past these guards?",
  "skill_check": {
    "skill": "DEX",
    "dc": 14,
    "success_next": "sneak_past"
  }
}
```

Fails → Dialogue ends, combat starts

#### Success/Failure Path
```json
{
  "text": "Attempt to bluff the merchant?",
  "skill_check": {
    "skill": "CHA",
    "dc": 12,
    "success_next": "merchant_fooled",
    "failure_next": "merchant_angry"
  }
}
```

Fails → Different dialogue path

#### Narrative Impact
```json
{
  "text": "Make a deal with the devil?",
  "skill_check": {
    "skill": "INT",
    "dc": 16,
    "success_next": "learned_truth",
    "failure_next": "cursed_path"
  },
  "triggers": [
    {"type": "flag", "flag": "made_devil_deal", "value": true}
  ]
}
```

Affects future story options

---

## NPC Relationships

### Relationship Tracking

Each NPC maintains a relationship value with player:

```python
class NPC:
    def __init__(self, npc_data: dict):
        self.id = npc_data["id"]
        self.name = npc_data["name"]
        self.relationship = 0  # -100 to +100
        self.is_recruitable = npc_data.get("recruitable", False)
        self.recruited = False
```

### Relationship Changes

Relationships change through:

```python
def modify_relationship(self, amount: int, reason: str):
    """
    Change NPC relationship.
    Typical amounts: ±5 for dialogue, ±10 for quest
    """
    self.relationship = max(-100, min(100, self.relationship + amount))
    
    # Trigger dialogue if thresholds crossed
    if self.relationship == 0:   # Neutral
        trigger_dialogue("neutral_reached")
    elif self.relationship == 50: # Liked
        trigger_dialogue("liked_reached")
        if self.is_recruitable:
            notify("NPC can now be recruited!")
    elif self.relationship == 100: # Loved
        trigger_dialogue("loved_reached", final=True)
```

### Relationship Tiers

| Range | Status | Benefits |
|-------|--------|----------|
| -100 to -50 | Hostile | NPC attacks on sight |
| -50 to 0 | Disliked | Poor dialogue options |
| 0 to 50 | Neutral | Standard interactions |
| 50 to 100 | Liked | Better prices, more quests |
| 100+ | Loved | Can recruit as party member |

### Recruitment

High-relationship NPCs can join the party:

```python
def recruit_npc(self, npc_id: str) -> bool:
    """Recruit NPC to party."""
    npc = self.world.get_npc(npc_id)
    
    if not npc.is_recruitable:
        raise NotRecruitable()
    
    if npc.relationship < 100:
        raise RelationshipTooLow()
    
    # Create party member from NPC
    party_member = Character.from_npc(npc)
    self.party.add_member(party_member)
    npc.recruited = True
    
    return True
```

---

## Narrative Branching

### Branch Types

#### Simple Branch (One Node)
```
Player chooses A or B → Same destination but different text shown
```

#### Exclusive Branches (Two Paths)
```
Choose A → Path A (cannot see Path B)
Choose B → Path B (cannot see Path A)
```

#### Convergent Branches (Many → One)
```
Path A ──┐
Path B ──┼─→ Convergence Point
Path C ──┘
```

#### Divergent Branches (One → Many)
```
Starting Point ──┬─→ Path A
                 ├─→ Path B
                 └─→ Path C
```

### State Tracking

Dialogue choices leave permanent marks:

```python
# Save choices for later reference
dialogue_state = {
    "saved_child_in_forest": bool,      # Quest A choice
    "sided_with_king": bool,            # Regional choice
    "learned_dark_secret": bool,        # Major story revelation
}

# Later dialogue responds to these choices
if player.dialogue_state["saved_child_in_forest"]:
    npc_text = "I've heard of your kindness..."
else:
    npc_text = "I wonder about your morals..."
```

### Major Story Branches

#### Good / Neutral / Evil Paths

```
Act 1 ──┬─→ Save Innocent (Good)
        ├─→ Do Nothing (Neutral)
        └─→ Harm Innocent (Evil)
         
Each path has different:
- NPC relationships
- Quest availability
- Ending cinematics
- Achievements
```

---

## Story Data Format

### Story Root File

`data/quests.json` contains all story data:

```json
{
  "story_arcs": {
    "main": {
      "title": "The Dark Rising",
      "chapters": [
        {
          "id": "chapter_1",
          "title": "A New Beginning",
          "required_quests": [],
          "unlocked_quests": ["meet_elder", "explore_village"],
          "description": "Begin your journey in the humble village"
        }
      ]
    }
  },
  "dialogue": {
    "elder_first_meet": {
      "text": "Welcome, traveler...",
      "nodes": {}
    }
  },
  "quests": {
    "rescue_princess": {
      "title": "Rescue the Princess",
      "giver": "knight_commander",
      "chapter": "chapter_2"
    }
  }
}
```

### Linking Story Components

```python
# Load complete story context
story = Story.load_from_data()

# Get quest for chapter
chapter_quests = story.get_quests_for_chapter("chapter_1")

# Get dialogue for NPC interaction
npc_dialogue = story.get_dialogue("elder_first_meet")

# Check story state
if story.is_chapter_complete("chapter_1"):
    unlock_chapter("chapter_2")
```

---

## Story Writing Guidelines

### Character Voice

Each NPC should have distinct dialogue style:

**Elder** (Wise, formal):
```
"The path ahead is perilous, young one. Steel yourself."
```

**Merchant** (Greedy, persuasive):
```
"Best prices in the kingdom, friend. What'll it be?"
```

**Rogue** (Cynical, casual):
```
"Life's too short for pleasantries. What do ya want?"
```

### Pacing

- **Act 1**: 3-5 main quests (30 mins gameplay)
- **Act 2**: 10-15 quests across regions (2 hours gameplay)
- **Act 3**: 5-8 finale quests (1.5 hours gameplay)

### Emotional Beats

Every act should have:
- **Hope**: Optimistic moment
- **Doubt**: Challenge emerges
- **Climax**: Major revelation/battle
- **Resolution**: Outcome shown

---

## Integration with Other Systems

See:
- [02-game-systems.md](02-game-systems.md) for quest system integration
- [05-player-system.md](05-player-system.md) for stat checks
- [09-game-loop.md](09-game-loop.md) for dialogue menu display
