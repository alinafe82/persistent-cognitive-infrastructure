# Service Boundaries

## Boundary Map

| Service | Owns | Does Not Own | Scaling Unit |
| --- | --- | --- | --- |
| Control Plane API | Tenant API, workload submission, graph reads, approvals, replay metadata | Long-running execution, connector polling | Horizontal FastAPI replicas |
| Event Ingestion | Webhooks, CDC adapters, MCP event adapters, schema normalization | Scheduling decisions, memory compression | Connector worker groups |
| Event Router | Topic routing, event persistence, replay cursors, lineage indexes | Semantic interpretation | NATS streams or Kafka partitions |
| Graph Projector | Event-to-graph materialization, claim state transitions, embeddings | Workflow execution | Projection workers by tenant and topic |
| Workload Scheduler | Workload scoring, routing, budgets, priority queues | Primitive execution | Scheduler replicas with leader election |
| Assembly Engine | Execution graph generation, policy compilation, primitive selection | External side effects | Stateless workers |
| Execution Runtime | Tool calls, code sandboxing, MCP invocation, LLM calls, deterministic activities | Graph authority | Temporal workers and Kubernetes jobs |
| Reconciliation Engine | Source-of-truth checks, drift detection, contradiction creation, confidence updates | Initial ingestion normalization | Reconciliation workers by connector |
| Memory Engine | Compression, distillation, snapshotting, retention, abstraction lifecycle | Policy authorization | Batch and streaming workers |
| Governance Service | RBAC, ABAC, policy decisions, approval state, audit events | Business-specific reasoning | Policy evaluators and audit writers |
| Model Gateway | Provider routing, model policy, token accounting, safety constraints | Workload scheduling | Provider-specific pools |
| UI Control Plane | Graph explorer, topology visualizer, timelines, approvals, replay inspector | Direct mutation of runtime state | Next.js app replicas |

## Core Ownership Rules

1. The event bus owns immutable event ordering, not truth.
2. The context graph owns current semantic state, not execution.
3. The scheduler owns admission and priority, not generated output.
4. The assembly engine owns topology, not external side effects.
5. The execution runtime owns side-effect execution, not source-of-truth mutation outside approved tools.
6. The reconciliation engine owns confidence correction, not arbitrary deletion.
7. The memory engine owns compression and retention, not policy exceptions.
8. Governance owns authorization and audit, not workload strategy.

## Write Paths

### Event Ingestion Write Path

```text
Connector -> Event Normalizer -> Schema Validation -> Event Bus -> Graph Projector -> Context Graph
```

### Workload Outcome Write Path

```text
Temporal Workflow -> Outcome Claims -> Policy Check -> Event Bus -> Graph Projector -> Context Graph
```

### Reconciliation Write Path

```text
Source Check -> Drift Finding -> Reconciliation Event -> Event Bus -> Graph Projector -> Confidence Update
```

### Memory Compression Write Path

```text
Trace Bundle -> Compression Plan -> Distilled Claims -> Review Gate when required -> Event Bus -> Graph Projection
```

## Trust Boundaries

| Boundary | Risk | Required Controls |
| --- | --- | --- |
| External SaaS connectors | Spoofed events, stale webhooks, overbroad tokens | Signature validation, least-privilege tokens, source authority registry |
| LLM provider boundary | Data leakage, nondeterminism, prompt injection | Provider policies, redaction, prompt provenance, output claim validation |
| MCP server boundary | Tool misuse, data exfiltration, untrusted responses | Tool allowlists, sandboxing, response provenance, approval gates |
| Code execution boundary | Arbitrary execution, lateral movement | Ephemeral containers, network policy, seccomp, read-only mounts |
| Tenant boundary | Cross-tenant leakage | Tenant-scoped keys, RLS, partition isolation, per-tenant audit |
| Approval boundary | Unauthorized side effects | Signed approvals, dual control for high-risk actions, immutable audit |

## API Boundary

The public API never exposes provider-specific prompts, raw secrets, or internal scheduler queues. It exposes semantic events, graph entities, workloads, approvals, confidence state, and replay handles.

## Internal Boundary

Internal services communicate through semantic events and typed workflow commands. Synchronous calls are reserved for low-latency reads such as policy decisions, tenant configuration, and graph query plans.
