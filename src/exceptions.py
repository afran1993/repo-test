"""
Custom exception classes for RPG Game.

Provides fine-grained error handling across the game engine.
"""


class GameException(Exception):
    """Base exception for all game-related errors."""
    
    def __init__(self, message: str, context: dict = None):
        """Initialize game exception.
        
        Args:
            message: Error message
            context: Additional context as dict (for logging/debugging)
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}


# ========== Game State Exceptions ==========

class GameStateError(GameException):
    """Raised when invalid game state transition occurs."""
    pass


class GameNotStarted(GameStateError):
    """Raised when trying to play without starting game."""
    
    def __init__(self):
        super().__init__("Game has not been started yet")


class GameAlreadyStarted(GameStateError):
    """Raised when trying to start game twice."""
    
    def __init__(self):
        super().__init__("Game is already running")


class GameOver(GameStateError):
    """Raised when game has ended."""
    
    def __init__(self, reason: str = "Unknown"):
        super().__init__(f"Game Over: {reason}", {"reason": reason})


# ========== Player Exceptions ==========

class PlayerException(GameException):
    """Base exception for player-related errors."""
    pass


class PlayerNotFound(PlayerException):
    """Raised when player cannot be found."""
    
    def __init__(self, player_name: str):
        super().__init__(
            f"Player '{player_name}' not found",
            {"player_name": player_name}
        )


class PlayerDefeated(PlayerException):
    """Raised when player is defeated."""
    
    def __init__(self, reason: str = "Unknown"):
        super().__init__(
            f"Player was defeated: {reason}",
            {"reason": reason}
        )


class InsufficientGold(PlayerException):
    """Raised when player doesn't have enough gold."""
    
    def __init__(self, required: int, have: int):
        super().__init__(
            f"Insufficient gold. Required: {required}, Have: {have}",
            {"required": required, "have": have}
        )


class InsufficientXP(PlayerException):
    """Raised when player doesn't have required XP."""
    
    def __init__(self, required: int, have: int):
        super().__init__(
            f"Insufficient XP. Required: {required}, Have: {have}",
            {"required": required, "have": have}
        )


# ========== Location Exceptions ==========

class LocationException(GameException):
    """Base exception for location-related errors."""
    pass


class LocationNotFound(LocationException):
    """Raised when location cannot be found."""
    
    def __init__(self, location_id: str):
        super().__init__(
            f"Location '{location_id}' not found",
            {"location_id": location_id}
        )


class LocationAccessDenied(LocationException):
    """Raised when player cannot access a location."""
    
    def __init__(self, location_id: str, reason: str):
        super().__init__(
            f"Cannot access '{location_id}': {reason}",
            {"location_id": location_id, "reason": reason}
        )


class InvalidConnection(LocationException):
    """Raised when location connection is invalid."""
    
    def __init__(self, from_id: str, direction: str):
        super().__init__(
            f"No connection from '{from_id}' to {direction}",
            {"from_id": from_id, "direction": direction}
        )


# ========== Combat Exceptions ==========

class CombatException(GameException):
    """Base exception for combat-related errors."""
    pass


class EnemyNotFound(CombatException):
    """Raised when enemy cannot be found."""
    
    def __init__(self, enemy_id: str):
        super().__init__(
            f"Enemy '{enemy_id}' not found",
            {"enemy_id": enemy_id}
        )


class CombatError(CombatException):
    """Raised when combat cannot proceed."""
    
    def __init__(self, reason: str):
        super().__init__(
            f"Combat error: {reason}",
            {"reason": reason}
        )


class InvalidAction(CombatException):
    """Raised when invalid action in combat."""
    
    def __init__(self, action: str, reason: str):
        super().__init__(
            f"Cannot perform '{action}': {reason}",
            {"action": action, "reason": reason}
        )


class AbilityOnCooldown(CombatException):
    """Raised when ability is on cooldown."""
    
    def __init__(self, ability_name: str, turns_remaining: int):
        super().__init__(
            f"Ability '{ability_name}' on cooldown for {turns_remaining} turns",
            {"ability": ability_name, "turns_remaining": turns_remaining}
        )


class InsufficientMana(CombatException):
    """Raised when not enough mana for ability."""
    
    def __init__(self, required: int, have: int):
        super().__init__(
            f"Insufficient mana. Required: {required}, Have: {have}",
            {"required": required, "have": have}
        )


# ========== Item/Inventory Exceptions ==========

class InventoryException(GameException):
    """Base exception for inventory-related errors."""
    pass


class ItemNotFound(InventoryException):
    """Raised when item is not in inventory."""
    
    def __init__(self, item_id: str):
        super().__init__(
            f"Item '{item_id}' not found in inventory",
            {"item_id": item_id}
        )


class InventoryFull(InventoryException):
    """Raised when inventory is full."""
    
    def __init__(self, capacity: int):
        super().__init__(
            f"Inventory full (capacity: {capacity})",
            {"capacity": capacity}
        )


class CannotEquip(InventoryException):
    """Raised when item cannot be equipped."""
    
    def __init__(self, item_id: str, reason: str):
        super().__init__(
            f"Cannot equip '{item_id}': {reason}",
            {"item_id": item_id, "reason": reason}
        )


# ========== NPC/Quest Exceptions ==========

class NPCException(GameException):
    """Base exception for NPC-related errors."""
    pass


class NPCNotFound(NPCException):
    """Raised when NPC cannot be found."""
    
    def __init__(self, npc_id: str):
        super().__init__(
            f"NPC '{npc_id}' not found",
            {"npc_id": npc_id}
        )


class QuestException(GameException):
    """Base exception for quest-related errors."""
    pass


class QuestNotFound(QuestException):
    """Raised when quest cannot be found."""
    
    def __init__(self, quest_id: str):
        super().__init__(
            f"Quest '{quest_id}' not found",
            {"quest_id": quest_id}
        )


class QuestAlreadyCompleted(QuestException):
    """Raised when trying to complete already completed quest."""
    
    def __init__(self, quest_id: str):
        super().__init__(
            f"Quest '{quest_id}' already completed",
            {"quest_id": quest_id}
        )


class InvalidQuestState(QuestException):
    """Raised when quest is in invalid state."""
    
    def __init__(self, quest_id: str, reason: str):
        super().__init__(
            f"Invalid state for quest '{quest_id}': {reason}",
            {"quest_id": quest_id, "reason": reason}
        )


# ========== Persistence Exceptions ==========

class PersistenceException(GameException):
    """Base exception for save/load errors."""
    pass


class SaveFailed(PersistenceException):
    """Raised when save fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            f"Save failed: {reason}",
            {"reason": reason}
        )


class LoadFailed(PersistenceException):
    """Raised when load fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            f"Load failed: {reason}",
            {"reason": reason}
        )


class SaveNotFound(PersistenceException):
    """Raised when save file not found."""
    
    def __init__(self, save_name: str):
        super().__init__(
            f"Save '{save_name}' not found",
            {"save_name": save_name}
        )


class CorruptedSave(PersistenceException):
    """Raised when save file is corrupted."""
    
    def __init__(self, save_name: str, reason: str):
        super().__init__(
            f"Save '{save_name}' corrupted: {reason}",
            {"save_name": save_name, "reason": reason}
        )


# ========== Data/Configuration Exceptions ==========

class DataException(GameException):
    """Base exception for data-related errors."""
    pass


class ConfigError(DataException):
    """Raised when configuration is invalid."""
    
    def __init__(self, key: str, reason: str):
        super().__init__(
            f"Configuration error '{key}': {reason}",
            {"key": key, "reason": reason}
        )


class DataLoadError(DataException):
    """Raised when data file cannot be loaded."""
    
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"Cannot load '{file_path}': {reason}",
            {"file_path": file_path, "reason": reason}
        )


class InvalidData(DataException):
    """Raised when data format is invalid."""
    
    def __init__(self, data_type: str, reason: str):
        super().__init__(
            f"Invalid {data_type}: {reason}",
            {"data_type": data_type, "reason": reason}
        )


# ========== Utility Function ==========

def is_game_exception(exception: Exception) -> bool:
    """Check if exception is a game exception.
    
    Args:
        exception: Exception to check
    
    Returns:
        True if exception is GameException subclass
    """
    return isinstance(exception, GameException)
