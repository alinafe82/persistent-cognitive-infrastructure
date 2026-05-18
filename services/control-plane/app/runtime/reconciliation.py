from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from app.domain.models import Claim, ClaimState, Confidence, ConfidenceBand
from app.runtime.confidence import ConfidenceCalculator, ConfidenceInputs


class ReconciliationFindingType(StrEnum):
    CONFIRMED = "confirmed"
    DRIFTED = "drifted"
    CONTRADICTED = "contradicted"
    SOURCE_UNAVAILABLE = "source_unavailable"
    NOT_AUTHORITATIVE = "not_authoritative"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class SourceSnapshot:
    source_system: str
    external_id: str
    observed_at: datetime
    values: dict[str, Any]
    authority_score: float


@dataclass(frozen=True)
class ReconciliationFinding:
    finding_id: UUID
    tenant_id: UUID
    claim_id: UUID
    finding_type: ReconciliationFindingType
    resulting_claim_state: ClaimState
    checked_at: datetime
    previous_confidence: Confidence
    recalculated_confidence: Confidence
    evidence_ids: list[UUID]
    explanation: str


class RealityReconciliationEngine:
    def __init__(self, confidence_calculator: ConfidenceCalculator | None = None) -> None:
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()

    def reconcile_claim(
        self,
        claim: Claim,
        snapshot: SourceSnapshot | None,
        authoritative_fields: set[str],
    ) -> ReconciliationFinding:
        if snapshot is None:
            recalculated = self._degrade_for_unavailable_source(claim.confidence)
            return self._finding(
                claim,
                ReconciliationFindingType.SOURCE_UNAVAILABLE,
                claim.state,
                recalculated,
                "source snapshot was unavailable within the reconciliation deadline",
            )

        if claim.predicate not in authoritative_fields:
            return self._finding(
                claim,
                ReconciliationFindingType.NOT_AUTHORITATIVE,
                claim.state,
                claim.confidence,
                "source does not authoritatively own this predicate",
            )

        source_value = snapshot.values.get(claim.predicate)
        if source_value == claim.object_value:
            recalculated = self.confidence_calculator.calculate(
                ConfidenceInputs(
                    source_authority=snapshot.authority_score,
                    extraction_quality=1.0,
                    evidence_strength=max(claim.confidence.evidence_score, 0.8),
                    age_seconds=0,
                    decay_rate=0.000001,
                    verification_multiplier=1.1,
                )
            )
            return self._finding(
                claim,
                ReconciliationFindingType.CONFIRMED,
                ClaimState.CONFIRMED,
                recalculated,
                "source-of-truth value confirmed the claim",
            )

        if source_value is None:
            recalculated = self._degrade_for_drift(claim.confidence)
            return self._finding(
                claim,
                ReconciliationFindingType.DRIFTED,
                ClaimState.DRIFTED,
                recalculated,
                "source no longer contains the claimed predicate",
            )

        recalculated = Confidence(
            score=0.0,
            band=ConfidenceBand.CONTRADICTED,
            authority_score=claim.confidence.authority_score,
            freshness_score=claim.confidence.freshness_score,
            evidence_score=claim.confidence.evidence_score,
            contradiction_penalty=0.0,
            calculated_at=datetime.now(UTC),
        )
        return self._finding(
            claim,
            ReconciliationFindingType.CONTRADICTED,
            ClaimState.CONTRADICTED,
            recalculated,
            "source-of-truth value contradicted the claim",
        )

    def _degrade_for_unavailable_source(self, confidence: Confidence) -> Confidence:
        return self.confidence_calculator.calculate(
            ConfidenceInputs(
                source_authority=confidence.authority_score,
                extraction_quality=1.0,
                evidence_strength=confidence.evidence_score,
                age_seconds=86400,
                decay_rate=0.000002,
                verification_multiplier=0.92,
            )
        )

    def _degrade_for_drift(self, confidence: Confidence) -> Confidence:
        return self.confidence_calculator.calculate(
            ConfidenceInputs(
                source_authority=confidence.authority_score,
                extraction_quality=0.8,
                evidence_strength=confidence.evidence_score,
                age_seconds=86400,
                decay_rate=0.000006,
                verification_multiplier=0.75,
            )
        )

    def _finding(
        self,
        claim: Claim,
        finding_type: ReconciliationFindingType,
        resulting_claim_state: ClaimState,
        recalculated: Confidence,
        explanation: str,
    ) -> ReconciliationFinding:
        return ReconciliationFinding(
            finding_id=uuid4(),
            tenant_id=claim.tenant_id,
            claim_id=claim.claim_id,
            finding_type=finding_type,
            resulting_claim_state=resulting_claim_state,
            checked_at=datetime.now(UTC),
            previous_confidence=claim.confidence,
            recalculated_confidence=recalculated,
            evidence_ids=claim.evidence_ids,
            explanation=explanation,
        )
