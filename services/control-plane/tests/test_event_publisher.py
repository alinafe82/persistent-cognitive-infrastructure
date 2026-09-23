from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.models import SemanticEventEnvelope
from app.runtime.event_publisher import EventPublisher, InMemoryEventPublisher


def _event(event_type: str) -> SemanticEventEnvelope:
    tenant_id = uuid4()
    return SemanticEventEnvelope.model_validate(
        {
            "tenant_id": tenant_id,
            "event_type": event_type,
            "schema_version": "v1",
            "source": {
                "source_system": "github",
                "authority_score": 0.93,
            },
            "occurred_at": datetime.now(UTC).isoformat(),
            "partition_key": f"{tenant_id}:publisher-contract",
            "payload": {"label": event_type},
            "payload_hash": "sha256:" + ("0" * 64),
        }
    )


def test_in_memory_event_publisher_preserves_envelopes_in_order() -> None:
    async def exercise() -> None:
        publisher = InMemoryEventPublisher()
        contract: EventPublisher = publisher
        first = _event("pci.test.first")
        second = _event("pci.test.second")

        await contract.publish(first)
        await contract.publish(second)

        assert publisher.events == (first, second)
        assert publisher.events[0] is first
        assert publisher.events[1] is second

    asyncio.run(exercise())


def test_in_memory_event_publisher_can_be_reset_between_tests() -> None:
    async def exercise() -> None:
        publisher = InMemoryEventPublisher()
        await publisher.publish(_event("pci.test.reset"))

        publisher.clear()

        assert publisher.events == ()

    asyncio.run(exercise())
