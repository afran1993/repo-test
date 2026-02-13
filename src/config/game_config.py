from dataclasses import dataclass
from typing import Dict


@dataclass
class CombatConfig:
    BASE_DAMAGE: int = 5
    DAMAGE_VARIANCE: int = 2
    BASE_EVASION: float = 0.1
    EVASION_PER_DEX: float = 0.02
    MAX_EVASION: float = 0.5
    FLEE_CHANCE: float = 0.5
    BOSS_ABILITY_INTERVAL: int = 3


@dataclass
class PotionConfig:
    POTION_SMALL: int = 12
    POTION_MEDIUM: int = 25
    POTION_STRONG: int = 50
    MANA_POTION: int = 20
    MANA_POTION_STRONG: int = 50


@dataclass
class PlayerConfig:
    STARTING_HP: int = 30
    STARTING_ATK: int = 6
    STARTING_DEX: int = 5
    STARTING_GOLD: int = 0
    HP_PER_LEVEL: int = 6
    ATK_PER_LEVEL: int = 2
    DEX_PER_LEVEL: int = 1
    XP_PER_LEVEL: int = 12
    STARTING_MANA: int = 20
    STARTING_MAX_MANA: int = 20


@dataclass
class PathConfig:
    DATA_DIR: str = "data"
    LOCALES_DIR: str = "locales"
    SAVE_FILE: str = "save.json"

    @property
    def locations_file(self) -> str:
        return f"{self.DATA_DIR}/locations.json"

    @property
    def enemies_file(self) -> str:
        return f"{self.DATA_DIR}/enemies.json"


class GameConfig:
    def __init__(self):
        self.combat = CombatConfig()
        self.potions = PotionConfig()
        self.player = PlayerConfig()
        self.paths = PathConfig()

    @classmethod
    def from_dict(cls, data: Dict) -> "GameConfig":
        cfg = cls()
        # Basic merging for known sections
        if 'combat' in data:
            for k, v in data['combat'].items():
                if hasattr(cfg.combat, k):
                    setattr(cfg.combat, k, v)
        if 'player' in data:
            for k, v in data['player'].items():
                if hasattr(cfg.player, k):
                    setattr(cfg.player, k, v)
        if 'paths' in data:
            for k, v in data['paths'].items():
                if hasattr(cfg.paths, k):
                    setattr(cfg.paths, k, v)
        return cfg


_config = GameConfig()


def get_config() -> GameConfig:
    return _config
