# Architecture

PCI stores operational state as claims with provenance. A claim is useful only if the system can show where it came from, when it was observed, what evidence supports it, how confident it is, and which source can verify it.

## Runtime Loop

```text
source event
-> event envelope
-> graph projection
-> workload decision
-> execution graph
-> outcome claims
-> reconciliation
```

## Components

| Component | Owns | Output |
| --- | --- | --- |
| Event ingestion | Source adapters, validation, tenant partitioning | `SemanticEventEnvelope` |
| Event bus | Append-only event storage, replay offsets | Ordered event stream |
| Graph projector | Event-to-entity and event-to-claim writes | Entities, relationships, claims |
| Workload scheduler | Admission, priority, depth, budget, approvals | `SchedulerDecision` |
| Assembly engine | Primitive graph construction | `ExecutionGraph` |
| Execution runtime | Tool calls, model calls, sandbox jobs, MCP calls | Primitive observations |
| Reconciliation engine | Source checks and confidence updates | Reconciliation findings |
| Memory engine | Reviewed summaries with source links | Memory records |
| Policy layer | Access, data routing, approval gates | Policy decisions and audit events |

## State Rules

1. Events are append-only.
2. Graph writes come from events or administrative repair flows.
3. Generated claims require evidence links.
4. Claims store confidence separately from truth.
5. Reconciliation updates confidence and contradiction state; it does not silently overwrite history.
6. Replay bundles never contain secret values.
7. Model output is evidence, not authority.

## Storage

Default local storage:

- Postgres for tenants, events, entities, claims, relationships, approvals, workloads, and audit records
- pgvector for embeddings
- object storage for large artifacts, source snapshots, and replay bundles
- Redis for cache and transient coordination

Optional large-deployment projections:

- Kafka instead of NATS for existing Kafka shops
- Neo4j, Memgraph, or JanusGraph for graph-heavy read paths
- dedicated vector store for large embedding volumes

## Deployment

Local:

- Docker Compose
- FastAPI
- Postgres with pgvector
- NATS JetStream
- Temporal
- Redis
- Prometheus and Grafana

Kubernetes:

- API replicas behind ingress
- worker pools by primitive class
- separate sandbox node pool for code execution
- network policy on source-system and model-provider egress
- Vault or cloud secrets manager
- OPA or Cedar policy service

## First Slice

The first useful slice is codebase accuracy:

- ingest repository, pull request, manifest, ownership, CI, deployment, incident, and policy events
- project repositories, services, dependencies, APIs, tests, deployments, incidents, owners, policies, and claims
- schedule reconciliation when confidence drops or source state changes
- record verification lineage and replay metadata
- expose graph, event, claim, confidence, and reconciliation views
