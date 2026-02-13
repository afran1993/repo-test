#!/usr/bin/env python3
"""
Main entry point for RPG Game.

Handles command-line parsing, game initialization, and startup.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add repo root to path
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, REPO_ROOT)

from src.data_loader import GameContext
from src.game_runner import GameRunner
from src.persistence import save_game, load_game
from src.players import Player
from src.i18n import i18n
from src.cli import (
    choose_language,
    get_player_name,
    display_load_menu,
)

# Import all the functions we need for GameRunner
from src.story import (
    check_story_milestone,
    get_story_status,
    get_boss_for_location,
    get_current_main_quest,
    update_story_progress,
    get_learned_skills,
    get_available_skills,
    teach_skill,
    check_location_access,
)
from src.npc_system import (
    get_npcs_in_location,
    interact_with_npc,
)
from src.models import Location, Enemy, get_location, set_locations_data, set_enemies_data
from src.combat import CombatEngine, create_fight_with_engine
from src.utils import get_element_modifier, get_enemy_emoji


def apply_boss_ability(player, boss, ability_name):
    """Apply boss special ability."""
    from src.combat.abilities import apply_ability
    return apply_ability(boss, player, ability_name)


def create_fight_wrapper(enemy_emojis=None):
    """Create a fight orchestration function.
    
    Args:
        enemy_emojis: Dict of enemy emojis (optional)
    
    Returns:
        Fight function
    """
    def fight(player, enemy, current_location=None, is_boss=False):
        """Execute a fight between player and enemy.
        
        Args:
            player: Player object
            enemy: Enemy object
            current_location: Current location
            is_boss: Whether this is a boss fight
        
        Returns:
            True if player wins, False otherwise
        """
        engine = CombatEngine(
            player=player,
            enemy=enemy,
            element_modifier_fn=get_element_modifier,
            apply_ability_fn=apply_boss_ability,
            is_boss=is_boss,
            current_location=current_location,
        )
        
        emoji_fn = enemy_emojis or get_enemy_emoji
        victory = create_fight_with_engine(
            engine=engine,
            player=player,
            enemy=enemy,
            emoji_getter=emoji_fn,
        )
        
        if victory:
            player.gold += enemy.gold_reward
            leveled = player.gain_xp(enemy.xp_reward)
            if leveled:
                print(f"🎉 Sei salito al livello {player.level}! HP ripristinati.")
            save_game(player)
            return True
        else:
            from src.persistence import hospital
            hospital(player)
            return False
    
    return fight


def create_game_runner(context: GameContext) -> GameRunner:
    """Create a GameRunner instance with all dependencies.
    
    Args:
        context: GameContext
    
    Returns:
        GameRunner instance
    """
    fight_fn = create_fight_wrapper()
    
    return GameRunner(
        context=context,
        fight_fn=fight_fn,
        get_location_fn=get_location,
        get_boss_fn=get_boss_for_location,
        check_access_fn=check_location_access,
        check_milestone_fn=check_story_milestone,
        get_current_quest_fn=get_current_main_quest,
        get_story_status_fn=get_story_status,
        get_learned_skills_fn=get_learned_skills,
        get_available_skills_fn=get_available_skills,
        teach_skill_fn=teach_skill,
        update_story_fn=update_story_progress,
        get_npcs_in_location_fn=get_npcs_in_location,
        interact_with_npc_fn=interact_with_npc,
        save_game_fn=save_game,
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RPG Game")
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run game in demo mode'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info("Starting RPG Game")
    
    try:
        # Initialize game context
        context = GameContext()
        context.load_all()
        logger.info("Game data loaded successfully")
        
        # Set module-level data for backward compatibility
        set_locations_data(context.get_locations())
        set_enemies_data(context.get_enemies())
        
        # Handle demo mode
        if args.demo:
            logger.info("Running in demo mode")
            from tools.auto_playtest import demo
            demo()
            return
        
        # Check for existing save
        save_path = os.path.join(REPO_ROOT, "save.json")
        if os.path.exists(save_path):
            choice = display_load_menu()
            
            if choice == "1":
                player = load_game()
                if player:
                    i18n.set_locale(player.language)
                    logger.info(f"Game loaded: {player.name}")
                else:
                    logger.error("Failed to load game")
                    return
            else:
                player = _create_new_player()
        else:
            player = _create_new_player()
        
        # Run game
        runner = create_game_runner(context)
        runner.run(player)
        
        logger.info("Game ended normally")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


def _create_new_player() -> Player:
    """Create a new player.
    
    Returns:
        New player object
    """
    language = choose_language()
    i18n.set_locale(language)
    
    name = get_player_name(language)
    player = Player(name)
    player.language = language
    
    logger.info(f"New player created: {name} ({language})")
    return player


if __name__ == "__main__":
    main()
