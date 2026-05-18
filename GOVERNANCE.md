# Project Governance

## Governance Model

PCI uses maintainer-led governance with public design artifacts and protected
repository controls. The project is open to external contribution, but runtime
contracts, security boundaries, and public API stability are owned by
maintainers.

## Maintainer Responsibilities

Maintainers are responsible for:

- reviewing design changes
- enforcing security boundaries
- maintaining public roadmap clarity
- triaging vulnerabilities privately
- approving releases
- protecting branch and release integrity
- preventing assistant-framework drift
- preserving the PCI runtime vocabulary

## Decision Records

Material architecture changes should be captured as an ADR under `docs/adr/`.
An ADR is required for:

- replacing the default event bus
- replacing the default workflow engine
- changing the claim confidence model
- changing tenant isolation
- changing public API semantics
- adding a new side-effect class to the execution runtime
- changing the license or trademark policy

## Protected Branch Policy

The `main` branch represents releasable public source. It requires:

- pull request review
- CODEOWNER approval
- passing CI
- passing security checks
- linear history or squash merge
- signed commits when enforced by the host organization
- administrator enforcement when supported

## Release Policy

Stable releases require:

- changelog entry
- migration notes
- security review for changed attack surface
- signed tag
- reproducible build metadata where supported
- container image digest publication
- SBOM publication
