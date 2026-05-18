# Contributing

PCI is public by default and protected by review, provenance, and security
controls. Contributions should strengthen the runtime contracts rather than
turn it into an assistant framework.

## Development Rules

- Keep runtime primitives typed, observable, and replayable.
- Keep durable semantic state separate from ephemeral execution topology.
- Treat model output as evidence, not truth.
- Add tests for scheduler, policy, reconciliation, and graph-state changes.
- Do not introduce hidden network calls or implicit side effects.
- Do not commit secrets, private data, generated tenant traces, or credentials.
- Preserve tenant isolation in every API and storage path.

## Pull Request Requirements

Every pull request should include:

- clear problem statement
- implementation summary
- test evidence
- migration notes when schemas change
- security impact notes for new tools, providers, connectors, or side effects
- observability notes for new runtime paths

## Commit Style

Use focused commits with imperative subjects:

```text
Add semantic event envelope schema
Enforce tenant scope in graph queries
Record replay metadata for model calls
```

## Design Review Required

Design review is required for changes to:

- event schemas
- graph schema
- scheduler scoring
- policy enforcement
- approval semantics
- memory promotion
- execution sandboxing
- public API contracts
- deployment security defaults
