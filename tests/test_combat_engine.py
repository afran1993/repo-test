from src.combat.combat import calculate_damage


class Dummy:
    def __init__(self, atk=6, defense=3):
        self.atk = atk
        self.defense = defense
        self.stats = {'str': atk, 'end': defense}


def test_calculate_damage_basic():
    attacker = Dummy(atk=8, defense=2)
    defender = Dummy(atk=4, defense=3)
    dmg = calculate_damage(attacker, defender)
    assert isinstance(dmg, int)
    assert dmg >= 1
