"""Core Player class with essential attributes and stat calculations."""

import random


class Player:
    """Rappresenta il giocatore con stats e abilità."""
    
    def __init__(self, name="Eroe"):
        # Stats base
        self.name = name
        self.level = 1
        self.xp = 0
        self.max_hp = 30
        self.hp = self.max_hp
        self.atk = 6
        self.dex = 5  # Agilità / Destrezza - influenza evasione
        self.gold = 0
        self.mana = 20
        self.max_mana = 20
        
        # Equipaggiamento
        self.equipped_weapon = None
        self.inventory = []
        self.accessories = {
            "ring": None,
            "necklace": None,
            "amulet": None,
            "bracelet": None,
        }
        
        # Armi disponibili
        self.weapons = [
            {"id": "sword_rusty", "name": "Spada Arrugginita", "atk": 3, "dex": 1, "evasion_bonus": 0.10},
        ]
        
        # Accessori disponibili
        self.available_accessories = [
            {"id": "ring_strength", "name": "Anello della Forza", "slot": "ring", "stats": {"atk": 3}},
            {"id": "ring_dexterity", "name": "Anello della Destrezza", "slot": "ring", "stats": {"dex": 3}, "evasion_bonus": 0.10},
            {"id": "necklace_power", "name": "Collana del Potere", "slot": "necklace", "stats": {"atk": 2, "dex": 1}},
            {"id": "amulet_wisdom", "name": "Amuleto della Saggezza", "slot": "amulet", "stats": {"atk": 1, "dex": 2}},
        ]
        
        # Pozioni
        self.potions = {
            "potion_small": 0,
            "potion_medium": 0,
            "potion_strong": 0,
            "mana_potion": 0,
            "mana_potion_strong": 0,
        }
        
        # Posizione sulla mappa
        self.current_location = "beach"
        
        # Lingua selezionata
        self.language = "it"
        
        # Sistema di storia principale
        self.story_progress = "act_1_awakening"
        self.story_stage = 0
        self.completed_acts = []
        self.postgame = False
        
        # Sistema di abilità progressive
        self.skills = {
            "swimming": False,
            "diving": False,
            "climbing": False,
            "pickpocketing": False,
            "stealth": False,
            "healing": False,
            "magic": False,
            "crafting": False,
        }
        
        # Dialoghi completati e scelte effettuate
        self.dialogues_completed = []
        self.dialogue_choices = {}

    def is_alive(self):
        """Controlla se il giocatore è ancora vivo."""
        return self.hp > 0

    def attack(self, target):
        """Attacca un nemico."""
        total_atk = self.get_total_atk()
        dmg = random.randint(max(1, total_atk - 2), total_atk + 2)
        target.hp -= dmg
        return dmg

    def use_potion(self, potion_type="potion_small"):
        """Usa una pozione."""
        if potion_type not in self.potions or self.potions[potion_type] <= 0:
            return 0
        
        if potion_type.startswith("mana"):
            mana_restore = 20 if potion_type == "mana_potion" else 50
            self.mana = min(self.max_mana, self.mana + mana_restore)
            self.potions[potion_type] -= 1
            return mana_restore
        else:
            # Pozione di cura
            heal_amounts = {
                "potion_small": 12,
                "potion_medium": 25,
                "potion_strong": 50
            }
            heal = heal_amounts.get(potion_type, 0)
            self.hp = min(self.get_total_max_hp(), self.hp + heal)
            self.potions[potion_type] -= 1
            return heal

    def gain_xp(self, amount):
        """Guadagna XP e effettua level up."""
        self.xp += amount
        lvl_up = False
        while self.xp >= self.level * 12:
            self.xp -= self.level * 12
            self.level += 1
            self.max_hp += 6
            self.atk += 2
            self.dex += 1
            self.hp = self.max_hp
            lvl_up = True
        return lvl_up

    def get_evasion_chance(self):
        """Calcola la probabilità di schivare basata su DEX e arma."""
        base_evasion = 0.1 + (self.dex * 0.02)  # 10% base + 2% per DEX
        weapon_bonus = self.equipped_weapon.get("evasion_bonus", 0) if self.equipped_weapon else 0
        
        # Bonus da accessori
        accessory_bonus = 0
        for acc in self.accessories.values():
            if acc:
                accessory_bonus += acc.get("evasion_bonus", 0)
        
        return max(0, min(0.5, base_evasion + weapon_bonus + accessory_bonus))

    def get_total_atk(self):
        """Calcola l'ATK totale includendo arma e accessori."""
        weapon_bonus = self.equipped_weapon.get("atk", 0) if self.equipped_weapon else 0
        accessory_bonus = 0
        for acc in self.accessories.values():
            if acc:
                accessory_bonus += acc.get("stats", {}).get("atk", 0)
        return self.atk + weapon_bonus + accessory_bonus

    def get_total_dex(self):
        """Calcola la DEX totale includendo arma e accessori."""
        weapon_bonus = self.equipped_weapon.get("dex", 0) if self.equipped_weapon else 0
        accessory_bonus = 0
        for acc in self.accessories.values():
            if acc:
                accessory_bonus += acc.get("stats", {}).get("dex", 0)
        return self.dex + weapon_bonus + accessory_bonus

    def get_total_max_hp(self):
        """Calcola l'HP massimo includendo accessori."""
        accessory_bonus = 0
        for acc in self.accessories.values():
            if acc:
                accessory_bonus += acc.get("stats", {}).get("max_hp", 0)
        return self.max_hp + accessory_bonus

    def equip_weapon(self, weapon_id):
        """Equipaggia un'arma."""
        for w in self.weapons:
            if w["id"] == weapon_id:
                self.equipped_weapon = w
                return True
        return False

    def equip_accessory(self, accessory_id):
        """Equipaggia un accessorio."""
        for acc in self.available_accessories:
            if acc["id"] == accessory_id:
                slot = acc["slot"]
                self.accessories[slot] = acc
                return True
        return False

    def unequip_accessory(self, slot):
        """Dis-equipaggia un accessorio."""
        if slot in self.accessories:
            self.accessories[slot] = None
            return True
        return False

    def status(self):
        """Ritorna lo status del giocatore."""
        from src.color_manager import format_status
        return format_status(self)
