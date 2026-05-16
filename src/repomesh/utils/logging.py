"""
Logging configuration for RepoMesh AI.

This module provides structured logging with Rich console output
and configurable log levels.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False,
) -> None:
    """Set up logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        json_format: Whether to use JSON format for file logging
    """
    # Create console for Rich output
    console = Console()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add Rich console handler
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
    )
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Format for console
    console_format = "%(message)s"
    console_handler.setFormatter(logging.Formatter(console_format))
    
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        if json_format:
            # JSON format for structured logging
            file_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        else:
            # Standard format
            file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        file_handler.setFormatter(logging.Formatter(file_format))
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Module-specific loggers
def get_repo_logger() -> logging.Logger:
    """Get repository management logger."""
    return get_logger("repomesh.repos")


def get_agent_logger() -> logging.Logger:
    """Get agent logger."""
    return get_logger("repomesh.agents")


def get_orchestrator_logger() -> logging.Logger:
    """Get orchestrator logger."""
    return get_logger("repomesh.orchestrator")


def get_context_logger() -> logging.Logger:
    """Get context logger."""
    return get_logger("repomesh.context")


def get_api_logger() -> logging.Logger:
    """Get API logger."""
    return get_logger("repomesh.api")

# Made with Bob
