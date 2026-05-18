# Deployment Topology

## Local Development

Local development uses Docker Compose:

- control plane API
- Postgres with pgvector
- NATS JetStream
- Redis
- Temporal
- OpenTelemetry collector
- Prometheus
- Grafana

This keeps PCI runnable on one machine while preserving production-like contracts.

## Single-Tenant Self-Hosted

Recommended topology:

- one Kubernetes cluster
- one PCI namespace
- managed or in-cluster Postgres
- NATS JetStream
- Temporal self-hosted
- object storage compatible with S3
- OPA sidecar or central policy service
- Vault or cloud secrets manager
- ingress with OIDC

## Multi-Tenant Enterprise

Recommended topology:

- separate control plane and execution namespaces
- tenant partitioning at database, stream, and object-storage layers
- dedicated connector workers for sensitive systems
- separate node pools for sandbox execution
- network policies between services
- Kafka or NATS supercluster
- Temporal namespaces per tenant or domain
- per-tenant encryption keys
- SIEM audit export
- data residency placement rules

## High Availability

| Component | HA Strategy |
| --- | --- |
| Control plane API | Horizontal replicas behind ingress |
| Event bus | Replicated streams or Kafka partitions |
| Postgres | Managed HA or CloudNativePG |
| Temporal | Multi-replica frontend, history, matching, worker services |
| Redis | HA Redis or replaceable cache |
| Workers | Horizontal autoscaling by queue lag |
| Object storage | Managed replicated storage |
| Policy service | Multiple replicas with cached bundles |
| Observability | Remote write for metrics and durable log backend |

## Network Zones

- Public ingress zone: UI and API ingress only
- Control zone: API, scheduler, policy, graph query
- Data zone: Postgres, event bus, object storage
- Execution zone: workers, sandboxes, model gateway, MCP adapters
- Connector zone: egress-controlled access to SaaS and internal systems
- Observability zone: collectors, metrics, logs, traces

## Production Release Strategy

1. Deploy database migrations.
2. Deploy event schemas and compatibility checks.
3. Roll out stateless API and scheduler.
4. Roll out workers by primitive class.
5. Enable connector sources in read-only observe mode.
6. Enable graph projection.
7. Enable scheduler admission for low-risk workloads.
8. Enable approvals and higher-risk workloads.
9. Enable memory promotion after governance review.

