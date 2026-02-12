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
        self.resistances = {}  # element -> resist value (0.0..1.0)
        self.wounds = []  # persistent wounds that may need treatment

    def is_alive(self):
        return self.hp > 0

    def apply_status(self, status_name, potency=1, duration=3):
        if not hasattr(self, 'statuses'):
            self.statuses = []
        self.statuses.append({'name': status_name, 'potency': potency, 'duration': duration})

    def tick_statuses(self):
        """Apply status effects each turn; reduces duration and removes expired."""
        if not hasattr(self, 'statuses'):
            return []
        applied = []
        remaining = []
        for s in self.statuses:
            name = s['name']
            pot = s.get('potency',1)
            # basic effects
            if name == 'Burn':
                dmg = max(1, pot)
                self.hp -= dmg
                applied.append((name, dmg))
            elif name == 'Poison':
                dmg = max(1, pot)
                self.hp -= dmg
                applied.append((name, dmg))
            elif name == 'Bleed':
                dmg = max(1, pot)
                self.hp -= dmg
                applied.append((name, dmg))
            # decrement
            s['duration'] -= 1
            if s['duration'] > 0:
                remaining.append(s)
        self.statuses = remaining
        return applied

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
        self.schedule = []  # list of (time, region, area) tuples or simple waypoints

    def tick_routine(self, time_of_day):
        """Advance routine based on time_of_day (e.g., morning, day, night)."""
        # simple example: cycle through schedule entries
        if not self.schedule:
            return None
        idx = time_of_day % len(self.schedule)
        entry = self.schedule[idx]
        # entry expected as dict {'region':..,'area':..}
        return entry
