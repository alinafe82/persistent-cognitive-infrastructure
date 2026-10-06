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
