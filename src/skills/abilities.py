"""Abilities and skills definitions + executors."""
from typing import Dict
from src.elements.elements import reaction_for


ABILITIES = {
    "fireball": {
        "name": "Fireball",
        "cost": {"mana": 8},
        "base": 12,
        "element": "Fire",
        "effects": [{"type": "status", "name": "Burn", "duration": 3}]
    },
    "stab": {
        "name": "Stab",
        "cost": {"stamina": 4},
        "base": 6,
        "element": "None",
        "effects": []
    }
}


CLASS_ABILITIES = {
    'warrior': ['stab'],
    'archer': ['stab'],
    'mage': ['fireball'],
    'druid': ['fireball'],
    'witch': ['fireball']
}


def tick_cooldowns(user):
    if not hasattr(user, 'ability_cooldowns'):
        return
    for k in list(user.ability_cooldowns.keys()):
        if user.ability_cooldowns[k] > 0:
            user.ability_cooldowns[k] = max(0, user.ability_cooldowns[k] - 1)


def use_ability(name: str, user, target) -> Dict:
    data = ABILITIES.get(name)
    if not data:
        return {"ok": False, "msg": "Unknown ability"}
    # check costs (simple)
    cost = data.get('cost', {})
    if cost.get('mana', 0) > getattr(user, 'mana', 0):
        return {"ok": False, "msg": "Not enough mana"}
    if cost.get('stamina', 0) > getattr(user, 'stamina', 0):
        return {"ok": False, "msg": "Not enough stamina"}
    # cooldown check
    if not hasattr(user, 'ability_cooldowns'):
        user.ability_cooldowns = {}
    cd = user.ability_cooldowns.get(name, 0)
    if cd > 0:
        return {"ok": False, "msg": "Ability on cooldown"}
    # pay costs
    user.mana = max(0, getattr(user, 'mana', 0) - cost.get('mana', 0))
    user.stamina = max(0, getattr(user, 'stamina', 0) - cost.get('stamina', 0))
    # damage
    base = data.get('base', 0)
    # simple stat scaling
    atk = base + user.stats.get('int', 0) if data.get('element') != 'None' else base + user.stats.get('str', 0)
    # apply element reactions
    reacted = False
    if data.get('element') and data.get('element') != 'None' and hasattr(target, 'resistances'):
        has_react, react = reaction_for(data.get('element'), target.resistances.get('vulnerable_to', ''))
        if has_react:
            atk = int(atk * react.get('modifier', 1.0))
            reacted = True

    # apply damage directly for now
    target.hp -= max(0, atk)
    result = {"ok": True, "damage": atk, "reacted": reacted}
    # set cooldown (simple fixed value)
    user.ability_cooldowns[name] = data.get('cooldown', 3)
    # decrement cooldowns stored on user (to be called each turn by engine)
    if hasattr(user, 'ability_cooldowns'):
        for k in list(user.ability_cooldowns.keys()):
            if user.ability_cooldowns[k] > 0 and k != name:
                user.ability_cooldowns[k] = max(0, user.ability_cooldowns[k])
    # apply any status
    for eff in data.get('effects', []):
        if eff.get('type') == 'status':
            if not hasattr(target, 'statuses'):
                target.statuses = []
            target.statuses.append({'name': eff.get('name'), 'duration': eff.get('duration', 1)})
    return result
