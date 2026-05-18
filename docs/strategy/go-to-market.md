# Go-To-Market Plan

The goal is to find a paid wedge before expanding the runtime. PCI should not sell a broad AI platform first. It should sell a specific operational outcome to a specific buyer.

## Initial Customer Profile

Start with engineering organizations that have:

- 50 or more engineers
- multiple repositories and services
- CI, deployment, incident, and security tools spread across systems
- audit or compliance pressure
- platform engineering ownership
- recurring questions about delivery state, service ownership, incident follow-up, or policy drift

Best early buyers:

- VP Engineering
- Head of Platform
- CTO at infrastructure-heavy SaaS companies
- Director of Developer Productivity
- Security Engineering leader with audit pressure

Avoid buyers who only want a chat interface. PCI should be sold as operational infrastructure.

## First Paid Offer

Offer a four-week delivery-state graph pilot.

Scope:

- ingest repository and pull request events
- ingest CI and deployment events when available
- model services, owners, deployments, incidents, and policies
- surface claims with evidence and confidence
- reconcile selected claims against source systems
- provide replay metadata for each automated workload

Output:

- a live control-plane view
- a written findings report
- a list of unreliable delivery-state assumptions
- a map of source systems and authority
- recommended next integrations

This is narrow enough to sell and concrete enough to evaluate.

## Buying Trigger

Lead with problems customers already feel:

- nobody knows which service is really deployed
- incident follow-up loses context
- ownership data is stale
- policy changes are not reconciled across repos
- audit evidence takes too long to assemble
- deployment state differs between tools
- teams ask the same delivery-state questions repeatedly

The pitch is not "AI that works for you." The pitch is "verified operational state across delivery systems."

## Pricing Hypothesis

Pilot:

- paid pilot: 10k to 25k
- duration: four weeks
- limited to one engineering org or platform group
- includes setup, connectors, report, and weekly review

Team subscription:

- 2k to 5k per month
- limited event retention
- standard connectors
- hosted or self-hosted dev deployment

Business subscription:

- 8k to 25k per month
- longer event retention
- multiple source systems
- audit export
- SSO
- managed workers

Regulated deployment:

- annual contract
- private deployment
- support response terms
- extended audit retention
- custom policy packs

Pricing should rise with retained events, connected systems, managed workers, and audit obligations.

## Revenue Lines

Prioritize revenue in this order:

1. Paid delivery-state graph pilots.
2. Hosted control plane subscriptions.
3. Self-hosted annual contracts.
4. Advanced connector packages.
5. Audit retention and evidence export.
6. SSO, directory, and access-control integrations.
7. Managed worker capacity for reconciliation and model calls.
8. Policy packs for regulated teams.
9. Implementation services for source-system integration.
10. Priority support and private deployment reviews.

The first cash should come from a buyer paying to solve a concrete delivery-state pain, not from a general platform subscription. The repeatable business comes after the same pilot workflow can be installed quickly and expanded across more systems.

## Product Packaging

Package the business as four products:

| Product | Buyer | What They Pay For |
| --- | --- | --- |
| Delivery State Pilot | Platform or engineering leader | Four-week mapping of repo, CI, deploy, incident, and policy state |
| PCI Cloud | Teams that want hosted infrastructure | Managed control plane, retained events, graph views, reconciliation jobs |
| PCI Self-Hosted | Security-conscious engineering orgs | Helm-based deployment, private data plane, support, upgrades |
| PCI Regulated | Teams with audit pressure | SSO, audit retention, evidence export, policy packs, private deployment review |

The pilot is the wedge. Cloud and self-hosted deployments are the compounding revenue.

## Proof Metrics

Track concrete before-and-after measurements:

- time to answer "what changed?"
- time to gather incident evidence
- number of stale ownership records found
- number of contradicted deployment claims found
- number of policy drift findings
- percentage of claims with authoritative evidence
- number of repeated questions replaced by graph queries

If these metrics do not improve, the wedge is wrong or the implementation is not useful yet.

## Demo Story

Use one believable scenario:

1. A pull request changes a service.
2. CI passes and a deployment event arrives.
3. PCI creates claims about service version, owner, deployment target, and policy state.
4. A later source-system check finds that the deployment rolled back.
5. PCI marks the prior claim as drifted, links evidence, and schedules follow-up.
6. The operator opens the claim and sees source, confidence, validity, and replay path.

This demo is stronger than a chatbot because it shows state, evidence, and correction over time.

## Outbound Message

Short version:

> We are building PCI, a control plane for verified delivery state across repos, CI, deploys, incidents, and policy. It stores claims with evidence, confidence, and reconciliation history instead of relying on chat memory. We are looking for platform teams with stale ownership, deployment drift, or audit evidence pain for a four-week pilot.

Follow-up question:

> What delivery-state question takes your team too long to answer today?

## Weekly Operating Cadence

Every week:

- talk to five platform or engineering leaders
- demo one real delivery-state workflow
- write down every repeated customer question
- convert one repeated question into a graph query or reconciliation workflow
- improve one connector or source authority rule
- publish one concrete technical note

Do not spend the week polishing broad architecture unless it helps sell or ship the first paid pilot.

## Fundraising Narrative

Raise only after there is evidence that operators want the wedge.

The narrative:

- AI adoption is creating side effects without enough state control
- PCI gives organizations a runtime for claims, evidence, confidence, replay, and reconciliation
- the first wedge is software delivery state
- the expansion path is more operational domains with the same trust model
- open source drives trust and self-hosting
- hosted and regulated deployments create revenue

## Immediate Tasks

1. Build GitHub event ingestion end to end.
2. Build the claim detail page in the UI.
3. Add one reconciliation adapter against GitHub.
4. Create a demo dataset with repo, CI, deployment, and incident events.
5. Record a short walkthrough.
6. Contact twenty platform leaders with the pilot offer.
7. Convert the first serious user into a paid pilot.
