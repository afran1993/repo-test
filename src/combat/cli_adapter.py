"""
CLI Adapter for Combat Engine

Translates CombatEvent objects into formatted console output.
"""

import time
from src.combat.event_engine import CombatEvent, CombatEventType


class CombatCLIRenderer:
    """Renders combat events to terminal with emoji and colors."""

    def __init__(self, delay_between_events: float = 0.2):
        """
        Initialize renderer.
        
        Args:
            delay_between_events: Time to wait between rendering events (seconds)
        """
        self.delay = delay_between_events

    def render(self, event: CombatEvent, emoji_map: dict = None):
        """
        Render a single combat event.
        
        Args:
            event: CombatEvent to render
            emoji_map: Optional dict mapping enemy IDs to emojis
        """
        if emoji_map is None:
            emoji_map = {}

        message = self._format_message(event, emoji_map)
        print(message)
        if self.delay > 0:
            time.sleep(self.delay)

    def render_batch(self, events: list, emoji_map: dict = None):
        """
        Render multiple events in sequence.
        
        Args:
            events: List of CombatEvent objects
            emoji_map: Optional emoji mapping
        """
        for event in events:
            self.render(event, emoji_map)

    def _format_message(self, event: CombatEvent, emoji_map: dict) -> str:
        """Format event message with appropriate emoji and styling."""
        typ = event.type

        if typ == CombatEventType.COMBAT_START:
            return f"⚔️  Combat Start: {event.message}"

        elif typ == CombatEventType.PLAYER_TURN:
            return f"\n--- Player Turn ---"

        elif typ == CombatEventType.PLAYER_ATTACK:
            return f"🗡️  {event.message}"

        elif typ == CombatEventType.PLAYER_EVADED:
            return f"🛡️  {event.message}"

        elif typ == CombatEventType.PLAYER_TOOK_DAMAGE:
            return f"💧 {event.message}"

        elif typ == CombatEventType.PLAYER_USED_POTION:
            return f"🧪 {event.message}"

        elif typ == CombatEventType.PLAYER_FLED_SUCCESS:
            return f"💨 {event.message}"

        elif typ == CombatEventType.PLAYER_FLED_FAIL:
            return f"❌ {event.message}"

        elif typ == CombatEventType.ENEMY_TURN:
            return f"\n--- {event.actor}'s Turn ---"

        elif typ == CombatEventType.ENEMY_ATTACK:
            return f"⚡ {event.message}"

        elif typ == CombatEventType.ENEMY_EVADED:
            return f"🛡️  {event.message}"

        elif typ == CombatEventType.ENEMY_ABILITY:
            effect = event.metadata.get("effect", "")
            return f"💥 >> {event.message}\n   {effect}"

        elif typ == CombatEventType.ELEMENT_ADVANTAGE:
            return f"  >>> ✨ {event.message} ✨"

        elif typ == CombatEventType.ELEMENT_DISADVANTAGE:
            return f"  >>> ❌ {event.message}"

        elif typ == CombatEventType.COMBAT_VICTORY:
            gold = event.metadata.get("gold_reward", 0)
            xp = event.metadata.get("xp_reward", 0)
            return f"✨ {event.message}! ✨\n⭐ Gained {xp} XP and {gold} gold."

        elif typ == CombatEventType.COMBAT_DEFEAT:
            return f"☠️  {event.message}"

        elif typ == CombatEventType.LEVEL_UP:
            return f"🎉 {event.message}"

        else:
            return str(event.message)


def create_fight_with_engine(engine, player, enemy, emoji_getter=None):
    """
    Run combat using the event-driven engine with CLI feedback.
    
    This is a bridge function that maintains compatibility with the old fight() interface.
    
    Args:
        engine: CombatEngine instance
        player: Player object
        enemy: Enemy object
        emoji_getter: Optional function to get emoji for enemy
        
    Returns:
        True if player won, False otherwise
    """
    renderer = CombatCLIRenderer(delay_between_events=0.2)
    
    # Render combat start
    for event in engine.events:
        renderer.render(event)
    
    # Combat loop
    while not engine.is_finished():
        print()
        print(f"  {player.status()}")
        enemy_emoji = emoji_getter(enemy) if emoji_getter else "👹"
        boss_str = " [BOSS]" if engine.is_boss else ""
        print(f"  Enemy: {enemy_emoji} {enemy.name}{boss_str} ({enemy.element}) - HP {enemy.hp}/{enemy.max_hp}")
        print()
        print("  Actions: (1)Attack  (2)Potion  (3)Flee")
        
        choice = input("  -> ").strip()
        
        # Convert CLI choice to engine action
        if choice == "1":
            action = "attack"
        elif choice == "2":
            potion_choice = _show_potion_menu(player)
            if potion_choice:
                action = f"potion:{potion_choice}"
            else:
                print("  No potions available!")
                continue
        elif choice == "3":
            action = "flee"
        else:
            print("  Invalid choice.")
            continue
        
        # Execute turn
        events = engine.step(action)
        renderer.render_batch(events)
        
        # Check for flee
        if action == "flee" and engine.is_finished() and not engine.is_won():
            # Fled successfully
            return False
    
    return engine.is_won()


def _show_potion_menu(player):
    """Show potion menu and return selected potion type or None."""
    available = [(k, v) for k, v in player.potions.items() if v > 0]
    
    if not available:
        return None
    
    print("  Available potions:")
    for i, (potion_type, count) in enumerate(available, 1):
        print(f"    ({i}) {potion_type.replace('_', ' ').title()} x{count}")
    print(f"    ({len(available) + 1}) Cancel")
    
    while True:
        try:
            choice = int(input("  Choose potion: ").strip())
            if 1 <= choice <= len(available):
                return available[choice - 1][0]
            elif choice == len(available) + 1:
                return None
        except ValueError:
            pass
        print("  Invalid choice.")
