# Implementation Plan

## 1. Repository Foundation

Build:

- public repository protection files
- CI and CodeQL
- dependency review
- security reporting
- no-personal-email verification

Done when:

- `scripts/verify.sh` passes
- branch protection settings are documented
- security contact uses a domain alias

## 2. Event Spine

Build:

- event envelope schema
- NATS JetStream streams
- event ingestion endpoint
- dead-letter stream
- replay cursor table

Done when:

- valid codebase and operational events are accepted
- invalid events are rejected or dead-lettered
- a tenant stream can be replayed from offset zero

## 3. Context Graph

Build:

- Postgres tables for entities, relationships, evidence, claims, and contradiction sets
- graph projector worker
- entity merge rules
- confidence calculation
- graph read API

Done when:

- repository, manifest, dependency, API, test, deployment, incident, owner, and policy events create graph records
- claims link to source events and evidence
- low-confidence and contradicted claims are queryable

## 4. Workload Scheduler

Build:

- scheduler scoring
- admission states
- resource pressure inputs
- policy-derived approvals
- dry-run API
- event coalescing

Done when:

- codebase drift, incident, and low-confidence events create workloads
- dry-run output explains score, depth, primitives, approvals, and rejection reasons
- duplicate event bursts do not create duplicate workloads

## 5. Execution Runtime

Build:

- Temporal worker
- primitive executor interface
- context retrieval primitive
- policy primitive
- verification primitive
- model call primitive
- source check primitive
- event emission primitive

Done when:

- each primitive writes trace metadata
- outcome claims include input event ids, graph snapshot id, policy decision id, and primitive observations
- replay can run in lineage-only mode

## 6. Reconciliation

Build:

- source authority registry
- source snapshot adapters
- drift findings
- confidence recalculation
- contradiction set updates

Done when:

- codebase and source-system changes lower or raise confidence through events
- contradictions are recorded without deleting old claims
- follow-up workloads are scheduled when drift exceeds threshold

## 7. Memory

Build:

- compression request API
- memory candidate records
- source-event and source-claim links
- review gate for sensitive summaries

Done when:

- summaries can be traced back to source claims and events
- sensitive summaries require approval before promotion

## 8. Control Plane UI

Build:

- event timeline
- codebase graph explorer
- workload inspector
- confidence view
- reconciliation findings view
- approval queue
- replay inspector

Done when:

- an operator can inspect a codebase claim, its evidence, confidence, source authority, reconciliation history, and workloads that changed it
