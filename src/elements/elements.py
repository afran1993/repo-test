"""Elemental system: elements, resistances, and reactions."""
from typing import Dict, Tuple

# Basic set of elements
ELEMENTS = ["None", "Fire", "Water", "Earth", "Air", "Ice", "Lightning", "Arcane"]

# Pairwise reactions (ordered tuple of source,target) -> reaction
REACTIONS = {
    ("Fire", "Water"): {"name": "Steam", "desc": "Creates steam, reduces visibility.", "modifier": 0.9},
    ("Water", "Fire"): {"name": "Steam", "desc": "Creates steam, reduces visibility.", "modifier": 0.9},
    ("Fire", "Ice"): {"name": "Melt", "desc": "Melts ice, increases damage.", "modifier": 1.2},
    ("Lightning", "Water"): {"name": "Conduct", "desc": "Electricity spreads through water.", "modifier": 1.3},
}


def element_index(name: str) -> int:
    try:
        return ELEMENTS.index(name)
    except ValueError:
        return 0


def element_modifier(attack_element: str, defender_resistances: Dict[str, float]) -> float:
    """
    Compute an elemental damage modifier based on attack element and defender resistances.
    defender_resistances: mapping element->resist_value (0.0 .. 1.0) where 0.2 means 20% reduction.
    Returns multiplier (e.g., 0.8 reduces, 1.2 increases).
    """
    if not attack_element or attack_element == "None":
        return 1.0
    resist = defender_resistances.get(attack_element, 0.0)
    # Positive resist reduces damage; negative (vulnerability) increases
    base = max(0.0, 1.0 - resist)
    return base


def reaction_for(a: str, b: str) -> Tuple[bool, dict]:
    key = (a, b)
    if key in REACTIONS:
        return True, REACTIONS[key]
    return False, {}
