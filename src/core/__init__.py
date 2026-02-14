"""
Core application components - Service container, configuration, and bootstrapping.
"""

from src.core.service_container import ServiceContainer
from src.core.service_configurator import configure_services
from src.core.logging_config import setup_logging

__all__ = ['ServiceContainer', 'configure_services', 'setup_logging']
