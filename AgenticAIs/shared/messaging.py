"""
Simple in-process Pub/Sub messaging for agents.

Agents and the orchestrator can `publish(topic, payload)` and
`subscribe(topic, callback)` to receive events. This is synchronous
and intended for local in-process communication during the workflow.
"""
from threading import Lock
from typing import Any, Callable, Dict, List


_subscribers: Dict[str, List[Callable[[str, Any], None]]] = {}
_lock = Lock()


def subscribe(topic: str, callback: Callable[[str, Any], None]):
    """Subscribe a callback to a topic. Returns an unsubscribe function."""
    with _lock:
        if topic not in _subscribers:
            _subscribers[topic] = []
        _subscribers[topic].append(callback)

    def unsubscribe():
        with _lock:
            if topic in _subscribers and callback in _subscribers[topic]:
                _subscribers[topic].remove(callback)

    return unsubscribe


def publish(topic: str, payload: Any):
    """Publish a payload to all subscribers of the topic.

    Callbacks are invoked synchronously in the publisher's thread.
    """
    # Copy list under lock to allow safe modifications during iteration
    with _lock:
        listeners = list(_subscribers.get(topic, []))

    for cb in listeners:
        try:
            cb(topic, payload)
        except Exception:
            # Don't let subscriber errors break the publisher
            continue
