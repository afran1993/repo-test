"""
Tests for CLI module - User interface and interaction.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.cli import (
    choose_language,
    ask_battle_count,
    display_character_status,
    display_location_info,
    display_story_status,
    display_inventory,
    display_skills,
    display_main_menu,
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
    display_fled_from_boss,
    display_fled_or_defeated,
    display_invalid_location,
    display_load_menu,
    get_player_name,
)


class TestLanguageSelection:
    """Tests for language selection."""
    
    @patch('src.cli.input', return_value='1')
    @patch('src.cli.print')
    def test_choose_language_italian(self, mock_print, mock_input):
        """Test Italian language selection."""
        result = choose_language()
        assert result == "it"
    
    @patch('src.cli.input', return_value='2')
    @patch('src.cli.print')
    def test_choose_language_english(self, mock_print, mock_input):
        """Test English language selection."""
        result = choose_language()
        assert result == "en"
    
    @patch('src.cli.input', return_value='invalid')
    @patch('src.cli.print')
    def test_choose_language_invalid_defaults_to_italian(self, mock_print, mock_input):
        """Test invalid choice defaults to Italian."""
        result = choose_language()
        assert result == "it"
    
    @patch('src.cli.input', return_value='')
    @patch('src.cli.print')
    def test_choose_language_empty_input(self, mock_print, mock_input):
        """Test empty input defaults to Italian."""
        result = choose_language()
        assert result == "it"


class TestBattleCount:
    """Tests for battle count input."""
    
    @patch('src.cli.input', return_value='5')
    @patch('src.cli.print')
    def test_ask_battle_count_valid(self, mock_print, mock_input):
        """Test valid battle count input."""
        result = ask_battle_count()
        assert result == 5
    
    @patch('src.cli.input', return_value='1')
    @patch('src.cli.print')
    def test_ask_battle_count_minimum(self, mock_print, mock_input):
        """Test minimum battle count (1)."""
        result = ask_battle_count()
        assert result == 1
    
    @patch('src.cli.input', return_value='100')
    @patch('src.cli.print')
    def test_ask_battle_count_large_number(self, mock_print, mock_input):
        """Test large battle count."""
        result = ask_battle_count()
        assert result == 100
    
    @patch('src.cli.input', return_value='0')
    @patch('src.cli.print')
    def test_ask_battle_count_zero_becomes_one(self, mock_print, mock_input):
        """Test zero count becomes 1."""
        result = ask_battle_count()
        assert result == 1
    
    @patch('src.cli.input', return_value='-5')
    @patch('src.cli.print')
    def test_ask_battle_count_negative(self, mock_print, mock_input):
        """Test negative count defaults to 1."""
        result = ask_battle_count()
        assert result == 1
    
    @patch('src.cli.input', side_effect=['invalid', '3'])
    @patch('src.cli.print')
    def test_ask_battle_count_invalid_input(self, mock_print, mock_input):
        """Test invalid input defaults to 1."""
        result = ask_battle_count()
        assert result == 1
    
    @patch('src.cli.input', return_value='  10  ')
    @patch('src.cli.print')
    def test_ask_battle_count_whitespace(self, mock_print, mock_input):
        """Test battle count with extra whitespace."""
        result = ask_battle_count()
        assert result == 10


class TestPlayerNameInput:
    """Tests for player name input."""
    
    @patch('src.cli.input', return_value='Aragorn')
    @patch('src.cli.print')
    def test_get_player_name_italian(self, mock_print, mock_input):
        """Test getting player name in Italian."""
        result = get_player_name("it")
        assert result == "Aragorn"
    
    @patch('src.cli.input', return_value='Legolas')
    @patch('src.cli.print')
    def test_get_player_name_english(self, mock_print, mock_input):
        """Test getting player name in English."""
        result = get_player_name("en")
        assert result == "Legolas"
    
    @patch('src.cli.input', return_value='')
    @patch('src.cli.print')
    def test_get_player_name_empty_italian_default(self, mock_print, mock_input):
        """Test empty name defaults to Italian 'Eroe'."""
        result = get_player_name("it")
        assert result == "Eroe"
    
    @patch('src.cli.input', return_value='')
    @patch('src.cli.print')
    def test_get_player_name_empty_english_default(self, mock_print, mock_input):
        """Test empty name defaults to English 'Hero'."""
        result = get_player_name("en")
        assert result == "Hero"
    
    @patch('src.cli.input', return_value='  ChampionX9  ')
    @patch('src.cli.print')
    def test_get_player_name_whitespace_trimmed(self, mock_print, mock_input):
        """Test player name whitespace is trimmed."""
        result = get_player_name("it")
        assert result == "ChampionX9"


class TestDisplayFunctions:
    """Tests for various display functions."""
    
    @patch('src.cli.print')
    def test_display_character_status(self, mock_print, mock_player):
        """Test character status display."""
        mock_player.status = Mock(return_value="TestHero Lvl 1 | 30/30 HP")
        
        display_character_status(mock_player)
        
        mock_player.status.assert_called_once()
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_location_info(self, mock_print, mock_player, mock_location):
        """Test location info display."""
        mock_location.describe = Mock(return_value="A peaceful village")
        mock_player.status = Mock(return_value="Status")
        
        display_location_info(mock_location, mock_player)
        
        mock_location.describe.assert_called_once()
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_story_status(self, mock_print, mock_player):
        """Test story status display."""
        story_fn = Mock(return_value="Act 1: Beginning")
        
        display_story_status(story_fn, mock_player)
        
        story_fn.assert_called_once_with(mock_player)
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_inventory_empty(self, mock_print, mock_player):
        """Test empty inventory display."""
        mock_player.inventory = []
        
        display_inventory(mock_player)
        
        assert mock_print.called
        # Check that empty message was printed
        calls_str = str(mock_print.call_args_list)
        assert "vuoto" in calls_str.lower() or "empty" in calls_str.lower()
    
    @patch('src.cli.print')
    def test_display_inventory_with_items(self, mock_print, mock_player):
        """Test inventory display with items."""
        mock_player.inventory = [
            {"name": "Wooden Sword", "id": "sword_1"},
            {"name": "Healing Potion", "id": "potion_1"}
        ]
        
        display_inventory(mock_player)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_skills(self, mock_print, mock_player):
        """Test skills display."""
        get_learned_fn = Mock(return_value=["Fireball", "Heal"])
        get_available_fn = Mock(return_value=["Lightning", "Ice"])
        
        display_skills(get_learned_fn, get_available_fn, mock_player)
        
        get_learned_fn.assert_called_once()
        get_available_fn.assert_called_once()
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_skills_none_learned(self, mock_print, mock_player):
        """Test skills display with no learned skills."""
        get_learned_fn = Mock(return_value=[])
        get_available_fn = Mock(return_value=["Lightning"])
        
        display_skills(get_learned_fn, get_available_fn, mock_player)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_main_menu(self, mock_print):
        """Test main menu display."""
        with patch('src.cli.input', return_value='1'):
            result = display_main_menu()
        
        assert result == '1'
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_main_menu_numeric_choices(self, mock_print):
        """Test main menu accepts numeric choices."""
        for choice in ['1', '5', '11']:
            with patch('src.cli.input', return_value=choice):
                result = display_main_menu()
                assert result == choice
    
    @patch('src.cli.print')
    def test_display_npc_list_empty(self, mock_print):
        """Test NPC list display when empty."""
        result = display_npc_list([])
        
        assert result is None
        assert mock_print.called
    
    @patch('src.cli.input', return_value='1')
    @patch('src.cli.print')
    def test_display_npc_list_select_first(self, mock_print, mock_input):
        """Test selecting first NPC from list."""
        npcs = [
            {"id": "elder", "name": "Village Elder"},
            {"id": "merchant", "name": "Merchant"}
        ]
        
        result = display_npc_list(npcs)
        
        assert result == npcs[0]
    
    @patch('src.cli.input', return_value='2')
    @patch('src.cli.print')
    def test_display_npc_list_select_second(self, mock_print, mock_input):
        """Test selecting second NPC from list."""
        npcs = [
            {"id": "elder", "name": "Village Elder"},
            {"id": "merchant", "name": "Merchant"}
        ]
        
        result = display_npc_list(npcs)
        
        assert result == npcs[1]
    
    @patch('src.cli.input', return_value='3')
    @patch('src.cli.print')
    def test_display_npc_list_leave(self, mock_print, mock_input):
        """Test leaving NPC list."""
        npcs = [
            {"id": "elder", "name": "Village Elder"},
            {"id": "merchant", "name": "Merchant"}
        ]
        
        result = display_npc_list(npcs)
        
        assert result is None
    
    @patch('src.cli.input', return_value='invalid')
    @patch('src.cli.print')
    def test_display_npc_list_invalid_choice(self, mock_print, mock_input):
        """Test invalid choice in NPC list."""
        npcs = [{"id": "elder", "name": "Village Elder"}]
        
        result = display_npc_list(npcs)
        
        assert result is None
    
    @patch('src.cli.print')
    def test_display_battle_results(self, mock_print, mock_player):
        """Test battle results display."""
        display_battle_results(5, 10, mock_player)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    @patch('src.cli.time.sleep')
    def test_display_game_start(self, mock_sleep, mock_print, mock_player):
        """Test game start display."""
        display_game_start(mock_player)
        
        assert mock_print.called
        mock_sleep.assert_called()
    
    @patch('src.cli.print')
    @patch('src.cli.time.sleep')
    def test_display_story_milestone(self, mock_sleep, mock_print):
        """Test story milestone display."""
        display_story_milestone("First Quest Complete")
        
        assert mock_print.called
        mock_sleep.assert_called()
    
    @patch('src.cli.print')
    def test_display_boss_victory(self, mock_print, mock_boss):
        """Test boss victory display."""
        display_boss_victory(mock_boss, 1000, 500)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_enemy_defeat(self, mock_print, sample_enemy):
        """Test enemy defeat display."""
        display_enemy_defeat(sample_enemy, 50, 25)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_level_up(self, mock_print, mock_player):
        """Test level up display."""
        mock_player.level = 2
        
        display_level_up(mock_player)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_battle_progress(self, mock_print):
        """Test battle progress display."""
        display_battle_progress(0, 10, 1)
        display_battle_progress(4, 10, 5)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_rest_message(self, mock_print):
        """Test rest message display."""
        display_rest_message(15)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_invalid_menu_choice(self, mock_print):
        """Test invalid menu choice display."""
        display_invalid_menu_choice()
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_exit_message(self, mock_print):
        """Test exit message display."""
        display_exit_message()
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_boss_not_found(self, mock_print):
        """Test boss not found display."""
        display_boss_not_found()
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_no_enemies_here(self, mock_print):
        """Test no enemies here display."""
        display_no_enemies_here()
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_fled_from_boss(self, mock_print):
        """Test fled from boss display."""
        display_fled_from_boss()
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_fled_or_defeated(self, mock_print):
        """Test fled or defeated display."""
        display_fled_or_defeated()
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_invalid_location(self, mock_print):
        """Test invalid location display."""
        display_invalid_location()
        
        assert mock_print.called


class TestLoadMenu:
    """Tests for load/new game menu."""
    
    @patch('src.cli.input', return_value='1')
    @patch('src.cli.print')
    def test_display_load_menu_load_game(self, mock_print, mock_input):
        """Test load game choice."""
        result = display_load_menu()
        
        assert result == '1'
    
    @patch('src.cli.input', return_value='2')
    @patch('src.cli.print')
    def test_display_load_menu_new_game(self, mock_print, mock_input):
        """Test new game choice."""
        result = display_load_menu()
        
        assert result == '2'
    
    @patch('src.cli.input', return_value='invalid')
    @patch('src.cli.print')
    def test_display_load_menu_invalid(self, mock_print, mock_input):
        """Test invalid choice in load menu."""
        result = display_load_menu()
        
        assert result == 'invalid'


class TestDisplayIntegration:
    """Integration tests for display components."""
    
    @patch('src.cli.print')
    def test_display_sequence(self, mock_print, mock_player, mock_location):
        """Test displaying multiple elements in sequence."""
        mock_location.describe = Mock(return_value="A place")
        mock_player.status = Mock(return_value="Status")
        
        # Simulate typical game loop display
        with patch('src.cli.input', return_value='1'):
            display_location_info(mock_location, mock_player)
            display_story_status(Mock(return_value="Story"), mock_player)
            result = display_main_menu()
        
        assert result == '1'
        assert mock_print.call_count > 3


class TestDisplayEdgeCases:
    """Tests for edge cases in display functions."""
    
    @patch('src.cli.print')
    def test_display_inventory_special_characters(self, mock_print, mock_player):
        """Test inventory with special characters in item names."""
        mock_player.inventory = [
            {"name": "⚔️ Legendary Sword", "id": "sword_1"},
            {"name": "🧪 Potion (×3)", "id": "potion_1"}
        ]
        
        display_inventory(mock_player)
        
        assert mock_print.called
    
    @patch('src.cli.print')
    def test_display_npc_list_many_npcs(self, mock_print):
        """Test NPC list with many NPCs."""
        npcs = [
            {"id": f"npc_{i}", "name": f"NPC {i}"}
            for i in range(20)
        ]
        
        with patch('src.cli.input', return_value='10'):
            result = display_npc_list(npcs)
        
        assert result == npcs[9]
    
    @patch('src.cli.print')
    def test_display_battle_results_extreme_numbers(self, mock_print, mock_player):
        """Test battle results with extreme numbers."""
        mock_player.level = 99
        mock_player.xp = 9999
        mock_player.gold = 999999
        mock_player.get_total_max_hp = Mock(return_value=9999)
        mock_player.hp = 9999
        
        display_battle_results(1000, 1000, mock_player)
        
        assert mock_print.called
