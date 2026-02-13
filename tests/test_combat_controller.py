from src.combat.event_engine import CombatEngine
from src.combat.combat_controller import CombatController


class DummyChar:
    def __init__(self, name, hp=10):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.potions = {}
        self.abilities = []

    def is_alive(self):
        return self.hp > 0


def test_controller_runs_with_finished_engine():
    player = DummyChar('Hero', hp=10)
    enemy = DummyChar('Slime', hp=0)

    # create engine but mark finished to avoid interactive loop
    engine = CombatEngine(player=player, enemy=enemy, element_modifier_fn=lambda a, b: 1.0)
    engine.finished = True
    engine.victory = True

    controller = CombatController(engine=engine)
    result = controller.run_fight(player, enemy)
    assert result is True
