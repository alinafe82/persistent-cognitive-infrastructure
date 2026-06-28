from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.api.routes import (
    control_plane_ui_state,
    create_replay_bundle,
    create_workload,
    decide_approval,
    ingest_event,
    list_entities,
    list_entity_claims,
    metrics,
    store,
)
from app.domain.models import (
    ApprovalDecisionRequest,
    ReplayRequest,
    SemanticEventEnvelope,
    WorkloadCreate,
)


def _event_payload(tenant_id: UUID, entity_id: UUID) -> SemanticEventEnvelope:
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
                "label": "repository default branch confirmed",
                "entities": [
                    {
                        "entity_id": entity_id,
                        "kind": "repository",
                        "canonical_name": "api-service",
                        "confidence_score": 0.88,
                    }
                ],
                "claims": [
                    {
                        "subject_entity_id": entity_id,
                        "predicate": "default_branch",
                        "object_value": "main",
                        "confidence_score": 0.91,
                    }
                ],
            },
            "payload_hash": "sha256:" + ("0" * 64),
        }
    )


def test_event_ingest_projects_graph_state_and_ui_snapshot() -> None:
    async def exercise() -> None:
        store.clear()
        tenant_id = uuid4()
        entity_id = uuid4()

        response = await ingest_event(_event_payload(tenant_id, entity_id))

        assert response.projected_entities == 1
        assert response.projected_claims == 1

        entities = await list_entities(tenant_id, kind="Repository")
        assert entities.entities[0].entity_id == entity_id
        assert entities.entities[0].canonical_name == "api-service"

        claims = await list_entity_claims(tenant_id, entity_id)
        assert claims.claims[0].predicate == "default_branch"
        assert claims.claims[0].object_value == "main"

        ui_state = await control_plane_ui_state()
        dumped = ui_state.model_dump(by_alias=True)
        assert dumped["graphNodes"]
        assert dumped["semanticEvents"][0]["label"] == "repository default branch confirmed"
        assert dumped["insights"][0]["id"] in {"runtime-clear", "graph-coverage"}

    asyncio.run(exercise())


def test_workload_admission_materializes_approval_and_replay_bundle() -> None:
    async def exercise() -> None:
        store.clear()
        tenant_id = uuid4()
        entity_id = uuid4()
        event_response = await ingest_event(_event_payload(tenant_id, entity_id))

        workload = await create_workload(
            WorkloadCreate(
                tenant_id=tenant_id,
                workload_class="governance",
                objective="Validate production deployment approval policy drift.",
                input_event_ids=[event_response.event_id],
                input_entity_ids=[entity_id],
            )
        )

        assert workload.state == "admitted_requires_approval"
        assert workload.approvals

        approval = workload.approvals[0]
        decision = await decide_approval(
            approval.approval_id,
            ApprovalDecisionRequest(decision="approved", reason="policy owner reviewed"),
        )
        assert decision.state == "approved"

        replay = await create_replay_bundle(
            workload.workload_id,
            ReplayRequest(mode="graph", include_artifacts=True),
        )
        assert replay.state == "ready"
        assert replay.event_count == 1
        assert replay.entity_count == 1
        assert replay.claim_count == 1
        assert replay.artifacts["event_ids"] == [str(event_response.event_id)]

        ui_state = await control_plane_ui_state()
        dumped = ui_state.model_dump(by_alias=True)
        assert dumped["insights"][0]["id"] == "approval-queue"
        assert dumped["insights"][0]["severity"] == "critical"

    asyncio.run(exercise())


def test_metrics_include_projection_and_approval_counts() -> None:
    async def exercise() -> None:
        store.clear()
        payload = await metrics()

        assert "pci_control_plane_events_total" in payload
        assert "pci_control_plane_entities_total" in payload
        assert "pci_control_plane_claims_total" in payload
        assert "pci_control_plane_approvals_total" in payload

    asyncio.run(exercise())
