"""
Game utility functions.

Contains helper functions for combat, enemies, elements, etc.
"""

from typing import Any, Dict

# Type matchup system (similar to Pokemon)
ELEMENT_MATCHUPS = {
    "Fire": {"strong_against": ["Earth", "Air"], "weak_against": ["Water"]},
    "Water": {"strong_against": ["Fire"], "weak_against": ["Earth", "Lightning"]},
    "Earth": {"strong_against": ["Water", "Lightning"], "weak_against": ["Fire", "Air"]},
    "Air": {"strong_against": ["Earth"], "weak_against": ["Lightning"]},
    "Lightning": {"strong_against": ["Water", "Air"], "weak_against": ["Earth"]},
    "Arcane": {"strong_against": ["Arcane"], "weak_against": ["None"]},
    "None": {"strong_against": [], "weak_against": []}
}

# Enemy emoji mappings
ENEMY_EMOJIS = {
    "slime": "🟢", "goblin": "👹", "wolf": "🐺", "dragon": "🐉", "skeleton": "💀",
    "ghost": "👻", "orc": "👿", "squid": "🐙", "bat": "🦇", "spider": "🕷️",
    "harpy": "🦅", "wraith": "👻", "knight": "🤺", "crab": "🦀", "bird": "🐦",
    "elemental": "⚡", "fire": "🔥", "water": "💧", "wind": "🌪️", "earth": "🪨",
    "construct": "🤖", "beast": "🐻", "undead": "💀", "spirit": "👻", "troll": "👹",
    "golem": "🪨", "serpent": "🐍", "chimera": "🦁", "lich": "💀", "bandit": "🗡️",
    "sprite": "✨", "wisp": "💫", "beetle": "🐞", "seagull": "🐦", "scorpion": "🦂", "boar": "🐗"
}


def get_element_modifier(attacker_element: str, defender_element: str) -> float:
    """
    Calculate damage modifier based on element matchup.
    
    - If attacker's element is strong against defender's: +25% damage
    - If attacker's element is weak against defender's: -25% damage
    - Otherwise: 1.0x damage
    
    Args:
        attacker_element: The attacking unit's element
        defender_element: The defending unit's element
    
    Returns:
        Damage modifier multiplier
    """
    modifier = 1.0
    
    matchup = ELEMENT_MATCHUPS.get(attacker_element, {})
    if defender_element in matchup.get("strong_against", []):
        modifier *= 1.25  # +25% advantage
    elif defender_element in matchup.get("weak_against", []):
        modifier *= 0.75  # -25% disadvantage
    
    return modifier


def get_enemy_emoji(enemy: Any) -> str:
    """
    Get appropriate emoji for an enemy based on tags or ID.
    
    Args:
        enemy: Enemy object with id, name, and optional tags
    
    Returns:
        Emoji string or default fallback
    """
    enemy_id = enemy.id.lower() if hasattr(enemy, 'id') else ""
    enemy_name = enemy.name.lower() if hasattr(enemy, 'name') else ""
    
    # Check tags if available
    if hasattr(enemy, 'tags'):
        for tag in enemy.tags:
            if tag in ENEMY_EMOJIS:
                return ENEMY_EMOJIS[tag]
    
    # Check by ID or name
    for key, emoji in ENEMY_EMOJIS.items():
        if key in enemy_id or key in enemy_name:
            return emoji
    
    return "👹"  # Default fallback emoji


def validate_element(element: str) -> bool:
    """
    Check if an element is valid.
    
    Args:
        element: Element name to validate
    
    Returns:
        True if element is valid, False otherwise
    """
    return element in ELEMENT_MATCHUPS
