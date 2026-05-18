# Security Policy

## Supported Surface

Security reports are accepted for:

- control plane API
- event ingestion and replay
- context graph access control
- execution runtime sandboxing
- MCP integration boundaries
- model gateway routing and redaction
- reconciliation adapters
- memory compression and retention
- deployment manifests
- CI and release configuration

## Reporting a Vulnerability

Do not open a public issue for a suspected vulnerability.

Use GitHub private vulnerability reporting when enabled. If it is not enabled,
send a concise report to `security@repowave.dev` and include:

- affected component
- impact
- reproduction steps
- affected versions or commits
- relevant logs with secrets removed
- whether exploitation requires credentials or tenant access

## Disclosure Target

The project targets:

- acknowledgement within 3 business days
- initial triage within 7 business days
- fix plan for confirmed high-severity issues within 14 business days
- coordinated disclosure after a patch or mitigation is available

## Public Repository Safety Rules

This repository must never contain:

- production secrets
- personal maintainer email addresses
- private keys
- tenant data
- customer data
- employee data
- unreleased customer names
- source system access tokens
- vendor API keys
- model provider API keys
- private deployment kubeconfigs
- raw execution traces from real tenants

## Required Repository Protections

Public deployment of this repository requires:

- branch protection on `main`
- owner-controlled pull request or direct-maintainer merge flow
- required CI checks
- secret scanning enabled
- push protection enabled
- Dependabot alerts enabled
- dependency review enabled
- signed release tags for stable releases
- private vulnerability reporting enabled
- no direct pushes to `main`

## Runtime Security Principles

PCI treats workload execution as untrusted by default. Model outputs, MCP
responses, connector payloads, compressed memories, and generated code must be
validated before they can affect durable state or external systems.
