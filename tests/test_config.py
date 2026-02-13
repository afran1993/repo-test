from src.config import get_config


def test_default_config_values():
    cfg = get_config()
    assert cfg.player.STARTING_HP == 30
    assert cfg.potions.POTION_SMALL == 12
    assert cfg.paths.DATA_DIR == "data"
