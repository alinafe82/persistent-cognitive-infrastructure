# Semantic Data Model

## Model Goals

The context graph is a live context graph. It stores claims about the organization with confidence, provenance, temporal validity, causality, and embeddings. It is not chat history and it is not a transcript store.

## Core Types

### Entity

An entity is a durable thing in the world.

Examples:

- Repository
- Service
- Deployment
- Pull request
- Incident
- Customer
- Employee
- Team
- Policy
- Document
- Decision
- System
- Secret
- Data set
- Contract

### Relationship

A relationship connects entities with temporal validity and confidence.

Examples:

- `OWNS`
- `DEPENDS_ON`
- `DEPLOYED_TO`
- `AUTHORED_BY`
- `APPROVED_BY`
- `MENTIONS`
- `CONTRADICTS`
- `DERIVED_FROM`
- `AFFECTS`
- `SUPERSEDES`

### Claim

A claim is an assertion that may be true, false, stale, contradicted, or uncertain. Claims are first-class because the runtime operates over uncertain state.

Claim fields:

- `claim_id`
- `tenant_id`
- `subject_entity_id`
- `predicate`
- `object_value` or `object_entity_id`
- `claim_state`
- `valid_time_start`
- `valid_time_end`
- `observed_time`
- `confidence`
- `authority_score`
- `freshness_score`
- `source_event_id`
- `evidence_ids`
- `contradiction_set_id`
- `created_by_workload_id`

Claims move through an explicit lifecycle. See `docs/architecture/claim-lifecycle.md`.

### Evidence

Evidence links graph state to source systems, events, documents, tool observations, model outputs, and approvals.

### Temporal State

Every semantic assertion carries:

- `valid_time`: when the claim is true in the modeled world
- `observed_time`: when PCI observed it
- `transaction_time`: when PCI recorded it

This allows backdated source events, late webhooks, replay, and temporal reasoning.

## Confidence Model

Confidence is stored separately from truth. A claim can be useful, low-confidence, stale, or contradicted.

Base confidence:

```text
base = source_authority * extraction_quality * evidence_strength
```

Freshness adjustment:

```text
freshness = exp(-decay_rate * age_seconds)
```

Contradiction penalty:

```text
contradiction_penalty = 1 - max_confidence_of_active_contradicting_claims
```

Final confidence:

```text
confidence = clamp(base * freshness * contradiction_penalty * verification_multiplier, 0, 1)
```

## Compression Model

Raw events are retained according to tenant policy. Durable memory is created through:

- episodic summaries
- entity snapshots
- decision records
- incident narratives
- concept nodes
- relationship abstractions
- contradiction records
- policy-derived constraints

Compression never destroys provenance. A compressed memory points back to source events, claims, evidence, and workload lineage.

## Storage Strategy

Default storage:

- Postgres for entities, relationships, claims, events, approvals, lineage, and tenant metadata
- pgvector for embeddings and semantic retrieval
- Object storage for large artifacts, trace bundles, source snapshots, and replay packages
- Optional graph read projection into Neo4j, Memgraph, or JanusGraph for graph-heavy enterprise workloads

## Source Authority

Each source system declares what it owns:

- entity kinds
- fields
- freshness SLO
- reconciliation cadence
- rate limit
- adapter version
- auth profile reference
- failure policy
- replay support

This keeps source-of-truth decisions out of prompt text and inside a reviewable registry.

## Graph Query Patterns

High-value graph queries:

- Find services with degraded deployment confidence.
- Find claims contradicted by source-of-truth events.
- Find customer escalations that intersect recent deployments.
- Find pull requests that changed regulated code without policy evidence.
- Find stale ownership claims for production systems.
- Find decisions that depend on superseded policies.
- Find workloads that produced claims later invalidated by reconciliation.
