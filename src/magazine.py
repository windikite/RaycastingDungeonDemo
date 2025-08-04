from collections import defaultdict
from typing import Callable, Any

class Mag:
    def __init__(self):
        self._subscribers: dict[str, list[Callable[...,Any]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[...,Any]) -> None:
        """Listen for `event_name`; callback will be called with **kwargs from publish()."""
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable[...,Any]) -> None:
        """Stop listening to `event_name`."""
        if callback in self._subscribers[event_name]:
            self._subscribers[event_name].remove(callback)

    def publish(self, event_name: str, **kwargs) -> None:
        """Emit an event; all subscribers get called in turn."""
        for callback in list(self._subscribers[event_name]):
            try:
                callback(**kwargs)
            except Exception:
                raise