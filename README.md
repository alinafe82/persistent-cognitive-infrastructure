# Persistent Cognitive Infrastructure

An event-driven runtime that maintains accurate shared context about a software system. It ingests codebase and operational changes, stores them as claims with evidence and confidence, schedules verification workloads when the graph state changes, runs those workloads through typed primitives, and reconciles its claims against source-of-truth systems.

This repo holds a runnable local control plane (FastAPI, in-memory repositories), the public contracts (OpenAPI, protobuf, JSON schemas, Postgres DDL), deployment manifests (Docker Compose, Kubernetes, Helm), and a Next.js UI backed by the control-plane API. Production durability, connectors, and worker pools are explicitly not in this repository yet; the "Current implementation status" section below lists the boundary.

## Five-minute local demo

In one terminal, start the local stack and leave it running:

```bash
docker compose -f deployments/docker-compose.yml up --build
```

In a second terminal, run the static-and-structural verifier:

```bash
scripts/verify.sh
```

What `scripts/verify.sh` actually does: `python -m compileall`, repository-shape checks (required directories, OpenAPI/JSON-schema validity), and a guard against pitch-style language in the README. It does **not** hit `localhost:8080` or run the API regression suite in `services/control-plane/tests`. Treat a passing verifier as evidence of structural sanity, not live runtime health.

For live API testing run the control-plane suite directly:

```bash
cd services/control-plane
pytest -q
```

For the UI (separate process, not part of `docker compose` above):

```bash
cd frontend/control-plane
npm install
npm run dev
```

What is not exercised by any of the above: Temporal worker pools, NATS publishing, durable Postgres, real connectors, the model gateway. Those are listed in "Current implementation status" and intentionally not yet implemented.

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

Run runtime verification:

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
- FastAPI control-plane API with in-memory event projection, workload admission, approvals, and replay bundles
- workload scheduler, confidence, reconciliation, and memory runtime modules
- claim lifecycle and source-authority contracts
- runtime regression tests
- Temporal workflow shape
- Docker Compose
- Kubernetes manifests
- Helm chart
- observability configs
- Next.js control-plane UI backed by the API snapshot endpoint

Not implemented yet:

- durable database repositories behind the API
- NATS event publisher and consumers
- external graph projector workers
- production policy engine integration
- real connector adapters
- model gateway
- sandbox worker pool
- persisted replay bundle storage

## Differentiation

Most adjacent systems are memory retrieval for model applications. PCI's narrower boundary is codebase accuracy and operational state control: source authority, claim lifecycle, policy-gated verification, replay metadata, and reconciliation against systems of record. The runtime earns its keep when it can explain what it believes about a codebase, where that belief came from, how stale it is, and what would invalidate it.

If those four questions are not interesting to your problem, you do not need this. Use a vector store and call it done.

## Interview Notes

See [docs/interview-notes.md](docs/interview-notes.md).
