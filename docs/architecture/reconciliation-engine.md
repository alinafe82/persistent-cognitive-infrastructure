# Reality Reconciliation Engine

## Purpose

Reality reconciliation is the structural answer to hallucination and stale context. PCI continuously validates graph claims against authoritative systems and updates confidence, contradictions, temporal validity, and memory state.

## Source Authority Registry

Every source system is registered with:

- source id
- entity types it can authoritatively validate
- fields it owns
- authentication profile
- freshness SLO
- rate limits
- reconciliation cadence
- trust score
- failure handling policy

Example:

| Source | Owns | Trust Score |
| --- | --- | --- |
| GitHub | repositories, branches, pull requests, reviews | 0.95 |
| Kubernetes API | deployments, pods, rollout state | 0.95 |
| HRIS | employee status, team membership | 0.98 |
| Okta | identities, group membership | 0.97 |
| Jira | issues, labels, workflow state | 0.90 |
| CRM | customer account state | 0.93 |

## Reconciliation Triggers

- source webhook received
- claim freshness below threshold
- contradiction set created
- confidence degradation event
- scheduled source sweep
- policy update
- high-risk workload completed
- entity ownership changed
- source adapter version changed

## Algorithm

1. Select claims needing validation.
2. Group by source authority and external identifier.
3. Fetch source snapshot with bounded timeout.
4. Compare claim object, temporal validity, and source metadata.
5. Produce one of:
   - `confirmed`
   - `drifted`
   - `contradicted`
   - `source_unavailable`
   - `not_authoritative`
   - `superseded`
6. Emit reconciliation event.
7. Update confidence and contradiction sets through graph projection.
8. Schedule follow-up workload when drift risk exceeds threshold.

## Drift Types

| Drift | Meaning | Example |
| --- | --- | --- |
| Value drift | Source field changed | Deployment version differs from graph |
| Temporal drift | Validity interval changed | Employee left company |
| Authority drift | Better source available | Manual claim superseded by HRIS |
| Policy drift | Rule changed under old decision | Deployment approval policy updated |
| Topology drift | Relationship changed | Service dependency removed |
| Confidence drift | Claim decayed below threshold | Ownership not checked in 90 days |

## Confidence Updates

Confirmed claims receive a verification multiplier. Drifted claims lose confidence and create a corrective claim. Contradicted claims join a contradiction set. Source failures lower freshness but do not automatically negate a claim.

## Reconciliation SLOs

Default targets:

- Critical production entities: 5 minutes
- Security and identity state: 15 minutes
- Customer escalation state: 15 minutes
- Repository and deployment metadata: 30 minutes
- Documentation and decisions: 24 hours
- Historical compressed memory: policy-defined

