# Codebase Accuracy Wedge

PCI's first wedge is codebase accuracy. It should answer factual questions about software systems with evidence, confidence, and freshness.

PCI should not be positioned as a product that takes autonomous action in code. It should be positioned as infrastructure that maintains verified claims about codebases.

## Problem

Large codebases become inaccurate in the places teams rely on most:

- ownership files drift from real maintainers
- service catalogs disagree with repositories
- dependency graphs miss runtime edges
- API contracts drift from implementations
- tests do not map cleanly to changed behavior
- deployments do not match the code people think is running
- security policy is not connected to code paths
- architectural decisions are scattered across documents and commits

Existing tools expose fragments. They do not maintain a persistent, reconciled model of what the codebase currently means.

## Core Product Claim

PCI maintains a codebase accuracy graph.

The graph stores claims such as:

- this service owns this endpoint
- this package depends on this library
- this file implements this contract
- this test covers this behavior
- this deployment runs this commit
- this policy applies to this path
- this owner last modified this subsystem
- this incident touched this service
- this architecture note is linked to this module

Every claim needs evidence, confidence, source authority, and freshness.

## What PCI Is Not

PCI is not:

- an autonomous coding tool
- a code generation product
- a pull request bot
- a chat interface over a repository
- a static analysis report stored once

Models can help extract candidate claims, but source systems and deterministic analysis decide authority.

## Source Authorities

The first authorities are:

- Git history for change chronology
- repository contents for declared structure
- package manifests for dependency declarations
- AST and symbol indexes for implementation facts
- CI results for test and build status
- deployment metadata for running version claims
- CODEOWNERS and ownership registries for declared ownership
- incident systems for production impact
- policy files for governance rules

Authority must be explicit. A model summary can suggest a claim, but it cannot confirm it by itself.

## First Pilot

Offer a codebase accuracy pilot.

Scope:

- connect one organization or product area
- ingest repositories, ownership files, manifests, CI results, and deployments
- create claims for services, owners, dependencies, APIs, tests, deployments, and policies
- reconcile claims when repositories or source systems change
- report stale, contradicted, missing, and low-confidence claims

Deliverables:

- codebase accuracy graph
- claim inspector with evidence and confidence
- stale ownership report
- dependency and API drift report
- deployment-to-commit accuracy report
- list of missing source authorities

## Accuracy Metrics

Measure:

- percentage of claims with authoritative evidence
- percentage of stale ownership claims
- number of contradicted deployment claims
- number of undocumented service dependencies
- number of API contract mismatches
- time to answer "who owns this?"
- time to answer "what changed?"
- time to answer "what is running?"
- time to answer "what breaks if this changes?"

These are better sales metrics than generic model quality.

## Initial UI

The control plane should prioritize:

- codebase graph explorer
- claim detail page
- source evidence panel
- confidence and freshness indicators
- drift findings
- change timeline
- reconciliation replay

The first screen should show codebase truth state, not a chat box.

## Paid Product

The paid product is codebase accuracy infrastructure.

Revenue lines:

- paid codebase accuracy pilot
- hosted codebase graph
- self-hosted deployment for private source code
- advanced repository and CI connectors
- source authority registry
- audit evidence export
- ownership drift monitoring
- API and dependency drift monitoring
- policy-to-code mapping
- support and implementation services

## Expansion Path

After codebase accuracy works, expand outward:

1. delivery state accuracy
2. incident context accuracy
3. security policy accuracy
4. compliance evidence accuracy
5. product and customer impact accuracy

The same core model applies: claims, evidence, confidence, authority, freshness, and reconciliation.

