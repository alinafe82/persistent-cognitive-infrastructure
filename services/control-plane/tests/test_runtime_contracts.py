from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.models import (
    Claim,
    ClaimState,
    Confidence,
    ConfidenceBand,
    PrimitiveType,
    Workload,
    WorkloadClass,
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
