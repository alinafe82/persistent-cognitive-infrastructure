from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataClassification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    REGULATED = "regulated"


class ConfidenceBand(StrEnum):
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"


class ClaimState(StrEnum):
    ASSERTED = "asserted"
    CONFIRMED = "confirmed"
    DRIFTED = "drifted"
    CONTRADICTED = "contradicted"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    RETRACTED = "retracted"


class ReasoningDepth(StrEnum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    DEEP = "deep"
    EXHAUSTIVE = "exhaustive"


class WorkloadClass(StrEnum):
    REACTIVE = "reactive"
    PREVENTIVE = "preventive"
    EXPLORATORY = "exploratory"
    RECONCILIATION = "reconciliation"
    COMPRESSION = "compression"
    GOVERNANCE = "governance"


class WorkloadState(StrEnum):
    CANDIDATE = "candidate"
    REJECTED_LOW_VALUE = "rejected_low_value"
    REJECTED_POLICY = "rejected_policy"
    DEFERRED_BUDGET = "deferred_budget"
    DEFERRED_CAPACITY = "deferred_capacity"
    ADMITTED = "admitted"
    ADMITTED_REQUIRES_APPROVAL = "admitted_requires_approval"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class ReplayMode(StrEnum):
    GRAPH = "graph"
    WORKLOAD = "workload"
    LINEAGE = "lineage"


class ApprovalState(StrEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"


class PrimitiveType(StrEnum):
    RETRIEVE_CONTEXT = "retrieve_context"
    EVALUATE_POLICY = "evaluate_policy"
    RANK_EVIDENCE = "rank_evidence"
    REASON_SYMBOLICALLY = "reason_symbolically"
    REASON_PROBABILISTICALLY = "reason_probabilistically"
    PLAN_EXECUTION = "plan_execution"
    CALL_MODEL = "call_model"
    RUN_TOOL = "run_tool"
    EXECUTE_CODE = "execute_code"
    SIMULATE = "simulate"
    VERIFY_CLAIMS = "verify_claims"
    COMPRESS_MEMORY = "compress_memory"
    RECONCILE_REALITY = "reconcile_reality"
    REQUEST_APPROVAL = "request_approval"
    EMIT_SEMANTIC_EVENT = "emit_semantic_event"


class BaseContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=False, validate_assignment=True)


class SourceRef(BaseContract):
    source_system: str = Field(min_length=1)
    source_event_id: str | None = None
    external_url: str | None = None
    authority_score: float = Field(default=0.5, ge=0, le=1)


class SourceAuthorityProfile(BaseContract):
    source_system_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    name: str = Field(min_length=1)
    authority_score: float = Field(ge=0, le=1)
    owns_entity_kinds: list[str] = Field(default_factory=list)
    owns_fields: list[str] = Field(default_factory=list)
    freshness_slo_seconds: int = Field(default=86400, ge=1)
    reconciliation_cadence_seconds: int = Field(default=86400, ge=1)
    rate_limit_per_minute: int | None = Field(default=None, ge=1)
    auth_profile_ref: str | None = None
    failure_policy: str = "degrade_freshness"
    adapter_version: str = "unversioned"
    supports_replay: bool = False


class ActorRef(BaseContract):
    actor_id: str
    actor_type: str
    display_name: str | None = None
    source_system: str | None = None


class Confidence(BaseContract):
    score: float = Field(ge=0, le=1)
    band: ConfidenceBand
    authority_score: float = Field(default=0.5, ge=0, le=1)
    freshness_score: float = Field(default=1.0, ge=0, le=1)
    evidence_score: float = Field(default=0.5, ge=0, le=1)
    contradiction_penalty: float = Field(default=1.0, ge=0, le=1)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SemanticEventEnvelope(BaseContract):
    event_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    event_type: str = Field(pattern=r"^pci\.[a-z0-9_]+\.[a-z0-9_]+$")
    schema_version: str = Field(pattern=r"^v[0-9]+$")
    source: SourceRef
    occurred_at: datetime
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    published_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    partition_key: str = Field(min_length=1)
    causation_id: UUID | None = None
    correlation_id: UUID | None = None
    trace_id: str | None = None
    actor: ActorRef | None = None
    data_classification: DataClassification = DataClassification.INTERNAL
    policy_tags: list[str] = Field(default_factory=list)
    payload: dict[str, Any]
    payload_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")

    @field_validator("occurred_at", "observed_at", "published_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            msg = "timestamps must be timezone-aware"
            raise ValueError(msg)
        return value


class Entity(BaseContract):
    entity_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    kind: str
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    confidence: Confidence
    data_classification: DataClassification = DataClassification.INTERNAL
    attributes: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseContract):
    claim_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    subject_entity_id: UUID
    predicate: str
    object_entity_id: UUID | None = None
    object_value: dict[str, Any] | str | float | int | bool | None = None
    state: ClaimState = ClaimState.ASSERTED
    valid_time_start: datetime | None = None
    valid_time_end: datetime | None = None
    confidence: Confidence
    source_event_id: UUID | None = None
    evidence_ids: list[UUID] = Field(default_factory=list)
    contradiction_set_id: UUID | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WorkloadCreate(BaseContract):
    tenant_id: UUID
    workload_class: WorkloadClass
    objective: str = Field(min_length=8, max_length=2000)
    input_event_ids: list[UUID] = Field(default_factory=list)
    input_entity_ids: list[UUID] = Field(default_factory=list)
    requested_depth: ReasoningDepth = ReasoningDepth.STANDARD
    max_data_classification: DataClassification = DataClassification.INTERNAL
    policy_tags: list[str] = Field(default_factory=list)
    deadline: datetime | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)


class SchedulerDecision(BaseContract):
    decision_id: UUID = Field(default_factory=uuid4)
    workload_id: UUID
    tenant_id: UUID
    admitted: bool
    admission_state: WorkloadState
    score: float
    selected_depth: ReasoningDepth
    primitive_allowlist: list[PrimitiveType]
    required_approval_classes: list[str] = Field(default_factory=list)
    score_components: dict[str, float]
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Workload(BaseContract):
    workload_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    workload_class: WorkloadClass
    objective: str
    input_event_ids: list[UUID]
    input_entity_ids: list[UUID]
    requested_depth: ReasoningDepth
    selected_depth: ReasoningDepth | None = None
    state: WorkloadState = WorkloadState.CANDIDATE
    policy_tags: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    deadline: datetime | None = None

    @classmethod
    def from_create(cls, request: WorkloadCreate) -> Workload:
        return cls(
            tenant_id=request.tenant_id,
            workload_class=request.workload_class,
            objective=request.objective,
            input_event_ids=request.input_event_ids,
            input_entity_ids=request.input_entity_ids,
            requested_depth=request.requested_depth,
            policy_tags=request.policy_tags,
            constraints=request.constraints,
            deadline=request.deadline,
        )


class WorkloadResponse(BaseContract):
    workload_id: UUID
    tenant_id: UUID
    state: WorkloadState
    decision: SchedulerDecision
    approvals: list[Approval] = Field(default_factory=list)


class PrimitiveNode(BaseContract):
    node_id: str
    primitive_type: PrimitiveType
    depends_on_node_ids: list[str] = Field(default_factory=list)
    input: dict[str, Any] = Field(default_factory=dict)
    output_contract: dict[str, Any] = Field(default_factory=dict)
    policy_tags: list[str] = Field(default_factory=list)
    retry_policy: str = "bounded_exponential"
    timeout_seconds: int = Field(default=120, ge=1, le=3600)


class ExecutionGraph(BaseContract):
    execution_graph_id: UUID = Field(default_factory=uuid4)
    workload_id: UUID
    tenant_id: UUID
    nodes: list[PrimitiveNode]
    assembled_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    policy_bundle_version: str


class ReplayRequest(BaseContract):
    mode: ReplayMode
    include_artifacts: bool = False


class ReplayResponse(BaseContract):
    replay_id: UUID = Field(default_factory=uuid4)
    workload_id: UUID
    mode: ReplayMode
    state: str = "ready"
    event_count: int = Field(default=0, ge=0)
    entity_count: int = Field(default=0, ge=0)
    claim_count: int = Field(default=0, ge=0)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class ReconciliationRequest(BaseContract):
    tenant_id: UUID
    claim_ids: list[UUID] = Field(default_factory=list)
    entity_ids: list[UUID] = Field(default_factory=list)
    source_system: str | None = None


class MemoryCompressionRequest(BaseContract):
    tenant_id: UUID
    compression_type: str
    source_event_ids: list[UUID] = Field(default_factory=list)
    source_claim_ids: list[UUID] = Field(default_factory=list)


class ApprovalDecisionRequest(BaseContract):
    decision: ApprovalState
    reason: str = Field(min_length=3)


class Approval(BaseContract):
    approval_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    workload_id: UUID
    approval_class: str
    state: ApprovalState = ApprovalState.REQUESTED
    reason: str | None = None
    decided_at: datetime | None = None


class HealthResponse(BaseContract):
    status: str = "ok"
    service: str = "pci-control-plane"


class EventIngestResponse(BaseContract):
    event_id: UUID
    accepted: bool
    stream: str
    projected_entities: int = Field(default=0, ge=0)
    projected_claims: int = Field(default=0, ge=0)
