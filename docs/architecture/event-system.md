# Semantic Event System

## Purpose

The semantic event bus carries normalized, tenant-scoped, schema-versioned events that describe meaningful changes in source systems or runtime state.

## Event Principles

1. Events are immutable.
2. Events are append-only.
3. Events carry tenant id, schema version, source, lineage, and causality.
4. Events represent semantic change, not implementation noise.
5. Events can be replayed into graph projections and scheduler decisions.
6. Events can be compacted into memory without losing provenance.

## Topic Taxonomy

| Topic | Meaning |
| --- | --- |
| `pci.world.repo` | Repository, branch, pull request, review, and commit events |
| `pci.world.deploy` | Deployment, rollout, rollback, environment, and drift events |
| `pci.world.incident` | Incident, alert, escalation, and postmortem events |
| `pci.world.customer` | Customer account, contract, support, and escalation events |
| `pci.world.policy` | Policy creation, updates, violations, and waivers |
| `pci.graph.claim` | Claim creation, update, contradiction, and confidence changes |
| `pci.workload.workload` | Workload lifecycle and scheduling decisions |
| `pci.workload.execution` | Primitive execution, tool observation, and model observation events |
| `pci.reconciliation` | Drift findings, source checks, confidence recalculations |
| `pci.memory` | Compression plans, memory candidates, memory promotions |
| `pci.governance.audit` | Policy decisions, approvals, access, and administrative actions |

## Event Envelope

Every event uses a common envelope:

- `event_id`
- `tenant_id`
- `event_type`
- `schema_version`
- `source`
- `source_event_id`
- `occurred_at`
- `observed_at`
- `published_at`
- `partition_key`
- `causation_id`
- `correlation_id`
- `trace_id`
- `actor`
- `data_classification`
- `payload`
- `payload_hash`

## Lineage

Lineage links events into causal chains:

```text
source event -> graph claim event -> workload event
-> execution observation event -> outcome claim event
-> reconciliation event -> memory compression event
```

## Replay

Replay modes:

- Rebuild graph projections from a tenant stream.
- Recompute scheduler decisions for a historical window.
- Rehydrate a workload from its event set.
- Rebuild confidence timelines for claims.
- Produce compliance evidence for a decision.

## Ordering

Partition keys must preserve causality for an entity or workload:

- Entity topics partition by `tenant_id:entity_id`.
- Workload topics partition by `tenant_id:workload_id`.
- Governance audit topics partition by `tenant_id:actor_id`.
- Reconciliation topics partition by `tenant_id:source_system:external_id`.

## Schema Evolution

Schemas are backward compatible within a major version. Event producers must:

- include `schema_version`
- avoid removing fields from active versions
- use additive fields for expansion
- publish migration notes
- register schema hashes before production rollout

## Dead Letter Handling

Invalid events are sent to `pci.system.dead_letter` with:

- validation error
- original envelope
- producer identity
- tenant id
- observed offset
- retry count
- operator action state

Dead-letter replay requires explicit operator approval when events affect graph state.
