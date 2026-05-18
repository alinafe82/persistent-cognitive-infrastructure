# Public Repository Protection

PCI is intended to be public source while maintaining strict operational
protection. Source code can be visible without exposing deployments,
credentials, private policy bundles, tenant data, or release authority.

Public contact surfaces must use project or domain aliases, not personal email
addresses. Security reports use `security@repowave.dev`.

## Public by Default

The repository may publicly include:

- source code
- deployment templates with non-secret defaults
- public architecture docs
- public API contracts
- local development fixtures
- synthetic test data
- CI configuration
- public security policy

The repository must not publicly include:

- personal maintainer email addresses
- production credentials
- tenant data
- customer data
- employee data
- private source snapshots
- raw model traces from private deployments
- private policy bundles
- vendor contracts
- deployment kubeconfigs
- signing keys

## GitHub Repository Settings

Enable these settings before announcing the public repository:

- Visibility: public
- Private vulnerability reporting: enabled
- Issues: enabled
- Discussions: optional
- Wiki: disabled unless actively maintained
- Projects: optional
- Allow forking: enabled
- Default branch: `main`
- Automatically delete head branches: enabled
- Require contributors to sign off on web-based commits when DCO is adopted

## Branch Protection for `main`

Configure `main` with:

- use owner-controlled pull requests for non-trivial changes
- do not require self-review for a single-maintainer repository
- require status checks to pass
- require branches to be up to date before merging
- require conversation resolution
- require signed commits when the organization supports it
- require linear history
- restrict who can push
- block force pushes
- block deletions
- include administrators

Required checks:

- `Verify scaffold`
- `CodeQL (python)`
- `CodeQL (javascript-typescript)`
- `Dependency review`

## Security Features

Enable:

- secret scanning
- push protection
- Dependabot alerts
- Dependabot security updates
- dependency graph
- CodeQL default setup or this repository's CodeQL workflow
- branch protection rulesets
- tag protection for `v*`

## Release Protection

Releases should use:

- protected `v*` tags
- signed tags
- release notes
- SBOM when container images are published
- immutable container image digests
- provenance attestation when available

## Public Communication Boundary

Do not describe PCI as an agent product. Public messaging should
stay specific:

- event-derived graph claims
- source authority and confidence scoring
- reconciliation against source systems
- governed execution primitives
- workload lineage and replay
- tenant isolation and policy gates
