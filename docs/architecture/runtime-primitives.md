# Core Runtime Primitives

PCI composes reasoning workloads from primitives. A primitive is a typed unit of work with explicit inputs, outputs, policies, observability, and replay behavior.

## Primitive Catalog

| Primitive | Purpose | Deterministic | Durable Output |
| --- | --- | --- | --- |
| `retrieve_context` | Fetch graph neighborhoods, embeddings, and source documents | Yes when snapshot-bound | Context bundle |
| `evaluate_policy` | Check RBAC, ABAC, data policy, and action policy | Yes | Policy decision |
| `rank_evidence` | Score evidence by authority, freshness, and relevance | Yes | Evidence ranking |
| `reason_symbolically` | Apply rules, constraints, and state machines | Yes | Derived claims |
| `reason_probabilistically` | Estimate uncertain outcomes using model or scorer | No | Scored hypotheses |
| `plan_execution` | Convert desired outcome into executable topology | No | Execution graph |
| `call_model` | Invoke an LLM through the model gateway | No | Model observation |
| `run_tool` | Invoke deterministic tool or MCP operation | Depends on tool | Tool observation |
| `execute_code` | Run code in sandbox | Yes when inputs pinned | Artifact and trace |
| `simulate` | Explore possible state transitions | Depends on engine | Simulation report |
| `verify_claims` | Validate claims against evidence and source systems | Yes for fixed sources | Verification result |
| `compress_memory` | Distill traces and episodes into reviewed summaries | No | Memory candidate |
| `reconcile_reality` | Check source-of-truth state and update confidence | Yes for fixed source snapshot | Reconciliation finding |
| `request_approval` | Pause for human authorization | Yes | Approval decision |
| `emit_semantic_event` | Persist semantic state changes | Yes | Event id and sequence |

## Primitive Contract

Every primitive must declare:

- `primitive_type`
- `input_schema`
- `output_schema`
- `required_capabilities`
- `data_classification`
- `policy_tags`
- `determinism_level`
- `replay_strategy`
- `timeout`
- `retry_policy`
- `cost_estimate`
- `telemetry_labels`
- `confidence_effect`

## Execution Graph

An execution graph is a directed acyclic graph of primitives for one workload. Cycles are modeled as Temporal workflow loops with explicit iteration limits and checkpoint events.

Node state:

- `pending`
- `admitted`
- `waiting_for_policy`
- `waiting_for_approval`
- `running`
- `retrying`
- `succeeded`
- `failed`
- `cancelled`
- `superseded`

Edge semantics:

- `requires_output`
- `requires_policy`
- `requires_approval`
- `validates`
- `enriches`
- `contradicts`
- `compresses`
- `emits`

## Workload Classes

| Class | Example | Scheduler Behavior |
| --- | --- | --- |
| Reactive | Incident opened | Low latency, high priority |
| Preventive | Deployment drift detected | Medium latency, confidence-driven |
| Exploratory | Explain ownership risk | Budget-capped, interactive |
| Reconciliation | GitHub branch protection changed | Source-authority prioritized |
| Compression | Weekly incident summary | Batch scheduled |
| Governance | Approval needed for production change | Blocking gate |

## Replay Model

Replay requires:

- Input event ids and stream offsets
- Graph snapshot ids
- Policy bundle version
- Model provider and model version
- Prompt and system instruction hashes
- Tool container image digests
- MCP server version
- Random seeds for stochastic components when supported
- Secrets reference ids, never secret values
- Output claims and evidence ids

Replay modes:

- `lineage_only`: show what happened without re-execution
- `deterministic`: rerun deterministic primitives
- `model_observed`: reuse captured model outputs
- `model_live`: call current model under explicit operator approval
- `source_snapshot`: replay against captured source snapshots
- `source_live`: replay against current source-of-truth systems
