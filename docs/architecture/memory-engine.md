# Memory Engine Design

## Purpose

The memory engine converts high-volume events, traces, and interactions into reviewed summaries. It is not chat memory and it does not optimize for token reuse alone.

## Memory Layers

| Layer | Description | Retention |
| --- | --- | --- |
| Raw event | Immutable semantic event | Tenant policy |
| Execution trace | Workflow, primitive, tool, model, and policy trace | Tenant policy |
| Episode | Bounded narrative of an incident, deployment, decision, or customer event | Long-lived |
| Entity snapshot | Current summarized state of an entity | Recomputed |
| Concept memory | Abstracted recurring pattern or domain concept | Long-lived with review |
| Decision memory | Why a decision was made, evidence, approvals, and outcome | Long-lived |
| Contradiction memory | Known conflict between claims and its status | Until resolved plus audit retention |

## Compression Lifecycle

1. Detect compression opportunity by event volume, episode completion, age, or operator request.
2. Build source bundle with events, claims, evidence, traces, and graph neighborhood.
3. Score importance, novelty, policy sensitivity, and future utility.
4. Generate memory candidate.
5. Verify candidate against evidence and source claims.
6. Apply governance review for regulated or sensitive content.
7. Promote memory into graph.
8. Link memory back to source artifacts.
9. Schedule decay, review, or revalidation.

## Importance Score

```text
importance =
  business_impact
+ recurrence_value
+ policy_relevance
+ relationship_centrality
+ future_query_likelihood
+ contradiction_value
- redundancy_penalty
- sensitivity_penalty
```

## Compression Types

### Episodic Compression

Creates a timeline and causal summary for a bounded event:

- incident
- deployment
- escalation
- legal or compliance review
- architectural decision
- major customer interaction

### Hierarchical Compression

Rolls up lower-level memories into broader abstractions:

- commit events into pull request summary
- pull requests into release summary
- release summaries into service evolution memory
- incidents into reliability pattern memory

### Concept Distillation

Creates reusable domain concepts:

- "payments service deploys require dual approval"
- "customer tier determines escalation SLO"
- "service A depends on identity provider B"

### Temporal Summarization

Maintains time-windowed summaries:

- daily operational state
- weekly risk digest
- monthly policy drift report
- quarterly architecture evolution

## Contradiction Handling

Compression must never erase unresolved contradictions. Memory candidates include:

- resolved claims
- unresolved conflicts
- confidence intervals
- source authority ranking
- validation gaps

## Retention and Privacy

The memory engine supports:

- tenant retention policies
- legal holds
- selective redaction
- embedding deletion and reindexing
- right-to-delete workflows where legally applicable
- audit-preserving tombstones

