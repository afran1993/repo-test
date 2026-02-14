"""
Structured Logging Configuration.

Centralizes logging setup across the application with:
- Consistent formatting
- Multiple output targets (console, file)
- Configurable log levels
- Suppression of noisy libraries
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Color codes for terminal output
COLORS = {
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Green
    'WARNING': '\033[33m',    # Yellow
    'ERROR': '\033[31m',      # Red
    'CRITICAL': '\033[35m',   # Magenta
    'RESET': '\033[0m',       # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for terminal."""
    
    def format(self, record):
        """Format log record with colors."""
        if sys.stdout.isatty():
            # Add color to level name
            levelname_color = COLORS.get(record.levelname, '')
            record.levelname = f"{levelname_color}{record.levelname}{COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    colored: bool = True
) -> None:
    """
    Configure structured logging for the game.
    
    Sets up:
    - Console handler with optional colored output
    - File handler (optional)
    - Consistent formatting across all loggers
    - Suppression of verbose third-party loggers
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file for persistent logging
        colored: Whether to use colored output (for terminal)
    
    Raises:
        ValueError: If level is not valid
    """
    
    # Validate level
    valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    if level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {level}. Must be one of {valid_levels}")
    
    # Create formatter
    format_string = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(message)s'
    )
    
    date_format = '%Y-%m-%d %H:%M:%S'
    
    if colored:
        formatter = ColoredFormatter(format_string, datefmt=date_format)
    else:
        formatter = logging.Formatter(format_string, datefmt=date_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level.upper())
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set root to lowest level
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # File gets all levels
        
        root_logger.addHandler(file_handler)
    
    # Suppress verbose third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    
    # Log setup completion
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={level}, file={log_file or 'none'}, colored={colored}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Convenience function for consistent logger naming.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def enable_debug_logging() -> None:
    """Set all loggers to DEBUG level for troubleshooting."""
    logging.getLogger().setLevel(logging.DEBUG)
    for handler in logging.getLogger().handlers:
        handler.setLevel(logging.DEBUG)
    
    logging.getLogger(__name__).debug("Debug logging enabled")


def disable_debug_logging() -> None:
    """Reset loggers to INFO level."""
    logging.getLogger().setLevel(logging.INFO)
    for handler in logging.getLogger().handlers:
        handler.setLevel(logging.INFO)
    
    logging.getLogger(__name__).debug("Debug logging disabled")
