"""
Game runner - Main game loop orchestration.

Handles game flow, battle orchestration, and main game loop.
"""

import time
import logging
from typing import Callable, Optional, Any

from src.data_loader import GameContext
from src.utils import get_element_modifier, get_enemy_emoji
from src.models import get_location
from src.cli import (
    display_main_menu,
    display_character_status,
    display_location_info,
    display_story_status,
    display_inventory,
    display_skills,
    display_map_connections,
    display_npc_list,
    display_battle_results,
    display_game_start,
    display_story_milestone,
    display_boss_victory,
    display_enemy_defeat,
    display_level_up,
    display_battle_progress,
    display_rest_message,
    display_invalid_menu_choice,
    display_exit_message,
    display_boss_not_found,
    display_no_enemies_here,
    display_fled_or_defeated,
    display_invalid_location,
    ask_battle_count,
)

logger = logging.getLogger(__name__)


class GameRunner:
    """Orchestrates main game loop and battle flow."""
    
    def __init__(
        self,
        context: GameContext,
        fight_fn: Callable,
        get_location_fn: Callable,
        get_boss_fn: Callable,
        check_access_fn: Callable,
        check_milestone_fn: Callable,
        get_current_quest_fn: Callable,
        get_story_status_fn: Callable,
        get_learned_skills_fn: Callable,
        get_available_skills_fn: Callable,
        teach_skill_fn: Callable,
        update_story_fn: Callable,
        get_npcs_in_location_fn: Callable,
        interact_with_npc_fn: Callable,
        save_game_fn: Callable,
    ):
        """Initialize game runner with dependencies.
        
        Args:
            context: GameContext containing all data
            fight_fn: Combat orchestration function
            get_location_fn: Function to get location by ID
            get_boss_fn: Function to get boss for location
            check_access_fn: Function to check location access
            check_milestone_fn: Function to check story milestones
            get_current_quest_fn: Function to get current quest
            get_story_status_fn: Function to get story status string
            get_learned_skills_fn: Function to get learned skills
            get_available_skills_fn: Function to get available skills
            teach_skill_fn: Function to teach skill
            update_story_fn: Function to update story progress
            get_npcs_in_location_fn: Function to get NPCs at location
            interact_with_npc_fn: Function to interact with NPC
            save_game_fn: Function to save game
        """
        self.context = context
        self.fight = fight_fn
        self.get_location = get_location_fn
        self.get_boss = get_boss_fn
        self.check_access = check_access_fn
        self.check_milestone = check_milestone_fn
        self.get_current_quest = get_current_quest_fn
        self.get_story_status = get_story_status_fn
        self.get_learned_skills = get_learned_skills_fn
        self.get_available_skills = get_available_skills_fn
        self.teach_skill = teach_skill_fn
        self.update_story = update_story_fn
        self.get_npcs_in_location = get_npcs_in_location_fn
        self.interact_with_npc = interact_with_npc_fn
        self.save_game = save_game_fn
    
    def execute_multiple_battles(
        self,
        player: Any,
        location: Any,
        is_boss: bool = False
    ) -> None:
        """Execute multiple consecutive battles.
        
        Args:
            player: Player object
            location: Current location
            is_boss: Whether this is a boss fight
        """
        battle_count = ask_battle_count()
        battles_won = 0
        
        for i in range(battle_count):
            if not player.is_alive():
                break
            
            if is_boss:
                self._handle_boss_battle(player, location, i, battle_count, battles_won)
                battles_won += 1 if player.is_alive() else 0
            else:
                result = self._handle_normal_battle(player, location, i, battle_count)
                if result:
                    battles_won += 1
                else:
                    break
            
            time.sleep(0.5)
        
        display_battle_results(battles_won, battle_count, player)
    
    def _handle_boss_battle(
        self,
        player: Any,
        location: Any,
        battle_num: int,
        total_battles: int,
        battles_won: int
    ) -> None:
        """Handle a single boss battle.
        
        Args:
            player: Player object
            location: Current location
            battle_num: Current battle number
            total_battles: Total battles
            battles_won: Battles won so far
        """
        boss = self.get_boss(player.current_location)
        if not boss:
            display_boss_not_found()
            return
        
        print(f"\n[Boss Battle {battle_num+1}/{total_battles}]")
        print(f"Incontri: {boss.name}!")
        time.sleep(0.5)
        
        result = self.fight(player, boss, location, is_boss=True)
        if result:
            display_boss_victory(boss, boss.xp_reward * 2, boss.gold_reward * 2)
            player.gold += boss.xp_reward * 2
            player.gain_xp(boss.xp_reward * 2)
            self.update_story(player)
        else:
            print("Sei dovuto fuggire dal boss...")
    
    def _handle_normal_battle(
        self,
        player: Any,
        location: Any,
        battle_num: int,
        total_battles: int
    ) -> bool:
        """Handle a single normal battle.
        
        Args:
            player: Player object
            location: Current location
            battle_num: Current battle number
            total_battles: Total battles
        
        Returns:
            True if won, False if fled
        """
        enemy = location.get_random_enemy()
        if not enemy:
            display_no_enemies_here()
            return False
        
        print(f"\n[Battaglia {battle_num+1}/{total_battles}] {enemy.name} appare!")
        time.sleep(0.3)
        
        result = self.fight(player, enemy, location)
        if result:
            display_enemy_defeat(enemy, enemy.xp_reward, enemy.gold_reward)
            display_battle_progress(battle_num, total_battles, battle_num + 1)
            return True
        else:
            display_fled_or_defeated()
            return False
    
    def handle_explore_combat(self, player: Any, location: Any) -> None:
        """Handle explore/combat menu option.
        
        Args:
            player: Player object
            location: Current location
        """
        boss = self.get_boss(player.current_location)
        if boss:
            quest = self.get_current_quest(player)
            is_boss = quest and quest.get("boss_encounter")
            self.execute_multiple_battles(player, location, is_boss=is_boss)
        else:
            self.execute_multiple_battles(player, location, is_boss=False)
    
    def handle_map(self, player: Any, location: Any) -> None:
        """Handle map navigation.
        
        Args:
            player: Player object
            location: Current location
        """
        display_map_connections(location, player, self.check_access)
        
        next_loc = input("Vai verso: ").strip().lower()
        if next_loc in location.connections:
            next_location = self.get_location(location.connections[next_loc])
            can_access, error_msg = self.check_access(
                player,
                location.connections[next_loc],
                next_location.element if next_location else None
            )
            
            if can_access:
                player.current_location = location.connections[next_loc]
                logger.info(f"Player moved to {player.current_location}")
                print(f"Ti sposti verso {next_loc}...")
            else:
                print(f"Non puoi andare there: {error_msg}")
        else:
            display_invalid_location()
    
    def handle_skills(self, player: Any) -> None:
        """Handle skills menu.
        
        Args:
            player: Player object
        """
        display_skills(
            self.get_learned_skills,
            self.get_available_skills,
            player
        )
    
    def handle_npc_interaction(self, player: Any) -> None:
        """Handle NPC interaction.
        
        Args:
            player: Player object
        """
        npcs_here = self.get_npcs_in_location(player.current_location, self.context.get_npcs())
        npc = display_npc_list(npcs_here)
        
        if npc:
            self.interact_with_npc(player, npc, self.context.get_npcs())
    
    def run(self, player: Any) -> bool:
        """Main game loop.
        
        Args:
            player: Player object
        
        Returns:
            True if game ended normally, False otherwise
        """
        display_game_start(player)
        
        while player.is_alive():
            location = self.get_location(player.current_location)
            if not location:
                logger.error(f"Location not found: {player.current_location}")
                return False
            
            # Check for story milestones
            milestone = self.check_milestone(player, player.current_location)
            if milestone:
                display_story_milestone(milestone)
            
            # Display UI
            display_location_info(location, player)
            display_story_status(self.get_story_status, player)
            
            # Get user input
            cmd = display_main_menu()
            logger.debug(f"Menu choice: {cmd}")
            
            # Handle menu choices
            if cmd == "1":
                self.handle_explore_combat(player, location)
            elif cmd == "2":
                # Treasure - delegated to imported function
                from src.menus import open_treasure
                open_treasure(player, location)
            elif cmd == "3":
                from src.menus import equip_weapon_menu
                equip_weapon_menu(player)
            elif cmd == "4":
                from src.menus import accessories_menu
                accessories_menu(player)
            elif cmd == "5":
                display_inventory(player)
            elif cmd == "6":
                self.handle_npc_interaction(player)
            elif cmd == "7":
                heal = min(player.get_total_max_hp() - player.hp, 15)
                player.hp += heal
                display_rest_message(heal)
            elif cmd == "8":
                self.handle_map(player, location)
            elif cmd == "9":
                self.handle_skills(player)
            elif cmd == "10":
                self.save_game(player)
                logger.info("Game saved")
            elif cmd == "11":
                display_exit_message()
                return True
            else:
                display_invalid_menu_choice()
        
        return False
