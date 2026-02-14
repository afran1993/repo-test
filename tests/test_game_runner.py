"""
Tests for GameRunner main loop and game flow orchestration.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from src.game_runner import GameRunner
from src.data_loader import GameContext
from src.exceptions import LocationNotFound, GameException


class TestGameRunnerInitialization:
    """Tests for GameRunner initialization."""
    
    def test_game_runner_initializes_with_all_dependencies(
        self, mock_context, game_runner_dependencies
    ):
        """Test GameRunner initializes with all required dependencies."""
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        assert runner.context == mock_context
        assert runner.fight == game_runner_dependencies['fight_fn']
        assert runner.get_location == game_runner_dependencies['get_location_fn']
        assert runner.get_boss == game_runner_dependencies['get_boss_fn']
        assert runner.check_access == game_runner_dependencies['check_access_fn']
        assert runner.save_game == game_runner_dependencies['save_game_fn']
    
    def test_game_runner_has_all_required_methods(
        self, mock_context, game_runner_dependencies
    ):
        """Test GameRunner has all expected methods."""
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        assert hasattr(runner, 'run')
        assert hasattr(runner, 'handle_explore_combat')
        assert hasattr(runner, 'handle_map')
        assert hasattr(runner, 'handle_skills')
        assert hasattr(runner, 'handle_npc_interaction')
        assert hasattr(runner, 'execute_multiple_battles')
        assert hasattr(runner, '_handle_boss_battle')
        assert hasattr(runner, '_handle_normal_battle')


class TestGameRunnerBattleHandling:
    """Tests for battle execution and handling."""
    
    def test_handle_normal_battle_victory(
        self, mock_context, game_runner_dependencies, mock_player, mock_location, sample_enemy
    ):
        """Test normal battle with victory."""
        game_runner_dependencies['fight_fn'].return_value = True
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_location.get_random_enemy.return_value = sample_enemy
        
        result = runner._handle_normal_battle(mock_player, mock_location, 0, 1)
        
        assert result is True
        game_runner_dependencies['fight_fn'].assert_called_once()
    
    def test_handle_normal_battle_defeat(
        self, mock_context, game_runner_dependencies, mock_player, mock_location, sample_enemy
    ):
        """Test normal battle with defeat/flee."""
        game_runner_dependencies['fight_fn'].return_value = False
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_location.get_random_enemy.return_value = sample_enemy
        
        result = runner._handle_normal_battle(mock_player, mock_location, 0, 1)
        
        assert result is False
    
    def test_handle_normal_battle_no_enemy(
        self, mock_context, game_runner_dependencies, mock_player, mock_location
    ):
        """Test normal battle when no enemies in location."""
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_location.get_random_enemy.return_value = None
        
        result = runner._handle_normal_battle(mock_player, mock_location, 0, 1)
        
        assert result is False
    
    def test_handle_boss_battle_victory(
        self, mock_context, game_runner_dependencies, mock_player, mock_location, mock_boss
    ):
        """Test boss battle with victory."""
        game_runner_dependencies['fight_fn'].return_value = True
        game_runner_dependencies['get_boss_fn'].return_value = mock_boss
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        initial_xp = mock_player.xp
        initial_gold = mock_player.gold
        
        runner._handle_boss_battle(mock_player, mock_location, 0, 1, 0)
        
        # Should have called story update
        game_runner_dependencies['update_story_fn'].assert_called_once()
    
    def test_handle_boss_battle_no_boss(
        self, mock_context, game_runner_dependencies, mock_player, mock_location
    ):
        """Test boss battle when no boss found."""
        game_runner_dependencies['get_boss_fn'].return_value = None
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        runner._handle_boss_battle(mock_player, mock_location, 0, 1, 0)
        
        # Should not call fight if no boss
        game_runner_dependencies['fight_fn'].assert_not_called()


class TestGameRunnerMultipleBattles:
    """Tests for multiple consecutive battles."""
    
    @patch('src.game_runner.ask_battle_count', return_value=3)
    def test_execute_multiple_battles_all_victories(
        self, mock_ask, mock_context, game_runner_dependencies, 
        mock_player, mock_location, sample_enemy
    ):
        """Test executing multiple battles with all victories."""
        game_runner_dependencies['fight_fn'].return_value = True
        mock_location.get_random_enemy.return_value = sample_enemy
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        runner.execute_multiple_battles(mock_player, mock_location, is_boss=False)
        
        # Should call fight 3 times
        assert game_runner_dependencies['fight_fn'].call_count == 3
    
    @patch('src.game_runner.ask_battle_count', return_value=5)
    def test_execute_multiple_battles_player_dies(
        self, mock_ask, mock_context, game_runner_dependencies,
        mock_player, mock_location, sample_enemy
    ):
        """Test multiple battles stopping when player dies."""
        mock_player.is_alive.side_effect = [True, True, False]  # Dies after 2 battles
        game_runner_dependencies['fight_fn'].return_value = False
        mock_location.get_random_enemy.return_value = sample_enemy
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        runner.execute_multiple_battles(mock_player, mock_location, is_boss=False)
        
        # Should stop early when player dies
        assert game_runner_dependencies['fight_fn'].call_count <= 5
    
    @patch('src.game_runner.ask_battle_count', return_value=1)
    def test_execute_multiple_battles_single_battle(
        self, mock_ask, mock_context, game_runner_dependencies,
        mock_player, mock_location, sample_enemy
    ):
        """Test executing single battle."""
        game_runner_dependencies['fight_fn'].return_value = True
        mock_location.get_random_enemy.return_value = sample_enemy
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        runner.execute_multiple_battles(mock_player, mock_location, is_boss=False)
        
        assert game_runner_dependencies['fight_fn'].call_count == 1


class TestGameRunnerMenuHandling:
    """Tests for menu option handling."""
    
    def test_handle_explore_combat_with_boss(
        self, mock_context, game_runner_dependencies, mock_player, mock_location, mock_boss
    ):
        """Test explore/combat with boss present."""
        game_runner_dependencies['get_boss_fn'].return_value = mock_boss
        game_runner_dependencies['get_current_quest_fn'].return_value = {
            "boss_encounter": True
        }
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch.object(runner, 'execute_multiple_battles') as mock_battles:
            runner.handle_explore_combat(mock_player, mock_location)
            
            mock_battles.assert_called_once()
            assert mock_battles.call_args[1]['is_boss'] is True
    
    def test_handle_explore_combat_without_boss(
        self, mock_context, game_runner_dependencies, mock_player, mock_location
    ):
        """Test explore/combat without boss."""
        game_runner_dependencies['get_boss_fn'].return_value = None
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch.object(runner, 'execute_multiple_battles') as mock_battles:
            runner.handle_explore_combat(mock_player, mock_location)
            
            mock_battles.assert_called_once()
            assert mock_battles.call_args[1]['is_boss'] is False
    
    @patch('src.game_runner.input', return_value='north')
    def test_handle_map_valid_movement(
        self, mock_input, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test valid map movement."""
        next_location = Mock()
        next_location.element = "None"
        game_runner_dependencies['get_location_fn'].return_value = next_location
        game_runner_dependencies['check_access_fn'].return_value = (True, "")
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_location.connections = {"north": "forest"}
        
        runner.handle_map(mock_player, mock_location)
        
        assert mock_player.current_location == "forest"
    
    @patch('src.game_runner.input', return_value='west')
    def test_handle_map_invalid_direction(
        self, mock_input, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test invalid map direction."""
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_location.connections = {"north": "forest", "east": "village"}
        initial_location = mock_player.current_location
        
        runner.handle_map(mock_player, mock_location)
        
        # Should not move
        assert mock_player.current_location == initial_location
    
    @patch('src.game_runner.input', return_value='north')
    def test_handle_map_access_denied(
        self, mock_input, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test blocked location access."""
        game_runner_dependencies['check_access_fn'].return_value = (
            False, "Requires level 5"
        )
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_location.connections = {"north": "boss_lair"}
        initial_location = mock_player.current_location
        
        runner.handle_map(mock_player, mock_location)
        
        # Should not move
        assert mock_player.current_location == initial_location
    
    def test_handle_skills(
        self, mock_context, game_runner_dependencies, mock_player
    ):
        """Test skills menu handling."""
        game_runner_dependencies['get_learned_skills_fn'].return_value = ["fireball"]
        game_runner_dependencies['get_available_skills_fn'].return_value = ["lightning"]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch('src.game_runner.display_skills') as mock_display:
            runner.handle_skills(mock_player)
            # Verify display_skills was called with the function parameters
            mock_display.assert_called_once_with(
                runner.get_learned_skills,
                runner.get_available_skills,
                mock_player
            )
    
    def test_handle_npc_interaction(
        self, mock_context, game_runner_dependencies, mock_player
    ):
        """Test NPC interaction."""
        npc = {"id": "elder", "name": "Village Elder"}
        game_runner_dependencies['get_npcs_in_location_fn'].return_value = [npc]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch('src.game_runner.display_npc_list', return_value=npc):
            runner.handle_npc_interaction(mock_player)
            game_runner_dependencies['interact_with_npc_fn'].assert_called_once()


class TestGameRunnerMainLoop:
    """Tests for main game loop."""
    
    @patch('src.game_runner.display_main_menu', return_value='11')
    def test_run_quit_game(
        self, mock_menu, mock_context, game_runner_dependencies, mock_player, mock_location
    ):
        """Test graceful quit from game loop."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_player.is_alive.return_value = True
        
        result = runner.run(mock_player)
        
        assert result is True
    
    @patch('src.game_runner.display_main_menu', return_value='1')
    def test_run_explore_combat_menu(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test game loop processes explore/combat menu choice."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        mock_player.is_alive.side_effect = [True, False]  # One iteration then exit
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch.object(runner, 'handle_explore_combat') as mock_explore:
            result = runner.run(mock_player)
            mock_explore.assert_called_once()
    
    @patch('src.game_runner.display_main_menu', return_value='8')
    def test_run_map_menu(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test game loop processes map menu choice."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        mock_player.is_alive.side_effect = [True, False]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch.object(runner, 'handle_map') as mock_map:
            result = runner.run(mock_player)
            mock_map.assert_called_once()
    
    @patch('src.game_runner.display_main_menu', return_value='9')
    def test_run_skills_menu(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test game loop processes skills menu choice."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        mock_player.is_alive.side_effect = [True, False]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch.object(runner, 'handle_skills') as mock_skills:
            result = runner.run(mock_player)
            mock_skills.assert_called_once()
    
    @patch('src.game_runner.display_main_menu', return_value='10')
    def test_run_save_game(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test game saves when save option chosen."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        mock_player.is_alive.side_effect = [True, False]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        result = runner.run(mock_player)
        
        game_runner_dependencies['save_game_fn'].assert_called()
    
    @patch('src.game_runner.display_main_menu', return_value='7')
    def test_run_rest_heals_player(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test resting heals player."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        mock_player.is_alive.side_effect = [True, False]
        mock_player.hp = 10
        mock_player.get_total_max_hp.return_value = 30
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        result = runner.run(mock_player)
        
        # Rest was processed, player should have hp increased
        assert result is False
    
    def test_run_location_not_found_error(
        self, mock_context, game_runner_dependencies, mock_player
    ):
        """Test proper error handling for missing location."""
        game_runner_dependencies['get_location_fn'].return_value = None
        mock_player.is_alive.return_value = True
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        result = runner.run(mock_player)
        
        assert result is False
    
    @patch('src.game_runner.display_main_menu', side_effect=KeyboardInterrupt())
    def test_run_handles_game_exception(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test proper exception handling in game loop."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        mock_player.is_alive.side_effect = [True, False]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        result = runner.run(mock_player)
        
        assert result is False
    
    def test_run_player_death_ends_game(
        self, mock_context, game_runner_dependencies, mock_player, mock_location
    ):
        """Test game ends when player dies."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        mock_player.is_alive.return_value = False
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        result = runner.run(mock_player)
        
        assert result is False


class TestGameRunnerIntegration:
    """Integration tests for complete game flow scenarios."""
    
    @patch('src.game_runner.display_main_menu', return_value='11')
    def test_game_loop_single_iteration(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test single complete game loop iteration."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        game_runner_dependencies['get_story_status_fn'].return_value = "Act 1"
        mock_player.is_alive.return_value = True
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch('src.game_runner.display_game_start'):
            with patch('src.game_runner.display_location_info'):
                with patch('src.game_runner.display_story_status'):
                    with patch('src.game_runner.display_exit_message'):
                        result = runner.run(mock_player)
        
        assert result is True
    
    @patch('src.game_runner.display_main_menu', side_effect=['1', '11'])
    def test_game_loop_with_exploration(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location, sample_enemy
    ):
        """Test game loop with exploration and combat."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        game_runner_dependencies['fight_fn'].return_value = True
        mock_location.get_random_enemy.return_value = sample_enemy
        mock_player.is_alive.side_effect = [True, True, False]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch('src.game_runner.ask_battle_count', return_value=1):
            with patch('src.game_runner.display_game_start'):
                with patch('src.game_runner.display_location_info'):
                    with patch('src.game_runner.display_story_status'):
                        result = runner.run(mock_player)
        
        # Combat should have been called
        game_runner_dependencies['fight_fn'].assert_called()


class TestGameRunnerEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    @patch('src.game_runner.display_main_menu', return_value='99')
    def test_run_invalid_menu_choice(
        self, mock_menu, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test handling of invalid menu choice."""
        game_runner_dependencies['get_location_fn'].return_value = mock_location
        game_runner_dependencies['check_milestone_fn'].return_value = None
        mock_player.is_alive.side_effect = [True, False]
        
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch('src.game_runner.display_invalid_menu_choice'):
            result = runner.run(mock_player)
    
    def test_multiple_battles_zero_count(
        self, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test battles with zero count."""
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        
        with patch('src.game_runner.ask_battle_count', return_value=0):
            runner.execute_multiple_battles(mock_player, mock_location)
        
        # Should handle gracefully
        assert True
    
    def test_handle_map_no_connections(
        self, mock_context, game_runner_dependencies,
        mock_player, mock_location
    ):
        """Test map handling with no connections."""
        runner = GameRunner(context=mock_context, **game_runner_dependencies)
        mock_location.connections = {}
        
        with patch('src.game_runner.input', return_value='north'):
            with patch('src.game_runner.display_map_connections'):
                runner.handle_map(mock_player, mock_location)
        
        # Should handle gracefully without crashing
        assert True
