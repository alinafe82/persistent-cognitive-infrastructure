# ADR 0002: Idempotent event ingestion

## Status

Accepted for the in-memory control-plane adapter.

## Context

Event producers retry after timeouts and cannot always know whether an earlier request was
accepted. Reprojecting an identical envelope can duplicate derived work, while accepting a reused
event ID with different content would violate the immutable, append-only event contract.

## Decision

The store treats an identical envelope with an existing `event_id` as an idempotent retry and
returns zero new projections. A different envelope using that ID raises an event-domain conflict.
The HTTP route maps that conflict to `409 Conflict`; transport concerns do not enter the store.

## Consequences

- Producers can safely retry byte-for-byte equivalent validated envelopes.
- Conflicting event identity is visible and fails closed.
- This in-memory adapter is process-local. A durable implementation must enforce the same rule
  atomically with event persistence and graph projection.
