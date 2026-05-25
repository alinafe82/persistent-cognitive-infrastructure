# Persistent Cognitive Infrastructure

PCI is an event-driven runtime for maintaining accurate shared context about software systems. It ingests codebase and operational changes, stores claims in a context graph, schedules bounded verification workloads, runs those workloads through governed primitives, and reconciles stored claims against source-of-truth systems.

This repository is a public, protected scaffold. It defines contracts, schemas, runtime boundaries, deployment manifests, and an initial control-plane UI. It is not a completed runtime.

## What PCI Is

PCI models organizational state as event-derived claims:

```text
Codebase event -> graph claim -> verification workload -> verified outcome -> reconciliation update
```

The core loop is:

1. Normalize codebase and operational changes into semantic events.
2. Project events into entities, relationships, claims, evidence, and confidence scores.
3. Schedule workloads when graph state changes, confidence decays, contradictions appear, or policy requires review.
4. Assemble short-lived verification graphs from typed primitives.
5. Run primitives through Temporal workers, sandboxed jobs, MCP servers, model providers, and deterministic tools.
6. Persist only semantic outcomes, evidence, lineage, approvals, and memory records.
7. Reconcile important claims against authoritative systems.

## What PCI Is Not

PCI is not:

- a chatbot
- a personal assistant
- an agent framework
- a prompt-chain library
- a roleplay-worker system
- a named-worker abstraction

LLMs can be used by PCI, but they are executors behind typed contracts. They do not own identity, authority, or stored state.

## Category Boundary

PCI is not positioned as a personal assistant, chat surface, channel gateway, or autonomous coding tool. It is a backend runtime for codebase accuracy and shared state:

- event-sourced claims
- codebase facts with evidence
- evidence and provenance
- confidence scoring
- source authority
- contradiction handling
- workload scheduling
- policy-gated primitive execution
- replay metadata
- tenant isolation
- reconciliation against source systems

## Public Repository Posture

The repository is intended to be public. It includes MIT licensing, security reporting, CODEOWNERS, CI, CodeQL, dependency review, Dependabot, branch-protection guidance, and a no-personal-email public contact rule. Security reports use `security@repowave.dev`.

## Search Terms

Codebase accuracy, context graph, source-of-truth reconciliation, confidence scoring,
workload scheduling, governed execution, Temporal, Kubernetes, FastAPI, Next.js, and
observability.

## Architecture

| Component | Responsibility |
| --- | --- |
| Semantic event bus | Persist, route, and replay typed domain events |
| Context graph engine | Store entities, relationships, claims, evidence, embeddings, temporal validity, and confidence |
| Workload scheduler | Admit, defer, or reject workloads based on value, urgency, risk, cost, policy, and capacity |
| Assembly engine | Build short-lived execution graphs from typed primitives |
| Execution runtime | Run tools, code, MCP operations, model calls, and deterministic checks with telemetry |
| Reconciliation engine | Validate graph claims against authoritative systems and update confidence |
| Memory engine | Promote verified summaries, decisions, episodes, and abstractions with provenance |
| Governance layer | Enforce tenant isolation, access policy, approvals, audit, secrets isolation, and data routing |

See [docs/architecture.md](docs/architecture.md) for the shorter portfolio-oriented
architecture summary.

## Repository Map

```text
persistent-cognitive-infrastructure/
  docs/
    api/openapi.yaml
    architecture/
    diagrams/
    repository/quality-gates.md
    repository/public-protection.md
    roadmap/mvp.md
    security/threat-model.md
    strategy/codebase-accuracy.md
    strategy/go-to-market.md
    strategy/vision.md
  proto/pci/v1/
  schemas/json/
  schemas/sql/001_core.sql
  services/control-plane/
  frontend/control-plane/
  deployments/
  scripts/
```

## Local Development

Prerequisites:

- Docker with Compose v2
- Python 3.12
- Node 20+

Run the local services:

```bash
docker compose -f deployments/docker-compose.yml up --build
```

Run scaffold verification:

```bash
scripts/verify.sh
```

Run the UI:

```bash
cd frontend/control-plane
npm install
npm run dev
```

Default local endpoints:

- Control plane API: `http://localhost:8080`
- UI: `http://localhost:3000`
- Temporal UI: `http://localhost:8233`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- NATS monitoring: `http://localhost:8222`

## Current Implementation Status

Implemented:

- public repository governance files
- OpenAPI contract
- protobuf contracts
- JSON schemas
- Postgres graph schema
- FastAPI control-plane shell
- workload scheduler, confidence, reconciliation, and memory runtime modules
- claim lifecycle and source-authority contracts
- runtime regression tests
- Temporal workflow shape
- Docker Compose
- Kubernetes manifests
- Helm chart
- observability configs
- Next.js control-plane UI demo

Not implemented yet:

- durable database repositories behind the API
- NATS event publisher and consumers
- graph projector workers
- production policy engine integration
- real connector adapters
- model gateway
- sandbox worker pool
- persisted replay bundles

## Differentiation

Many adjacent systems focus on memory retrieval for model applications. PCI's narrower boundary is codebase accuracy and operational state control: source authority, claim lifecycle, policy-gated verification, replay metadata, and reconciliation against systems of record. The runtime is useful only if it can explain what it believes about a codebase, where that belief came from, how stale it is, and what would invalidate it.

## Interview Notes

See [docs/interview-notes.md](docs/interview-notes.md).
