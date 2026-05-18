from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.domain.models import (
    Approval,
    ApprovalDecisionRequest,
    Claim,
    Workload,
    WorkloadCreate,
    Entity,
    HealthResponse,
    MemoryCompressionRequest,
    ReconciliationRequest,
    ReplayRequest,
    ReplayResponse,
    SchedulerDecision,
    SemanticEventEnvelope,
    WorkloadClass,
    WorkloadResponse,
)
from app.runtime.scheduler import WorkloadScheduler

router = APIRouter()


class InMemoryControlPlaneStore:
    def __init__(self) -> None:
        self.events: dict[UUID, SemanticEventEnvelope] = {}
        self.entities: dict[UUID, Entity] = {}
        self.claims: dict[UUID, Claim] = {}
        self.workloads: dict[UUID, Workload] = {}
        self.decisions: dict[UUID, SchedulerDecision] = {}
        self.approvals: dict[UUID, Approval] = {}

    def put_workload(
        self,
        workload: Workload,
        decision: SchedulerDecision,
    ) -> WorkloadResponse:
        self.workloads[workload.workload_id] = workload
        self.decisions[workload.workload_id] = decision
        return WorkloadResponse(
            workload_id=workload.workload_id,
            tenant_id=workload.tenant_id,
            state=workload.state,
            decision=decision,
        )


store = InMemoryControlPlaneStore()
scheduler = WorkloadScheduler()


@router.get("/healthz", response_model=HealthResponse, tags=["system"])
async def healthz() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@router.get("/metrics", include_in_schema=False, response_class=PlainTextResponse)
async def metrics() -> str:
    workload_count = len(store.workloads)
    event_count = len(store.events)
    return "\n".join(
        [
            "# HELP pci_control_plane_workloads_total Workloads tracked by the control plane process.",
            "# TYPE pci_control_plane_workloads_total gauge",
            f"pci_control_plane_workloads_total {workload_count}",
            "# HELP pci_control_plane_events_total Events tracked by the control plane process.",
            "# TYPE pci_control_plane_events_total gauge",
            f"pci_control_plane_events_total {event_count}",
            "",
        ]
    )


@router.post(
    "/v1/events",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["events"],
)
async def ingest_event(event: SemanticEventEnvelope) -> dict[str, object]:
    store.events[event.event_id] = event
    return {
        "event_id": event.event_id,
        "accepted": True,
        "stream": event.event_type,
    }


@router.get("/v1/tenants/{tenant_id}/graph/entities", tags=["graph"])
async def list_entities(
    tenant_id: Annotated[UUID, Path()],
    kind: str | None = None,
    q: str | None = None,
    limit: int = 50,
) -> dict[str, list[Entity]]:
    entities = [entity for entity in store.entities.values() if entity.tenant_id == tenant_id]
    if kind:
        entities = [entity for entity in entities if entity.kind == kind]
    if q:
        entities = [entity for entity in entities if q.lower() in entity.canonical_name.lower()]
    return {"entities": entities[: max(1, min(limit, 200))]}


@router.get("/v1/tenants/{tenant_id}/graph/entities/{entity_id}", response_model=Entity, tags=["graph"])
async def get_entity(tenant_id: UUID, entity_id: UUID) -> Entity:
    entity = store.entities.get(entity_id)
    if entity is None or entity.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="entity not found")
    return entity


@router.get("/v1/tenants/{tenant_id}/graph/entities/{entity_id}/claims", tags=["graph"])
async def list_entity_claims(
    tenant_id: UUID,
    entity_id: UUID,
    predicate: str | None = None,
    include_contradicted: bool = True,
) -> dict[str, list[Claim]]:
    claims = [
        claim
        for claim in store.claims.values()
        if claim.tenant_id == tenant_id and claim.subject_entity_id == entity_id
    ]
    if predicate:
        claims = [claim for claim in claims if claim.predicate == predicate]
    if not include_contradicted:
        claims = [claim for claim in claims if claim.contradiction_set_id is None]
    return {"claims": claims}


@router.post("/v1/workloads/dry-run", response_model=SchedulerDecision, tags=["workloads"])
async def dry_run_workload(request: WorkloadCreate) -> SchedulerDecision:
    workload = Workload.from_create(request)
    return scheduler.dry_run(workload)


@router.post(
    "/v1/workloads",
    response_model=WorkloadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["workloads"],
)
async def create_workload(request: WorkloadCreate) -> WorkloadResponse:
    workload = Workload.from_create(request)
    decision = scheduler.admit(workload)
    return store.put_workload(workload, decision)


@router.get("/v1/workloads/{workload_id}", response_model=WorkloadResponse, tags=["workloads"])
async def get_workload(workload_id: UUID) -> WorkloadResponse:
    workload = store.workloads.get(workload_id)
    decision = store.decisions.get(workload_id)
    if workload is None or decision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workload not found")
    return WorkloadResponse(
        workload_id=workload.workload_id,
        tenant_id=workload.tenant_id,
        state=workload.state,
        decision=decision,
    )


@router.post(
    "/v1/workloads/{workload_id}/replay",
    response_model=ReplayResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["replay"],
)
async def create_replay_bundle(workload_id: UUID, request: ReplayRequest) -> ReplayResponse:
    if workload_id not in store.workloads:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workload not found")
    state = f"{request.mode}_requested"
    return ReplayResponse(state=state)


@router.post(
    "/v1/reconciliation/checks",
    response_model=WorkloadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["reconciliation"],
)
async def request_reconciliation(request: ReconciliationRequest) -> WorkloadResponse:
    workload = Workload.from_create(
        WorkloadCreate(
            tenant_id=request.tenant_id,
            workload_class=WorkloadClass.RECONCILIATION,
            objective="Reconcile graph claims against authoritative source systems",
            input_entity_ids=request.entity_ids,
            constraints={
                "claim_ids": [str(claim_id) for claim_id in request.claim_ids],
                "source_system": request.source_system,
            },
        )
    )
    decision = scheduler.admit(workload)
    return store.put_workload(workload, decision)


@router.post(
    "/v1/memory/compressions",
    response_model=WorkloadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["memory"],
)
async def request_memory_compression(request: MemoryCompressionRequest) -> WorkloadResponse:
    workload = Workload.from_create(
        WorkloadCreate(
            tenant_id=request.tenant_id,
            workload_class=WorkloadClass.COMPRESSION,
            objective=f"Compress {request.compression_type} memory from supplied provenance",
            input_event_ids=request.source_event_ids,
            constraints={
                "compression_type": request.compression_type,
                "source_claim_ids": [str(claim_id) for claim_id in request.source_claim_ids],
            },
        )
    )
    decision = scheduler.admit(workload)
    return store.put_workload(workload, decision)


@router.post("/v1/approvals/{approval_id}/decisions", response_model=Approval, tags=["governance"])
async def decide_approval(approval_id: UUID, request: ApprovalDecisionRequest) -> Approval:
    approval = store.approvals.get(approval_id)
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="approval not found")
    approval.state = request.decision
    approval.reason = request.reason
    approval.decided_at = datetime.now(UTC)
    return approval
