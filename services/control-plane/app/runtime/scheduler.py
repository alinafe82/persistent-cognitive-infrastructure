from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.models import (
    Workload,
    PrimitiveType,
    ReasoningDepth,
    SchedulerDecision,
    WorkloadClass,
    WorkloadState,
)


@dataclass(frozen=True)
class SchedulerWeights:
    urgency: float = 0.22
    expected_value: float = 0.24
    confidence_risk: float = 0.2
    drift_severity: float = 0.16
    policy_criticality: float = 0.12
    normalized_cost: float = 0.04
    resource_pressure: float = 0.02


@dataclass(frozen=True)
class ResourcePressure:
    workflow_slots: float = 0.0
    model_budget: float = 0.0
    connector_budget: float = 0.0
    graph_pressure: float = 0.0
    approval_queue: float = 0.0

    def normalized(self) -> float:
        values = [
            self.workflow_slots,
            self.model_budget,
            self.connector_budget,
            self.graph_pressure,
            self.approval_queue,
        ]
        return max(0.0, min(1.0, sum(values) / len(values)))


@dataclass(frozen=True)
class RuntimeSignals:
    urgency: float
    expected_value: float
    confidence_risk: float
    drift_severity: float
    policy_criticality: float
    normalized_cost: float
    resource_pressure: ResourcePressure


class WorkloadScheduler:
    def __init__(self, weights: SchedulerWeights | None = None) -> None:
        self.weights = weights or SchedulerWeights()

    def dry_run(self, workload: Workload, signals: RuntimeSignals | None = None) -> SchedulerDecision:
        active_signals = signals or self._default_signals(workload)
        components = self._score_components(active_signals)
        score = round(sum(components.values()), 4)
        selected_depth = self._select_depth(workload, score, active_signals)
        required_approvals = self._required_approvals(workload, selected_depth, active_signals)
        admitted, state = self._admission(score, active_signals, required_approvals)

        return SchedulerDecision(
            decision_id=uuid4(),
            workload_id=workload.workload_id,
            tenant_id=workload.tenant_id,
            admitted=admitted,
            admission_state=state,
            score=score,
            selected_depth=selected_depth,
            primitive_allowlist=self._primitive_allowlist(workload.workload_class, selected_depth),
            required_approval_classes=required_approvals,
            score_components=components,
            decided_at=datetime.now(UTC),
        )

    def admit(self, workload: Workload, signals: RuntimeSignals | None = None) -> SchedulerDecision:
        decision = self.dry_run(workload, signals)
        workload.selected_depth = decision.selected_depth
        workload.state = decision.admission_state
        workload.updated_at = datetime.now(UTC)
        return decision

    def _score_components(self, signals: RuntimeSignals) -> dict[str, float]:
        pressure = signals.resource_pressure.normalized()
        return {
            "urgency": self.weights.urgency * self._clamp(signals.urgency),
            "expected_value": self.weights.expected_value * self._clamp(signals.expected_value),
            "confidence_risk": self.weights.confidence_risk * self._clamp(signals.confidence_risk),
            "drift_severity": self.weights.drift_severity * self._clamp(signals.drift_severity),
            "policy_criticality": self.weights.policy_criticality * self._clamp(signals.policy_criticality),
            "cost_penalty": -self.weights.normalized_cost * self._clamp(signals.normalized_cost),
            "resource_penalty": -self.weights.resource_pressure * pressure,
        }

    def _select_depth(
        self,
        workload: Workload,
        score: float,
        signals: RuntimeSignals,
    ) -> ReasoningDepth:
        if workload.requested_depth == ReasoningDepth.EXHAUSTIVE:
            return ReasoningDepth.EXHAUSTIVE
        if signals.policy_criticality >= 0.85 or signals.confidence_risk >= 0.9:
            return ReasoningDepth.EXHAUSTIVE
        if workload.requested_depth == ReasoningDepth.DEEP or score >= 0.68:
            return ReasoningDepth.DEEP
        if score >= 0.32:
            return ReasoningDepth.STANDARD
        return ReasoningDepth.MINIMAL

    def _required_approvals(
        self,
        workload: Workload,
        depth: ReasoningDepth,
        signals: RuntimeSignals,
    ) -> list[str]:
        approvals: list[str] = []
        if depth == ReasoningDepth.EXHAUSTIVE:
            approvals.append("high_risk_workload")
        if "side_effect:external" in workload.policy_tags:
            approvals.append("external_side_effect")
        if signals.policy_criticality >= 0.75:
            approvals.append("policy_owner")
        return sorted(set(approvals))

    def _admission(
        self,
        score: float,
        signals: RuntimeSignals,
        required_approvals: list[str],
    ) -> tuple[bool, WorkloadState]:
        if signals.resource_pressure.normalized() >= 0.95:
            return False, WorkloadState.DEFERRED_CAPACITY
        if score < 0.15:
            return False, WorkloadState.REJECTED_LOW_VALUE
        if required_approvals:
            return True, WorkloadState.ADMITTED_REQUIRES_APPROVAL
        return True, WorkloadState.ADMITTED

    def _primitive_allowlist(
        self,
        workload_class: WorkloadClass,
        depth: ReasoningDepth,
    ) -> list[PrimitiveType]:
        primitives = [
            PrimitiveType.RETRIEVE_CONTEXT,
            PrimitiveType.EVALUATE_POLICY,
            PrimitiveType.RANK_EVIDENCE,
            PrimitiveType.VERIFY_CLAIMS,
            PrimitiveType.EMIT_SEMANTIC_EVENT,
        ]
        if depth in {ReasoningDepth.STANDARD, ReasoningDepth.DEEP, ReasoningDepth.EXHAUSTIVE}:
            primitives.extend([PrimitiveType.CALL_MODEL, PrimitiveType.REASON_SYMBOLICALLY])
        if depth in {ReasoningDepth.DEEP, ReasoningDepth.EXHAUSTIVE}:
            primitives.extend([PrimitiveType.REASON_PROBABILISTICALLY, PrimitiveType.SIMULATE])
        if workload_class == WorkloadClass.RECONCILIATION:
            primitives.append(PrimitiveType.RECONCILE_REALITY)
        if workload_class == WorkloadClass.COMPRESSION:
            primitives.append(PrimitiveType.COMPRESS_MEMORY)
        if depth == ReasoningDepth.EXHAUSTIVE:
            primitives.append(PrimitiveType.REQUEST_APPROVAL)
        return sorted(set(primitives), key=lambda value: value.value)

    def _default_signals(self, workload: Workload) -> RuntimeSignals:
        class_defaults = {
            WorkloadClass.REACTIVE: (0.85, 0.75, 0.55, 0.45, 0.4, 0.5),
            WorkloadClass.PREVENTIVE: (0.45, 0.65, 0.7, 0.7, 0.45, 0.4),
            WorkloadClass.EXPLORATORY: (0.3, 0.45, 0.35, 0.2, 0.25, 0.6),
            WorkloadClass.RECONCILIATION: (0.65, 0.7, 0.85, 0.9, 0.55, 0.45),
            WorkloadClass.COMPRESSION: (0.25, 0.55, 0.3, 0.25, 0.35, 0.35),
            WorkloadClass.GOVERNANCE: (0.75, 0.7, 0.6, 0.4, 0.95, 0.3),
        }
        urgency, value, risk, drift, policy, cost = class_defaults[workload.workload_class]
        return RuntimeSignals(
            urgency=urgency,
            expected_value=value,
            confidence_risk=risk,
            drift_severity=drift,
            policy_criticality=policy,
            normalized_cost=cost,
            resource_pressure=ResourcePressure(),
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

