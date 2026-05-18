#!/usr/bin/env bash
set -euo pipefail

python3 -m compileall -q services/control-plane/app

python3 - <<'PY'
from __future__ import annotations

import json
from pathlib import Path

required = [
    ".dockerignore",
    ".env.example",
    ".gitattributes",
    "README.md",
    "SECURITY.md",
    "GOVERNANCE.md",
    "docs/api/openapi.yaml",
    "docs/architecture/claim-lifecycle.md",
    "docs/security/threat-model.md",
    "docs/repository/public-protection.md",
    "docs/repository/public-release-checklist.md",
    "docs/repository/quality-gates.md",
    "proto/pci/v1/common.proto",
    "proto/pci/v1/events.proto",
    "proto/pci/v1/graph.proto",
    "proto/pci/v1/runtime.proto",
    "schemas/sql/001_core.sql",
    "deployments/docker-compose.yml",
    "deployments/helm/pci/Chart.yaml",
    "frontend/control-plane/package.json",
    "frontend/control-plane/app/page.tsx",
    ".github/CODEOWNERS",
    ".github/workflows/ci.yml",
    ".github/workflows/security.yml",
]

missing = [path for path in required if not Path(path).exists()]
if missing:
    raise SystemExit(f"missing required files: {missing}")

for path in Path("schemas/json").glob("*.json"):
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)

private_terms = [
    "".join(chr(code) for code in [109, 97, 116, 101, 110, 100, 97]),
    "".join(chr(code) for code in [103, 109, 97, 105, 108, 46, 99, 111, 109]),
    "".join(chr(code) for code in [105, 98, 105, 115, 108, 97, 98, 115, 46, 97, 105]),
]
removed_project = "".join(chr(code) for code in [111, 112, 101, 110, 99, 108, 97, 119])
blocked_pitch_terms = [
    "kubernetes for cognition",
    "linux kernel",
    "world-class",
    "revolutionary",
    "nervous system",
    "ai coworker",
    "ai employee",
    "post-agent",
    "semantic operating system",
    "cognitive operating system",
    "magic",
    "autonomous personas",
    "visionary",
    "gimmick",
    "agent marketplace",
    "mvp thesis",
    "enterprise scope",
    "success criteria",
    "durable meaning",
    "product feature",
    "execution mesh",
]

excluded_parts = {".git", ".next", ".playwright-cli", "node_modules", "__pycache__"}
excluded_slop_files = {
    Path("scripts/verify.sh"),
    Path("frontend/control-plane/package-lock.json"),
}

for path in Path(".").rglob("*"):
    if path.is_file() and not excluded_parts.intersection(path.parts):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lowered = text.casefold()
        for term in private_terms:
            if term in lowered:
                raise SystemExit(f"personal information leaked in {path}")
        if removed_project in lowered:
            raise SystemExit(f"removed project reference leaked in {path}")
        if path not in excluded_slop_files:
            for term in blocked_pitch_terms:
                if term in lowered:
                    raise SystemExit(f"blocked pitch term {term!r} found in {path}")

print("PCI scaffold verification passed")
PY
