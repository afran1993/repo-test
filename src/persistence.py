"""Game persistence (save/load) functionality."""

import json
import os
import time
from src.players.player import Player


def save_game(player, path="save.json"):
    """Salva la partita del giocatore."""
    data = {
        "name": player.name,
        "level": player.level,
        "xp": player.xp,
        "max_hp": player.max_hp,
        "hp": player.hp,
        "atk": player.atk,
        "dex": player.dex,
        "gold": player.gold,
        "potions": player.potions,
        "equipped_weapon": player.equipped_weapon,
        "accessories": player.accessories,
    }
    with open(path, "w") as f:
        json.dump(data, f)
    print("Partita salvata.")


def load_game(path="save.json"):
    """Carica una partita salvata."""
    if not os.path.exists(path):
        print("Nessun salvataggio trovato.")
        return None
    
    with open(path, "r") as f:
        data = json.load(f)
    
    p = Player(data.get("name", "Eroe"))
    p.level = data.get("level", 1)
    p.xp = data.get("xp", 0)
    p.max_hp = data.get("max_hp", 30)
    p.hp = data.get("hp", p.max_hp)
    p.atk = data.get("atk", 6)
    p.dex = data.get("dex", 5)
    p.gold = data.get("gold", 0)
    p.potions = data.get("potions", {})
    p.equipped_weapon = data.get("equipped_weapon", None)
    p.accessories = data.get("accessories", {"ring": None, "necklace": None, "amulet": None, "bracelet": None})
    print("Partita caricata.")
    return p


def hospital(player):
    """Cura il giocatore dopo una sconfitta e applica penalità di oro."""
    print("\n--- OSPEDALE ---")
    print("Sei stato portato in ospedale e ti stai riprendendo...")
    time.sleep(0.5)
    
    # Punizione: perdere oro
    penalty = max(5, player.gold // 3)  # Perdi 1/3 dell'oro (minimo 5)
    player.gold = max(0, player.gold - penalty)
    
    # Guarigione completa
    player.hp = player.get_total_max_hp()
    
    print(f"Ti sei ripreso completamente.")
    print(f"Hai pagato {penalty} gold per le cure.")
    print(f"Oro rimasto: {player.gold}\n")
    
    # Salva il giocatore guarito
    save_game(player)
    time.sleep(0.5)
