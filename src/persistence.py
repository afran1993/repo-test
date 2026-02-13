"""Game persistence (save/load) functionality."""

import json
import os
import time
import logging
from src.players.player import Player

logger = logging.getLogger(__name__)


def save_game(player, path="save.json"):
    """Save player game to file."""
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
        "current_location": player.current_location,
        "language": player.language,
    }
    with open(path, "w") as f:
        json.dump(data, f)
    logger.info(f"Game saved: {player.name} at {player.current_location}")
    print("Partita salvata.")


def load_game(path="save.json"):
    """Load a saved game from file."""
    if not os.path.exists(path):
        logger.warning(f"Save file not found: {path}")
        print("Nessun salvataggio trovato.")
        return None
    
    try:
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
        p.current_location = data.get("current_location", "beach")
        p.language = data.get("language", "it")
        logger.info(f"Game loaded: {p.name} from {p.current_location}")
        print("Partita caricata.")
        return p
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading game: {e}")
        print("Errore nel caricamento del salvataggio.")
        return None

def hospital(player):
    """Heal player after defeat and apply gold penalty."""
    logger.warning(f"Player {player.name} defeated, going to hospital")
    print("\n--- OSPEDALE ---")
    print("Sei stato portato in ospedale e ti stai riprendendo...")
    time.sleep(0.5)
    
    # Punishment: lose gold
    penalty = max(5, player.gold // 3)  # Lose 1/3 of gold (minimum 5)
    player.gold = max(0, player.gold - penalty)
    
    # Full healing
    player.hp = player.get_total_max_hp()
    
    logger.info(f"Player healed, lost {penalty} gold")
    print(f"Ti sei ripreso completamente.")
    print(f"Hai pagato {penalty} gold per le cure.")
    print(f"Oro rimasto: {player.gold}\n")
    
    # Salva il giocatore guarito
    save_game(player)
    time.sleep(0.5)
