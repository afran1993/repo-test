import random


def breath_fire(user, target):
    base = user.data.get('atk', 10)
    dmg = base + random.randint(2, 8)
    # apply burn status
    try:
        target.apply_status('Burn', potency=2, duration=3)
    except Exception:
        pass
    target.hp -= max(0, dmg)
    return {'name': 'breath_fire', 'damage': dmg}


def poison_bite(user, target):
    base = user.data.get('atk', 8)
    dmg = base + random.randint(1, 6)
    try:
        target.apply_status('Poison', potency=1, duration=4)
    except Exception:
        pass
    target.hp -= max(0, dmg)
    return {'name': 'poison_bite', 'damage': dmg}


def multi_attack(user, target):
    hits = []
    for i in range(3):
        dmg = user.data.get('atk', 6) + random.randint(0, 6)
        target.hp -= max(0, dmg)
        hits.append(dmg)
    return {'name': 'multi_attack', 'hits': hits, 'damage': sum(hits)}


def raise_skeleton(user, engine=None, location=None):
    # signal to engine to spawn a skeleton near location
    return {'name': 'raise_skeleton', 'spawn': 'skeleton_warrior', 'count': 1}


ABILITY_MAP = {
    'breath_fire': breath_fire,
    'poison_bite': poison_bite,
    'multi_attack': multi_attack,
    'raise_skeleton': raise_skeleton
}


def use_enemy_ability(name, user, target, engine=None):
    fn = ABILITY_MAP.get(name)
    if not fn:
        return {'ok': False, 'msg': 'Unknown ability'}
    if name == 'raise_skeleton':
        return fn(user, engine=engine, location=getattr(user, 'location', None))
    return fn(user, target)
