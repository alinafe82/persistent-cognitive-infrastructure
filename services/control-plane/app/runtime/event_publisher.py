from __future__ import annotations

from typing import Protocol

from app.domain.models import SemanticEventEnvelope


class EventPublisher(Protocol):
    async def publish(self, event: SemanticEventEnvelope) -> None:
        """Publish one accepted semantic event."""
        ...


class InMemoryEventPublisher:
    """Deterministic publisher used until a durable transport is introduced."""

    def __init__(self) -> None:
        self._events: list[SemanticEventEnvelope] = []

    @property
    def events(self) -> tuple[SemanticEventEnvelope, ...]:
        return tuple(self._events)

    async def publish(self, event: SemanticEventEnvelope) -> None:
        self._events.append(event)

    def clear(self) -> None:
        self._events.clear()
