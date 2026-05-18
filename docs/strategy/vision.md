# Venture Strategy

PCI is a runtime for governed operational intelligence. The bet is that teams will not manage high-value AI through chat surfaces, named workers, or prompt chains. They will need shared state, evidence, confidence, replay, policy, and reconciliation around the systems that already run the business.

This document is the forward-looking strategy. It separates what is already proven from what PCI must prove.

## The Bet

Organizations are adding model calls and tool protocols faster than they are adding control planes. That creates a gap:

- model output is useful but not authoritative
- tool calls create side effects but often lack replayable lineage
- memory is stored as text rather than validated operational state
- state changes across source systems are hard to reconcile
- governance is often added after workflows already exist

PCI should own that gap. The core category is not agents. The category is persistent context infrastructure for operational systems.

## First Market

The first wedge is software delivery intelligence for platform and engineering teams.

Start with systems that already expose structured events:

- repositories
- pull requests
- CI runs
- deployments
- incidents
- service ownership
- policy files
- security findings

This wedge is narrow enough to build and broad enough to matter. It also has strong source-of-truth systems, clear drift, audit needs, and concrete operator workflows.

The first buyer is the engineering leader or platform owner who wants a reliable view of delivery state across code, deploys, incidents, and policy.

## What Is Proven

PCI is built from infrastructure patterns that already work:

- append-only event logs
- durable workflows
- source-of-truth reconciliation
- policy decision points
- immutable audit trails
- graph-shaped operational state
- telemetry with traces, metrics, and logs
- tenant isolation
- sandboxed execution
- role-based access control

The new work is not inventing each primitive. The new work is composing these primitives around operational context, confidence, and model-assisted reasoning.

## What Must Be Proven

PCI still needs proof in four areas:

1. A focused team can build the first vertical slice without collapsing into a general platform.
2. Operators trust claim state, confidence, provenance, and reconciliation enough to use it in real workflows.
3. The workload scheduler can reduce manual investigation time without hiding important decisions.
4. The memory engine can promote useful summaries without becoming stale text storage.

If these do not hold, PCI should shrink to a narrower delivery-state control plane before expanding.

## Differentiation

PCI should win by being boring where correctness matters and adaptive where reasoning helps.

The important differences:

- claims store evidence, validity windows, source authority, and confidence
- model output is evidence, not truth
- reconciliation is a runtime loop, not a cleanup task
- every workload has replay metadata
- memory promotion requires provenance
- governance is part of workload admission
- short-lived execution graphs persist outcomes, not transcripts

The product should be judged by whether it can answer:

- what does the system believe?
- where did that belief come from?
- which source can verify it?
- how stale is it?
- what changed it?
- what would invalidate it?
- who or what approved the side effect?

## Initial Product Shape

The first usable product should be a control plane with five views:

- event timeline
- context graph explorer
- claim and confidence inspector
- reconciliation findings
- workload replay inspector

The first valuable workflow:

1. A repo, deployment, incident, or policy event arrives.
2. PCI projects the event into graph claims.
3. The scheduler detects drift, contradiction, or low confidence.
4. A bounded workload checks source systems and updates claims.
5. The operator sees the evidence, confidence change, and replay path.

## Business Model

Use open-core distribution.

Open source:

- schemas
- local runtime
- core control plane
- basic connectors
- policy and replay contracts
- Helm chart

Paid:

- managed cloud
- enterprise self-hosted support
- advanced connectors
- audit retention
- SSO and directory integration
- policy packs
- regulated deployment templates
- managed workers
- private model-provider routing

Pricing should map to operational value:

- free local development
- team tier by connected source systems and retained events
- business tier by seats, event volume, and managed workers
- regulated tier by audit retention, deployment isolation, and support response

## Moat

The moat should come from operating trust, not from a prompt library.

Defensible assets:

- source authority registry
- claim lifecycle model
- connector event normalization
- replayable workload traces
- policy packs for real operational domains
- reconciliation adapters
- public schemas that become familiar to operators
- reference deployments that pass security review

The repository should make the core architecture credible enough that advanced users self-host it, while the hosted product removes operational burden.

## Near-Term Execution

Next 30 days:

- make the repo installable from one command
- implement durable event ingestion against Postgres and NATS
- add GitHub repository and pull request ingestion
- persist graph claims from those events
- expose claim detail in the UI

Next 60 days:

- add deployment and incident event types
- implement reconciliation adapters for GitHub and CI
- persist workload traces
- add confidence and contradiction views
- publish a demo dataset

Next 90 days:

- ship a hosted preview
- onboard five design partners
- measure investigation time on real delivery questions
- add SSO, audit retention, and tenant isolation hardening
- publish a public architecture walkthrough

## Kill Criteria

The project should change direction if:

- users only want chat
- operators do not trust the claim model
- source-system reconciliation is too expensive for common workflows
- the scheduler cannot explain decisions clearly
- the first wedge does not reduce investigation time

The fallback is still useful: a delivery-state graph with provenance, confidence, and reconciliation.

## Operating Principle

Do not sell intelligence as a persona. Sell verified operational state.

