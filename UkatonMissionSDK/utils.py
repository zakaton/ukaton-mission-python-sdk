from enum import Enum

# based on https://github.com/mrdoob/eventdispatcher.js/blob/master/src/EventDispatcher.js


class EventDispatcher():
    def __init__(self, event_enum: Enum):
        self._listeners: dict[str, list] = {}
        for event_name in event_enum:
            self._listeners[event_name] = []

    def add_event_listener(self, event_name, callback):
        if event_name not in self._listeners:
            raise RuntimeError(f'invalid event name "{event_name}"')
        elif callback not in self._listeners[event_name]:
            self._listeners[event_name].append(callback)

    def remove_event_listener(self, event_name, callback):
        if event_name in self._listeners and callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    def dispatch(self, event_name, *args, **kargs):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kargs)
