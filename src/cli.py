"""
CLI module - User interface and interaction.

Handles all menus, dialogue, and game loop presentation.
Separated from game logic and engine.
"""

import time
from typing import Optional, Callable, Any, Tuple

from src.data_loader import GameContext
from src.utils import get_enemy_emoji


def choose_language() -> str:
    """Ask player which language to use.
    
    Returns:
        "it" for Italian or "en" for English
    """
    print("\n" + "="*60)
    print("SCEGLI LA LINGUA / CHOOSE LANGUAGE")
    print("="*60)
    print("1) Italiano")
    print("2) English")
    print("="*60 + "\n")
    
    choice = input("Scelta / Choice (1 o 2): ").strip()
    return "en" if choice == "2" else "it"


def ask_battle_count() -> int:
    """Ask player how many enemies to fight in a row.
    
    Returns:
        Number of battles to fight (minimum 1)
    """
    print("\nQuanti nemici vuoi combattere di fila? (inserisci un numero, ad es: 1, 5, 10, 1000)")
    try:
        count = int(input("-> ").strip())
        return max(1, count) if count > 0 else 1
    except ValueError:
        print("Numero non valido, combatterai 1 nemico.")
        return 1


def display_character_status(player: Any) -> None:
    """Display player status information.
    
    Args:
        player: Player object
    """
    print(f"\n{player.status()}\n")


def display_location_info(location: Any, player: Any) -> None:
    """Display location information and connections.
    
    Args:
        location: Location object
        player: Player object
    """
    print("\n" + "="*60)
    print(location.describe())
    print(f"\n{player.status()}\n")
    print("="*60 + "\n")


def display_story_status(get_story_fn: Callable, player: Any) -> None:
    """Display current story progress.
    
    Args:
        get_story_fn: Function to get story status
        player: Player object
    """
    print("--- STORIA PRINCIPALE ---")
    print(get_story_fn(player))
    print("="*60 + "\n")


def display_main_menu() -> str:
    """Display main menu and get user choice.
    
    Returns:
        User's menu choice
    """
    print("Cosa vuoi fare?")
    print("1) Esplora/Combatti  2) Forzieri  3) Armi  4) Accessori  5) Inventario")
    print("6) Parla a NPCs  7) Riposa  8) Mappa  9) Abilità  10) Salva  11) Esci")
    return input("-> ").strip()


def display_inventory(player: Any) -> None:
    """Display player inventory.
    
    Args:
        player: Player object
    """
    if player.inventory:
        print("\nInventario:")
        for i, item in enumerate(player.inventory, 1):
            print(f"{i}) {item.get('name', item.get('id'))}")
    else:
        print("Inventario vuoto.")


def display_skills(
    get_learned_fn: Callable,
    get_available_fn: Callable,
    player: Any
) -> None:
    """Display player skills.
    
    Args:
        get_learned_fn: Function to get learned skills
        get_available_fn: Function to get available skills
        player: Player object
    """
    print("\n" + "="*60)
    print("LE TUE ABILITÀ")
    print("="*60)
    
    learned = get_learned_fn(player)
    available = get_available_fn(player)
    
    if learned:
        print("\n✓ Abilità Imparate:")
        for skill in learned:
            print(f"  ✓ {skill.title()}")
    else:
        print("\n✓ Abilità Imparate: Nessuna ancora")
    
    print(f"\n? Abilità Disponibili: {len(available)}")
    print("Chiedi agli NPC nei villaggi come imparare nuove abilità!")
    print("="*60 + "\n")


def display_map_connections(
    location: Any,
    player: Any,
    check_access_fn: Callable
) -> None:
    """Display available map connections.
    
    Args:
        location: Current location
        player: Player object
        check_access_fn: Function to check location access
    """
    print("\nConnessioni disponibili:")
    for direction, loc_id in location.connections.items():
        # TODO: Get location element for access check
        can_access, error_msg = check_access_fn(player, loc_id, None)
        
        if can_access:
            print(f"  {direction}: {loc_id}")
        else:
            print(f"  {direction}: {loc_id} [BLOCCATO: {error_msg}]")


def display_npc_list(npcs: list) -> Optional[Any]:
    """Display available NPCs and let player choose one.
    
    Args:
        npcs: List of NPC objects
    
    Returns:
        Chosen NPC or None
    """
    if not npcs:
        print("Non c'è nessuno qui con cui parlare.")
        return None
    
    print("\nPersone in questa location:")
    for i, npc in enumerate(npcs, 1):
        print(f"{i}) {npc.get('name', 'Sconosciuto')}")
    print(f"{len(npcs) + 1}) Vai via")
    
    npc_choice = input("Parla con chi? ").strip()
    try:
        npc_idx = int(npc_choice) - 1
        if npc_idx == len(npcs):
            print("Ti allontani...")
            return None
        elif 0 <= npc_idx < len(npcs):
            return npcs[npc_idx]
    except ValueError:
        print("Scelta non valida.")
    
    return None


def display_battle_results(
    battles_won: int,
    battle_count: int,
    player: Any
) -> None:
    """Display results of multiple battles.
    
    Args:
        battles_won: Number of battles won
        battle_count: Total battles fought
        player: Player object
    """
    print(f"\n{'='*60}")
    print(f"📊 RISULTATI BATTAGLIA: {battles_won} vittorie su {battle_count}")
    print(f"Livello: {player.level}, XP: {player.xp}/{player.level*12}")
    print(f"Gold totale: {player.gold}, HP: {player.hp}/{player.get_total_max_hp()}")
    print(f"{'='*60}\n")


def display_game_start(player: Any) -> None:
    """Display game start sequence.
    
    Args:
        player: Player object
    """
    print("\n" + "="*60)
    print("BENVENUTO NELL'AVVENTURA")
    print("="*60)
    print(f"Ti svegli sulla spiaggia senza memoria e senza armi...")
    time.sleep(1)


def display_story_milestone(milestone_text: str) -> None:
    """Display story milestone message.
    
    Args:
        milestone_text: Message to display
    """
    print(f"\n✦ {milestone_text} ✦\n")
    time.sleep(1)


def display_boss_victory(boss: Any, xp_reward: int, gold_reward: int) -> None:
    """Display boss defeat message.
    
    Args:
        boss: Defeated boss object
        xp_reward: XP reward multiplier
        gold_reward: Gold reward multiplier
    """
    print(f"\n✦✦✦ HAI SCONFITTO IL BOSS! ✦✦✦")
    print(f"{boss.name} soccombe!")
    print(f"Ottieni {xp_reward} XP e {gold_reward} gold!")


def display_enemy_defeat(enemy: Any, xp_reward: int, gold_reward: int) -> None:
    """Display enemy defeat message.
    
    Args:
        enemy: Defeated enemy object
        xp_reward: XP reward
        gold_reward: Gold reward
    """
    print(f"\n✨ Hai sconfitto il {enemy.name}! ✨")
    print(f"⭐ Ottieni {xp_reward} XP e {gold_reward} gold.")


def display_level_up(player: Any) -> None:
    """Display level up message.
    
    Args:
        player: Player object
    """
    print(f"🎉 Sei salito al livello {player.level}! HP ripristinati.")


def display_battle_progress(
    current_battle: int,
    total_battles: int,
    battles_won: int
) -> None:
    """Display progress during multiple battles.
    
    Args:
        current_battle: Current battle number
        total_battles: Total battles to fight
        battles_won: Battles won so far
    """
    if (current_battle + 1) % 5 == 0 or current_battle == 0:
        print(f"\n📊 Progressi: {battles_won}/{current_battle+1} vittorie")


def display_rest_message(heal_amount: int) -> None:
    """Display rest/recovery message.
    
    Args:
        heal_amount: HP recovered
    """
    print(f"Riposi e recuperi {heal_amount} HP.")


def display_new_ability_learned(skill_name: str, message: str) -> None:
    """Display ability learned message.
    
    Args:
        skill_name: Name of skill learned
        message: Custom message
    """
    print(f"\n{message}")


def display_no_npcs_here() -> None:
    """Display message when no NPCs in location."""
    print("Non c'è nessuno qui con cui parlare.")


def display_invalid_menu_choice() -> None:
    """Display invalid menu choice message."""
    print("Opzione non valida.")


def display_exit_message() -> None:
    """Display exit message."""
    print("Alla prossima avventura!")


def display_boss_not_found() -> None:
    """Display message when boss not found."""
    print("Il boss non è qui!")


def display_no_enemies_here() -> None:
    """Display message when no enemies in location."""
    print("🚫 Non trovi nemici qui.")


def display_fled_from_boss() -> None:
    """Display message when player flees from boss."""
    print("Sei dovuto fuggire dal boss...")


def display_fled_or_defeated() -> None:
    """Display message when player flees or is defeated."""
    print("💨 Sei dovuto fuggire o sconfitto...")


def display_invalid_location() -> None:
    """Display invalid location message."""
    print("Direzione non valida.")


def display_save_confirmation() -> None:
    """Display save confirmation."""
    # Handled by persistence module
    pass


def display_load_menu() -> str:
    """Display load/new game menu.
    
    Returns:
        User's choice ("1" for load, "2" for new)
    """
    print("📂 Trovato un salvataggio precedente!")
    print("Cosa vuoi fare?")
    print("1) Carica partita   2) Inizia una nuova partita")
    return input("-> ").strip()


def get_player_name(language: str) -> str:
    """Get player name from input.
    
    Args:
        language: Current language ("it" or "en")
    
    Returns:
        Player name or default
    """
    prompt = "Come ti chiami, avventuriero? " if language == "it" else "What is your name, adventurer? "
    default = "Eroe" if language == "it" else "Hero"
    name = input(prompt).strip()
    return name or default
