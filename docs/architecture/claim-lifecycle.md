# Claim Lifecycle

PCI treats organizational knowledge as claims with explicit state. A claim is not accepted as true just because it exists in the graph.

## States

| State | Meaning | Allowed Next States |
| --- | --- | --- |
| `asserted` | Recorded from an event, extraction, connector, operator input, or workload output | `confirmed`, `drifted`, `contradicted`, `superseded`, `expired`, `retracted` |
| `confirmed` | Checked against an authoritative source or approved evidence set | `drifted`, `contradicted`, `superseded`, `expired` |
| `drifted` | Source data changed or the claim no longer matches the current source snapshot | `confirmed`, `contradicted`, `superseded`, `expired` |
| `contradicted` | An authoritative source or stronger claim conflicts with this claim | `confirmed`, `superseded`, `retracted` |
| `superseded` | A newer claim replaces this one | terminal except audit correction |
| `expired` | Validity window or retention policy ended | terminal except audit correction |
| `retracted` | Producer or operator withdrew the claim | terminal except audit correction |

## Invariants

- Claims are append-first. State transitions should be represented by new events and graph projection updates.
- Confidence is not state. A low-confidence claim can still be asserted; a contradicted claim must carry explicit contradiction state.
- Source authority determines whether reconciliation can confirm or contradict a claim.
- Superseded, expired, and retracted claims remain queryable for replay and audit.
- Memory records may summarize claims, but they must preserve source claim ids.

## Authority Resolution

When multiple sources can speak about a field, PCI resolves authority in this order:

1. Tenant source registry field ownership.
2. Policy override for regulated or high-risk fields.
3. Source freshness SLO and adapter version.
4. Evidence strength and source snapshot integrity.
5. Human approval, if policy requires it.

If no source is authoritative for a field, reconciliation returns `not_authoritative` and leaves the claim state unchanged.

## Drift Handling

Drift creates a new event instead of mutating history in place:

```text
claim asserted -> source snapshot fetched -> drift finding emitted -> graph projection updates active state
```

The active graph view may hide superseded claims by default, but replay and audit views must expose the full transition chain.

## Operator Contract

Operators need to answer four questions for any claim:

- What source produced it?
- What source can confirm or contradict it?
- What evidence was used?
- What transition moved it into its current state?
