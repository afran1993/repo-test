"""Quest generator: create modular quests (fetch, kill, escort, explore)."""
import random
from src.quests.quest import Quest


def generate_fetch_quest(region: str, area: str, level: int = 1) -> Quest:
    item = random.choice(['Ancient Relic', 'Herbal Bundle', 'Lost Letter'])
    stages = [f"Talk to the quest giver in {area}", f"Find the {item} in nearby ruins", f"Return the {item}"]
    q = Quest(f"fetch_{random.randint(1000,9999)}", f"Retrieve {item}", f"A local requests a {item}.", stages=stages, reward={'gold': 20 + level*5})
    return q


def generate_kill_quest(region: str, area: str, level: int = 1) -> Quest:
    target = random.choice(['Worg', 'Bandit Leader', 'Cave Troll'])
    stages = [f"Talk to the quest giver in {area}", f"Defeat the {target}", f"Return to the quest giver"]
    q = Quest(f"kill_{random.randint(1000,9999)}", f"Eliminate {target}", f"Locals want the {target} dealt with.", stages=stages, reward={'gold': 30 + level*10})
    return q


def generate_branching_quest(region: str, area: str, level: int = 1) -> Quest:
    """Generate a quest with multiple solution approaches: combat, stealth, or negotiation."""
    target = random.choice(['Worg', 'Bandit Leader', 'Cave Troll'])
    stages = [f"Talk to quest giver in {area}", f"Resolve the {target} problem (multiple approaches)", f"Report back"]
    q = Quest(f"branch_{random.randint(1000,9999)}", f"Resolve: {target}", f"A problem involving {target} near {area}.", stages=stages,
              reward={'gold': 40 + level*10},)
    # meta describing possible solutions
    q.solutions = ['combat', 'stealth', 'negotiate']
    return q
