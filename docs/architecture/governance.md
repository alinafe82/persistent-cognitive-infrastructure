# Trust and Governance Model

## Governance Goals

PCI must be safe enough for enterprise operations. Governance is part of the runtime, not an afterthought attached to user interfaces.

## Controls

| Control | Purpose |
| --- | --- |
| RBAC | Role-based access to tenants, domains, entities, and APIs |
| ABAC | Attribute-based decisions using data classification, source, action, and environment |
| Policy engine | OPA or Cedar policy evaluation for actions and runtime primitives |
| Approval workflows | Human gates for risky, expensive, sensitive, or irreversible operations |
| Audit log | Immutable record of access, policy decisions, approvals, and execution |
| Secrets isolation | Vault or cloud secrets manager, never persisted in replay bundles |
| Model governance | Provider allowlists, data classification routing, token budgets, retention settings |
| Tool governance | MCP/tool allowlists, capability scopes, side-effect classification |
| Data residency | Tenant and workload placement constraints |
| Explainability | Lineage from claim to events, tools, model calls, policies, and approvals |

## Policy Evaluation Points

Policy is evaluated at:

- event ingestion
- graph read
- workload admission
- primitive assembly
- model routing
- tool invocation
- code execution
- memory promotion
- reconciliation write
- export and replay

## Approval Classes

| Class | Examples | Required Approval |
| --- | --- | --- |
| `observe` | Read graph, fetch public repo metadata | None when authorized |
| `enrich` | Create low-risk derived claims | Automated policy |
| `recommend` | Produce recommendation for human action | Automated policy |
| `prepare_change` | Draft pull request, create ticket, prepare config | Single approver |
| `execute_change` | Merge, deploy, alter permissions | Dual approval when production or regulated |
| `export_sensitive` | Export customer, employee, legal, or security data | Data owner approval |
| `memory_promote_sensitive` | Persist compressed regulated memory | Data owner or compliance approval |

## Immutable Audit Events

Audit events include:

- actor
- tenant
- action
- target
- policy bundle version
- decision
- reason codes
- approval ids
- workload id
- trace id
- source IP or workload identity
- timestamp

Audit logs are written append-only and can be mirrored to customer SIEM.

## Secrets Model

Secrets are referenced by id. Workflows receive short-lived scoped credentials through the execution runtime. Replay bundles contain secret reference ids and access decisions, never secret values.

## Explainability Model

Every durable claim can be explained with:

- source events
- evidence
- graph neighborhood at decision time
- policy decisions
- model observations
- tool observations
- human approvals
- confidence timeline
- reconciliation results

