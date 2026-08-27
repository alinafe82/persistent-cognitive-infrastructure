from __future__ import annotations

from datetime import UTC, datetime, tzinfo
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.models import (
    Claim,
    ClaimState,
    Confidence,
    ConfidenceBand,
    PrimitiveType,
    Workload,
    WorkloadClass,
    WorkloadCreate,
    WorkloadState,
)
from app.runtime.confidence import ConfidenceCalculator, ConfidenceInputs
from app.runtime.reconciliation import (
    RealityReconciliationEngine,
    ReconciliationFindingType,
    SourceSnapshot,
)
from app.runtime.scheduler import ResourcePressure, RuntimeSignals, WorkloadScheduler


def _confidence(score: float = 0.8) -> Confidence:
    return Confidence(
        score=score,
        band=ConfidenceBand.HIGH,
        authority_score=0.9,
        freshness_score=0.9,
        evidence_score=0.9,
        contradiction_penalty=1.0,
    )


class _NaiveTimezone(tzinfo):
    def utcoffset(self, dt: datetime | None):
        return None


def _claim(object_value: str = "main") -> Claim:
    return Claim(
        tenant_id=uuid4(),
        subject_entity_id=uuid4(),
        predicate="default_branch",
        object_value=object_value,
        confidence=_confidence(),
        observed_at=datetime.now(UTC),
    )


def test_confidence_calculator_marks_hard_contradiction() -> None:
    confidence = ConfidenceCalculator().calculate(
        ConfidenceInputs(
            source_authority=0.95,
            extraction_quality=1.0,
            evidence_strength=1.0,
            age_seconds=0,
            decay_rate=0.1,
            max_contradicting_confidence=0.98,
        )
    )

    assert confidence.band == ConfidenceBand.CONTRADICTED
    assert confidence.contradiction_penalty == 0.020000000000000018


def test_reconciliation_confirms_authoritative_claim() -> None:
    claim = _claim("main")
    snapshot = SourceSnapshot(
        source_system="github",
        external_id="repo-1",
        observed_at=datetime.now(UTC),
        values={"default_branch": "main"},
        authority_score=0.98,
    )

    finding = RealityReconciliationEngine().reconcile_claim(
        claim,
        snapshot,
        authoritative_fields={"default_branch"},
    )

    assert finding.finding_type == ReconciliationFindingType.CONFIRMED
    assert finding.resulting_claim_state == ClaimState.CONFIRMED
    assert finding.recalculated_confidence.band == ConfidenceBand.VERIFIED


def test_reconciliation_contradicts_existing_claim() -> None:
    claim = _claim("main")
    snapshot = SourceSnapshot(
        source_system="github",
        external_id="repo-1",
        observed_at=datetime.now(UTC),
        values={"default_branch": "trunk"},
        authority_score=0.9,
    )

    finding = RealityReconciliationEngine().reconcile_claim(
        claim,
        snapshot,
        authoritative_fields={"default_branch"},
    )

    assert finding.finding_type == ReconciliationFindingType.CONTRADICTED
    assert finding.resulting_claim_state == ClaimState.CONTRADICTED
    assert finding.recalculated_confidence.band == ConfidenceBand.CONTRADICTED
    assert finding.recalculated_confidence.score == 0


def test_scheduler_requires_policy_owner_for_high_policy_risk() -> None:
    workload = Workload(
        tenant_id=uuid4(),
        workload_class=WorkloadClass.GOVERNANCE,
        objective="Validate production deployment approval policy drift.",
        input_event_ids=[],
        input_entity_ids=[],
        requested_depth="standard",
    )
    decision = WorkloadScheduler().dry_run(
        workload,
        RuntimeSignals(
            urgency=0.9,
            expected_value=0.9,
            confidence_risk=0.8,
            drift_severity=0.7,
            policy_criticality=0.95,
            normalized_cost=0.2,
            resource_pressure=ResourcePressure(),
        ),
    )

    assert decision.admission_state == WorkloadState.ADMITTED_REQUIRES_APPROVAL
    assert "policy_owner" in decision.required_approval_classes
    assert PrimitiveType.REQUEST_APPROVAL in decision.primitive_allowlist


def test_workload_create_rejects_timezone_naive_deadline() -> None:
    with pytest.raises(ValidationError, match="deadline must be timezone-aware"):
        WorkloadCreate(
            tenant_id=uuid4(),
            workload_class=WorkloadClass.REACTIVE,
            objective="Investigate the active runtime incident.",
            deadline=datetime(2026, 8, 23, 12, 0),
        )

    with pytest.raises(ValidationError, match="deadline must be timezone-aware"):
        WorkloadCreate(
            tenant_id=uuid4(),
            workload_class=WorkloadClass.REACTIVE,
            objective="Investigate the active runtime incident.",
            deadline=datetime(2026, 8, 23, 12, 0, tzinfo=_NaiveTimezone()),
        )


def test_workload_rejects_timezone_naive_deadline_when_deserialized() -> None:
    with pytest.raises(ValidationError, match="deadline must be timezone-aware"):
        Workload(
            tenant_id=uuid4(),
            workload_class=WorkloadClass.REACTIVE,
            objective="Investigate the active runtime incident.",
            input_event_ids=[],
            input_entity_ids=[],
            requested_depth="standard",
            deadline=datetime(2026, 8, 23, 12, 0),
        )


def test_claim_rejects_reversed_valid_time_window() -> None:
    with pytest.raises(ValidationError, match="valid_time_end must be after"):
        Claim(
            tenant_id=uuid4(),
            subject_entity_id=uuid4(),
            predicate="deployment_window",
            object_value="closed",
            valid_time_start=datetime(2026, 8, 23, 12, 0, tzinfo=UTC),
            valid_time_end=datetime(2026, 8, 23, 11, 0, tzinfo=UTC),
            confidence=_confidence(),
        )


def test_claim_rejects_timezone_naive_valid_time() -> None:
    with pytest.raises(ValidationError, match="valid-time timestamps must be timezone-aware"):
        Claim(
            tenant_id=uuid4(),
            subject_entity_id=uuid4(),
            predicate="deployment_window",
            object_value="closed",
            valid_time_start=datetime(2026, 8, 23, 12, 0),
            confidence=_confidence(),
        )
