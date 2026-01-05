"""
Events package for Phase V event-driven architecture.
"""
from .publisher import EventPublisher, get_event_publisher

__all__ = ["EventPublisher", "get_event_publisher"]
