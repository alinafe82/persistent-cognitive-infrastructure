from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import exp

from app.domain.models import Confidence, ConfidenceBand


@dataclass(frozen=True)
class ConfidenceInputs:
    source_authority: float
    extraction_quality: float
    evidence_strength: float
    age_seconds: float
    decay_rate: float
    max_contradicting_confidence: float = 0.0
    verification_multiplier: float = 1.0


class ConfidenceCalculator:
    def calculate(self, inputs: ConfidenceInputs) -> Confidence:
        authority = self._clamp(inputs.source_authority)
        extraction = self._clamp(inputs.extraction_quality)
        evidence = self._clamp(inputs.evidence_strength)
        freshness = self._clamp(exp(-inputs.decay_rate * max(inputs.age_seconds, 0)))
        contradiction_penalty = self._clamp(1 - inputs.max_contradicting_confidence)
        verification = max(inputs.verification_multiplier, 0)

        score = self._clamp(authority * extraction * evidence * freshness * contradiction_penalty * verification)
        return Confidence(
            score=score,
            band=self.band(score, contradiction_penalty),
            authority_score=authority,
            freshness_score=freshness,
            evidence_score=evidence,
            contradiction_penalty=contradiction_penalty,
            calculated_at=datetime.now(UTC),
        )

    @staticmethod
    def band(score: float, contradiction_penalty: float = 1.0) -> ConfidenceBand:
        if contradiction_penalty <= 0.05:
            return ConfidenceBand.CONTRADICTED
        if score >= 0.92:
            return ConfidenceBand.VERIFIED
        if score >= 0.75:
            return ConfidenceBand.HIGH
        if score >= 0.45:
            return ConfidenceBand.MEDIUM
        if score > 0:
            return ConfidenceBand.LOW
        return ConfidenceBand.UNKNOWN

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

