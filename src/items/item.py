class Item:
    def __init__(self, data):
        self.id = data.get('id')
        self.name_key = data.get('name_key')
        self.display = data.get('display')
        self.type = data.get('type', 'weapon')
        self.weapon_type = data.get('weapon_type')
        self.allowed_classes = data.get('allowed_classes', [])
        self.stats = data.get('stats', {})
        self.element = data.get('element', 'None')
        self.slot = data.get('slot', 'main')

    def short(self):
        from src.i18n import t
        name = t(self.name_key) if self.name_key else self.display
        return f"{name} ({self.weapon_type})"
