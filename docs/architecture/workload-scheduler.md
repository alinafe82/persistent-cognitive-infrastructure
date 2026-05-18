# Workload Scheduler Design

## Role

The workload scheduler allocates reasoning work. It decides which semantic events and graph deltas justify a workload, which primitives are allowed, what depth is needed, what policies apply, and how much latency or cost is acceptable.

It is not a cron scheduler and it is not an agent router.

## Inputs

- Semantic events
- Graph deltas
- Claim confidence changes
- Reconciliation findings
- Tenant budgets
- Policy constraints
- Workload class
- Source authority
- User or system priority
- Runtime capacity
- Historical success and cost
- SLOs and deadlines

## Outputs

- `Workload`
- admission decision
- priority class
- reasoning depth
- primitive allowlist
- model routing constraints
- required approvals
- retry strategy
- trace sampling policy
- deadline and cancellation policy

## Scoring Model

The scheduler scores candidate workloads with:

```text
score =
  urgency_weight * urgency
+ value_weight * expected_value
+ risk_weight * confidence_risk
+ drift_weight * drift_severity
+ policy_weight * policy_criticality
- cost_weight * normalized_cost
- saturation_weight * resource_pressure
```

The score is adjusted by tenant quotas, cooldown windows, dependency readiness, and approval requirements.

## Reasoning Depth

| Depth | Use Case | Primitive Set |
| --- | --- | --- |
| `minimal` | Low-risk enrichment | retrieval, deterministic checks |
| `standard` | Normal operational reasoning | retrieval, policy, model call, verification |
| `deep` | Incidents, contradictions, high-risk decisions | decomposition, multiple evidence paths, simulation, verification |
| `exhaustive` | Regulated or irreversible actions | deep path plus approvals, replay bundle, independent verifier |

## Admission States

- `candidate`
- `rejected_low_value`
- `rejected_policy`
- `deferred_budget`
- `deferred_capacity`
- `admitted`
- `admitted_requires_approval`
- `superseded`

## Capacity Management

Capacity is measured across:

- workflow slots
- model provider token budgets
- connector API budgets
- sandbox CPU and memory
- graph query pressure
- event lag
- tenant spend budget
- human approval queue depth

## Anti-Storm Controls

The scheduler must prevent workload storms:

- entity-level cooldowns
- contradiction-set grouping
- event coalescing windows
- deduplication by payload hash and causality
- priority decay for repeated low-value workloads
- tenant circuit breakers
- source-system backpressure

## Deterministic Dry Run

The scheduler exposes a dry-run endpoint so operators can inspect why a workload would be admitted or rejected without executing it. Dry runs must return:

- score components
- policy constraints
- selected reasoning depth
- expected cost
- selected primitives
- required approvals
- resource pressure snapshot

