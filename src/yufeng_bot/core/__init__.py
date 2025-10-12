"""
核心包 - 系统核心组件
"""

from .event_bus import event_bus, EventBus, EventNames, EventPriority

__all__ = ["event_bus", "EventBus", "EventNames", "EventPriority"]