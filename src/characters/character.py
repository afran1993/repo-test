import random


class Character:
    def __init__(self, id_, name, archetype=None, level=1, stats=None, inventory=None):
        self.id = id_
        self.name = name
        self.archetype = archetype
        self.level = level
        self.xp = 0
        self.stats = stats or {"str": 5, "dex": 5, "int": 5, "cha": 5, "end": 5}
        self.max_hp = 20 + self.stats['end'] * 2
        self.hp = self.max_hp
        self.max_mana = 10 + self.stats['int'] * 2
        self.mana = self.max_mana
        self.stamina = 10 + self.stats['str']
        self.inventory = inventory or []
        self.equipment = {}

    def is_alive(self):
        return self.hp > 0

    def gain_xp(self, amount):
        self.xp += amount
        # simple level up
        leveled = False
        while self.xp >= self.level * 20:
            self.xp -= self.level * 20
            self.level += 1
            self.max_hp += 5
            self.hp = self.max_hp
            leveled = True
        return leveled

    def equip(self, item):
        # item is a dict-like with 'slot'
        slot = item.get('slot', 'main')
        self.equipment[slot] = item

    def unequip(self, slot):
        return self.equipment.pop(slot, None)

    def describe(self):
        return f"{self.name} (Lv {self.level}) HP {self.hp}/{self.max_hp}"


class PlayerCharacter(Character):
    def __init__(self, id_, name, archetype=None, level=1, stats=None):
        super().__init__(id_, name, archetype, level, stats)
        self.gold = 50
        self.reputation = {}
        self.quests = []


class NPC(Character):
    def __init__(self, id_, name, archetype=None, level=1, stats=None, dialog=None):
        super().__init__(id_, name, archetype, level, stats)
        self.dialog = dialog or []
        self.behavior = 'neutral'
