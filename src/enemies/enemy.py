from src.characters.character import NPC


class GameEnemy(NPC):
    def __init__(self, data: dict, level: int = None):
        # map data fields to NPC constructor
        name = data.get('display')
        eid = data.get('id')
        stats = {'str': data.get('atk', 5), 'end': data.get('def', 1), 'int': 0}
        super().__init__(eid, name, archetype=data.get('id'), level=level or data.get('tier', 1), stats=stats)
        self.base_hp = data.get('hp', 10)
        self.hp = self.base_hp
        self.element = data.get('element', 'None')
        self.tags = data.get('tags', [])
        self.data = data
        self.abilities = data.get('abilities', [])
        self.regeneration = data.get('regeneration', 0)
        self.immunities = set(data.get('immunities', []))
        self.vulnerabilities = set(data.get('vulnerabilities', []))
        self.resistances = data.get('resistances', {})
        self.drops = data.get('drops', [])

    def describe(self):
        return f"{self.name} (HP {self.hp}/{self.base_hp})"

    def tick_regen(self):
        if self.regeneration and self.hp > 0:
            self.hp = min(self.base_hp, self.hp + self.regeneration)

    def roll_drops(self):
        """Roll drops and return dict with 'gold' and 'items' lists."""
        import random
        result = {'gold': 0, 'items': []}
        for d in self.drops:
            chance = d.get('chance', 1.0)
            if random.random() <= chance:
                if 'gold' in d:
                    g = d['gold']
                    mn = g.get('min', 0)
                    mx = g.get('max', 0)
                    result['gold'] += random.randint(mn, mx)
                if 'item' in d:
                    cnt = d.get('count', 1)
                    for _ in range(cnt):
                        result['items'].append(d['item'])
        return result
