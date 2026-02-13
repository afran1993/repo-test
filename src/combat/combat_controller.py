from src.combat.event_engine import CombatEngine
from src.combat.cli_adapter import create_fight_with_engine


class CombatController:
    """Orchestrates combat using a CombatEngine and a view/renderer.

    The controller composes the engine and the view; for CLI usage it
    currently delegates to the existing `create_fight_with_engine` helper.
    """

    def __init__(self, engine: CombatEngine, view=None):
        self.engine = engine
        self.view = view

    def run_fight(self, player, enemy):
        # Delegate to existing adapter which renders CLI events
        return create_fight_with_engine(self.engine, player, enemy)
