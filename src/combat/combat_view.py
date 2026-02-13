from src.combat.cli_adapter import CombatCLIRenderer


class CombatView:
    """Simple UI wrapper around the CLI renderer."""

    def __init__(self, delay_between_events: float = 0.0):
        self.renderer = CombatCLIRenderer(delay_between_events=delay_between_events)

    def display_combat_start(self, player_name: str, enemy_name: str):
        # Render a simple start event via the renderer
        print(f"Combat start: {player_name} vs {enemy_name}")

    def display_actions(self, available_actions):
        for idx, action in enumerate(available_actions, 1):
            print(f"({idx}) {action}")

    def get_player_choice(self) -> str:
        return input('-> ').strip()
