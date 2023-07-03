from enum import Enum
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class EventListener:
    callback: Callable
    once: bool = False

# based on https://github.com/mrdoob/eventdispatcher.js/blob/master/src/EventDispatcher.js


class EventDispatcher():
    def __init__(self, event_enum: Enum):
        self._listeners: dict[str, list[EventListener]] = {}
        for event_name in event_enum:
            self._listeners[event_name] = []

    def _get_event_listener_by_callback(self, event_name: Enum, callback: Callable):
        if event_name in self._listeners:
            for event_listener in self._listeners[event_name]:
                if event_listener.callback == callback:
                    return event_listener
        return None

    def _has_callback_for_event(self, event_name: Enum, callback: Callable) -> bool:
        return self._get_event_listener_by_callback(event_name, callback) is not None

    def add_event_listener(self, event_name: Enum, callback: Callable, once: bool = False) -> Optional[EventListener]:
        if event_name not in self._listeners:
            raise RuntimeError(f'invalid event name "{event_name}"')
        elif not self._has_callback_for_event(event_name, callback):
            event_listener = EventListener(callback, once)
            self._listeners[event_name].append(event_listener)
            return event_listener

    def remove_event_listener(self, event_name, event_listener: EventListener):
        event_listener = self._get_event_listener_by_callback(
            event_name, event_listener)
        if event_listener is not None:
            self._listeners[event_name].remove(event_listener)

    def dispatch(self, event_name, *args, **kargs):
        if event_name in self._listeners:
            for event_listener in self._listeners[event_name]:
                event_listener.callback(*args, **kargs)
                if event_listener.once:
                    self._listeners[event_name].remove(event_listener)
