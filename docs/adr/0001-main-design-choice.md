# ADR 0001: Model Codebase Knowledge as Evidence-Backed Claims

## Status

Accepted

## Context

Internal tooling often stores summaries that become stale. Without evidence, source authority,
or invalidation rules, those summaries are hard to trust in reviews or incidents.

## Decision

PCI models shared codebase knowledge as claims with evidence, confidence, provenance, and
reconciliation paths back to source systems.

## Consequences

This makes the system more complex than a retrieval or chat application, but it gives platform
teams a clearer path for governance, replay, and correction. The current repo is a scaffold
that defines the contracts and boundaries before implementing the full runtime.
