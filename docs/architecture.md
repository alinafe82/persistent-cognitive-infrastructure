# Architecture

## Problem

Engineering teams lose time when codebase facts, operational ownership, and design decisions
drift away from their sources of truth. PCI is a scaffold for maintaining those facts as
claims with evidence, confidence, lineage, and reconciliation paths.

## Intended User

The intended user is a platform or engineering productivity team building internal systems for
codebase accuracy, service ownership, and operational review.

## Components

- Semantic event bus: normalizes codebase and operational events.
- Context graph: stores entities, claims, evidence, and confidence.
- Workload scheduler: decides when verification work should run.
- Runtime primitives: execute deterministic checks, tool calls, and governed model calls.
- Reconciliation engine: compares stored claims with source-of-truth systems.
- Control plane: exposes the API and early UI for runtime visibility.

## Data Flow

Events become claims in the graph. Claim changes, confidence decay, contradictions, or policy
rules create verification workloads. Workloads execute through typed primitives, produce
evidence, and update confidence or reconciliation state.

## Design Choices

I chose an event-derived claim model because stale internal knowledge is usually not fixed by a
chat surface. The system needs to know what it believes, why it believes it, and what should
invalidate that belief.

I kept LLM use behind typed runtime primitives. That allows model calls to be governed like any
other executor instead of giving them identity, authority, or ownership of stored state.

## What Is Not Built

This repository is not a completed runtime. Durable repositories, real connector adapters,
event consumers, a model gateway, and worker pools are not implemented yet.

## Extension Points

- Add source connectors for GitHub, CI, service catalogs, and incident systems.
- Implement durable repositories behind the API.
- Add worker pools for deterministic checks and governed model calls.
- Persist replay bundles for audits and debugging.

## Operational Considerations

A production implementation would need tenant isolation, secrets isolation, audit logs,
approval workflows, replay controls, cost controls, and explicit data retention rules.

## Testing Strategy

Current tests focus on runtime contracts. The next test layer should cover API behavior,
schema compatibility, scheduler decisions, and reconciliation outcomes with fixture-backed
source systems.
