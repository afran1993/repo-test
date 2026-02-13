"""Menu functions for player interactions."""

import time


def potion_menu(player):
    """Menu per la selezione delle pozioni durante il combattimento."""
    available = [(k, v) for k, v in player.potions.items() if v > 0]
    if not available:
        return None
    
    print("\nPozioni disponibili:")
    for i, (potion_type, count) in enumerate(available, 1):
        print(f"{i}) {potion_type.replace('_', ' ').title()} x{count}")
    print(f"{len(available) + 1}) Indietro")
    
    choice = input("Scegli: ").strip()
    try:
        idx = int(choice) - 1
        if idx == len(available):
            return None
        elif 0 <= idx < len(available):
            return available[idx][0]
    except ValueError:
        pass
    return None


def equip_weapon_menu(player):
    """Menu per equipaggiare armi."""
    print("\n--- EQUIPAGGIA ARMA ---")
    for i, w in enumerate(player.weapons, 1):
        equipped = " [EQUIPPED]" if player.equipped_weapon and player.equipped_weapon["id"] == w["id"] else ""
        print(f"{i}) {w['name']} - ATK +{w['atk']}, DEX {w['dex']:+d}, Evasione {w['evasion_bonus']:+.0%}{equipped}")
    print(f"{len(player.weapons) + 1}) Niente (Pugno)")
    choice = input("Scegli: ").strip()
    try:
        idx = int(choice) - 1
        if idx == len(player.weapons):
            player.equipped_weapon = None
            print("Stacchi l'arma.")
        elif 0 <= idx < len(player.weapons):
            player.equipped_weapon = player.weapons[idx]
            print(f"Equipaggi {player.equipped_weapon['name']}!")
    except ValueError:
        print("Scelta non valida.")


def accessories_menu(player):
    """Menu per equipaggiare accessori (anelli, collane, amuleti, braccialetti)."""
    print("\n--- EQUIPAGGIA ACCESSORI ---")
    for i, acc in enumerate(player.available_accessories, 1):
        equipped = " [EQUIPPED]" if player.accessories.get(acc["slot"]) and player.accessories[acc["slot"]]["id"] == acc["id"] else ""
        atk_bonus = acc.get("stats", {}).get("atk", 0)
        dex_bonus = acc.get("stats", {}).get("dex", 0)
        hp_bonus = acc.get("stats", {}).get("max_hp", 0)
        bonuses = []
        if atk_bonus: bonuses.append(f"ATK +{atk_bonus}")
        if dex_bonus: bonuses.append(f"DEX +{dex_bonus}")
        if hp_bonus: bonuses.append(f"HP +{hp_bonus}")
        bonus_str = ", ".join(bonuses) if bonuses else "Nessun bonus"
        print(f"{i}) {acc['name']} ({acc['slot']}) - {bonus_str}{equipped}")
    print(f"{len(player.available_accessories) + 1}) Esci dal menu")
    choice = input("Scegli: ").strip()
    try:
        idx = int(choice) - 1
        if idx == len(player.available_accessories):
            return
        elif 0 <= idx < len(player.available_accessories):
            acc = player.available_accessories[idx]
            slot = acc["slot"]
            if player.accessories[slot] and player.accessories[slot]["id"] == acc["id"]:
                player.unequip_accessory(slot)
                print(f"Hai rimosso {acc['name']}.")
            else:
                player.equip_accessory(acc["id"])
                print(f"Hai equipaggiato {acc['name']}!")
    except ValueError:
        print("Scelta non valida.")


def shop(player):
    """Shop per l'acquisto di pozioni."""
    print("🏪 Bottega: (1)Pozione (5 gold)  (2)Niente")
    choice = input("-> ").strip()
    if choice == "1":
        if player.gold >= 5:
            player.gold -= 5
            player.potions["potion_small"] += 1
            print("✅ Acquistata pozione.")
        else:
            print("❌ Non hai abbastanza gold.")
    else:
        print("Esci dalla bottega.")


def open_treasure(player, location):
    """Apre un forziere in una location."""
    # ITEMS_DATA accessed as global
    if not location.treasure:
        print("Non ci sono forzieri qui.")
        return
    
    print("\nForzieri disponibili:")
    for i, treasure in enumerate(location.treasure, 1):
        print(f"{i}) {treasure.get('type', 'chest')} ({treasure.get('rarity', 'common')})")
    print(f"{len(location.treasure) + 1}) Indietro")
    
    choice = input("Quale forziere apri? ").strip()
    try:
        idx = int(choice) - 1
        if idx == len(location.treasure):
            return
        elif 0 <= idx < len(location.treasure):
            treasure = location.treasure[idx]
            print(f"\nApri il {treasure.get('type', 'forziere')}...")
            time.sleep(0.3)
            
            drops = treasure.get('drops', [])
            for drop_item in drops:
                # TODO: Handle treasure drops with ITEMS_DATA
                pass
            
            # Rimuovi il forziere (può essere aperto solo una volta per partita)
            location.treasure.pop(idx)
    except ValueError:
        print("Scelta non valida.")
