# Threat Model

## Scope

This threat model covers the PCI control plane, semantic event bus, context graph, workload scheduler, execution runtime, reconciliation engine, memory engine, governance layer, public repository, and deployment manifests.

## Assets

- tenant semantic graph
- source events
- durable claims
- execution traces
- model observations
- tool observations
- memory summaries
- replay bundles
- source-system credentials
- policy bundles
- approval records
- audit logs
- embeddings

## Actors

- unauthenticated internet user
- authenticated tenant user
- malicious tenant user
- compromised connector
- compromised MCP server
- malicious model output
- compromised execution worker
- maintainer with repository access
- cloud administrator

## Trust Boundaries

| Boundary | Main Risk | Control |
| --- | --- | --- |
| Public API | unauthorized access | OIDC, JWT validation, RBAC, ABAC |
| Tenant data | cross-tenant leakage | tenant-scoped queries, RLS, partitioning |
| Event ingestion | spoofed facts | signatures, schema validation, source authority |
| Model provider | data leakage | routing policy, redaction, provider retention controls |
| MCP server | tool abuse | capability scopes, sandboxing, policy checks |
| Code execution | arbitrary execution | ephemeral containers, no default egress, seccomp |
| Memory compression | false summaries | provenance, verification, review gates |
| Reconciliation | source poisoning | authority registry, signed adapters, drift evidence |
| Public repository | supply-chain compromise | branch protection, CODEOWNERS, CI, CodeQL, dependency review |

## Abuse Paths

### Prompt Injection Becomes Durable Claim

Risk:

Untrusted source text instructs a model to create false memory or call a tool.

Mitigations:

- model output is treated as evidence, not truth
- verification primitive required before durable claim emission
- source authority score limits confidence
- policy gate before side effects
- reconciliation later validates against source systems

### Cross-Tenant Graph Read

Risk:

An API query or graph projection reads another tenant's semantic state.

Mitigations:

- tenant id required in every graph contract
- database RLS in production
- tenant id in every event partition
- authorization checks at graph read and workload admission
- audit events for graph access

### Malicious MCP Server Exfiltrates Data

Risk:

An MCP server receives sensitive context and sends it outside approved channels.

Mitigations:

- tool allowlists
- data classification routing
- per-tool capability scopes
- sandbox egress controls
- redacted context bundles
- audit logs for every invocation

### Public Pull Request Weakens Runtime Boundary

Risk:

A public contribution bypasses policy, telemetry, or tenant isolation.

Mitigations:

- CODEOWNERS
- required reviews
- required CI
- CodeQL
- dependency review
- design review requirement for sensitive areas
- protected branch rules

### Stale Memory Drives Wrong Action

Risk:

Compressed memory persists after source-of-truth reality changes.

Mitigations:

- memory links to source claims
- confidence decay
- scheduled reconciliation
- contradiction sets
- review-after timestamps
- source authority registry

## Security Requirements

- no personal maintainer emails in public source
- no production secrets in public source
- all side effects require policy evaluation
- regulated data routes only to approved providers
- replay bundles exclude secret values
- every durable semantic mutation has provenance
- every high-risk workload emits audit evidence

