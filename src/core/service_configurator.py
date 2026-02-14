"""
Service Configurator - Registers and configures all game services.

Sets up the dependency injection container with all required services,
following the proper order of registration and initialization.
"""

import logging
from typing import TYPE_CHECKING

from src.core.service_container import ServiceContainer

if TYPE_CHECKING:
    from src.data_loader import GameContext

logger = logging.getLogger(__name__)


def configure_services(container: ServiceContainer, context: 'GameContext') -> None:
    """
    Configure all game services in the dependency injection container.
    
    Registration strategy:
    - Repositories: Singleton (expensive, reusable)
    - Game data: Singleton (loaded once)
    - Game engines: Factory (stateful, new per use)
    - Configurations: Instance (pre-loaded)
    
    Args:
        container: The ServiceContainer to configure
        context: GameContext containing loaded game data
    
    Raises:
        ValueError: If service registration fails
    """
    
    logger.info("Configuring game services...")
    
    # ============================================================================
    # REPOSITORIES - Singleton (expensive initialization, reused throughout)
    # ============================================================================
    
    logger.debug("Registering repositories...")
    
    container.register_singleton(
        'location_repository',
        lambda: context.get_location_repository()
    )
    
    container.register_singleton(
        'enemy_repository',
        lambda: context.get_enemy_repository()
    )
    
    container.register_singleton(
        'npc_repository',
        lambda: context.get_npc_repository()
    )
    
    container.register_singleton(
        'item_repository',
        lambda: context.get_item_repository()
    )
    
    container.register_singleton(
        'ability_repository',
        lambda: context.get_ability_repository()
    )
    
    # ============================================================================
    # GAME DATA - Singleton
    # ============================================================================
    
    logger.debug("Registering game data...")
    
    container.register_instance(
        'locations_data',
        context.get_locations()
    )
    
    container.register_instance(
        'enemies_data',
        context.get_enemies()
    )
    
    container.register_instance(
        'npcs_data',
        context.get_npcs()
    )
    
    container.register_instance(
        'items_data',
        context.get_items()
    )
    
    container.register_instance(
        'abilities_data',
        context.get_abilities()
    )
    
    container.register_instance(
        'archetypes_data',
        context.get_archetypes()
    )
    
    container.register_instance(
        'quests_data',
        context.get_quests()
    )
    
    # ============================================================================
    # CONFIGURATION - Instance
    # ============================================================================
    
    logger.debug("Registering configuration...")
    
    from src.config.game_config import get_config
    container.register_instance(
        'config',
        get_config()
    )
    
    # ============================================================================
    # GAME ENGINES - Factory (stateful, create new for each use)
    # ============================================================================
    
    logger.debug("Registering game engines...")
    
    from src.combat.combat_engine import CombatEngine
    
    container.register_factory(
        'combat_engine',
        lambda: CombatEngine(
            config=container.resolve('config').combat
        )
    )
    
    from src.combat.damage_engine import DamageEngine
    
    container.register_factory(
        'damage_engine',
        lambda: DamageEngine()
    )
    
    from src.combat.event_engine import EventEngine
    
    container.register_factory(
        'event_engine',
        lambda: EventEngine()
    )
    
    # ============================================================================
    # GAME CONTEXT - Instance
    # ============================================================================
    
    logger.debug("Registering game context...")
    
    container.register_instance(
        'context',
        context
    )
    
    logger.info(f"Services configured successfully. Stats: {container.get_stats()}")


def resolve_from_container(container: ServiceContainer, context: 'GameContext'):
    """
    Resolve main game objects from container.
    
    Creates the GameRunner and other top-level objects with all dependencies
    properly injected.
    
    Args:
        container: Configured ServiceContainer
        context: GameContext
    
    Returns:
        Tuple of (GameRunner, other dependencies)
    """
    from src.game_runner import GameRunner
    from src.story import (
        get_location,
        get_boss_for_location,
        check_location_access,
        check_story_milestone,
        get_current_quest,
        get_story_status,
        get_learned_skills,
        get_available_skills,
        teach_skill,
        update_story_progress,
    )
    from src.npc_system import (
        get_npcs_in_location,
        interact_with_npc,
    )
    from src.persistence import save_game, load_game
    
    logger.debug("Resolving GameRunner with dependencies...")
    
    # Create GameRunner with all dependencies
    runner = GameRunner(
        context=context,
        fight_fn=lambda player, enemy, location, is_boss=False: (
            container.resolve('combat_engine').combat(
                player, enemy, location, is_boss
            )
        ),
        get_location_fn=lambda loc_id: get_location(context, loc_id),
        get_boss_fn=lambda loc_id: get_boss_for_location(context, loc_id),
        check_access_fn=lambda player, loc_id, element: check_location_access(
            player, loc_id, context, element
        ),
        check_milestone_fn=lambda player, loc_id: check_story_milestone(
            player, loc_id, context
        ),
        get_current_quest_fn=lambda player: get_current_quest(player, context),
        get_story_status_fn=lambda player: get_story_status(player, context),
        get_learned_skills_fn=lambda player: get_learned_skills(player),
        get_available_skills_fn=lambda player: get_available_skills(player),
        teach_skill_fn=lambda player, skill: teach_skill(player, skill),
        update_story_fn=lambda player: update_story_progress(player, context),
        get_npcs_in_location_fn=lambda loc_id, npcs: get_npcs_in_location(
            loc_id, npcs
        ),
        interact_with_npc_fn=lambda player, npc, npcs: interact_with_npc(
            player, npc, npcs
        ),
        save_game_fn=lambda player: save_game(player),
    )
    
    logger.info("GameRunner resolved successfully")
    
    return runner
