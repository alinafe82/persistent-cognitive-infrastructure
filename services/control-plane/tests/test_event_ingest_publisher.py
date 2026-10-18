from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.routes import ingest_event, publisher, store
from app.domain.models import SemanticEventEnvelope


def _event() -> SemanticEventEnvelope:
    tenant_id = uuid4()
    entity_id = uuid4()
    return SemanticEventEnvelope.model_validate(
        {
            "tenant_id": tenant_id,
            "event_type": "pci.graph.claim",
            "schema_version": "v1",
            "source": {
                "source_system": "github",
                "authority_score": 0.93,
            },
            "occurred_at": datetime.now(UTC).isoformat(),
            "partition_key": f"{tenant_id}:{entity_id}",
            "payload": {
                "entities": [
                    {
                        "entity_id": entity_id,
                        "kind": "repository",
                        "canonical_name": "publisher-contract",
                    }
                ]
            },
            "payload_hash": "sha256:" + ("0" * 64),
        }
    )


def test_ingest_publishes_only_newly_accepted_event() -> None:
    async def exercise() -> None:
        store.clear()
        publisher.clear()
        event = _event()

        first = await ingest_event(event)
        repeated = await ingest_event(event)

        assert first.accepted is True
        assert repeated.accepted is True
        assert publisher.events == (event,)

        conflicting = event.model_copy(
            update={"payload_hash": "sha256:" + ("1" * 64)}
        )
        with pytest.raises(HTTPException) as exc_info:
            await ingest_event(conflicting)

        assert exc_info.value.status_code == 409
        assert publisher.events == (event,)
        assert len(store.events) == 1

    asyncio.run(exercise())


def test_ingest_retries_incomplete_publication(monkeypatch: pytest.MonkeyPatch) -> None:
    original_publish = publisher.publish
    attempts = 0

    async def publish_with_transient_failure(event: SemanticEventEnvelope) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary publisher outage")
        await original_publish(event)

    monkeypatch.setattr(publisher, "publish", publish_with_transient_failure)

    async def exercise() -> None:
        store.clear()
        publisher.clear()
        event = _event()

        with pytest.raises(RuntimeError, match="temporary publisher outage"):
            await ingest_event(event)

        assert event.event_id in store.events
        assert publisher.events == ()
        assert (await ingest_event(event)).accepted is True
        assert (await ingest_event(event)).accepted is True
        assert publisher.events == (event,)
        assert attempts == 2

    asyncio.run(exercise())
