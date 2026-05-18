from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.models import DataClassification


class MemoryType(StrEnum):
    EPISODIC = "episodic"
    HIERARCHICAL = "hierarchical"
    CONCEPT = "concept"
    TEMPORAL = "temporal"
    DECISION = "decision"
    CONTRADICTION = "contradiction"


@dataclass(frozen=True)
class MemoryImportanceSignals:
    business_impact: float
    recurrence_value: float
    policy_relevance: float
    relationship_centrality: float
    future_query_likelihood: float
    contradiction_value: float
    redundancy_penalty: float
    sensitivity_penalty: float


@dataclass(frozen=True)
class MemoryCandidate:
    memory_id: UUID
    tenant_id: UUID
    memory_type: MemoryType
    title: str
    body: str
    source_event_ids: list[UUID]
    source_claim_ids: list[UUID]
    confidence_score: float
    importance_score: float
    data_classification: DataClassification
    created_at: datetime


class MemoryCompressionEngine:
    def score_importance(self, signals: MemoryImportanceSignals) -> float:
        positive = (
            signals.business_impact
            + signals.recurrence_value
            + signals.policy_relevance
            + signals.relationship_centrality
            + signals.future_query_likelihood
            + signals.contradiction_value
        ) / 6
        penalty = (signals.redundancy_penalty + signals.sensitivity_penalty) / 2
        return self._clamp(positive * 0.82 + (1 - penalty) * 0.18)

    def create_candidate(
        self,
        tenant_id: UUID,
        memory_type: MemoryType,
        title: str,
        body: str,
        source_event_ids: list[UUID],
        source_claim_ids: list[UUID],
        confidence_score: float,
        importance_signals: MemoryImportanceSignals,
        data_classification: DataClassification,
    ) -> MemoryCandidate:
        if not source_event_ids and not source_claim_ids:
            msg = "memory candidates require event or claim provenance"
            raise ValueError(msg)
        return MemoryCandidate(
            memory_id=uuid4(),
            tenant_id=tenant_id,
            memory_type=memory_type,
            title=title,
            body=body,
            source_event_ids=source_event_ids,
            source_claim_ids=source_claim_ids,
            confidence_score=self._clamp(confidence_score),
            importance_score=self.score_importance(importance_signals),
            data_classification=data_classification,
            created_at=datetime.now(UTC),
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

