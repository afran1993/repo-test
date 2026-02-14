"""
Tests for NPC system - Dialogue and interaction management.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.npc_system import (
    start_dialogue,
    display_dialogue,
    execute_dialogue_choice,
    get_npcs_in_location,
    interact_with_npc,
)
from src.exceptions import NPCNotFound


class TestStartDialogue:
    """Tests for starting dialogues with NPCs."""
    
    def test_start_dialogue_basic(self, mock_player):
        """Test starting basic dialogue with NPC."""
        npcs_data = {
            "npcs": [
                {
                    "id": "elder",
                    "name": "Village Elder",
                    "location": "village",
                    "dialogs": [
                        {
                            "npc_name": "Elder",
                            "text": "Welcome, traveler!",
                            "options": []
                        }
                    ]
                }
            ]
        }
        
        dialog = start_dialogue(mock_player, "elder", npcs_data)
        
        assert dialog is not None
        assert dialog["npc_name"] == "Elder"
        assert "Welcome" in dialog["text"]
    
    def test_start_dialogue_npc_not_found(self, mock_player):
        """Test dialogue with non-existent NPC."""
        npcs_data = {"npcs": []}
        
        with pytest.raises(NPCNotFound):
            start_dialogue(mock_player, "nonexistent", npcs_data)
    
    def test_start_dialogue_no_dialogs(self, mock_player):
        """Test dialogue when NPC has no dialogs."""
        npcs_data = {
            "npcs": [
                {
                    "id": "silent_npc",
                    "name": "Silent Person",
                    "dialogs": []
                }
            ]
        }
        
        dialog = start_dialogue(mock_player, "silent_npc", npcs_data)
        
        assert dialog is None
    
    def test_start_dialogue_with_skill_requirement_met(self, mock_player):
        """Test dialogue with met skill requirement."""
        mock_player.skills = {"fireball": 1}
        
        npcs_data = {
            "npcs": [
                {
                    "id": "mage",
                    "name": "Mage",
                    "dialogs": [
                        {
                            "text": "You know FireBall!",
                            "requires_skill": "fireball"
                        }
                    ]
                }
            ]
        }
        
        with patch('src.npc_system.has_skill', return_value=True):
            dialog = start_dialogue(mock_player, "mage", npcs_data)
        
        assert dialog is not None
    
    def test_start_dialogue_with_skill_requirement_not_met(self, mock_player):
        """Test dialogue with unmet skill requirement."""
        mock_player.skills = {}
        
        npcs_data = {
            "npcs": [
                {
                    "id": "mage",
                    "name": "Mage",
                    "dialogs": [
                        {
                            "text": "You know FireBall!",
                            "requires_skill": "fireball"
                        },
                        {
                            "text": "Hello stranger",
                            "id": "default"
                        }
                    ]
                }
            ]
        }
        
        with patch('src.npc_system.has_skill', return_value=False):
            dialog = start_dialogue(mock_player, "mage", npcs_data)
        
        assert dialog is not None
        assert dialog.get("id") == "default"
    
    def test_start_dialogue_with_story_requirement_met(self, mock_player):
        """Test dialogue with met story requirement."""
        mock_player.story_progress = "act_2"
        
        npcs_data = {
            "npcs": [
                {
                    "id": "quest_giver",
                    "name": "Quest Giver",
                    "dialogs": [
                        {
                            "text": "Here is your next quest",
                            "requires_act": "act_2"
                        }
                    ]
                }
            ]
        }
        
        dialog = start_dialogue(mock_player, "quest_giver", npcs_data)
        
        assert dialog is not None
        assert "next quest" in dialog["text"]
    
    def test_start_dialogue_with_story_requirement_not_met(self, mock_player):
        """Test dialogue with unmet story requirement."""
        mock_player.story_progress = "act_1"
        
        npcs_data = {
            "npcs": [
                {
                    "id": "quest_giver",
                    "name": "Quest Giver",
                    "dialogs": [
                        {
                            "text": "Here is your next quest",
                            "requires_act": "act_2"
                        },
                        {
                            "text": "Come back later",
                            "id": "default"
                        }
                    ]
                }
            ]
        }
        
        dialog = start_dialogue(mock_player, "quest_giver", npcs_data)
        
        assert dialog is not None
        assert dialog.get("id") == "default"
    
    def test_start_dialogue_with_choice_requirement_met(self, mock_player):
        """Test dialogue with met previous choice requirement."""
        mock_player.dialogue_choices = {"elder": "helped_village"}
        
        npcs_data = {
            "npcs": [
                {
                    "id": "elder",
                    "name": "Elder",
                    "dialogs": [
                        {
                            "text": "Thank you for helping!",
                            "requires_choice": "helped_village"
                        }
                    ]
                }
            ]
        }
        
        dialog = start_dialogue(mock_player, "elder", npcs_data)
        
        assert dialog is not None
        assert "Thank you" in dialog["text"]
    
    def test_start_dialogue_with_choice_requirement_not_met(self, mock_player):
        """Test dialogue with unmet previous choice requirement."""
        mock_player.dialogue_choices = {"elder": "ignored_request"}
        
        npcs_data = {
            "npcs": [
                {
                    "id": "elder",
                    "name": "Elder",
                    "dialogs": [
                        {
                            "text": "Thank you for helping!",
                            "requires_choice": "helped_village"
                        },
                        {
                            "text": "Hello stranger",
                            "id": "default"
                        }
                    ]
                }
            ]
        }
        
        dialog = start_dialogue(mock_player, "elder", npcs_data)
        
        assert dialog is not None
        assert dialog.get("id") == "default"


class TestDisplayDialogue:
    """Tests for displaying dialogue."""
    
    @patch('src.npc_system.print')
    def test_display_dialogue_basic(self, mock_print):
        """Test displaying basic dialogue."""
        dialog = {
            "npc_name": "Merchant",
            "text": "What can I sell you?"
        }
        
        result = display_dialogue(dialog)
        
        assert result is None
        assert mock_print.called
    
    @patch('src.npc_system.print')
    def test_display_dialogue_with_options(self, mock_print):
        """Test displaying dialogue with options."""
        dialog = {
            "npc_name": "Merchant",
            "text": "What can I sell you?",
            "options": [
                {"text": "Buy item", "id": "buy"},
                {"text": "Sell item", "id": "sell"}
            ]
        }
        
        result = display_dialogue(dialog)
        
        assert result is not None
        assert len(result) == 2
        assert result[0]["id"] == "buy"
    
    @patch('src.npc_system.print')
    def test_display_dialogue_none(self, mock_print):
        """Test displaying None dialogue."""
        result = display_dialogue(None)
        
        assert result is None
    
    @patch('src.npc_system.print')
    def test_display_dialogue_no_options(self, mock_print):
        """Test displaying dialogue without options."""
        dialog = {
            "npc_name": "Guard",
            "text": "You shall not pass!",
            "options": []
        }
        
        result = display_dialogue(dialog)
        
        assert result is None


class TestExecuteDialogueChoice:
    """Tests for executing dialogue choices and consequences."""
    
    def test_execute_dialogue_choice_teaches_skill(self, mock_player):
        """Test choice that teaches a skill."""
        choice = {
            "id": "learn_magic",
            "teaches_skill": "fireball"
        }
        npcs_data = {"npcs": []}
        
        with patch('src.npc_system.teach_skill', return_value=(True, "You learned Fireball!")):
            consequence = execute_dialogue_choice(mock_player, choice, "mage", npcs_data)
        
        assert "Fireball" in consequence
    
    def test_execute_dialogue_choice_updates_story(self, mock_player):
        """Test choice that updates story."""
        choice = {
            "id": "accept_quest",
            "updates_story": "quest_accepted"
        }
        npcs_data = {"npcs": []}
        
        consequence = execute_dialogue_choice(mock_player, choice, "quest_giver", npcs_data)
        
        assert mock_player.story_progress == "quest_accepted"
        assert "La storia avanza" in consequence
    
    def test_execute_dialogue_choice_xp_reward(self, mock_player):
        """Test choice with XP reward."""
        mock_player.gain_xp = Mock()
        choice = {
            "id": "accept_quest",
            "xp_reward": 100
        }
        npcs_data = {"npcs": []}
        
        consequence = execute_dialogue_choice(mock_player, choice, "npc", npcs_data)
        
        mock_player.gain_xp.assert_called_once_with(100)
        assert "100 XP" in consequence
    
    def test_execute_dialogue_choice_gold_reward(self, mock_player):
        """Test choice with gold reward."""
        choice = {
            "id": "accept_quest",
            "gold_reward": 50
        }
        npcs_data = {"npcs": []}
        initial_gold = mock_player.gold
        
        consequence = execute_dialogue_choice(mock_player, choice, "npc", npcs_data)
        
        assert mock_player.gold == initial_gold + 50
        assert "50 gold" in consequence
    
    def test_execute_dialogue_choice_multiple_rewards(self, mock_player):
        """Test choice with multiple rewards."""
        mock_player.gain_xp = Mock()
        choice = {
            "id": "complete_quest",
            "xp_reward": 250,
            "gold_reward": 100,
            "teaches_skill": "ice_spell",
            "updates_story": "act_changed"
        }
        npcs_data = {"npcs": []}
        
        with patch('src.npc_system.teach_skill', return_value=(True, "Skill learned!")):
            consequence = execute_dialogue_choice(mock_player, choice, "npc", npcs_data)
        
        mock_player.gain_xp.assert_called_once_with(250)
        assert mock_player.gold > 0
        assert mock_player.story_progress == "act_changed"
    
    def test_execute_dialogue_choice_saves_choice(self, mock_player):
        """Test that dialogue choice is saved to player."""
        choice = {
            "id": "option_1"
        }
        npcs_data = {"npcs": []}
        
        execute_dialogue_choice(mock_player, choice, "test_npc", npcs_data)
        
        assert mock_player.dialogue_choices["test_npc"] == "option_1"
    
    def test_execute_dialogue_choice_none_choice(self, mock_player):
        """Test executing None choice."""
        consequence = execute_dialogue_choice(mock_player, None, "npc", {})
        
        assert consequence == ""


class TestGetNPCsInLocation:
    """Tests for getting NPCs at a location."""
    
    def test_get_npcs_in_location_single(self):
        """Test getting single NPC at location."""
        npcs_data = {
            "npcs": [
                {"id": "elder", "name": "Elder", "location": "village"},
                {"id": "merchant", "name": "Merchant", "location": "market"}
            ]
        }
        
        result = get_npcs_in_location("village", npcs_data)
        
        assert len(result) == 1
        assert result[0]["id"] == "elder"
    
    def test_get_npcs_in_location_multiple(self):
        """Test getting multiple NPCs at location."""
        npcs_data = {
            "npcs": [
                {"id": "elder", "name": "Elder", "location": "village"},
                {"id": "guard", "name": "Guard", "location": "village"},
                {"id": "merchant", "name": "Merchant", "location": "market"}
            ]
        }
        
        result = get_npcs_in_location("village", npcs_data)
        
        assert len(result) == 2
        assert all(npc["location"] == "village" for npc in result)
    
    def test_get_npcs_in_location_none(self):
        """Test getting NPCs when none at location."""
        npcs_data = {
            "npcs": [
                {"id": "merchant", "name": "Merchant", "location": "market"}
            ]
        }
        
        result = get_npcs_in_location("empty_location", npcs_data)
        
        assert len(result) == 0
    
    def test_get_npcs_in_location_empty_npcs(self):
        """Test getting NPCs with empty NPC list."""
        npcs_data = {"npcs": []}
        
        result = get_npcs_in_location("village", npcs_data)
        
        assert len(result) == 0


class TestInteractWithNPC:
    """Tests for full NPC interaction flow."""
    
    @patch('src.npc_system.input', return_value='2')
    @patch('src.npc_system.print')
    def test_interact_with_npc_basic(self, mock_print, mock_input, mock_player):
        """Test basic NPC interaction."""
        npc = {"id": "elder", "name": "Elder"}
        npcs_data = {
            "npcs": [
                {
                    "id": "elder",
                    "name": "Elder",
                    "dialogs": [
                        {
                            "npc_name": "Elder",
                            "text": "Hello!",
                            "options": [
                                {"text": "Hi", "response": "Nice to meet you"},
                                {"text": "Goodbye", "response": "Farewell"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        with patch('src.npc_system.start_dialogue') as mock_start:
            with patch('src.npc_system.display_dialogue') as mock_display:
                mock_start.return_value = npcs_data["npcs"][0]["dialogs"][0]
                mock_display.return_value = npcs_data["npcs"][0]["dialogs"][0]["options"]
                
                interact_with_npc(mock_player, npc, npcs_data)
                
                mock_print.assert_called()
    
    @patch('src.npc_system.input', return_value='1')
    @patch('src.npc_system.print')
    def test_interact_with_npc_no_dialog(self, mock_print, mock_input, mock_player):
        """Test NPC interaction with no dialogue."""
        npc = {"id": "silent", "name": "Silent Person"}
        npcs_data = {"npcs": []}
        
        with patch('src.npc_system.start_dialogue', return_value=None):
            interact_with_npc(mock_player, npc, npcs_data)
        
        assert mock_print.called
    
    @patch('src.npc_system.input', return_value='2')
    @patch('src.npc_system.print')
    def test_interact_with_npc_leave(self, mock_print, mock_input, mock_player):
        """Test player leaving NPC conversation."""
        npc = {"id": "elder", "name": "Elder"}
        npcs_data = {"npcs": []}
        
        options = [
            {"text": "First option", "response": "OK"},
        ]
        
        with patch('src.npc_system.start_dialogue', return_value={"text": "Hi"}):
            with patch('src.npc_system.display_dialogue', return_value=options):
                interact_with_npc(mock_player, npc, npcs_data)
        
        assert mock_print.call_args_list[-1][0][0] == "Ti allontani..."
    
    @patch('src.npc_system.input', return_value='invalid')
    @patch('src.npc_system.print')
    def test_interact_with_npc_invalid_choice(self, mock_print, mock_input, mock_player):
        """Test NPC interaction with invalid choice."""
        npc = {"id": "elder", "name": "Elder"}
        npcs_data = {"npcs": []}
        
        options = [{"text": "Option", "response": "Response"}]
        
        with patch('src.npc_system.start_dialogue', return_value={"text": "Hi"}):
            with patch('src.npc_system.display_dialogue', return_value=options):
                interact_with_npc(mock_player, npc, npcs_data)
        
        assert mock_print.called
    
    @patch('src.npc_system.input', return_value='1')
    @patch('src.npc_system.print')
    def test_interact_with_npc_requires_skill(self, mock_print, mock_input, mock_player):
        """Test NPC choice requiring a skill."""
        npc = {"id": "mage", "name": "Mage"}
        npcs_data = {"npcs": []}
        
        choice = {
            "text": "Learn magic",
            "requires_skill": "fireball",
            "response": "You need to learn fireball first"
        }
        
        with patch('src.npc_system.start_dialogue', return_value={"text": "Hello"}):
            with patch('src.npc_system.display_dialogue', return_value=[choice]):
                with patch('src.npc_system.has_skill', return_value=False):
                    interact_with_npc(mock_player, npc, npcs_data)
        
        assert mock_print.called


class TestNPCSystemIntegration:
    """Integration tests for complete NPC interaction flow."""
    
    @patch('src.npc_system.input', return_value='1')
    @patch('src.npc_system.print')
    def test_complete_quest_dialogue_flow(self, mock_print, mock_input, mock_player):
        """Test complete quest dialogue flow."""
        mock_player.gain_xp = Mock()
        mock_player.story_progress = "start"
        
        npcs_data = {
            "npcs": [
                {
                    "id": "quest_giver",
                    "name": "Quest Giver",
                    "location": "village",
                    "dialogs": [
                        {
                            "npc_name": "Quest Giver",
                            "text": "Will you help us?",
                            "options": [
                                {
                                    "text": "I will help",
                                    "response": "Great! Go defeat the goblin!",
                                    "xp_reward": 100,
                                    "gold_reward": 50,
                                    "updates_story": "quest_accepted"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        npc = npcs_data["npcs"][0]
        
        with patch('src.npc_system.has_skill', return_value=True):
            interact_with_npc(mock_player, npc, npcs_data)
        
        assert mock_print.called
        mock_player.gain_xp.assert_called()
    
    def test_multiple_dialogue_branches(self, mock_player):
        """Test NPC with multiple dialogue branches."""
        npcs_data = {
            "npcs": [
                {
                    "id": "trainer",
                    "name": "Trainer",
                    "dialogs": [
                        {
                            "npc_name": "Trainer",
                            "text": "I only train combat masters",
                            "requires_skill": "combat_master"
                        },
                        {
                            "npc_name": "Trainer",
                            "text": "Come back when you are stronger",
                            "id": "default"
                        }
                    ]
                }
            ]
        }
        
        # First time without skill
        with patch('src.npc_system.has_skill', return_value=False):
            dialog1 = start_dialogue(mock_player, "trainer", npcs_data)
            assert dialog1.get("id") == "default"
        
        # Second time with skill
        with patch('src.npc_system.has_skill', return_value=True):
            dialog2 = start_dialogue(mock_player, "trainer", npcs_data)
            assert "combat master" in dialog2.get("text", "").lower()


class TestNPCSystemErrorHandling:
    """Tests for error handling in NPC system."""
    
    def test_start_dialogue_empty_npc_id(self, mock_player):
        """Test start dialogue with empty NPC ID."""
        npcs_data = {"npcs": [{"id": "npc1", "name": "NPC"}]}
        
        with pytest.raises(NPCNotFound):
            start_dialogue(mock_player, "", npcs_data)
    
    def test_start_dialogue_missing_npcs_key(self, mock_player):
        """Test start dialogue with missing npcs key."""
        npcs_data = {}
        
        with pytest.raises(NPCNotFound):
            start_dialogue(mock_player, "any_npc", npcs_data)
    
    def test_get_npcs_in_location_missing_npcs_key(self):
        """Test get NPCs with missing npcs key."""
        npcs_data = {}
        
        result = get_npcs_in_location("village", npcs_data)
        
        assert result == []
    
    @patch('src.npc_system.input', return_value='abc')
    @patch('src.npc_system.print')
    def test_interact_with_npc_non_numeric_choice(self, mock_print, mock_input, mock_player):
        """Test NPC interaction with non-numeric choice."""
        npc = {"id": "npc", "name": "NPC"}
        npcs_data = {"npcs": []}
        
        options = [{"text": "Option", "response": "OK"}]
        
        with patch('src.npc_system.start_dialogue', return_value={"text": "Hi"}):
            with patch('src.npc_system.display_dialogue', return_value=options):
                interact_with_npc(mock_player, npc, npcs_data)
        
        assert mock_print.called
