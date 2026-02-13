#!/usr/bin/env python3
import random
import json
import os
import argparse
import time

from src.combat import CombatEngine, create_fight_with_engine, init_abilities_registry, get_registry
from src.players import Player
from src.persistence import save_game, load_game, hospital
from src.menus import potion_menu, equip_weapon_menu, accessories_menu, shop, open_treasure
from src.story import (
    check_story_milestone, get_story_status, get_boss_for_location,
    get_current_main_quest, update_story_progress, teach_skill, has_skill,
    get_available_skills, get_learned_skills, check_location_access
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))


# Carica i dati
LOCATIONS_DATA = None
ENEMIES_DATA = None
ITEMS_DATA = None
QUESTS_DATA = None
NPCS_DATA = None

# Mappa emoji per i nemici
ENEMY_EMOJIS = {
    "slime": "🟢", "goblin": "👹", "wolf": "🐺", "dragon": "🐉", "skeleton": "💀",
    "ghost": "👻", "orc": "👿", "squid": "🐙", "bat": "🦇", "spider": "🕷️",
    "harpy": "🦅", "wraith": "👻", "knight": "🤺", "crab": "🦀", "bird": "🐦",
    "elemental": "⚡", "fire": "🔥", "water": "💧", "wind": "🌪️", "earth": "🪨",
    "construct": "🤖", "beast": "🐻", "undead": "💀", "spirit": "👻", "troll": "👹",
    "golem": "🪨", "serpent": "🐍", "chimera": "🦁", "lich": "💀", "bandit": "🗡️",
    "sprite": "✨", "wisp": "💫", "beetle": "🐞", "seagull": "🐦"
}

def load_data():
    global LOCATIONS_DATA, ENEMIES_DATA, ITEMS_DATA, QUESTS_DATA, NPCS_DATA
    with open(os.path.join(ROOT, 'data', 'locations.json'), 'r') as f:
        LOCATIONS_DATA = json.load(f)
    with open(os.path.join(ROOT, 'data', 'enemies.json'), 'r') as f:
        ENEMIES_DATA = json.load(f)
    with open(os.path.join(ROOT, 'data', 'items.json'), 'r') as f:
        ITEMS_DATA = json.load(f)
    with open(os.path.join(ROOT, 'data', 'quests.json'), 'r') as f:
        QUESTS_DATA = json.load(f)
    with open(os.path.join(ROOT, 'data', 'npcs.json'), 'r') as f:
        NPCS_DATA = json.load(f)
    
    # Initialize abilities registry
    init_abilities_registry(os.path.join(ROOT, 'data', 'abilities.json'))


# Type matchup system (simile a Pokemon)
ELEMENT_MATCHUPS = {
    "Fire": {"strong_against": ["Earth", "Air"], "weak_against": ["Water"]},
    "Water": {"strong_against": ["Fire"], "weak_against": ["Earth", "Lightning"]},
    "Earth": {"strong_against": ["Water", "Lightning"], "weak_against": ["Fire", "Air"]},
    "Air": {"strong_against": ["Earth"], "weak_against": ["Lightning"]},
    "Lightning": {"strong_against": ["Water", "Air"], "weak_against": ["Earth"]},
    "Arcane": {"strong_against": ["Arcane"], "weak_against": ["None"]},
    "None": {"strong_against": [], "weak_against": []}
}


def get_element_modifier(attacker_element, defender_element):
    """
    Calcola il modifier di danno basato sugli elementi.
    - Se l'attaccante usa un elemento che è forte contro quello del difensore, +25% danno
    - Se l'attaccante usa un elemento che è debole contro quello del difensore, -25% danno
    """
    modifier = 1.0
    
    matchup = ELEMENT_MATCHUPS.get(attacker_element, {})
    if defender_element in matchup.get("strong_against", []):
        modifier *= 1.25  # +25% vantaggio
    elif defender_element in matchup.get("weak_against", []):
        modifier *= 0.75  # -25% svantaggio
    
    return modifier


def get_enemy_emoji(enemy):
    """Ritorna l'emoji appropriato per un nemico basato su tag o ID."""
    enemy_id = enemy.id.lower() if hasattr(enemy, 'id') else ""
    enemy_name = enemy.name.lower() if hasattr(enemy, 'name') else ""
    
    # Controlla i tag se disponibili
    if hasattr(enemy, 'tags'):
        for tag in enemy.tags:
            if tag in ENEMY_EMOJIS:
                return ENEMY_EMOJIS[tag]
    
    # Controlla per ID o nome
    for key, emoji in ENEMY_EMOJIS.items():
        if key in enemy_id or key in enemy_name:
            return emoji
    
    return "👹"  # Emoji predefinita fallback


# Story quest system

def get_current_main_quest(player):
    """Ottiene la quest principale corrente del giocatore."""
    if not QUESTS_DATA:
        return None
    for quest in QUESTS_DATA.get("main_story", []):
        if quest["id"] == player.story_progress:
            return quest
    return None


def get_story_status(player):
    """Ritorna una descrizione dello status della storia."""
    quest = get_current_main_quest(player)
    if not quest:
        if player.postgame:
            return "✦ POSTGAME - Sfida nemici infiniti!"
        return "?"
    
    chapter = quest.get("chapter", 0)
    title = quest.get("title", "???")
    stage = player.story_stage
    stages = quest.get("stages", [])
    
    status = f"Atto {chapter}: {title}\n"
    status += f"  Progresso: {stage}/{len(stages)}\n"
    if stage < len(stages):
        status += f"  Missione: {stages[stage]}"
    return status


def update_story_progress(player):
    """Avanza la storia principale al prossimo stage."""
    quest = get_current_main_quest(player)
    if not quest:
        return False
    
    stages = quest.get("stages", [])
    if player.story_stage < len(stages) - 1:
        player.story_stage += 1
        return False  # Non completata
    else:
        # Quest completata!
        player.completed_acts.append(player.story_progress)
        next_quest_id = quest.get("reward", {}).get("unlocks")
        
        if next_quest_id == "postgame":
            player.postgame = True
            print(f"\n✦✦✦ HAI COMPLETATO LA STORIA PRINCIPALE! ✦✦✦")
            print(f"Titolo: {quest.get('reward', {}).get('title', 'Eroe')}")
            return True
        elif next_quest_id:
            # Controlla se il prossimo atto esiste
            found = False
            for q in QUESTS_DATA.get("main_story", []):
                if q["id"] == next_quest_id:
                    player.story_progress = next_quest_id
                    player.story_stage = 0
                    found = True
                    break
            return found
    
    return False


def check_story_milestone(player, location_id):
    """Controlla se il giocatore ha raggiunto un milestone di storia."""
    quest = get_current_main_quest(player)
    if not quest:
        return None
    
    triggers = quest.get("location_triggers", {})
    if location_id in triggers:
        message = triggers[location_id]
        update_story_progress(player)
        return message
    
    return None


def get_boss_for_location(location_id):
    """Ritorna il boss nemico per una location specifica (se esiste)."""
    quest = None
    for q in QUESTS_DATA.get("main_story", []):
        if location_id in q.get("location_triggers", {}):
            quest = q
            break
    
    if not quest:
        return None
    
    boss_id = quest.get("boss_encounter")
    if boss_id:
        for enemy_data in ENEMIES_DATA.get("enemies", []):
            if enemy_data.get("id") == boss_id:
                return Enemy(enemy_data)
    
    return None


def apply_boss_ability(player, boss, ability_name):
    """
    Applica una abilità speciale del boss (data-driven).
    
    Now uses the centralized abilities registry from data/abilities.json.
    Maintains backward compatibility with existing code.
    """
    from src.combat.abilities import apply_ability
    
    return apply_ability(boss, player, ability_name)


# Sistema di abilità e dialoghi
def teach_skill(player, skill_name):
    """Insegna una nuova abilità al giocatore."""
    if skill_name not in player.skills:
        return False, f"Abilità '{skill_name}' non riconosciuta."
    
    if player.skills[skill_name]:
        return False, f"Conosci già '{skill_name}'!"
    
    player.skills[skill_name] = True
    
    skill_messages = {
        "swimming": "✦ HAI IMPARATO A NUOTARE! ✦\nOra puoi accedere alle lagune e alle rive dell'acqua.",
        "diving": "✦ HAI IMPARATO L'IMMERSIONE SUBACQUEA! ✦\nOra puoi esplorare le caverne sommerse.",
        "climbing": "✦ HAI IMPARATO AD ARRAMPICARTI! ✦\nOra puoi scalare montagne e alberi.",
        "pickpocketing": "✦ HAI IMPARATO L'ARTE DEL FURTO! ✦\nOra puoi rubare negli insediamenti.",
        "stealth": "✦ HAI IMPARATO LA FURTIVITÀ! ✦\nOra puoi muoverti senza essere notato.",
        "healing": "✦ HAI IMPARATO LA GUARIGIONE! ✦\nOra puoi curare le tue ferite più efficacemente.",
        "magic": "✦ HAI IMPARATO LA MAGIA! ✦\nOra puoi lanciare incantesimi in battaglia.",
        "crafting": "✦ HAI IMPARATO L'ARTIGIANATO! ✦\nOra puoi creare oggetti dai materiali.",
    }
    
    return True, skill_messages.get(skill_name, f"Hai imparato {skill_name}!")


def has_skill(player, skill_name):
    """Controlla se il giocatore possiede un'abilità."""
    return player.skills.get(skill_name, False)


def get_available_skills(player):
    """Ritorna una lista di abilità non ancora imparate."""
    return [skill for skill, learned in player.skills.items() if not learned]


def get_learned_skills(player):
    """Ritorna una lista di abilità già imparate."""
    return [skill for skill, learned in player.skills.items() if learned]


def check_location_access(player, location_id, location_element):
    """Controlla se il giocatore ha accesso a una location in base alle abilità."""
    access_requirements = {
        "lagoon": {"skill": "swimming", "message": "Non sai ancora nuotare! Devi imparare prima."},
        "underwater_cave": {"skill": "diving", "message": "Non sai ancora tuffarti sott'acqua! Devi imparare a nuotare e poi ad immergerti."},
        "summit": {"skill": "climbing", "message": "Non sai ancora arrampicarti! Devi imparare prima."},
        "sky_temple": {"skill": "climbing", "message": "Hai bisogno di saper arrampicarti per raggiungere il tempio."},
    }
    
    if location_id in access_requirements:
        required_skill = access_requirements[location_id]["skill"]
        if not has_skill(player, required_skill):
            return False, access_requirements[location_id]["message"]
    
    return True, None


# Dialogo e storia

def start_dialogue(player, npc_id, npcs_data):
    """Avvia un dialogo con un NPC."""
    npc = None
    for n in npcs_data.get("npcs", []):
        if n.get("id") == npc_id:
            npc = n
            break
    
    if not npc:
        return None
    
    # Controlla se è un dialogo ramificato
    dialogs = npc.get("dialogs", [])
    if not dialogs:
        return None
    
    # Ottieni il dialogo corretto in base allo stato della storia
    available_dialog = None
    for dialog in dialogs:
        required_skill = dialog.get("requires_skill")
        required_act = dialog.get("requires_act")
        
        # Se richiede un'abilità, controllala
        if required_skill and not has_skill(player, required_skill):
            continue
        
        # Se richiede un atto specifico, controllalo
        if required_act and player.story_progress != required_act:
            continue
        
        # Se richiede scelte precedenti, controllale
        required_choice = dialog.get("requires_choice")
        if required_choice:
            if player.dialogue_choices.get(npc_id) != required_choice:
                continue
        
        # Questo dialogo è idoneo
        available_dialog = dialog
        break
    
    if not available_dialog:
        available_dialog = dialogs[0] if dialogs else None
    
    return available_dialog


def display_dialogue(dialog):
    """Mostra un dialogo con le opzioni."""
    if not dialog:
        return None
    
    print(f"\n{'='*60}")
    print(f"NPC: {dialog.get('npc_name', 'Persona Sconosciuta')}")
    print(f"{'='*60}\n")
    print(dialog.get("text", "..."))
    print()
    
    options = dialog.get("options", [])
    if not options:
        return None
    
    for i, option in enumerate(options, 1):
        print(f"{i}) {option.get('text', '??')}")
    
    print(f"{len(options) + 1}) Vai via")
    print()
    
    return options


def execute_dialogue_choice(player, choice, npc_id, npcs_data):
    """Esegue le conseguenze di una scelta di dialogo."""
    if not choice:
        return ""
    
    consequence = ""
    
    # Insegna abilità se specificata
    if "teaches_skill" in choice:
        skill_name = choice["teaches_skill"]
        success, message = teach_skill(player, skill_name)
        if success:
            consequence += f"\n{message}\n"
    
    # Aggiorna lo stato della storia
    if "updates_story" in choice:
        player.story_progress = choice["updates_story"]
        player.story_stage = 0
        consequence += f"\n✦ La storia avanza! ✦\n"
    
    # Modifica lo XP
    if "xp_reward" in choice:
        player.gain_xp(choice["xp_reward"])
        consequence += f"Guadagni {choice['xp_reward']} XP!\n"
    
    # Modifica l'oro
    if "gold_reward" in choice:
        player.gold += choice["gold_reward"]
        consequence += f"Guadagni {choice['gold_reward']} gold!\n"
    
    # Salva la scelta effettuata
    player.dialogue_choices[npc_id] = choice.get("id")
    
    return consequence


def get_npcs_in_location(location_id, npcs_data):
    """Ritorna una lista di NPCs in una location."""
    npcs_list = []
    for npc in npcs_data.get("npcs", []):
        if npc.get("location") == location_id:
            npcs_list.append(npc)
    return npcs_list


def interact_with_npc(player, npc, npcs_data):
    """Interagisce con un NPC tramite dialogo ramificato."""
    dialog = start_dialogue(player, npc.get("id"), npcs_data)
    
    if not dialog:
        print(f"{npc.get('name', 'Sconosciuto')}: ...")
        return
    
    options = display_dialogue(dialog)
    
    if not options:
        print(f"{npc.get('name', 'Sconosciuto')}: Buona fortuna, viaggiatore.")
        return
    
    # Mostra le opzioni
    choice_num = input("Scegli: ").strip()
    
    try:
        choice_idx = int(choice_num) - 1
        if choice_idx == len(options):
            print("Ti allontani...")
            return
        elif 0 <= choice_idx < len(options):
            choice = options[choice_idx]
            
            # Controlla se la scelta richiede un'abilità
            if "requires_skill" in choice:
                required_skill = choice["requires_skill"]
                if not has_skill(player, required_skill):
                    print(f"\n{npc.get('name', 'Sconosciuto')}: Mi dispiace, ma devi prima imparare {required_skill}!")
                    return
            
            # Esegui le conseguenze della scelta
            consequence = execute_dialogue_choice(player, choice, npc.get("id"), npcs_data)
            
            # Mostra la risposta dell'NPC
            print(f"\n{npc.get('name', 'Sconosciuto')}:")
            print(choice.get("response", ""))
            
            if consequence:
                print(consequence)
        else:
            print("Scelta non valida.")
    except ValueError:
        print("Scelta non valida.")


class Enemy:
    """Nemico del gioco."""
    def __init__(self, enemy_data):
        self.id = enemy_data.get("id")
        self.name = enemy_data.get("display", "Unknown")
        self.hp = enemy_data.get("hp", 10)

        self.max_hp = self.hp
        self.atk = enemy_data.get("atk", 3)
        self.def_ = enemy_data.get("def", 0)
        self.element = enemy_data.get("element", "None")
        self.xp_reward = enemy_data.get("tier", 1) * 10
        self.gold_reward = random.randint(enemy_data.get("tier", 1) * 2, enemy_data.get("tier", 1) * 5)
        
    def is_alive(self):
        return self.hp > 0
    
    def describe(self):
        return f"{self.name} ({self.element}) - HP {self.hp}/{self.max_hp}"


class Location:
    """Una location sulla mappa."""
    def __init__(self, location_data):
        self.id = location_data.get("id")
        self.name = location_data.get("name")
        self.description = location_data.get("description")
        self.difficulty = location_data.get("difficulty", 0)
        self.element = location_data.get("element", "None")
        self.terrain = location_data.get("terrain", "unknown")
        self.enemies = location_data.get("enemies", [])
        self.connections = location_data.get("connections", {})
        self.treasure = location_data.get("treasure", [])
        self.npc = location_data.get("npc", None)
        
    def describe(self):
        desc = f"\n=== {self.name} ===\n{self.description}\n"
        return desc

    def describe_for(self, player=None):
        """Descrizione estesa visibile al giocatore che include info su connessioni bloccate."""
        desc = f"\n=== {self.name} ===\n{self.description}\n"

        if player:
            # Mostra se questa stessa location è bloccata (utile se chiamata per preview)
            can_access, err = check_location_access(player, self.id, self.element)
            if not can_access:
                desc += f"\n>>> BLOCCATO: {err} <<<\n"

        if self.connections:
            desc += "\nConnessioni:\n"
            for direction, loc_id in self.connections.items():
                target = get_location(loc_id)
                if player:
                    can_access, err = check_location_access(player, loc_id, target.element if target else None)
                    if can_access:
                        desc += f"  - {direction}: {loc_id}\n"
                    else:
                        desc += f"  - {direction}: {loc_id} [BLOCCATO: {err}]\n"
                else:
                    desc += f"  - {direction}: {loc_id}\n"

        return desc
    
    def get_random_enemy(self):
        """Ritorna un nemico casuale per questa location."""
        if not self.enemies:
            return None
        choice = random.choices(self.enemies, weights=[e.get("chance", 0.5) for e in self.enemies])[0]
        enemy_id = choice.get("id")
        
        # Cerca il nemico nel ENEMIES_DATA
        for enemy_data in ENEMIES_DATA.get("enemies", []):
            if enemy_data.get("id") == enemy_id:
                return Enemy(enemy_data)
        return None








def get_location(location_id):
    """Ottiene una Location dal suo ID."""
    if not LOCATIONS_DATA:
        return None
    for loc_data in LOCATIONS_DATA.get("locations", []):
        if loc_data.get("id") == location_id:
            return Location(loc_data)
    return None


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


def fight(player, enemy, current_location=None, is_boss=False):
    """
    Main fight function - now using decoupled CombatEngine.
    
    Maintains backward compatibility with existing code.
    """
    # Create engine with element modifier and ability application
    engine = CombatEngine(
        player=player,
        enemy=enemy,
        element_modifier_fn=get_element_modifier,
        apply_ability_fn=apply_boss_ability,
        is_boss=is_boss,
        current_location=current_location,
    )
    
    # Use CLI adapter to handle the fight
    victory = create_fight_with_engine(
        engine=engine,
        player=player,
        enemy=enemy,
        emoji_getter=get_enemy_emoji,
    )
    
    # Post-fight logic
    if victory:
        player.gold += enemy.gold_reward
        leveled = player.gain_xp(enemy.xp_reward)
        if leveled:
            print(f"🎉 Sei salito al livello {player.level}! HP ripristinati.")
        save_game(player)
        return True
    else:
        # Check if it was a flee or a defeat
        if engine.finished and not engine.victory:
            # If finished but not victory, it was a defeat (unless it was a flee)
            if player.is_alive():
                # Player fled successfully
                return False
            else:
                # Player was defeated
                hospital(player)
                return False
        else:
            hospital(player)
            return False


def game_loop_map(player):
    """Nuovo game loop con sistema di mappa e storia principale."""
    print("\n" + "="*60)
    print("BENVENUTO NELL'AVVENTURA")
    print("="*60)
    print(f"Ti svegli sulla spiaggia senza memoria e senza armi...")
    time.sleep(1)
    
    while player.is_alive():
        location = get_location(player.current_location)
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
            # Controlla se c'è un boss in questa location
            boss = get_boss_for_location(player.current_location)
            if boss:
                quest = get_current_main_quest(player)
                if quest and quest.get("boss_encounter"):
                    print(f"\n!!! BOSS FIGHT !!!")
                    print(f"Incontri: {boss.name}!")
                    time.sleep(1)
                    result = fight(player, boss, location, is_boss=True)
                    if result:
                        print(f"\n✦✦✦ HAI SCONFITTO IL BOSS! ✦✦✦")
                        print(f"{boss.name} soccombe!")
                        print(f"Ottieni {boss.xp_reward * 2} XP e {boss.gold_reward * 2} gold!")
                        player.gold += boss.gold_reward * 2
                        player.gain_xp(boss.xp_reward * 2)
                        update_story_progress(player)
                    else:
                        print("Sei dovuto fuggire dal boss...")
                else:
                    enemy = location.get_random_enemy()
                    if enemy:
                        result = fight(player, enemy, location)
                        if result:
                            print(f"\n✨ Hai sconfitto il {enemy.name}! ✨")
                            print(f"⭐ Ottieni {enemy.xp_reward} XP e {enemy.gold_reward} gold.")
                            player.gold += enemy.gold_reward
                            player.gain_xp(enemy.xp_reward)
                        else:
                            print("💨 Sei dovuto fuggire...")
            else:
                enemy = location.get_random_enemy()
                if enemy:
                    result = fight(player, enemy, location)
                    if result:
                        print(f"\n✨ Hai sconfitto il {enemy.name}! ✨")
                        print(f"⭐ Ottieni {enemy.xp_reward} XP e {enemy.gold_reward} gold.")
                        player.gold += enemy.gold_reward
                        player.gain_xp(enemy.xp_reward)
                    else:
                        print("💨 Sei dovuto fuggire...")
                else:
                    print("🚫 Non trovi nemici qui.")
        
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
            # Mappa - mostra connessioni
            print("\nConnessioni disponibili:")
            for direction, loc_id in location.connections.items():
                # Controlla se puoi accedere a questa location
                next_location = get_location(loc_id)
                can_access, error_msg = check_location_access(player, loc_id, next_location.element if next_location else None)
                
                if can_access:
                    print(f"  {direction}: {loc_id}")
                else:
                    print(f"  {direction}: {loc_id} [BLOCCATO: {error_msg}]")
            
            next_loc = input("Vai verso: ").strip().lower()
            if next_loc in location.connections:
                next_location = get_location(location.connections[next_loc])
                can_access, error_msg = check_location_access(player, location.connections[next_loc], next_location.element)
                
                if can_access:
                    player.current_location = location.connections[next_loc]
                    print(f"Ti sposti verso {next_loc}...")
                else:
                    print(f"Non puoi andare there: {error_msg}")
            else:
                print("Direzione non valida.")
        
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

def random_enemy(player_level=1):
    """
    Genera un nemico casuale basato sul livello del giocatore.
    Seleziona nemici con tier vicino al livello del player.
    """
    if not ENEMIES_DATA:
        return None

    enemies = ENEMIES_DATA.get("enemies", [])
    if not enemies:
        return None

    # Filtra nemici con tier compatibile
    possible = []
    for e in enemies:
        tier = e.get("tier", 1)

        # Permette nemici con tier +/- 1 rispetto al livello
        if abs(tier - player_level) <= 1:
            possible.append(e)

    # Se non trovi nulla, fallback su tutti
    if not possible:
        possible = enemies

    chosen_data = random.choice(possible)

    # Copia dati per scaling leggero
    scaled_data = chosen_data.copy()

    # Scaling HP e ATK in base al livello
    level_diff = player_level - scaled_data.get("tier", 1)

    if level_diff > 0:
        scaled_data["hp"] += level_diff * 5
        scaled_data["atk"] += level_diff * 2

    return Enemy(scaled_data)




def main_loop(player):
    print("Benvenuto nell'avventura!")
    while True:
        print()
        print(player.status())
        print("Cosa vuoi fare?")
        print("1) Esplora   2) Bottega   3) Armi   4) Accessori   5) Riposa   6) Salva   7) Carica   8) Esci")
        cmd = input("-> ").strip()
        if cmd == "1":
            if random.random() < 0.75:
                enemy = random_enemy(player.level)
                result = fight(player, enemy)
            else:
                found = random.choice(["gold", "potion", "nothing"])
                if found == "gold":
                    g = random.randint(3, 12)
                    player.gold += g
                    print(f"💰 Trovi {g} gold!")
                elif found == "potion":
                    player.potions["potion_small"] += 1
                    print("🧪 Trovi una pozione!")
                else:
                    print("Niente di interessante qui.")
        elif cmd == "2":
            shop(player)
        elif cmd == "3":
            equip_weapon_menu(player)
        elif cmd == "4":
            accessories_menu(player)
        elif cmd == "5":
            heal = min(player.get_total_max_hp() - player.hp, random.randint(6, 14))
            player.hp += heal
            print(f"😴 Riposi e recuperi {heal} HP.")
        elif cmd == "6":
            save_game(player)
        elif cmd == "7":
            loaded = load_game()
            if loaded:
                player = loaded
        elif cmd == "8":
            print("Alla prossima avventura!")
            return True
        else:
            print("Opzione non valida.")


def demo():
    load_data()
    p = Player("Demo")
    location = get_location("beach")
    if location:
        enemy = location.get_random_enemy()
        if enemy:
            print("Eseguo demo rapida (automatica)...")
            fight_auto(p, enemy)


def fight_auto(player, enemy):
    print(f"Incontro! {enemy.name} appare (HP {enemy.hp})")
    while player.is_alive() and enemy.is_alive():
        dmg = player.attack(enemy)
        print(f"{player.name} attacca il {enemy.name} per {dmg} danni. (HP nemico {max(0, enemy.hp)})")
        if not enemy.is_alive():
            break
        edmg = random.randint(max(1, enemy.atk - 2), enemy.atk + 2)
        player.hp -= edmg
        print(f"{enemy.name} colpisce per {edmg} danni. (HP tuo {max(0, player.hp)})")
        time.sleep(0.2)
    if player.is_alive():
        print(f"Demo: hai sconfitto il {enemy.name}!")
        save_game(player)
    else:
        print("Demo: sei stato sconfitto...")
        hospital(player)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RPG Game")

    # Aggiungi i flag prima di fare parse_args()
    parser.add_argument(
        '--demo', 
        action='store_true',  
        help='Esegui il gioco in modalità demo'
    )

    args = parser.parse_args()

    load_data()  # Carica tutti i dati (locations, enemies, items, quests, npcs)

    if args.demo:
        demo()
    else:
        # Controlla se esiste un salvataggio
        if os.path.exists("save.json"):
            print("📂 Trovato un salvataggio precedente!")
            print("Cosa vuoi fare?")
            print("1) Carica partita   2) Inizia una nuova partita")
            choice = input("-> ").strip()
            
            if choice == "1":
                player = load_game()
                if player:
                    game_loop_map(player)
            else:
                name = input("Come ti chiami, avventuriero? ").strip() or "Eroe"
                player = Player(name)
                game_loop_map(player)
        else:
            name = input("Come ti chiami, avventuriero? ").strip() or "Eroe"
            player = Player(name)
            game_loop_map(player)
