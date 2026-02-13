"""Game logic and game loop management."""

import time
from src.story import (
    check_story_milestone, get_story_status, get_boss_for_location,
    get_current_main_quest, update_story_progress, check_location_access,
    get_npcs_in_location, interact_with_npc, get_available_skills, get_learned_skills
)
from src.menus import equip_weapon_menu, accessories_menu, open_treasure
from src.persistence import save_game
from src.i18n import i18n
from src.map_system import print_map, show_world_map, list_locations, navigate_location


def choose_language():
    """Chiede al giocatore quale lingua usare."""
    print("\n" + "="*60)
    print("SCEGLI LA LINGUA / CHOOSE LANGUAGE")
    print("="*60)
    print("1) Italiano")
    print("2) English")
    print("="*60 + "\n")
    
    choice = input("Scelta / Choice (1 o 2): ").strip()
    if choice == "2":
        return "en"
    else:
        return "it"


def ask_battle_count():
    """Chiede al giocatore quanti nemici vuole combattere."""
    print("\nQuanti nemici vuoi combattere di fila? (inserisci un numero, ad es: 1, 5, 10, 1000)")
    try:
        count = int(input("-> ").strip())
        if count > 0:
            return count
        else:
            print("Inserisci un numero positivo.")
            return 1
    except ValueError:
        print("Numero non valido, combatterai 1 nemico.")
        return 1


def execute_multiple_battles(player, location, is_boss, fight_fn, get_boss_fn, get_location_fn):
    """Esegue più combattimenti in sequenza."""
    battle_count = ask_battle_count()
    battles_won = 0
    
    for i in range(battle_count):
        if not player.is_alive():
            break
        
        # Se è un boss, combatti solo il boss
        if is_boss:
            boss = get_boss_fn(player.current_location)
            if not boss:
                print("Il boss non è qui!")
                break
            
            print(f"\n[Boss Battle {i+1}/{battle_count}]")
            print(f"Incontri: {boss.name}!")
            time.sleep(0.5)
            
            result = fight_fn(player, boss, location, is_boss=True)
            if result:
                print(f"\n✦✦✦ HAI SCONFITTO IL BOSS! ✦✦✦")
                print(f"{boss.name} soccombe!")
                print(f"Ottieni {boss.xp_reward * 2} XP e {boss.gold_reward * 2} gold!")
                player.gold += boss.xp_reward * 2
                player.gain_xp(boss.xp_reward * 2)
                update_story_progress(player)
                battles_won += 1
            else:
                print("Sei dovuto fuggire dal boss...")
                break
        else:
            # Combatti nemici normali
            enemy = location.get_random_enemy()
            if not enemy:
                print("🚫 Non trovi nemici qui.")
                break
            
            print(f"\n[Battaglia {i+1}/{battle_count}] {enemy.name} appare!")
            time.sleep(0.3)
            
            result = fight_fn(player, enemy, location)
            if result:
                battles_won += 1
                print(f"\n✨ Hai sconfitto il {enemy.name}! ✨")
                print(f"⭐ Ottieni {enemy.xp_reward} XP e {enemy.gold_reward} gold.")
                
                # Se è il primo nemico o ogni 5 nemici, mostra i progressi
                if (i + 1) % 5 == 0 or i == 0:
                    print(f"\n📊 Progressi: {battles_won}/{i+1} vittorie")
                    print(f"Totale XP: {player.xp}, Totale Gold: {player.gold}")
            else:
                print("💨 Sei dovuto fuggire o sconfitto...")
                break
        
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"📊 RISULTATI BATTAGLIA: {battles_won} vittorie su {battle_count}")
    print(f"Livello: {player.level}, XP: {player.xp}/{player.level*12}")
    print(f"Gold totale: {player.gold}, HP: {player.hp}/{player.get_total_max_hp()}")
    print(f"{'='*60}\n")


def game_loop_map(player, fight_fn, get_location_fn, get_boss_fn, get_enemy_emoji_fn, LOCATIONS_DATA, NPCS_DATA):
    """Nuovo game loop con sistema di mappa e storia principale."""
    print("\n" + "="*60)
    print("BENVENUTO NELL'AVVENTURA")
    print("="*60)
    print(f"Ti svegli sulla spiaggia senza memoria e senza armi...")
    time.sleep(1)
    
    while player.is_alive():
        location = get_location_fn(player.current_location)
        if not location:
            print("Errore: location non trovata!")
            return False
        
        # Controlla milestone di storia quando arriva in una location
        milestone = check_story_milestone(player, player.current_location)
        if milestone:
            print(f"\n✦ {milestone} ✦\n")
            time.sleep(1)
        
        print("\n" + "="*60)
        print(location.describe())
        print(f"\n{player.status()}\n")
        
        # Mostra lo status della storia principale
        print("--- STORIA PRINCIPALE ---")
        print(get_story_status(player))
        print("="*60 + "\n")
        
        print("Cosa vuoi fare?")
        print("1) Esplora/Combatti  2) Forzieri  3) Armi  4) Accessori  5) Inventario  6) Parla a NPCs  7) Riposa  8) Mappa  9) Abilità  10) Salva  11) Esci")
        
        cmd = input("-> ").strip()
        
        if cmd == "1":
            # Esplora e combatti
            boss = get_boss_fn(player.current_location)
            if boss:
                quest = get_current_main_quest(player)
                if quest and quest.get("boss_encounter"):
                    execute_multiple_battles(player, location, True, fight_fn, get_boss_fn, get_location_fn)
                else:
                    execute_multiple_battles(player, location, False, fight_fn, get_boss_fn, get_location_fn)
            else:
                execute_multiple_battles(player, location, False, fight_fn, get_boss_fn, get_location_fn)
        
        elif cmd == "2":
            # Forzieri
            open_treasure(player, location)
        
        elif cmd == "3":
            equip_weapon_menu(player)
        
        elif cmd == "4":
            accessories_menu(player)
        
        elif cmd == "5":
            # Inventario
            if player.inventory:
                print("\nInventario:")
                for i, item in enumerate(player.inventory, 1):
                    print(f"{i}) {item.get('name', item.get('id'))}")
            else:
                print("Inventario vuoto.")
        
        elif cmd == "6":
            # Parla con NPCs in questa location
            npcs_here = get_npcs_in_location(player.current_location, NPCS_DATA)
            if npcs_here:
                print("\nPersone in questa location:")
                for i, npc in enumerate(npcs_here, 1):
                    print(f"{i}) {npc.get('name', 'Sconosciuto')}")
                print(f"{len(npcs_here) + 1}) Vai via")
                
                npc_choice = input("Parla con chi? ").strip()
                try:
                    npc_idx = int(npc_choice) - 1
                    if npc_idx == len(npcs_here):
                        print("Ti allontani...")
                    elif 0 <= npc_idx < len(npcs_here):
                        interact_with_npc(player, npcs_here[npc_idx], NPCS_DATA)
                except ValueError:
                    print("Scelta non valida.")
            else:
                print("Non c'è nessuno qui con cui parlare.")
        
        elif cmd == "7":
            # Riposa
            heal = min(player.get_total_max_hp() - player.hp, 15)
            player.hp += heal
            print(f"Riposi e recuperi {heal} HP.")
        
        elif cmd == "8":
            # Mappa interattiva
            print("\n" + "="*60)
            print(i18n.t('map.menu', 'MAPPA - COSA VUOI FARE?'))
            print("="*60)
            print("1) Mappa attuale (connessioni)")
            print("2) Mappa del mondo (tutte le locazioni)")
            print("3) Elenco tutti i luoghi")
            print("4) Naviga verso una locazione")
            print("5) Indietro")
            print("="*60)
            
            map_choice = input("-> ").strip()
            
            if map_choice == "1":
                # Mappa attuale con connessioni
                locations_by_id = {loc['id']: loc for loc in LOCATIONS_DATA['locations']}
                print_map(player.current_location, locations_by_id)
            
            elif map_choice == "2":
                # Mappa mondo completa
                locations_by_id = {loc['id']: loc for loc in LOCATIONS_DATA['locations']}
                show_world_map()
            
            elif map_choice == "3":
                # Elenco di tutte le locazioni
                locations_by_id = {loc['id']: loc for loc in LOCATIONS_DATA['locations']}
                list_locations(locations_by_id)
            
            elif map_choice == "4":
                # Navigazione con validazione
                next_loc = input(i18n.t('map.navigate', "Verso quale direzione? (nord/south/est/ovest/east/west): ")).strip().lower()
                
                if next_loc in location.connections:
                    next_location = get_location_fn(location.connections[next_loc])
                    can_access, error_msg = check_location_access(player, location.connections[next_loc], next_location.element)
                    
                    if can_access:
                        player.current_location = location.connections[next_loc]
                        print(f"\n🚶 Ti sposti verso {next_loc}...")
                        time.sleep(1)
                    else:
                        print(f"\n❌ Non puoi andare: {error_msg}")
                else:
                    available = ", ".join(location.connections.keys())
                    print(f"\n❌ Direzione non valida. Disponibili: {available}")
            
            elif map_choice == "5":
                pass  # Torna al menu
            
            else:
                print("Opzione non valida.")
        
        elif cmd == "9":
            # Mostra abilità
            print("\n" + "="*60)
            print("LE TUE ABILITÀ")
            print("="*60)
            learned = get_learned_skills(player)
            available = get_available_skills(player)
            
            if learned:
                print("\n✓ Abilità Imparate:")
                for skill in learned:
                    print(f"  ✓ {skill.title()}")
            else:
                print("\n✓ Abilità Imparate: Nessuna ancora")
            
            print(f"\n? Abilità Disponibili: {len(available)}")
            print("Chiedi agli NPC nei villaggi come imparare nuove abilità!")
            print("="*60 + "\n")
        
        elif cmd == "10":
            save_game(player)
        
        elif cmd == "11":
            print("Alla prossima avventura!")
            return True
        
        else:
            print("Opzione non valida.")
    
    return False
