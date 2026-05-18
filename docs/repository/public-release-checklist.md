# Public Release Checklist

Run this before publishing a release or changing repository visibility.

## Privacy

- `scripts/verify.sh` passes.
- No personal email addresses, local filesystem paths, private domains, or user names appear in publishable files.
- Git author metadata for release commits uses a project contact address.
- Ignored artifacts such as `.env`, `.next`, `.playwright-cli`, logs, keys, kubeconfigs, replay bundles, tenant data, and source snapshots are not staged.

## Repository Controls

- `SECURITY.md`, `GOVERNANCE.md`, `CODEOWNERS`, contribution rules, and issue templates are present.
- Branch protection requires CI and security checks before merging to `main`.
- Dependency review, CodeQL, Dependabot, and package audits are enabled.
- Docker build contexts exclude secrets, local artifacts, and generated output.

## Verification

- `scripts/verify.sh`
- `npm ci` in `frontend/control-plane`
- `npm run lint` in `frontend/control-plane`
- `npm run build` in `frontend/control-plane`
- `npm audit --audit-level=high` in `frontend/control-plane`
- `helm template pci deployments/helm/pci`
