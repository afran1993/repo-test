"""
NPC System - Dialogue and NPC interaction management.

Handles NPC dialogue, branching conversations, and NPC interaction.
"""

from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def start_dialogue(player: Any, npc_id: str, npcs_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Start a dialogue with an NPC.
    
    Args:
        player: Player object
        npc_id: ID of the NPC
        npcs_data: Dictionary of NPCs data
    
    Returns:
        Dialogue dict or None
    """
    from src.story import has_skill
    
    npc = None
    for n in npcs_data.get("npcs", []):
        if n.get("id") == npc_id:
            npc = n
            break
    
    if not npc:
        logger.debug(f"NPC not found: {npc_id}")
        return None
    
    dialogs = npc.get("dialogs", [])
    if not dialogs:
        logger.debug(f"No dialogs for NPC: {npc_id}")
        return None
    
    # Find appropriate dialogue based on story state
    available_dialog = None
    for dialog in dialogs:
        required_skill = dialog.get("requires_skill")
        required_act = dialog.get("requires_act")
        
        # Check skill requirement
        if required_skill and not has_skill(player, required_skill):
            continue
        
        # Check story requirement
        if required_act and player.story_progress != required_act:
            continue
        
        # Check previous choices
        required_choice = dialog.get("requires_choice")
        if required_choice:
            if player.dialogue_choices.get(npc_id) != required_choice:
                continue
        
        # This dialogue is available
        available_dialog = dialog
        break
    
    if not available_dialog:
        available_dialog = dialogs[0] if dialogs else None
    
    logger.debug(f"Starting dialogue with {npc_id}")
    return available_dialog


def display_dialogue(dialog: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Display a dialogue with options.
    
    Args:
        dialog: Dialogue dict
    
    Returns:
        List of options or None
    """
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


def execute_dialogue_choice(
    player: Any,
    choice: Dict[str, Any],
    npc_id: str,
    npcs_data: Dict[str, Any]
) -> str:
    """
    Execute the consequences of a dialogue choice.
    
    Args:
        player: Player object
        choice: Choice dict
        npc_id: ID of the NPC
        npcs_data: Dictionary of NPCs data
    
    Returns:
        Consequence message
    """
    from src.story import teach_skill
    
    if not choice:
        return ""
    
    consequence = ""
    
    # Teach skill if specified
    if "teaches_skill" in choice:
        skill_name = choice["teaches_skill"]
        success, message = teach_skill(player, skill_name)
        if success:
            consequence += f"\n{message}\n"
    
    # Update story
    if "updates_story" in choice:
        player.story_progress = choice["updates_story"]
        player.story_stage = 0
        consequence += f"\n✦ La storia avanza! ✦\n"
        logger.info(f"Story updated to {choice['updates_story']}")
    
    # Modify XP
    if "xp_reward" in choice:
        player.gain_xp(choice["xp_reward"])
        consequence += f"Guadagni {choice['xp_reward']} XP!\n"
    
    # Modify gold
    if "gold_reward" in choice:
        player.gold += choice["gold_reward"]
        consequence += f"Guadagni {choice['gold_reward']} gold!\n"
    
    # Save choice
    player.dialogue_choices[npc_id] = choice.get("id")
    logger.debug(f"Dialogue choice saved for {npc_id}")
    
    return consequence


def get_npcs_in_location(location_id: str, npcs_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get all NPCs at a specific location.
    
    Args:
        location_id: ID of the location
        npcs_data: Dictionary of NPCs data
    
    Returns:
        List of NPCs at the location
    """
    npcs_list = []
    for npc in npcs_data.get("npcs", []):
        if npc.get("location") == location_id:
            npcs_list.append(npc)
    return npcs_list


def interact_with_npc(
    player: Any,
    npc: Dict[str, Any],
    npcs_data: Dict[str, Any]
) -> None:
    """
    Interact with an NPC through branching dialogue.
    
    Args:
        player: Player object
        npc: NPC dict
        npcs_data: Dictionary of NPCs data
    """
    from src.story import has_skill
    
    dialog = start_dialogue(player, npc.get("id"), npcs_data)
    
    if not dialog:
        print(f"{npc.get('name', 'Sconosciuto')}: ...")
        return
    
    options = display_dialogue(dialog)
    
    if not options:
        print(f"{npc.get('name', 'Sconosciuto')}: Buona fortuna, viaggiatore.")
        return
    
    # Show options
    choice_num = input("Scegli: ").strip()
    
    try:
        choice_idx = int(choice_num) - 1
        if choice_idx == len(options):
            print("Ti allontani...")
            return
        elif 0 <= choice_idx < len(options):
            choice = options[choice_idx]
            
            # Check if choice requires a skill
            if "requires_skill" in choice:
                required_skill = choice["requires_skill"]
                if not has_skill(player, required_skill):
                    print(f"\n{npc.get('name', 'Sconosciuto')}: Mi dispiace, ma devi prima imparare {required_skill}!")
                    return
            
            # Execute choice consequences
            consequence = execute_dialogue_choice(player, choice, npc.get("id"), npcs_data)
            
            # Show NPC response
            print(f"\n{npc.get('name', 'Sconosciuto')}:")
            print(choice.get("response", ""))
            
            if consequence:
                print(consequence)
            
            logger.info(f"NPC interaction completed with {npc.get('id')}")
        else:
            print("Scelta non valida.")
    except ValueError:
        print("Scelta non valida.")
        logger.warning("Invalid choice in NPC dialogue")
