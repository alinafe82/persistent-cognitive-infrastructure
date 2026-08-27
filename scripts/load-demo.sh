#!/usr/bin/env bash
set -euo pipefail

api_url="${PCI_CONTROL_PLANE_URL:-http://127.0.0.1:8080}"
api_url="${api_url%/}"
occurred_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

curl -fsS "${api_url}/healthz" >/dev/null

curl -fsS -H "Content-Type: application/json" -d @- "${api_url}/v1/events" >/dev/null <<JSON
{
  "event_id": "22222222-2222-4222-8222-222222222222",
  "tenant_id": "11111111-1111-4111-8111-111111111111",
  "event_type": "pci.graph.claim",
  "schema_version": "v1",
  "source": {"source_system": "github-demo", "authority_score": 0.94},
  "occurred_at": "${occurred_at}",
  "partition_key": "demo:repository",
  "data_classification": "internal",
  "payload": {
    "label": "Repository ownership and deployment policy projected",
    "entities": [
      {"entity_id": "33333333-3333-4333-8333-333333333333", "kind": "repository", "canonical_name": "payments-api", "confidence_score": 0.94},
      {"entity_id": "44444444-4444-4444-8444-444444444444", "kind": "policy", "canonical_name": "production approval policy", "confidence_score": 0.79}
    ],
    "claims": [
      {"subject_entity_id": "33333333-3333-4333-8333-333333333333", "predicate": "governed_by", "object_entity_id": "44444444-4444-4444-8444-444444444444", "confidence_score": 0.86}
    ]
  },
  "payload_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
}
JSON

curl -fsS -H "Content-Type: application/json" -d @- "${api_url}/v1/events" >/dev/null <<JSON
{
  "event_id": "55555555-5555-4555-8555-555555555555",
  "tenant_id": "11111111-1111-4111-8111-111111111111",
  "event_type": "pci.deployment.observed",
  "schema_version": "v1",
  "source": {"source_system": "deployment-demo", "authority_score": 0.81},
  "occurred_at": "${occurred_at}",
  "partition_key": "demo:deployment",
  "data_classification": "internal",
  "payload": {
    "label": "Production deployment observed without a fresh ownership check",
    "entities": [
      {"entity_id": "66666666-6666-4666-8666-666666666666", "kind": "deployment", "canonical_name": "payments-api 2026.08.24", "confidence_score": 0.48}
    ],
    "claims": [
      {"subject_entity_id": "66666666-6666-4666-8666-666666666666", "predicate": "deploys", "object_entity_id": "33333333-3333-4333-8333-333333333333", "confidence_score": 0.48}
    ]
  },
  "payload_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
}
JSON

curl -fsS -H "Content-Type: application/json" -d @- "${api_url}/v1/workloads" >/dev/null <<'JSON'
{
  "tenant_id": "11111111-1111-4111-8111-111111111111",
  "workload_class": "governance",
  "objective": "Verify the production deployment against the current approval policy",
  "input_event_ids": [
    "22222222-2222-4222-8222-222222222222",
    "55555555-5555-4555-8555-555555555555"
  ],
  "input_entity_ids": [
    "33333333-3333-4333-8333-333333333333",
    "44444444-4444-4444-8444-444444444444",
    "66666666-6666-4666-8666-666666666666"
  ],
  "requested_depth": "deep",
  "max_data_classification": "internal"
}
JSON

echo "Demo state loaded. Open the dashboard and choose Refresh state."
