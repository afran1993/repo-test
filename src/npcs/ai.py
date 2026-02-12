"""Simple NPC AI and scheduler to run basic routines."""
from typing import List


def tick_npcs(npc_list: List, time_of_day: int):
    """Advance NPC schedules. time_of_day is an int (e.g., hour or abstract slot)."""
    movements = []
    for n in npc_list:
        entry = n.tick_routine(time_of_day)
        if entry:
            movements.append((n.id, entry))
            # in a full engine we'd update npc location here (engine should move NPC)
    return movements


def react_to_event(npc, event):
    """Basic reaction: NPC may change behavior or location based on event dict."""
    # event example: {'type':'battle','region':'hearthvale'}
    if event.get('type') == 'battle' and npc.behavior == 'neutral':
        npc.behavior = 'alert'
        return True
    return False
