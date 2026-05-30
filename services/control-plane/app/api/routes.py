from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import NAMESPACE_URL, UUID, uuid5

from fastapi import APIRouter, HTTPException, Path, status
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.domain.models import (
    Approval,
    ApprovalDecisionRequest,
    ApprovalState,
    Claim,
    ClaimState,
    Confidence,
    ConfidenceBand,
    DataClassification,
    Entity,
    EventIngestResponse,
    HealthResponse,
    MemoryCompressionRequest,
    ReconciliationRequest,
    ReplayRequest,
    ReplayResponse,
    SchedulerDecision,
    SemanticEventEnvelope,
    Workload,
    WorkloadClass,
    WorkloadCreate,
    WorkloadResponse,
    WorkloadState,
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

    def clear(self) -> None:
        self.events.clear()
        self.entities.clear()
        self.claims.clear()
        self.workloads.clear()
        self.decisions.clear()
        self.approvals.clear()

    def put_workload(
        self,
        workload: Workload,
        decision: SchedulerDecision,
    ) -> WorkloadResponse:
        self.workloads[workload.workload_id] = workload
        self.decisions[workload.workload_id] = decision
        approvals = self._materialize_approvals(workload, decision)
        return WorkloadResponse(
            workload_id=workload.workload_id,
            tenant_id=workload.tenant_id,
            state=workload.state,
            decision=decision,
            approvals=approvals,
        )

    def put_event(self, event: SemanticEventEnvelope) -> tuple[int, int]:
        self.events[event.event_id] = event
        projected_entities = 0
        projected_claims = 0

        for entity_payload in self._entity_payloads(event.payload):
            entity = self._entity_from_payload(event, entity_payload)
            if entity is None:
                continue
            self.entities[entity.entity_id] = entity
            projected_entities += 1

        for claim_payload in self._claim_payloads(event.payload, event.event_type):
            claim = self._claim_from_payload(event, claim_payload)
            if claim is None:
                continue
            self.claims[claim.claim_id] = claim
            projected_claims += 1

        return projected_entities, projected_claims

    def workload_response(self, workload_id: UUID) -> WorkloadResponse | None:
        workload = self.workloads.get(workload_id)
        decision = self.decisions.get(workload_id)
        if workload is None or decision is None:
            return None
        return WorkloadResponse(
            workload_id=workload.workload_id,
            tenant_id=workload.tenant_id,
            state=workload.state,
            decision=decision,
            approvals=self.approvals_for_workload(workload_id),
        )

    def approvals_for_workload(self, workload_id: UUID) -> list[Approval]:
        return [
            approval
            for approval in self.approvals.values()
            if approval.workload_id == workload_id
        ]

    def replay_bundle(
        self,
        workload_id: UUID,
        request: ReplayRequest,
    ) -> ReplayResponse | None:
        workload = self.workloads.get(workload_id)
        if workload is None:
            return None

        event_ids = set(workload.input_event_ids)
        events = [event for event in self.events.values() if event.event_id in event_ids]
        entities = [
            entity
            for entity in self.entities.values()
            if entity.tenant_id == workload.tenant_id
            and (not workload.input_entity_ids or entity.entity_id in workload.input_entity_ids)
        ]
        claims = [
            claim
            for claim in self.claims.values()
            if claim.tenant_id == workload.tenant_id
            and (
                not workload.input_entity_ids
                or claim.subject_entity_id in workload.input_entity_ids
            )
        ]

        artifacts: dict[str, object] = {}
        if request.include_artifacts:
            artifacts = {
                "event_ids": [str(event.event_id) for event in events],
                "entity_ids": [str(entity.entity_id) for entity in entities],
                "claim_ids": [str(claim.claim_id) for claim in claims],
            }

        return ReplayResponse(
            workload_id=workload_id,
            mode=request.mode,
            event_count=len(events),
            entity_count=len(entities),
            claim_count=len(claims),
            artifacts=artifacts,
        )

    def ui_state(self) -> dict[str, list[dict[str, object]]]:
        entities = sorted(self.entities.values(), key=lambda item: item.canonical_name.lower())
        claims = sorted(self.claims.values(), key=lambda item: item.observed_at, reverse=True)
        events = sorted(self.events.values(), key=lambda item: item.occurred_at, reverse=True)
        workloads = sorted(self.workloads.values(), key=lambda item: item.created_at, reverse=True)

        return {
            "graphNodes": [
                {
                    "id": str(entity.entity_id),
                    "label": entity.canonical_name,
                    "kind": entity.kind,
                    "confidence": entity.confidence.score,
                }
                for entity in entities
            ],
            "graphLinks": [
                {
                    "source": str(claim.subject_entity_id),
                    "target": str(claim.object_entity_id),
                    "predicate": claim.predicate,
                }
                for claim in claims
                if claim.object_entity_id is not None
            ],
            "semanticEvents": [
                {
                    "id": str(event.event_id),
                    "topic": event.event_type,
                    "label": self._event_label(event),
                    "time": event.occurred_at.strftime("%H:%M"),
                    "severity": self._event_severity(event),
                }
                for event in events
            ],
            "workloads": [
                {
                    "id": str(workload.workload_id),
                    "className": workload.workload_class.value,
                    "state": workload.state.value,
                    "depth": self.decisions[workload.workload_id].selected_depth.value,
                    "score": self.decisions[workload.workload_id].score,
                    "primitives": [
                        primitive.value
                        for primitive in self.decisions[workload.workload_id].primitive_allowlist
                    ],
                }
                for workload in workloads
                if workload.workload_id in self.decisions
            ],
            "insights": self._decision_insights(entities, claims, events, workloads),
        }

    def _decision_insights(
        self,
        entities: list[Entity],
        claims: list[Claim],
        events: list[SemanticEventEnvelope],
        workloads: list[Workload],
    ) -> list[dict[str, object]]:
        insights: list[dict[str, object]] = []

        pending_approvals = [
            approval
            for approval in self.approvals.values()
            if approval.state == ApprovalState.REQUESTED
        ]
        if pending_approvals:
            blocked_workloads = {
                approval.workload_id
                for approval in pending_approvals
                if approval.workload_id in self.workloads
            }
            blocked_count = len(blocked_workloads)
            insights.append(
                {
                    "id": "approval-queue",
                    "severity": "critical",
                    "title": f"{len(pending_approvals)} approval request"
                    f"{'' if len(pending_approvals) == 1 else 's'} waiting",
                    "detail": f"{blocked_count} admitted workload"
                    f"{'' if blocked_count == 1 else 's'} cannot proceed until "
                    "governance responds.",
                    "action": "Review requested approvals before admitting deeper runs.",
                    "confidence": 0.98,
                    "signalCount": len(pending_approvals),
                }
            )

        critical_events = [
            event for event in events if self._event_severity(event) == "critical"
        ]
        if critical_events:
            latest = critical_events[0]
            insights.append(
                {
                    "id": "restricted-data",
                    "severity": "critical",
                    "title": "Restricted or regulated data entered the runtime",
                    "detail": f"Latest critical signal: {self._event_label(latest)}.",
                    "action": "Limit replay scope and require policy evaluation.",
                    "confidence": latest.source.authority_score,
                    "signalCount": len(critical_events),
                }
            )

        low_confidence_entities = [
            entity for entity in entities if entity.confidence.score < 0.55
        ]
        low_confidence_claims = [
            claim for claim in claims if claim.confidence.score < 0.55
        ]
        if low_confidence_entities or low_confidence_claims:
            weakest_entity = min(
                low_confidence_entities,
                key=lambda entity: entity.confidence.score,
                default=None,
            )
            weakest_claim = min(
                low_confidence_claims,
                key=lambda claim: claim.confidence.score,
                default=None,
            )
            weakest_score = min(
                [
                    item.confidence.score
                    for item in [weakest_entity, weakest_claim]
                    if item is not None
                ],
                default=0,
            )
            label = (
                weakest_entity.canonical_name
                if weakest_entity is not None
                else "a projected claim"
            )
            insights.append(
                {
                    "id": "confidence-floor",
                    "severity": "warning",
                    "title": "Confidence floor is below review threshold",
                    "detail": f"{label} is carrying {round(weakest_score * 100)}% confidence.",
                    "action": "Run reconciliation before high-impact reasoning.",
                    "confidence": max(0.6, 1 - weakest_score),
                    "signalCount": len(low_confidence_entities) + len(low_confidence_claims),
                }
            )

        claimed_entity_ids = {
            claim.subject_entity_id for claim in claims
        } | {
            claim.object_entity_id for claim in claims if claim.object_entity_id is not None
        }
        isolated_entities = [
            entity for entity in entities if entity.entity_id not in claimed_entity_ids
        ]
        if isolated_entities and claims:
            insights.append(
                {
                    "id": "graph-coverage",
                    "severity": "warning",
                    "title": "Graph context has isolated entities",
                    "detail": f"{len(isolated_entities)} of {len(entities)} entities have "
                    "no projected claim edges.",
                    "action": "Ingest relation claims or schedule reconciliation.",
                    "confidence": 0.86,
                    "signalCount": len(isolated_entities),
                }
            )

        stalled_workloads = [
            workload
            for workload in workloads
            if workload.state
            in {
                WorkloadState.DEFERRED_BUDGET,
                WorkloadState.DEFERRED_CAPACITY,
                WorkloadState.REJECTED_LOW_VALUE,
                WorkloadState.REJECTED_POLICY,
                WorkloadState.FAILED,
            }
        ]
        if stalled_workloads:
            latest_stalled = stalled_workloads[0]
            insights.append(
                {
                    "id": "workload-stalls",
                    "severity": "warning",
                    "title": "Scheduler is refusing or deferring work",
                    "detail": f"Latest stalled workload is {latest_stalled.state.value}.",
                    "action": "Inspect scheduler score components before retrying the objective.",
                    "confidence": 0.9,
                    "signalCount": len(stalled_workloads),
                }
            )

        if not insights:
            title = (
                "Runtime is ready for semantic input"
                if not events
                else "Runtime state is coherent"
            )
            detail = (
                "Ingest events, entities, and workloads to activate the decision queue."
                if not events
                else "No approval, risk, confidence, or coverage issue is above threshold."
            )
            insights.append(
                {
                    "id": "runtime-clear",
                    "severity": "normal",
                    "title": title,
                    "detail": detail,
                    "action": "Continue monitoring projected context and admitted workloads.",
                    "confidence": 0.82,
                    "signalCount": 0,
                }
            )

        severity_rank = {"critical": 0, "warning": 1, "normal": 2}
        return sorted(
            insights,
            key=lambda insight: (
                severity_rank[str(insight["severity"])],
                -float(insight["confidence"]),
                -int(insight["signalCount"]),
            ),
        )[:5]

    def _materialize_approvals(
        self,
        workload: Workload,
        decision: SchedulerDecision,
    ) -> list[Approval]:
        approvals: list[Approval] = []
        for approval_class in decision.required_approval_classes:
            approval_id = self._stable_uuid(
                "approval",
                str(workload.workload_id),
                approval_class,
            )
            approval = self.approvals.get(approval_id) or Approval(
                approval_id=approval_id,
                tenant_id=workload.tenant_id,
                workload_id=workload.workload_id,
                approval_class=approval_class,
            )
            self.approvals[approval_id] = approval
            approvals.append(approval)
        return approvals

    def _entity_payloads(self, payload: dict[str, object]) -> list[dict[str, object]]:
        values = self._payload_items(payload, "entity", "entities")
        if not values and self._looks_like_entity(payload):
            values.append(payload)
        return values

    def _claim_payloads(
        self,
        payload: dict[str, object],
        event_type: str,
    ) -> list[dict[str, object]]:
        values = self._payload_items(payload, "claim", "claims")
        if not values and event_type == "pci.graph.claim" and self._looks_like_claim(payload):
            values.append(payload)
        return values

    @staticmethod
    def _payload_items(
        payload: dict[str, object],
        singular_key: str,
        plural_key: str,
    ) -> list[dict[str, object]]:
        items: list[dict[str, object]] = []
        plural = payload.get(plural_key)
        if isinstance(plural, list):
            items.extend(item for item in plural if isinstance(item, dict))
        singular = payload.get(singular_key)
        if isinstance(singular, dict):
            items.append(singular)
        return items

    @staticmethod
    def _looks_like_entity(payload: dict[str, object]) -> bool:
        return any(key in payload for key in ("kind", "entity_kind")) and any(
            key in payload for key in ("canonical_name", "name", "title", "external_id")
        )

    @staticmethod
    def _looks_like_claim(payload: dict[str, object]) -> bool:
        return any(key in payload for key in ("predicate", "field")) and any(
            key in payload for key in ("subject_entity_id", "entity_id", "subject")
        )

    def _entity_from_payload(
        self,
        event: SemanticEventEnvelope,
        payload: dict[str, object],
    ) -> Entity | None:
        kind = self._text(payload, "kind", "entity_kind", "type")
        canonical_name = self._text(payload, "canonical_name", "name", "title", "external_id")
        if not kind or not canonical_name:
            return None

        entity_id = self._uuid_from_payload(payload, "entity_id", "id") or self._stable_uuid(
            "entity",
            str(event.tenant_id),
            event.source.source_system,
            kind,
            canonical_name,
        )
        aliases = payload.get("aliases")
        attributes = payload.get("attributes")
        return Entity(
            entity_id=entity_id,
            tenant_id=event.tenant_id,
            kind=self._normalize_token(kind),
            canonical_name=canonical_name,
            aliases=[str(alias) for alias in aliases] if isinstance(aliases, list) else [],
            confidence=self._confidence_from_payload(payload, event.source.authority_score),
            data_classification=self._data_classification_from_payload(payload, event),
            attributes=(
                attributes
                if isinstance(attributes, dict)
                else {"source_event_id": str(event.event_id)}
            ),
        )

    def _claim_from_payload(
        self,
        event: SemanticEventEnvelope,
        payload: dict[str, object],
    ) -> Claim | None:
        subject_id = self._uuid_from_payload(payload, "subject_entity_id", "entity_id")
        subject = payload.get("subject")
        if subject_id is None and isinstance(subject, dict):
            subject_entity = self._entity_from_payload(event, subject)
            if subject_entity is not None:
                self.entities[subject_entity.entity_id] = subject_entity
                subject_id = subject_entity.entity_id

        predicate = self._text(payload, "predicate", "field", "name")
        if subject_id is None or not predicate:
            return None

        object_entity_id = self._uuid_from_payload(payload, "object_entity_id")
        object_value = payload.get("object_value")
        if object_value is None and "value" in payload:
            object_value = payload["value"]

        evidence_ids = payload.get("evidence_ids")
        claim_id = self._uuid_from_payload(payload, "claim_id", "id") or self._stable_uuid(
            "claim",
            str(event.tenant_id),
            str(subject_id),
            predicate,
            str(object_entity_id or object_value),
        )
        return Claim(
            claim_id=claim_id,
            tenant_id=event.tenant_id,
            subject_entity_id=subject_id,
            predicate=self._normalize_token(predicate),
            object_entity_id=object_entity_id,
            object_value=object_value,
            state=self._claim_state_from_payload(payload),
            confidence=self._confidence_from_payload(payload, event.source.authority_score),
            source_event_id=event.event_id,
            evidence_ids=self._uuid_list(evidence_ids),
            observed_at=event.observed_at,
        )

    def _event_label(self, event: SemanticEventEnvelope) -> str:
        payload_label = self._text(event.payload, "label", "title", "summary", "name")
        return payload_label or event.event_type

    @staticmethod
    def _event_severity(event: SemanticEventEnvelope) -> str:
        high_risk_classifications = {
            DataClassification.RESTRICTED,
            DataClassification.REGULATED,
        }
        if event.data_classification in high_risk_classifications:
            return "critical"
        if any(tag in {"policy:critical", "severity:warning"} for tag in event.policy_tags):
            return "warning"
        return "normal"

    @staticmethod
    def _text(payload: dict[str, object], *keys: str) -> str | None:
        for key in keys:
            value = payload.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return None

    @staticmethod
    def _normalize_token(value: str) -> str:
        return value.strip().lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _uuid_from_payload(payload: dict[str, object], *keys: str) -> UUID | None:
        for key in keys:
            value = payload.get(key)
            if value is None:
                continue
            try:
                return UUID(str(value))
            except ValueError:
                continue
        return None

    @staticmethod
    def _uuid_list(value: object) -> list[UUID]:
        if not isinstance(value, list):
            return []
        parsed: list[UUID] = []
        for item in value:
            try:
                parsed.append(UUID(str(item)))
            except ValueError:
                continue
        return parsed

    @staticmethod
    def _stable_uuid(*parts: str) -> UUID:
        return uuid5(NAMESPACE_URL, ":".join(parts))

    def _confidence_from_payload(
        self,
        payload: dict[str, object],
        default_score: float,
    ) -> Confidence:
        confidence = payload.get("confidence")
        score = default_score
        band: ConfidenceBand | None = None
        if isinstance(confidence, dict):
            score = self._float(confidence.get("score"), score)
            band_value = confidence.get("band")
            if band_value is not None:
                try:
                    band = ConfidenceBand(str(band_value))
                except ValueError:
                    band = None
        score = self._float(payload.get("confidence_score"), score)
        return Confidence(
            score=score,
            band=band or self._band_for_score(score),
            authority_score=default_score,
            freshness_score=1.0,
            evidence_score=score,
            contradiction_penalty=1.0,
        )

    @staticmethod
    def _float(value: object, default: float) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return max(0.0, min(1.0, default))

    @staticmethod
    def _band_for_score(score: float) -> ConfidenceBand:
        if score >= 0.95:
            return ConfidenceBand.VERIFIED
        if score >= 0.75:
            return ConfidenceBand.HIGH
        if score >= 0.45:
            return ConfidenceBand.MEDIUM
        if score > 0:
            return ConfidenceBand.LOW
        return ConfidenceBand.UNKNOWN

    @staticmethod
    def _claim_state_from_payload(payload: dict[str, object]) -> ClaimState:
        state = payload.get("state")
        if state is None:
            return ClaimState.ASSERTED
        try:
            return ClaimState(str(state))
        except ValueError:
            return ClaimState.ASSERTED

    @staticmethod
    def _data_classification_from_payload(
        payload: dict[str, object],
        event: SemanticEventEnvelope,
    ) -> DataClassification:
        value = payload.get("data_classification")
        if value is None:
            return event.data_classification
        try:
            return DataClassification(str(value))
        except ValueError:
            return event.data_classification


store = InMemoryControlPlaneStore()
scheduler = WorkloadScheduler()


@router.get("/healthz", response_model=HealthResponse, tags=["system"])
async def healthz() -> HealthResponse:
    return HealthResponse(service=settings.service_name)


@router.get("/metrics", include_in_schema=False, response_class=PlainTextResponse)
async def metrics() -> str:
    workload_count = len(store.workloads)
    event_count = len(store.events)
    entity_count = len(store.entities)
    claim_count = len(store.claims)
    approval_count = len(store.approvals)
    return "\n".join(
        [
            "# HELP pci_control_plane_workloads_total "
            "Workloads tracked by the control plane process.",
            "# TYPE pci_control_plane_workloads_total gauge",
            f"pci_control_plane_workloads_total {workload_count}",
            "# HELP pci_control_plane_events_total Events tracked by the control plane process.",
            "# TYPE pci_control_plane_events_total gauge",
            f"pci_control_plane_events_total {event_count}",
            "# HELP pci_control_plane_entities_total Entities projected by the control plane.",
            "# TYPE pci_control_plane_entities_total gauge",
            f"pci_control_plane_entities_total {entity_count}",
            "# HELP pci_control_plane_claims_total Claims projected by the control plane.",
            "# TYPE pci_control_plane_claims_total gauge",
            f"pci_control_plane_claims_total {claim_count}",
            "# HELP pci_control_plane_approvals_total Approvals tracked by the control plane.",
            "# TYPE pci_control_plane_approvals_total gauge",
            f"pci_control_plane_approvals_total {approval_count}",
            "",
        ]
    )


@router.post(
    "/v1/events",
    response_model=EventIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["events"],
)
async def ingest_event(event: SemanticEventEnvelope) -> EventIngestResponse:
    projected_entities, projected_claims = store.put_event(event)
    return EventIngestResponse(
        event_id=event.event_id,
        accepted=True,
        stream=event.event_type,
        projected_entities=projected_entities,
        projected_claims=projected_claims,
    )


@router.get("/v1/control-plane/ui-state", tags=["system"])
async def control_plane_ui_state() -> dict[str, list[dict[str, object]]]:
    return store.ui_state()


@router.get("/v1/tenants/{tenant_id}/graph/entities", tags=["graph"])
async def list_entities(
    tenant_id: Annotated[UUID, Path()],
    kind: str | None = None,
    q: str | None = None,
    limit: int = 50,
) -> dict[str, list[Entity]]:
    entities = [entity for entity in store.entities.values() if entity.tenant_id == tenant_id]
    if kind:
        normalized_kind = kind.strip().lower().replace(" ", "_").replace("-", "_")
        entities = [entity for entity in entities if entity.kind == normalized_kind]
    if q:
        entities = [entity for entity in entities if q.lower() in entity.canonical_name.lower()]
    return {"entities": entities[: max(1, min(limit, 200))]}


@router.get(
    "/v1/tenants/{tenant_id}/graph/entities/{entity_id}",
    response_model=Entity,
    tags=["graph"],
)
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
    response = store.workload_response(workload_id)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workload not found")
    return response


@router.get("/v1/workloads/{workload_id}/approvals", tags=["governance"])
async def list_workload_approvals(workload_id: UUID) -> dict[str, list[Approval]]:
    if workload_id not in store.workloads:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workload not found")
    return {"approvals": store.approvals_for_workload(workload_id)}


@router.post(
    "/v1/workloads/{workload_id}/replay",
    response_model=ReplayResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["replay"],
)
async def create_replay_bundle(workload_id: UUID, request: ReplayRequest) -> ReplayResponse:
    replay = store.replay_bundle(workload_id, request)
    if replay is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workload not found")
    return replay


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
